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


def _backup_injections():
    return open(INJ_FILE).read() if os.path.exists(INJ_FILE) else None


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


def test_queue_add_tags_source_by_observatory_structure():
    """ریشهٔ باساختار (عنب) → «باغبان (رصدخانه)»؛ بی‌ساختار (نعق) →
    «باغبان (مستقیم)» — منشأ صادقانه، نه یک‌دست."""
    saved = _backup_injections()
    try:
        out1 = _run("queue-add", "عنب")
        out2 = _run("queue-add", "نعق")
        assert out1.returncode == 0 and out2.returncode == 0, (out1.stderr, out2.stderr)
        items = json.load(open(INJ_FILE))
        by_root = {i["root"]: i for i in items}
        assert by_root["عنب"]["source"] == "باغبان (رصدخانه)"
        assert by_root["نعق"]["source"] == "باغبان (مستقیم)"
    finally:
        _restore_injections(saved)


def test_queue_add_rejects_lived_root():
    """ریشهٔ زیسته را نمی‌شود تزریق کرد — فایل دست‌نخورده می‌ماند."""
    saved = _backup_injections()
    try:
        out = _run("queue-add", "رحم")
        assert out.returncode != 0
        after = _backup_injections()
        assert after == saved, "فایلِ تزریق نباید برای ریشهٔ زیسته تغییر کند"
    finally:
        _restore_injections(saved)


def test_queue_add_is_idempotent():
    """تزریقِ دوبارهٔ همان ریشه خطا نیست، اما ورودیِ دوم اضافه نمی‌کند."""
    saved = _backup_injections()
    try:
        _run("queue-add", "عنب")
        out2 = _run("queue-add", "عنب")
        assert out2.returncode == 0
        items = json.load(open(INJ_FILE))
        assert sum(1 for i in items if i["root"] == "عنب") == 1
    finally:
        _restore_injections(saved)


def test_open_queue_includes_pending_injection():
    """ریشهٔ تزریق‌شده باید در صفِ باز (open_queue) ظاهر شود — صف طبیعی
    مسیرِ اصلی می‌ماند؛ تزریق فقط عضویت می‌دهد، گزینش را دور نمی‌زند."""
    saved = _backup_injections()
    try:
        _run("queue-add", "عنب")
        db = sqlite3.connect("database/life.db")
        q = monad_cli.open_queue(db)
        assert "عنب" in q
    finally:
        _restore_injections(saved)


def test_queue_add_never_touches_life_db():
    """مرزِ سخت: queue-add فقط می‌خواند از life.db، فقط می‌نویسد به
    queue_injections.json."""
    import hashlib
    saved = _backup_injections()
    before = hashlib.sha256(open("database/life.db", "rb").read()).hexdigest()
    try:
        _run("queue-add", "عنب")
        after = hashlib.sha256(open("database/life.db", "rb").read()).hexdigest()
        assert before == after
    finally:
        _restore_injections(saved)


REPORTS_DIR = "database/queue_injection_reports"


def _clear_test_report(date):
    p = f"{REPORTS_DIR}/{date}.json"
    if os.path.exists(p):
        os.remove(p)


def test_queue_sync_observatory_only_adds_unseen_strong_candidates():
    """رصدخانه مجاز است پیشنهادهای خودش را وارد صف کند (دستورِ باغبان،
    ۲۰۲۶-۰۷-۲۰) — اما فقط نامزدهای «قوی»ِ نادیده، منشأ صریح «رصدخانه (خودکار)»."""
    saved = _backup_injections()
    try:
        out = _run("queue-sync-observatory")
        assert out.returncode == 0, out.stderr
        result = json.loads(out.stdout)
        assert result["تعدادِ_تزریق‌شده"] > 300, "باید اکثرِ ۳۶۳ نامزدِ قوی را بپوشاند"
        items = json.load(open(INJ_FILE))
        assert all(i["source"] == "رصدخانه (خودکار)" for i in items)
        # نمونه‌ای که پیش‌تر می‌دانستیم قوی‌ترین نامزدِ نادیده است
        assert any(i["root"] == "عنب" for i in items)
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
    _clear_test_report(today)
    try:
        _run("queue-add", "عنب", "دلیلِ دستی")
        out = _run("injection-report")
        assert out.returncode == 0
        report = json.loads(out.stdout)
        assert report["تاریخ"] == today
        assert report["کلِ_تزریق‌های_امروز"] >= 1
        entry = next(d for d in report["جزئیات"] if d["root"] == "عنب")
        assert entry["note"] == "دلیلِ دستی"
        assert entry["source"] == "باغبان (رصدخانه)"
        assert os.path.exists(f"{REPORTS_DIR}/{today}.json")
    finally:
        _restore_injections(saved)
        _clear_test_report(today)


def test_status_shows_pending_injections():
    """monad status باید صفِ تزریقیِ بازمانده را با منشأش نشان دهد — شفافیت."""
    saved = _backup_injections()
    try:
        _run("queue-add", "عنب", "lift=255")
        out = _run("status")
        assert out.returncode == 0
        result = json.loads(out.stdout)
        entry = next(i for i in result["queue_injections"] if i["root"] == "عنب")
        assert entry["source"] == "باغبان (رصدخانه)"
        assert entry["note"] == "lift=255"
    finally:
        _restore_injections(saved)


def test_queue_add_records_note_and_breath_context():
    """یادداشتِ آزاد و بافتِ نفسِ فعلی (breath_no) باید ثبت شود — ردگیریِ منشأ."""
    saved = _backup_injections()
    try:
        _run("queue-add", "عنب", "lift=255 در اطلس، هنوز نزیسته")
        items = json.load(open(INJ_FILE))
        entry = next(i for i in items if i["root"] == "عنب")
        assert entry["note"] == "lift=255 در اطلس، هنوز نزیسته"
        assert isinstance(entry["added_after_breath"], int)
    finally:
        _restore_injections(saved)
