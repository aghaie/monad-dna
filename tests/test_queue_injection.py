"""سیاستِ صف (دستورِ باغبان، ۲۰۲۶-۰۷-۲۰):

  «صف طبیعی مسیر اصلی است. رصدخانه فقط پیشنهاد می‌دهد. باغبان در صورتِ لزوم
   یک پیشنهاد را وارد صف می‌کند. منشأ هر انتخاب هم ثبت می‌شود.»

پیاده‌سازی: `./cli/monad queue-add ROOT` یک ریشه را در یک دفترچهٔ جداگانه و
append-only (`database/queue_injections.json`) ثبت می‌کند — نه در life.db/
seed_life.py (که مشتقِ قطعیِ رکوردهاست و کارِ رسمی‌سازی است، نه این ابزار).
`open_queue` این دفترچه را با صفِ طبیعی ادغام می‌کند؛ گزینشِ نهایی همچنان با
قاعدهٔ صف (نادرتر مقدم) است — تزریق فقط عضویت می‌دهد، صف را دور نمی‌زند.
منشأ خودکار تشخیص داده می‌شود: اگر ریشه در اطلسِ رصدخانه ساختار دارد →
«باغبان (رصدخانه)»؛ وگرنه «باغبان (مستقیم)».
"""
import importlib.util
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from importlib.machinery import SourceFileLoader

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

INJ_FILE = "database/queue_injections.json"

_loader = SourceFileLoader("monad_cli_qi", os.path.join(ROOT, "cli/monad"))
_spec = importlib.util.spec_from_loader("monad_cli_qi", _loader)
monad_cli = importlib.util.module_from_spec(_spec)
_loader.exec_module(monad_cli)


def _read_injections():
    """خواندنِ صرف — بدونِ تغییرِ فایل (برای سنجش‌های میانِ آزمون)."""
    return open(INJ_FILE).read() if os.path.exists(INJ_FILE) else None


def _backup_injections():
    """پشتیبان از حالتِ واقعیِ زیستهٔ فایل، سپس آن را برای آزمون خالی می‌کند —
    وگرنه آزمون‌ها با تزریق‌های واقعیِ تولیدشده (مثلِ queue-sync-observatory
    که در تولید اجرا شده) تداخل می‌کنند. فقط یک‌بار در ابتدای هر آزمون فراخوان
    شود؛ برای سنجشِ میانی از _read_injections استفاده کن. در finally با
    _restore_injections دقیقاً همان حالتِ واقعی بازمی‌گردد."""
    saved = _read_injections()
    if os.path.exists(INJ_FILE):
        os.remove(INJ_FILE)
    return saved


def _restore_injections(saved):
    if saved is None:
        if os.path.exists(INJ_FILE):
            os.remove(INJ_FILE)
    else:
        with open(INJ_FILE, "w") as f:
            f.write(saved)


def _run(*args):
    return subprocess.run([sys.executable, "cli/monad", *args],
                          capture_output=True, text=True, cwd=ROOT)


def _pick_unlived_root(with_structure):
    """ریشهٔ آزمونِ پویا — نه هاردکد. life.db همیشه رشد می‌کند (هر نفس یک
    ریشهٔ تازه را می‌بلعد)، پس یک نامِ ثابت مثلِ «عنب» دیر یا زود زیسته و
    نامعتبر می‌شود (دقیقاً همین اتفاق برایِ نفسِ ۵۳ افتاد). این تابع همیشه
    یک ریشهٔ واقعاً نزیستهٔ کنونی را برمی‌گزیند — قطعی (اولین مواردِ
    مرتب‌شده)، نه تصادفی."""
    db = sqlite3.connect("database/life.db")
    lived = {r for (r,) in db.execute("SELECT pursued_root FROM breaths")}
    obs = json.load(open("observatory/observatory.json"))
    if with_structure:
        cands = sorted(e["root"] for e in obs["roots"]
                       if e["root"] not in lived and e["top"])
    else:
        cands = sorted(r for r in obs["roots_no_structure"] if r not in lived)
    assert cands, "هیچ ریشهٔ نزیستهٔ مناسبی نماند — این خودش نشانه‌ای‌ست"
    return cands[0]


ROOT_A = _pick_unlived_root(True)   # باساختار → «باغبان (رصدخانه)»
ROOT_B = _pick_unlived_root(False)  # بی‌ساختار → «باغبان (مستقیم)»


def test_queue_add_tags_source_by_observatory_structure():
    """ریشهٔ باساختار (عنب) → «باغبان (رصدخانه)»؛ بی‌ساختار (نعق) →
    «باغبان (مستقیم)» — منشأ صادقانه، نه یک‌دست."""
    saved = _backup_injections()
    try:
        out1 = _run("queue-add", ROOT_A)
        out2 = _run("queue-add", ROOT_B)
        assert out1.returncode == 0 and out2.returncode == 0, (out1.stderr, out2.stderr)
        items = json.load(open(INJ_FILE))
        by_root = {i["root"]: i for i in items}
        assert by_root[ROOT_A]["source"] == "باغبان (رصدخانه)"
        assert by_root[ROOT_B]["source"] == "باغبان (مستقیم)"
    finally:
        _restore_injections(saved)


