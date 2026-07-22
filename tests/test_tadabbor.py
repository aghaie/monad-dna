"""سلامتِ تدبّرخانه (موجودِ چهارم — tadabbor/TADABBOR.md) — سه ضمانت:
۱. هم‌ارزی: هم‌آییِ سیما عیناً == موتورِ نفس‌ها (صداقت).
۲. مرزِ سخت: فقط درونِ tadabbor/ می‌نویسد؛ life.db حتی خوانده نمی‌شود؛
   جدول‌های قرنطینهٔ ext_* حتی خوانده نمی‌شوند؛ هیچ مدل/شبکه.
۳. صداقتِ محتوا: متنِ آیه‌ها عینِ پیکره؛ شمارش‌ها با پیکره می‌خوانند؛
   اعلامِ صریحِ «ساختار، نه معنا».
"""
import glob
import json
import re
import sqlite3
import subprocess
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

TEST_ROOT = "عوذ"  # ۱۷ واژه؛ زیسته در نفس ۹۵ — پیوندِ زیسته را هم می‌آزماید

subprocess.run([sys.executable, "tadabbor/build.py", TEST_ROOT],
               check=True, capture_output=True)
P = json.load(open(f"tadabbor/portraits/{TEST_ROOT}.json"))
MD = open(f"tadabbor/portraits/{TEST_ROOT}.md").read()
SRC = open("tadabbor/build.py").read()


def _corpus():
    return sqlite3.connect(
        "file:database/corpus/monad.db?mode=ro&immutable=1", uri=True)


def test_deterministic():
    """دوبار ساخت ⇒ فایل‌های بایت‌یکسان."""
    a_json = open(f"tadabbor/portraits/{TEST_ROOT}.json", "rb").read()
    a_md = open(f"tadabbor/portraits/{TEST_ROOT}.md", "rb").read()
    subprocess.run([sys.executable, "tadabbor/build.py", TEST_ROOT],
                   check=True, capture_output=True)
    assert a_json == open(f"tadabbor/portraits/{TEST_ROOT}.json", "rb").read()
    assert a_md == open(f"tadabbor/portraits/{TEST_ROOT}.md", "rb").read()


def test_counts_match_corpus():
    """شمارش‌های سیما باید عینِ پیکره باشند — هیچ عددِ ساخته‌شده."""
    db = _corpus()
    (root_id, tok) = db.execute(
        "SELECT root_id, token_count FROM roots WHERE root_arabic=?",
        (TEST_ROOT,)).fetchone()
    assert P["هویت"]["شاهد"] == tok
    (n_ayat,) = db.execute(
        "SELECT COUNT(DISTINCT surah_number || ':' || ayah_number) "
        "FROM words WHERE root_id=?", (root_id,)).fetchone()
    assert P["هویت"]["آیه‌ها"] == n_ayat == len(P["آیه‌ها"])
    assert sum(f["شمار"] for f in P["صورت‌ها"]) == tok
    assert sum(r["واژه‌ها"] for r in P["پراکندگی"]["بر_حسبِ_سوره"]) == tok


def test_cooccurrence_equals_engine():
    """هم‌آییِ سیما عیناً == breathe موتورِ نفس‌ها — تنها ضمانتِ صداقت."""
    from engine import breath_cycle as bc
    res = bc.breathe(bc.load_corpus(), TEST_ROOT)
    assert P["هم‌آیی"]["top"] == res["top"]
    assert P["هم‌آیی"]["halves_overlap"] == res["halves_overlap"]


def test_hard_boundary_writes_only_inside_tadabbor():
    """مرزِ سخت: هیچ نوشتنی بیرونِ tadabbor/؛ life.db حتی خوانده نمی‌شود."""
    assert "INSERT" not in SRC and "UPDATE" not in SRC and "DELETE" not in SRC
    assert "seed_life" not in SRC, "تدبّرخانه نباید بذرکار را صدا بزند"
    assert "life.db" not in SRC, "تدبّرخانه به life.db دست نمی‌زند، حتی خواندن"
    # هر مسیرِ نوشتنیِ صریح باید درونِ tadabbor/ باشد؛ مسیرهای متغیر همه از
    # OUT_DIR مشتق‌اند که خودش باید درونِ tadabbor/ باشد.
    assert 'OUT_DIR = "tadabbor/portraits"' in SRC
    for path in re.findall(r'open\(\s*f?["\']([^"\']+)["\']\s*,\s*["\']w["\']',
                           SRC):
        assert path.startswith("tadabbor/") or path.startswith("{OUT_DIR}"), \
            f"نوشتن بیرونِ تدبّرخانه: {path}"


