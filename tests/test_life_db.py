"""سلامتِ بذرکاریِ life.db — هیچ حالتِ پنهانی، هیچ جدولِ مستندنشده‌ای."""
import os
import sqlite3
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

subprocess.run([sys.executable, "database/seed/seed_life.py"],
               check=True, capture_output=True)
db = sqlite3.connect("database/life.db")


def test_axioms_exact():
    rows = db.execute("SELECT id, text_fa FROM axioms ORDER BY id").fetchall()
    assert [t for _, t in rows] == [
        "خدا هست.",
        "قرآن کلامِ خداست.",
        "قرآن تناقض ندارد.",
        "اگر تناقضی پدیدار شد، تناقض در فهم است، هرگز درونِ قرآن.",
        "حقیقت تنها از آنِ خداست.",
        "هیچ آفریده‌ای مجاز نیست سرچشمهٔ حقیقت شود.",
    ]


def test_counts():
    assert db.execute("SELECT COUNT(*) FROM breaths").fetchone()[0] == 145
    assert db.execute("SELECT COUNT(*) FROM findings WHERE tier='قوی'").fetchone()[0] == 265
    assert db.execute("SELECT COUNT(*) FROM encounters").fetchone()[0] == 8
    assert db.execute("SELECT COUNT(*) FROM method_records").fetchone()[0] == 7


def test_absence_evidence_in_db():
    row = db.execute(
        "SELECT shared_ayat FROM pair_comparisons WHERE root_a='ذنب' AND root_b='عفو'"
    ).fetchone()
    assert row == (0,), "شاهدِ غیابِ ذنب↔عفو باید ثبت باشد"


def test_open_queue():
    q = [r for (r,) in db.execute("SELECT root FROM queue_events WHERE event='queued'")]
    p = {r for (r,) in db.execute("SELECT root FROM queue_events WHERE event='pursued'")}
    open_q = {r for r in q if r not in p}
    assert open_q == {"احد", "اتي", "اجر", "اخر", "اذن", "ارض", "امم", "امن", "اول", "ايي", "بشر",
                       "بصر", "بعد", "بني", "بين", "جري", "جعل", "جنن", "حرم", "حسن", "خلف", "خلق",
                       "دعو", "دنو", "ذكر", "راي", "ربب", "رجع", "رسل", "رضو", "ريب", "سجد",
                       "سخر", "سرر", "سكن", "سمع", "سمو", "سوع", "شطن", "شكر", "شيا", "ضلل",
                       "طوع", "طيب", "ثلث", "عدو", "عذب", "علم", "عمل", "عند", "عود", "غني", "غير",
                       "فضل", "قبل", "قتل", "قرب", "قلب", "قلل", "كلل", "قول", "قوم", "كتب", "كفر",
                       "كون", "لقي", "ملك", "موت", "مول", "نجو", "نزل", "نعم", "نفس",
                       "نور", "نوس", "هدي", "هزا", "وفي", "وقي", "ولي", "يمن", "يوم"}


def test_every_finding_traceable():
    """هر یافته باید به نفس، اسکریپت و رکورد بند باشد (ردگیریِ کامل)."""
    orphan = db.execute("""SELECT COUNT(*) FROM findings f
        LEFT JOIN breaths b ON f.breath_no = b.breath_no
        WHERE b.breath_no IS NULL""").fetchone()[0]
    assert orphan == 0
    missing = db.execute(
        "SELECT record_file FROM breaths").fetchall()
    for (rf,) in missing:
        assert os.path.exists(rf), f"record file missing: {rf}"


def test_no_undocumented_tables():
    tables = {t for (t,) in db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
    assert tables == {"axioms", "breaths", "findings", "pair_comparisons",
                      "queue_events", "provenance_spines", "encounters",
                      "method_records", "audit_trail"}
