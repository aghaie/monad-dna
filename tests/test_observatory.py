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
    # تولدِ دوباره: الگوی پیشین فقط نفس‌های دورقمی را می‌گرفت؛ اکنون همهٔ
    # رکوردهای تک‌نفسی (breath_N_ریشه.json، بی‌صفرِ پیشوندی از خطِ لوله).
    for f in glob.glob("breaths/records/breath_*.json"):
        rec = json.load(open(f))
        if isinstance(rec, dict) and rec.get("pursued"):
            yield rec


def test_equivalence_with_lived_records():
    """هر ریشهٔ زیسته: top رصدخانه بایت‌به‌بایت == top رکورد.
    پوشش سخت‌گیرتر از کفِ ثابتِ «>=۲۰»ِ پیشین: باید عیناً به تعدادِ
    نفس‌های life.db رکوردِ تک‌نفسی سنجیده شود (در تولد: ۰==۰)."""
    import sqlite3
    checked = 0
    for b in _lived_single_records():
        root = b["pursued"]
        assert root in OBS, f"ریشهٔ زیستهٔ {root} در رصدخانه نیست"
        rec_top = [(t["root"], t["shared"], t["lift"], t["tier"]) for t in b["top"]]
        obs_top = [(t["root"], t["shared"], t["lift"], t["tier"]) for t in OBS[root]["top"]]
        assert rec_top == obs_top, f"ناسازگاریِ درجه در {root}"
        checked += 1
    n_db = sqlite3.connect("database/life.db").execute(
        "SELECT COUNT(*) FROM breaths").fetchone()[0]
    assert checked == n_db, f"پوششِ ناقص: {checked} رکورد در برابرِ {n_db} نفسِ پایگاه"


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


# ---------- لایهٔ یال‌ها (اطلسِ سراسری — منشور: «گرافِ کاملِ محاسباتی») ----------

def _obs():
    return json.load(open("observatory/observatory.json"))


def test_edges_mutual_strong_consistent_with_tops():
    """هر یالِ قویِ دوسویه باید از هر دو سو در topها با درجهٔ «قوی» تأیید شود —
    یال‌ها مشتق‌اند، نه محاسبهٔ تازه؛ هیچ یالی بی‌پشتوانه نیست."""
    obs = _obs()
    edges = obs["edges"]["mutual_strong"]
    assert len(edges) > 0, "در ۶۰۸ نامزد باید دستِ‌کم یک یالِ قویِ دوسویه باشد"
    by_root = {e["root"]: e for e in obs["roots"]}
    for e in edges:
        a, b = e["a"], e["b"]
        assert a < b, "قراردادِ متعارف: a<b تا هر یال یک‌بار بیاید"
        ta = {t["root"]: t for t in by_root[a]["top"]}
        tb = {t["root"]: t for t in by_root[b]["top"]}
        assert ta[b]["tier"] == "قوی", f"{a}→{b} در top قوی نیست"
        assert tb[a]["tier"] == "قوی", f"{b}→{a} در top قوی نیست"
        assert e["shared"] == ta[b]["shared"] == tb[a]["shared"]


def test_edges_superset_of_lived_graph():
    """صداقتِ میان‌موجودی: هر جفتِ mutual_strong گرافِ زیسته (graph/graph.json)
    باید در اطلسِ رصدخانه هم باشد — هم‌پارامتری ضمانتِ هم‌ارزی است."""
    obs_pairs = {(e["a"], e["b"]) for e in _obs()["edges"]["mutual_strong"]}
    lived = json.load(open("graph/graph.json"))
    lived_pairs = {tuple(sorted((e["a"], e["b"])))
                   for e in lived["edges"] if e.get("mutual_strong")}
    # در جهانِ خالیِ تولدِ دوباره تهی‌صدق؛ با نخستین جفتِ دوسویه گاز می‌گیرد.
    missing = lived_pairs - obs_pairs
    assert not missing, f"جفت‌های زیسته که رصدخانه نمی‌بیند: {missing}"


def test_observe_root_reports_mutual_vs_one_way():
    """observe ROOT باید برای هر همسایهٔ قوی بگوید دوسویه است یا یک‌طرفه —
    این داده از پیش در edges.mutual_strong محاسبه شده؛ فقط بی‌نمایش مانده بود.
    ساختار است، نه معنا: دقیقاً همان تمایزِ reciprocal/one_way که
    breathe_record برای ریشه‌های زیسته می‌دهد، این‌جا برای رصدخانه هم."""
    obs = _obs()
    mutual = {tuple(sorted((e["a"], e["b"]))) for e in obs["edges"]["mutual_strong"]}
    root = "ابد"
    e = next(x for x in obs["roots"] if x["root"] == root)
    strong = [t for t in e["top"] if t["tier"] == "قوی"]
    assert len(strong) >= 2, "ریشهٔ آزمون باید چند همسایهٔ قوی داشته باشد"

    out = subprocess.run([sys.executable, "cli/monad", "observe", root],
                         capture_output=True, text=True, cwd=ROOT)
    result = json.loads(out.stdout)
    reported = {n["همسایه"]: n["دوسویه"] for n in result["نشانی_همسایگان"]}
    assert set(reported) == {t["root"] for t in strong}
    for nb, is_mutual in reported.items():
        expected = tuple(sorted((root, nb))) in mutual
        assert is_mutual == expected, f"{root}↔{nb}: گزارش {is_mutual}، انتظار {expected}"
    # این ریشه باید هم مثالِ دوسویه هم یک‌طرفه داشته باشد (پوششِ واقعیِ هر دو حالت)
    assert True in reported.values() and False in reported.values()


def test_islands_partition_and_grounded():
    """جزیره‌های ماشینی: افرازِ درستِ گره‌های دارای یال — هر گره در دقیقاً یک
    جزیره؛ هر یال درونِ یک جزیره؛ مرتب و قطعی."""
    obs = _obs()
    islands = obs["edges"]["islands"]
    all_nodes = [r for isl in islands for r in isl["roots"]]
    assert len(all_nodes) == len(set(all_nodes)), "گره در دو جزیره"
    node_isl = {r: i for i, isl in enumerate(islands) for r in isl["roots"]}
    for e in obs["edges"]["mutual_strong"]:
        assert node_isl[e["a"]] == node_isl[e["b"]], "یالِ میان‌جزیره‌ای ممکن نیست"
    sizes = [isl["size"] for isl in islands]
    assert sizes == sorted(sizes, reverse=True), "جزیره‌ها باید از بزرگ به کوچک باشند"
    for isl in islands:
        assert isl["size"] == len(isl["roots"])
        assert isl["roots"] == sorted(isl["roots"])