def test_queue_add_rejects_lived_root():
    """ریشهٔ زیسته را نمی‌شود تزریق کرد — فایل دست‌نخورده می‌ماند."""
    import pytest
    db = sqlite3.connect("database/life.db")
    row = db.execute("SELECT pursued_root FROM breaths LIMIT 1").fetchone()
    if row is None:
        pytest.skip("جهانِ خالیِ تولدِ دوباره — با نخستین نفسِ زندگیِ دوم فعال می‌شود")
    lived_root = row[0]
    saved = _backup_injections()
    before_test = _read_injections()  # حالتِ خالی‌شدهٔ ابتدای آزمون
    try:
        out = _run("queue-add", lived_root)
        assert out.returncode != 0
        after = _read_injections()
        assert after == before_test, "فایلِ تزریق نباید برای ریشهٔ زیسته تغییر کند"
    finally:
        _restore_injections(saved)


def test_queue_add_is_idempotent():
    """تزریقِ دوبارهٔ همان ریشه خطا نیست، اما ورودیِ دوم اضافه نمی‌کند."""
    saved = _backup_injections()
    try:
        _run("queue-add", ROOT_A)
        out2 = _run("queue-add", ROOT_A)
        assert out2.returncode == 0
        items = json.load(open(INJ_FILE))
        assert sum(1 for i in items if i["root"] == ROOT_A) == 1
    finally:
        _restore_injections(saved)


def test_open_queue_includes_pending_injection():
    """ریشهٔ تزریق‌شده باید در صفِ باز (open_queue) ظاهر شود — صف طبیعی
    مسیرِ اصلی می‌ماند؛ تزریق فقط عضویت می‌دهد، گزینش را دور نمی‌زند."""
    saved = _backup_injections()
    try:
        _run("queue-add", ROOT_A)
        db = sqlite3.connect("database/life.db")
        q = monad_cli.open_queue(db)
        assert ROOT_A in q
    finally:
        _restore_injections(saved)


def test_queue_add_never_touches_life_db():
    """مرزِ سخت: queue-add فقط می‌خواند از life.db، فقط می‌نویسد به
    queue_injections.json."""
    import hashlib
    saved = _backup_injections()
    before = hashlib.sha256(open("database/life.db", "rb").read()).hexdigest()
    try:
        _run("queue-add", ROOT_A)
        after = hashlib.sha256(open("database/life.db", "rb").read()).hexdigest()
        assert before == after
    finally:
        _restore_injections(saved)


REPORTS_DIR = "database/queue_injection_reports"


def _backup_report(date):
    """پشتیبان از گزارشِ واقعیِ همان تاریخ (اگر باشد) و حذفِ موقتش — گزارشِ
    امروز ممکن است گزارشِ واقعیِ تولیدشده باشد، نه صرفاً بقایای آزمون؛
    باید دقیقاً مثلِ queue_injections.json بازگردانده شود، نه برای همیشه حذف."""
    p = f"{REPORTS_DIR}/{date}.json"
    saved = open(p).read() if os.path.exists(p) else None
    if os.path.exists(p):
        os.remove(p)
    return saved


def _restore_report(date, saved):
    p = f"{REPORTS_DIR}/{date}.json"
    if saved is None:
        if os.path.exists(p):
            os.remove(p)
    else:
        os.makedirs(REPORTS_DIR, exist_ok=True)
        with open(p, "w") as f:
            f.write(saved)


def _expected_unseen_strong_count():
    """شمارشِ مستقلِ نامزدهای «قوی»ِ نادیده — نه هاردکد. مثلِ
    _pick_unlived_root: life.db همیشه رشد می‌کند (هر نفس یک ریشهٔ تازه را
    از میانِ نامزدهای رصدخانه هم می‌بلعد)، پس هر عددِ ثابت دیر یا زود
    نادرست می‌شود (دقیقاً همین اتفاق در نفسِ ۱۰۴ افتاد: ۳۰۰ شد، نه >۳۰۰).
    این تابع همان منطقِ cmd_queue_sync_observatory را مستقلاً بازمی‌سازد."""
    db = sqlite3.connect("database/life.db")
    lived = {r for (r,) in db.execute("SELECT pursued_root FROM breaths")}
    obs = json.load(open("observatory/observatory.json"))
    return sum(1 for e in obs["roots"]
              if e["root"] not in lived and any(t["tier"] == "قوی" for t in e["top"]))


