//! خواندن `kiosk.config.json` (آدرس سرور، کلید کیوسک، مقصد چاپگر).
//! ترتیب جست‌وجو: متغیر KIOSK_CONFIG ← کنار فایل اجرایی ← پوشه‌ی جاری.

use serde::{Deserialize, Serialize};
use std::path::PathBuf;

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
#[serde(default)]
pub struct KioskConfig {
    pub api_base: String,
    pub kiosk_key: String,
    /// `tcp:HOST:PORT` یا `HOST:PORT` یا مسیر فایل/دستگاه (مثل `\\localhost\Receipt`، `\\.\USB001`، `/dev/usb/lp0`)
    pub printer: String,
}

fn candidates() -> Vec<PathBuf> {
    let mut v = Vec::new();
    if let Ok(p) = std::env::var("KIOSK_CONFIG") {
        v.push(PathBuf::from(p));
    }
    if let Ok(exe) = std::env::current_exe() {
        if let Some(dir) = exe.parent() {
            v.push(dir.join("kiosk.config.json"));
        }
    }
    v.push(PathBuf::from("kiosk.config.json"));
    v
}

pub fn load() -> KioskConfig {
    for p in candidates() {
        if let Ok(text) = std::fs::read_to_string(&p) {
            match serde_json::from_str::<KioskConfig>(&text) {
                Ok(c) => return c,
                Err(e) => eprintln!("kiosk.config.json نامعتبر است ({}): {e}", p.display()),
            }
        }
    }
    KioskConfig::default()
}
