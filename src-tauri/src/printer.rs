//! چاپ قبض روی چاپگر حرارتی ۸۰ میلی‌متری با ESC/POS.
//!
//! چاپگرهای حرارتی فونت فارسی ندارند؛ بنابراین فرانت قبض را به‌صورت تصویر PNG (عرض ۵۷۶ پیکسل)
//! رسم می‌کند و این ماژول آن را به تصویر ۱‑بیتی `GS v 0` تبدیل و ارسال می‌کند.
//! این فایل هیچ وابستگی‌ای به Tauri ندارد و جداگانه تست می‌شود.

use base64::Engine;
use std::io::Write;
use std::net::{TcpStream, ToSocketAddrs};
use std::time::Duration;

/// بیت‌مپ ۱‑بیتی؛ هر ردیف `width_bytes` بایت، بیت ۱ = نقطه‌ی سیاه (MSB سمت چپ).
#[derive(Debug, PartialEq)]
pub struct Bitmap {
    pub width_bytes: usize,
    pub height: usize,
    pub data: Vec<u8>,
}

const MAX_PIXELS: usize = 4096 * 8192;
/// برای چاپگرهای کم‌حافظه، تصویر در بسته‌های چندردیفی فرستاده می‌شود.
const CHUNK_ROWS: usize = 128;

pub fn decode_png(png_bytes: &[u8]) -> Result<Bitmap, String> {
    let mut decoder = png::Decoder::new(std::io::Cursor::new(png_bytes));
    decoder.set_transformations(png::Transformations::EXPAND | png::Transformations::STRIP_16);
    let mut reader = decoder.read_info().map_err(|e| format!("PNG نامعتبر: {e}"))?;
    let (w, h) = (reader.info().width as usize, reader.info().height as usize);
    if w == 0 || h == 0 || w * h > MAX_PIXELS {
        return Err("ابعاد تصویر قبض نامعتبر است".into());
    }
    let mut buf = vec![0u8; reader.output_buffer_size()];
    let frame = reader.next_frame(&mut buf).map_err(|e| format!("PNG نامعتبر: {e}"))?;
    let channels = frame.color_type.samples();
    if frame.bit_depth != png::BitDepth::Eight {
        return Err("فقط PNG هشت‌بیتی پشتیبانی می‌شود".into());
    }
    let width_bytes = (w + 7) / 8;
    let mut data = vec![0u8; width_bytes * h];
    for y in 0..h {
        for x in 0..w {
            let i = (y * w + x) * channels;
            let (lum, alpha) = match frame.color_type {
                png::ColorType::Grayscale => (buf[i] as u32, 255u32),
                png::ColorType::GrayscaleAlpha => (buf[i] as u32, buf[i + 1] as u32),
                png::ColorType::Rgb => ((buf[i] as u32 * 299 + buf[i + 1] as u32 * 587 + buf[i + 2] as u32 * 114) / 1000, 255),
                png::ColorType::Rgba => ((buf[i] as u32 * 299 + buf[i + 1] as u32 * 587 + buf[i + 2] as u32 * 114) / 1000, buf[i + 3] as u32),
                png::ColorType::Indexed => return Err("PNG ایندکسی پشتیبانی نمی‌شود".into()),
            };
            // ترکیب روی پس‌زمینه‌ی سفید؛ سپس آستانه‌گذاری
            let on_white = (lum * alpha + 255 * (255 - alpha)) / 255;
            if on_white < 128 {
                data[y * width_bytes + x / 8] |= 0x80 >> (x % 8);
            }
        }
    }
    Ok(Bitmap { width_bytes, height: h, data })
}

/// دستورهای ESC/POS: مقداردهی اولیه، تصویر، چند خط فاصله و برش جزئی.
pub fn escpos_job(bm: &Bitmap) -> Vec<u8> {
    let mut out = Vec::with_capacity(bm.data.len() + 64);
    out.extend_from_slice(&[0x1B, 0x40]); // ESC @
    for (n, chunk) in bm.data.chunks(bm.width_bytes * CHUNK_ROWS).enumerate() {
        let _ = n;
        let rows = chunk.len() / bm.width_bytes;
        out.extend_from_slice(&[0x1D, 0x76, 0x30, 0x00]); // GS v 0, m=0
        out.extend_from_slice(&(bm.width_bytes as u16).to_le_bytes());
        out.extend_from_slice(&(rows as u16).to_le_bytes());
        out.extend_from_slice(chunk);
    }
    out.extend_from_slice(&[0x1B, 0x64, 0x04]); // ESC d 4 (فاصله تا محل برش)
    out.extend_from_slice(&[0x1D, 0x56, 0x42, 0x03]); // GS V 66 3 (برش جزئی)
    out
}