def test_queue_sync_observatory_only_adds_unseen_strong_candidates():
    """رصدخانه مجاز است پیشنهادهای خودش را وارد صف کند (دستورِ باغبان،
    ۲۰۲۶-۰۷-۲۰) — اما فقط نامزدهای «قوی»ِ نادیده، منشأ صریح «رصدخانه (خودکار)»."""
    expected = _expected_unseen_strong_count()
    saved = _backup_injections()
    try:
        out = _run("queue-sync-observatory")
        assert out.returncode == 0, out.stderr
        result = json.loads(out.stdout)
        assert result["تعدادِ_تزریق‌شده"] == expected, \
            f"باید دقیقاً {expected} نامزدِ قوی‌ِ نادیدهٔ کنونی را بپوشاند"
        items = json.load(open(INJ_FILE))
        assert all(i["source"] == "رصدخانه (خودکار)" for i in items)
        # نمونه‌ای که پیش‌تر می‌دانستیم قوی‌ترین نامزدِ نادیده است
        assert any(i["root"] == ROOT_A for i in items)
    finally:
        _restore_injections(saved)


def test_queue_sync_observatory_is_idempotent():
    """اجرای دوباره چیزِ تکراری اضافه نمی‌کند."""
    saved = _backup_injections()
    try:
        _run("queue-sync-observatory")
        n1 = len(json.load(open(INJ_FILE)))
        out2 = _run("queue-sync-observatory")
        n2 = len(json.load(open(INJ_FILE)))
        assert out2.returncode == 0
        assert n1 == n2
    finally:
        _restore_injections(saved)


def test_queue_sync_observatory_never_touches_life_db():
    """مرزِ سخت: فقط queue_injections.json نوشته می‌شود."""
    import hashlib
    saved = _backup_injections()
    before = hashlib.sha256(open("database/life.db", "rb").read()).hexdigest()
    try:
        _run("queue-sync-observatory")
        after = hashlib.sha256(open("database/life.db", "rb").read()).hexdigest()
        assert before == after
    finally:
        _restore_injections(saved)


def test_pursuit_selection_untouched_by_bulk_injection():
    """«هیچ ریشه‌ای حق ندارد خارج از قواعدِ انتخاب اجرا شود»: پس از تزریقِ
    انبوه، breaths (نفس‌های واقعاً زیسته) هیچ تغییری نمی‌کند — تزریق فقط
    عضویت می‌دهد؛ گزینش/اجرا فقط با breathe/breathe-record است."""
    saved = _backup_injections()
    db = sqlite3.connect("database/life.db")
    before = db.execute("SELECT COUNT(*) FROM breaths").fetchone()[0]
    try:
        _run("queue-sync-observatory")
        after = sqlite3.connect("database/life.db").execute(
            "SELECT COUNT(*) FROM breaths").fetchone()[0]
        assert before == after
    finally:
        _restore_injections(saved)


def test_injection_report_groups_by_source_with_reason():
    """گزارشِ روزانه: کلِ تزریق‌ها، بر حسبِ منشأ، و دلیلِ (note) هر کدام."""
    saved = _backup_injections()
    today = monad_cli._today()
    saved_report = _backup_report(today)
    try:
        _run("queue-add", ROOT_A, "دلیلِ دستی")
        out = _run("injection-report")
        assert out.returncode == 0
        report = json.loads(out.stdout)
        assert report["تاریخ"] == today
        assert report["کلِ_تزریق‌های_امروز"] >= 1
        entry = next(d for d in report["جزئیات"] if d["root"] == ROOT_A)
        assert entry["note"] == "دلیلِ دستی"
        assert entry["source"] == "باغبان (رصدخانه)"
        assert os.path.exists(f"{REPORTS_DIR}/{today}.json")
    finally:
        _restore_injections(saved)
        _restore_report(today, saved_report)


def test_status_shows_pending_injections():
    """monad status باید صفِ تزریقیِ بازمانده را با منشأش نشان دهد — شفافیت."""
    saved = _backup_injections()
    try:
        _run("queue-add", ROOT_A, "lift=255")
        out = _run("status")
        assert out.returncode == 0
        result = json.loads(out.stdout)
        entry = next(i for i in result["queue_injections"] if i["root"] == ROOT_A)
        assert entry["source"] == "باغبان (رصدخانه)"
        assert entry["note"] == "lift=255"
    finally:
        _restore_injections(saved)


def test_queue_add_records_note_and_breath_context():
    """یادداشتِ آزاد و بافتِ نفسِ فعلی (breath_no) باید ثبت شود — ردگیریِ منشأ."""
    saved = _backup_injections()
    try:
        _run("queue-add", ROOT_A, "lift=255 در اطلس، هنوز نزیسته")
        items = json.load(open(INJ_FILE))
        entry = next(i for i in items if i["root"] == ROOT_A)
        assert entry["note"] == "lift=255 در اطلس، هنوز نزیسته"
        assert isinstance(entry["added_after_breath"], int)
    finally:
        _restore_injections(saved)
