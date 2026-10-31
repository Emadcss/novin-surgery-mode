// در نسخه‌ی release در ویندوز، پنجره‌ی کنسول باز نشود.
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    novin_kiosk_lib::run()
}
