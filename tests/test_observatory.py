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
    assert lived_pairs, "گرافِ زیسته باید جفتِ دوسویه داشته باشد"
    missing = lived_pairs - obs_pairs
    assert not missing, f"جفت‌های زیسته که رصدخانه نمی‌بیند: {missing}"


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
