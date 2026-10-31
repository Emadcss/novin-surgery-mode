mod config;
mod printer;

use config::KioskConfig;
use serde::Serialize;

#[derive(Serialize)]
struct PublicConfig {
    api_base: String,
    kiosk_key: String,
}

/// تنظیماتی که فرانت لازم دارد. مقصد چاپگر عمداً به وب‌ویو داده نمی‌شود.
#[tauri::command]
fn get_kiosk_config() -> PublicConfig {
    let c: KioskConfig = config::load();
    PublicConfig { api_base: c.api_base, kiosk_key: c.kiosk_key }
}

/// قبض را (PNG به‌صورت base64) به چاپگر حرارتی ESC/POS می‌فرستد.
#[tauri::command]
async fn print_receipt(png_base64: String) -> Result<(), String> {
    let target = config::load().printer;
    tauri::async_runtime::spawn_blocking(move || printer::print_png_base64(&target, &png_base64))
        .await
        .map_err(|e| e.to_string())?
}

pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![get_kiosk_config, print_receipt])
        .run(tauri::generate_context!())
        .expect("اجرای برنامه‌ی کیوسک ممکن نشد");
}