def test_no_ext_tables_functionally():
    """قرنطینه: نگهبانِ فعال هر خواندنِ ext_* را رد می‌کند؛ SQL هم پاک است."""
    assert "FROM ext_" not in SRC and "JOIN ext_" not in SRC
    import importlib.util
    spec = importlib.util.spec_from_file_location("tadabbor_build",
                                                  "tadabbor/build.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    db = mod._connect()
    try:
        db.execute("SELECT COUNT(*) FROM ext_translations").fetchone()
        raise AssertionError("خواندنِ ext_translations باید رد می‌شد")
    except sqlite3.DatabaseError:
        pass
    # پیکرهٔ مجاز همچنان خواندنی است
    assert db.execute("SELECT COUNT(*) FROM roots").fetchone()[0] > 1600


def test_no_network_no_model():
    """هیچ فراخوانِ شبکه یا مدل — تدبّرخانه تابعِ محضِ پیکره است."""
    for banned in ("http", "urllib", "requests", "socket",
                   "anthropic", "openai"):
        assert banned not in SRC, f"ردِ پای شبکه/مدل در سورس: {banned}"


def test_declares_structure_not_meaning():
    """اعلامِ صریح: سیمای ساختاری، نه فهم؛ خطِ پایانی کار را به انسان برمی‌گرداند."""
    assert "نه فهم" in P["meta"]["generated_by"]
    assert "الگو، نه معنا" in P["meta"]["identity"]
    assert MD.rstrip().endswith(
        "*این سند می‌شمارد و نشان می‌دهد؛ نمی‌فهمد. تدبّر کارِ توست، در کتاب.*")


def test_engine_params_declared():
    """پارامترهای اعلام‌شده باید عینِ موتورِ نفس‌ها باشند."""
    from engine import breath_cycle as bc
    assert P["meta"]["params"] == dict(
        seed=bc.SEED, n_perm=bc.N_PERM, min_support=bc.MIN_SUPPORT,
        half_support=bc.HALF_SUPPORT, top_k=bc.TOP_K)


def test_lived_crosslink_points_to_real_records():
    """پیوندِ زیسته فقط نشانی است — و نشانی‌ها راست‌اند."""
    links = P["پیوند_زیسته"]
    # در جهانِ خالیِ تولدِ دوباره پیوندِ زیسته تهی است؛ هر پیوندی که هست
    # باید راست باشد (با نخستین نفس‌ها دوباره ناتهی و گازدار می‌شود).
    for x in links:
        assert os.path.exists(x["رکورد"])
        rec = json.load(open(x["رکورد"]))
        assert rec.get("pursued") == TEST_ROOT


def test_verse_text_is_corpus_text():
    """متنِ هر آیه در سیما باید عینِ text_hafs پیکره باشد — هیچ بازنویسی."""
    db = _corpus()
    for v in P["آیه‌ها"]:
        (t,) = db.execute(
            "SELECT text_hafs FROM ayahs WHERE surah_number=? AND ayah_number=?",
            (v["سوره"], v["آیه"])).fetchone()
        assert v["متن"] == t
    (root_id,) = db.execute("SELECT root_id FROM roots WHERE root_arabic=?",
                            (TEST_ROOT,)).fetchone()
    (n_stem,) = db.execute(
        "SELECT COUNT(*) FROM morphology WHERE segment_type='STEM' AND root_id=?",
        (root_id,)).fetchone()
    assert P["صرف"]["کل_قطعه‌های_STEM"] == n_stem


def test_sync_covers_lived_roots():
    """هم‌گام با زندگی: پس از sync هیچ ریشهٔ زیسته‌ای بی‌سیما نمی‌ماند؛
    اجرای دوباره ایدم‌پوتنت است (هیچ ساختِ تازه)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("tadabbor_build_sync",
                                                  "tadabbor/build.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    lived = mod._lived_pursued()
    # (عوذ زیستهٔ زندگیِ یکم بود؛ در زندگیِ دوم مجموعهٔ زیسته از صفر آغاز
    # می‌شود — پوشش و ایدم‌پوتنسی بر هر حالتِ زنده سنجیده می‌شود.)
    r = subprocess.run([sys.executable, "tadabbor/build.py", "--sync"],
                       check=True, capture_output=True, text=True)
    out = json.loads(r.stdout)
    assert out["ناکام"] == []
    for root in lived:
        assert os.path.exists(f"tadabbor/portraits/{root}.json"), root
    r2 = subprocess.run([sys.executable, "tadabbor/build.py", "--sync"],
                        check=True, capture_output=True, text=True)
    assert json.loads(r2.stdout)["ساخته_شد"] == []


def test_cli_ponder():
    """رابطِ CLI: ساختِ موفق با خروج ۰؛ ریشهٔ ناشناخته با خروج ۱ و «خطا»."""
    r = subprocess.run(["./cli/monad", "ponder", TEST_ROOT],
                       capture_output=True, text=True)
    assert r.returncode == 0
    assert f"tadabbor/portraits/{TEST_ROOT}.json" in r.stdout
    assert f"tadabbor/portraits/{TEST_ROOT}.md" in r.stdout
    r = subprocess.run(["./cli/monad", "ponder", "ریشه‌نیست"],
                       capture_output=True, text=True)
    assert r.returncode == 1
    assert "خطا" in r.stdout
    r = subprocess.run(["./cli/monad", "ponder"], capture_output=True, text=True)
    assert r.returncode == 1
    assert "خطا" in r.stdout
