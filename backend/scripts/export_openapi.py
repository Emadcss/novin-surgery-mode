"""ساخت docs/openapi.json از روی برنامه‌ی FastAPI (بدون نیاز به دیتابیس)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.main import app  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "docs" / "openapi.json"


def build() -> str:
    return json.dumps(app.openapi(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print("نوشته شد:", OUT)