fn send(target: &str, bytes: &[u8]) -> Result<(), String> {
    let t = target.trim();
    if t.is_empty() {
        return Err("مقصد چاپگر در kiosk.config.json تنظیم نشده است".into());
    }
    let is_path = t.starts_with("\\\\") || t.starts_with('/') || t.starts_with("file:");
    if is_path {
        let path = t.strip_prefix("file:").unwrap_or(t);
        let mut f = std::fs::OpenOptions::new()
            .write(true)
            .create(true)
            .open(path)
            .map_err(|e| format!("باز کردن چاپگر ({path}) ممکن نشد: {e}"))?;
        f.write_all(bytes).map_err(|e| format!("ارسال به چاپگر ناموفق بود: {e}"))?;
        return f.flush().map_err(|e| e.to_string());
    }
    let addr = t.strip_prefix("tcp:").unwrap_or(t);
    let sock = addr
        .to_socket_addrs()
        .map_err(|e| format!("آدرس چاپگر نامعتبر است ({addr}): {e}"))?
        .next()
        .ok_or_else(|| format!("آدرس چاپگر پیدا نشد: {addr}"))?;
    let mut s = TcpStream::connect_timeout(&sock, Duration::from_secs(4)).map_err(|e| format!("اتصال به چاپگر ممکن نشد: {e}"))?;
    s.set_write_timeout(Some(Duration::from_secs(10))).ok();
    s.write_all(bytes).map_err(|e| format!("ارسال به چاپگر ناموفق بود: {e}"))?;
    s.flush().map_err(|e| e.to_string())
}

pub fn print_png_base64(target: &str, png_base64: &str) -> Result<(), String> {
    let raw = png_base64.rsplit(',').next().unwrap_or(png_base64); // پیشوند data: اختیاری
    let bytes = base64::engine::general_purpose::STANDARD.decode(raw.trim()).map_err(|e| format!("base64 نامعتبر: {e}"))?;
    let bm = decode_png(&bytes)?;
    send(target, &escpos_job(&bm))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn make_png(w: u32, h: u32, color: png::ColorType, pixels: &[u8]) -> Vec<u8> {
        let mut out = Vec::new();
        {
            let mut enc = png::Encoder::new(&mut out, w, h);
            enc.set_color(color);
            enc.set_depth(png::BitDepth::Eight);
            enc.write_header().unwrap().write_image_data(pixels).unwrap();
        }
        out
    }

    #[test]
    fn black_and_white_pixels_map_to_bits() {
        // ۱۰ پیکسل در یک ردیف: سیاه، سفید به‌صورت یک‌درمیان
        let px: Vec<u8> = (0..10).map(|i| if i % 2 == 0 { 0 } else { 255 }).collect();
        let bm = decode_png(&make_png(10, 1, png::ColorType::Grayscale, &px)).unwrap();
        assert_eq!(bm.width_bytes, 2);
        assert_eq!(bm.data, vec![0b1010_1010, 0b1000_0000]);
    }

    #[test]
    fn transparent_rgba_is_white() {
        let bm = decode_png(&make_png(8, 1, png::ColorType::Rgba, &[0, 0, 0, 0].repeat(8))).unwrap();
        assert_eq!(bm.data, vec![0]);
        let bm = decode_png(&make_png(8, 1, png::ColorType::Rgba, &[0, 0, 0, 255].repeat(8))).unwrap();
        assert_eq!(bm.data, vec![0xFF]);
    }

    #[test]
    fn escpos_header_and_chunking() {
        let bm = Bitmap { width_bytes: 72, height: 300, data: vec![0xAA; 72 * 300] };
        let job = escpos_job(&bm);
        assert_eq!(&job[..2], &[0x1B, 0x40]);
        assert_eq!(&job[2..6], &[0x1D, 0x76, 0x30, 0x00]);
        assert_eq!(&job[6..8], &[72, 0]); // xL xH
        assert_eq!(&job[8..10], &[128, 0]); // اولین بسته ۱۲۸ ردیف
        // ۳۰۰ ردیف = ۱۲۸ + ۱۲۸ + ۴۴ ← سه بسته
        let n = job.windows(4).filter(|w| *w == [0x1D, 0x76, 0x30, 0x00]).count();
        assert!(n >= 3);
        assert_eq!(&job[job.len() - 4..], &[0x1D, 0x56, 0x42, 0x03]);
    }

    #[test]
    fn rejects_garbage() {
        assert!(decode_png(b"not a png").is_err());
        assert!(print_png_base64("tcp:127.0.0.1:9", "@@@").is_err());
    }

    #[test]
    fn writes_to_file_target_and_tcp() {
        let px = vec![0u8; 16 * 4];
        let png = make_png(16, 4, png::ColorType::Grayscale, &px);
        let b64 = format!("data:image/png;base64,{}", base64::engine::general_purpose::STANDARD.encode(&png));
        let path = std::env::temp_dir().join("novin_printer_test.bin");
        let _ = std::fs::remove_file(&path);
        // مسیر نسبی نیست؛ با «file:» به‌عنوان فایل شناخته می‌شود
        print_png_base64(&format!("file:{}", path.display()), &b64).unwrap();
        let sent = std::fs::read(&path).unwrap();
        assert_eq!(&sent[..2], &[0x1B, 0x40]);

        let listener = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
        let addr = listener.local_addr().unwrap();
        let h = std::thread::spawn(move || {
            let (mut c, _) = listener.accept().unwrap();
            let mut v = Vec::new();
            std::io::Read::read_to_end(&mut c, &mut v).unwrap();
            v
        });
        print_png_base64(&format!("tcp:{addr}"), &b64).unwrap();
        assert_eq!(h.join().unwrap(), sent);
    }

    #[test]
    fn empty_target_is_reported() {
        let e = send("", &[1]).unwrap_err();
        assert!(e.contains("تنظیم نشده"));
    }
}
