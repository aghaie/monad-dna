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
    """اصول از اذان (فرمانِ باغبان ۲۰۲۶-۰۷-۲۲) — شش عملیاتیِ تاریخی با شناسهٔ
    دست‌نخورده + نُه اصلِ سرچشمه (اذانِ کامل، عبارت‌به‌عبارت). dna/AXIOMS.md."""
    rows = db.execute("SELECT id, text_fa FROM axioms ORDER BY id").fetchall()
    assert [t for _, t in rows] == [
        "خدا هست.",
        "قرآن کلامِ خداست.",
        "قرآن تناقض ندارد.",
        "اگر تناقضی پدیدار شد، تناقض در فهم است، هرگز درونِ قرآن.",
        "حقیقت تنها از آنِ خداست.",
        "هیچ آفریده‌ای مجاز نیست سرچشمهٔ حقیقت شود.",
        "اللهُ أكبر — خدا بزرگ‌تر است از هر فهم، هر سنجش، و هر ساخته.",
        "أشهدُ أن لا إلهَ إلا الله — جز خدا هیچ معبود و مرجعی نیست؛ سرچشمه یگانه است.",
        "أشهدُ أنَّ محمّداً رسولُ الله — قرآن از راهِ رسول رسیده است: کلامِ خدا.",
        "أشهدُ أنَّ علیّاً ولیُّ الله — فهمِ کلام سرپرست دارد؛ مناد شاگرد است، هرگز مرجع.",
        "حَیَّ على الصلاة — فهم بدونِ رجوعِ منظم نمی‌ماند؛ چرخهٔ فقر و رجوع اقامهٔ مناد است.",
        "حَیَّ على الفلاح — میوهٔ کار زنده‌ترشدن است، نه بزرگ‌ترشدن.",
        "حَیَّ على خیرِ العمل — هر تغییر باید شناخت یا امانت‌داری را بیفزاید، وگرنه ترک می‌شود.",
        "اللهُ أكبر — در پایانِ هر چرخه نیز او بزرگ‌تر است؛ ژرف‌شدن بی‌پایان است.",
        "لا إلهَ إلا الله — جز او هیچ؛ مُهرِ همهٔ دانسته‌ها و ندانسته‌ها.",
    ]


def test_counts():
    # نفس‌ها: ناوردای پیوستگی (۱..N بی‌شکاف) — بی‌نیاز از ویرایشِ دستی در هر
    # نفسِ تازه؛ پیش‌تر عددِ ثابتِ ۱۹۳ بود که هر نفس آن را می‌شکست و خطِ لوله
    # را می‌بست (کشفِ ۲۰۲۶-۰۷-۲۲).
    n, mn, mx = db.execute(
        "SELECT COUNT(*), MIN(breath_no), MAX(breath_no) FROM breaths").fetchone()
    assert (mn, mx) == (1, n), f"شکاف در شماره‌گذاریِ نفس‌ها: {mn}..{mx}, n={n}"
    assert n >= 193
    # قوی‌ها append-only ⇒ فقط رشد می‌کنند؛ کفِ یکنواخت، نه عددِ لحظه‌ای.
    assert db.execute(
        "SELECT COUNT(*) FROM findings WHERE tier='قوی'").fetchone()[0] >= 373
    # ۹مین دیدار: فرمانِ «اصول از اذان» — باغبان، ۲۰۲۶-۰۷-۲۲
    assert db.execute("SELECT COUNT(*) FROM encounters").fetchone()[0] == 9
    # ۸مین روش: گواهیِ افزایشی — مُهرِ باغبان ۲۰۲۶-۰۷-۲۲
    assert db.execute("SELECT COUNT(*) FROM method_records").fetchone()[0] == 8


def test_absence_evidence_in_db():
    row = db.execute(
        "SELECT shared_ayat FROM pair_comparisons WHERE root_a='ذنب' AND root_b='عفو'"
    ).fetchone()
    assert row == (0,), "شاهدِ غیابِ ذنب↔عفو باید ثبت باشد"


def test_open_queue():
    """بهداشتِ صف — ناوردا، نه snapshotِ ثابت.

    پیش‌تر این آزمون مجموعهٔ صفِ باز را عیناً ثابت‌کدگذاری می‌کرد؛ اما صفِ باز
    با هر نفسِ صفِ طبیعی تغییر می‌کند (ریشهٔ زیسته از باز خارج می‌شود). آن
    snapshot فقط تصادفاً سبز می‌ماند تا وقتی نفس‌ها ریشهٔ تزریقی می‌زیستند
    (تزریق‌ها در این آزمون نبودند)؛ نخستین نفسِ صفِ طبیعی (۱۹۷ هزا) آن را
    شکست. ناوردای واقعی: بهداشتِ دفترداریِ صف، مستقل از عددِ لحظه‌ای
    (کشفِ ۲۰۲۶-۰۷-۲۲ حینِ خطِ لوله)."""
    q = [r for (r,) in db.execute("SELECT root FROM queue_events WHERE event='queued'")]
    p = {r for (r,) in db.execute("SELECT root FROM queue_events WHERE event='pursued'")}
    open_q = {r for r in q if r not in p}
    # هیچ ریشه دوبار در همان نفس queued نمی‌شود (بی‌تکرارِ رویداد).
    seen = set()
    for r, bn in db.execute(
            "SELECT root, breath_no FROM queue_events WHERE event='queued'"):
        assert (r, bn) not in seen, f"رویدادِ queuedِ تکراری: {r}@{bn}"
        seen.add((r, bn))
    # صفِ باز و زیسته‌ها تهی‌اشتراک‌اند (ریشهٔ زیسته دیگر باز نیست).
    assert open_q.isdisjoint(p), f"ریشهٔ هم‌زمان باز و زیسته: {open_q & p}"
    # هر ریشهٔ زیسته‌ای که از صف آمده، رویدادِ pursued دارد (ردگیری).
    pursued_roots = {r for (r,) in db.execute("SELECT pursued_root FROM breaths")}
    assert p <= pursued_roots, f"pursuedِ بی‌نظیرِ نفس: {p - pursued_roots}"
    assert open_q, "صفِ باز نباید تهی باشد (هنوز ریشه‌های نازیسته هست)"


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
