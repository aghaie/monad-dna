"""سلامتِ رصدخانه (موجودِ سوم) — دو ضمانت:
۱. هم‌ارزی: درجه‌های رصدخانه برای ریشه‌های زیسته == درجه‌های رکورد (صداقت).
۲. مرزِ سخت: رصدخانه هرگز به life.db یا breaths/records/ نمی‌نویسد.
"""
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# رصدخانه را قطعی بساز (چند ثانیه)
subprocess.run([sys.executable, "observatory/build.py"],
               check=True, capture_output=True)
OBS = {e["root"]: e for e in json.load(open("observatory/observatory.json"))["roots"]}


def _lived_single_records():
    for f in glob.glob("breaths/records/breath_[0-9][0-9]_*.json"):
        rec = json.load(open(f))
        if isinstance(rec, dict) and rec.get("pursued"):
            yield rec


def test_equivalence_with_lived_records():
    """هر ریشهٔ زیسته: top رصدخانه بایت‌به‌بایت == top رکورد."""
    checked = 0
    for b in _lived_single_records():
        root = b["pursued"]
        assert root in OBS, f"ریشهٔ زیستهٔ {root} در رصدخانه نیست"
        rec_top = [(t["root"], t["shared"], t["lift"], t["tier"]) for t in b["top"]]
        obs_top = [(t["root"], t["shared"], t["lift"], t["tier"]) for t in OBS[root]["top"]]
        assert rec_top == obs_top, f"ناسازگاریِ درجه در {root}"
        checked += 1
    assert checked >= 20, "باید دستِ‌کم ۲۰ ریشهٔ زیسته سنجیده شود"


def test_deterministic():
    """دوبار ساخت ⇒ فایلِ بایت‌یکسان."""
    a = open("observatory/observatory.json", "rb").read()
    subprocess.run([sys.executable, "observatory/build.py"],
                   check=True, capture_output=True)
    b = open("observatory/observatory.json", "rb").read()
    assert a == b, "رصدخانه قطعی نیست"


def test_hard_boundary_no_writes_to_life():
    """مرزِ سخت: رصدخانه فقط به observatory/ می‌نویسد؛ خواندنِ رکوردها مجاز است،
    اما هیچ نوشتنِ پایگاهِ زندگی/بذرکاری/رکورد نباید باشد."""
    import re
    src = open("observatory/build.py").read()
    assert "INSERT" not in src, "رصدخانه نباید به پایگاه بنویسد"
    assert "seed_life" not in src, "رصدخانه نباید بذرکار را صدا بزند"
    assert 'connect("database/life.db")' not in src, "اتصالِ نوشتنی به life.db ممنوع"
    # هر open(..., "w") باید درونِ observatory/ باشد
    for path in re.findall(r'open\(\s*["\']([^"\']+)["\']\s*,\s*["\']w["\']\)', src):
        assert path.startswith("observatory/"), f"نوشتن بیرونِ رصدخانه: {path}"


def test_observatory_declares_itself_computation():
    """رصدخانه باید صریح خود را «محاسبه، نه زندگی» بنامد."""
    meta = json.load(open("observatory/observatory.json"))["meta"]
    assert "محاسبه" in meta["generated_by"]
    assert "مرجعِ نهایی نیست" in meta["identity"]
