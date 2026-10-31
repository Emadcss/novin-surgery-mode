import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
from scripts.export_openapi import OUT, build  # noqa: E402


def _norm(path: str) -> str:
    return re.sub(r"\{[^}]*\}", "{}", path).rstrip("/")


def test_openapi_snapshot_is_current():
    assert OUT.read_text(encoding="utf-8") == build(), "docs/openapi.json قدیمی است؛ python scripts/export_openapi.py را اجرا کنید"


def test_api_md_and_code_list_the_same_routes():
    doc = (ROOT / "docs" / "API.md").read_text(encoding="utf-8")
    documented = {_norm(m) for m in re.findall(r"`(?:GET|POST|PATCH|DELETE|PUT) (/api/[^`?\s]*)", doc)}
    spec = json.loads(OUT.read_text(encoding="utf-8"))
    actual = {_norm(p) for p in spec["paths"]}
    assert actual - documented == set(), f"در API.md نیامده: {sorted(actual - documented)}"
    assert documented - actual == set(), f"در کد وجود ندارد: {sorted(documented - actual)}"
