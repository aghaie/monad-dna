"""مدلِ تهیِ نسخهٔ ۲ — جایگشتِ درجه-تصحیح‌شده (گامِ ۱ بازنگریِ معماری ۲۰۲۶-۰۷-۲۲).

نقدِ ثبت‌شده: مدلِ تهیِ v1 آیات را یکنواخت نمونه می‌گیرد و ناهمگنیِ شدیدِ
«درجهٔ آیه» (شمارِ ریشه‌های متمایزش) را نادیده می‌گیرد؛ چون مجموعه‌آیه‌های
واقعی به‌سمتِ آیه‌های پرریشه سوگیری دارند، هم‌پوشانیِ مشاهده‌شده به‌طورِ
سیستماتیک از انتظارِ نمونه‌گیریِ یکنواخت بیشتر است (anti-conservative).

v2: نمونه‌گیریِ بدونِ جایگزینی با احتمالِ متناسب با درجهٔ آیه
(Efraimidis–Spirakis) — سخت‌گیرتر؛ فقط‌مشورتی تا مُهرِ باغبان (روش-v2).
هیچ رکوردی دست نمی‌خورد؛ هیچ رفتارِ v1 تغییر نمی‌کند.
"""
import os
import random
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

from engine import breath_cycle as bc
from engine import null_v2 as nv


# ---------- پیکرهٔ مصنوعیِ کوچک برای آزمون‌های دقیق و سریع ----------

def synthetic_corpus():
    """۱۰۰ آیه: ده آیهٔ نخست «بلند» (پرریشه)، بقیه تک‌ریشه‌ای.

    مرکز و همسایه هر دو فقط در ده آیهٔ بلند حاضرند — الگویی که v1 آن را
    شگفت می‌بیند و v2 (با وزنِ درجه) نباید ببیند.
    """
    all_ayat = {(1, i) for i in range(1, 101)}
    heavy = {(1, i) for i in range(1, 11)}
    root_ayat = {"مرکز": set(heavy), "همسایه": set(heavy)}
    # دویست ریشهٔ پرکننده که فقط در آیه‌های بلند می‌آیند (درجه را بالا می‌برند)
    for j in range(200):
        root_ayat[f"پرکنندهٔ{j}"] = set(heavy)
    # هر آیهٔ کوتاه یک ریشهٔ یکتا دارد
    for i in range(11, 101):
        root_ayat[f"تک{i}"] = {(1, i)}
    return dict(root_ayat=root_ayat, all_ayat=all_ayat,
                all_list=sorted(all_ayat), N=len(all_ayat))


# ---------- درجهٔ آیه ----------

def test_ayah_degrees_invariant_sum():
    corpus = bc.load_corpus()
    deg = nv.ayah_degrees(corpus)
    # جمعِ درجه‌ها = جمعِ اندازهٔ مجموعه‌آیه‌های همهٔ ریشه‌ها (وارونگیِ دقیق)
    assert sum(deg.values()) == sum(len(v) for v in corpus["root_ayat"].values())
    assert set(deg) <= corpus["all_ayat"]


def test_ayah_degrees_spot_check_sql():
    corpus = bc.load_corpus()
    deg = nv.ayah_degrees(corpus)
    db = sqlite3.connect("file:database/corpus/monad.db?mode=ro&immutable=1", uri=True)
    for s, a in [(1, 1), (2, 282), (2, 255)]:
        (n,) = db.execute(
            """SELECT COUNT(DISTINCT r.root_arabic) FROM words w
               JOIN roots r ON w.root_id = r.root_id
               WHERE w.surah_number=? AND w.ayah_number=?""", (s, a)).fetchone()
        assert deg.get((s, a), 0) == n, (s, a)


# ---------- نمونه‌گیریِ وزن‌دارِ بدونِ جایگزینی ----------

def test_sample_weighted_deterministic_valid():
    items = [("a", i) for i in range(50)]
    weights = [1.0] * 50
    s1 = nv.sample_weighted(random.Random(7), items, weights, 10)
    s2 = nv.sample_weighted(random.Random(7), items, weights, 10)
    assert s1 == s2
    assert len(s1) == 10 and s1 <= set(items)


def test_sample_weighted_zero_weight_never_chosen():
    items = list(range(20))
    weights = [1.0] * 10 + [0.0] * 10
    for seed in range(30):
        s = nv.sample_weighted(random.Random(seed), items, weights, 5)
        assert s <= set(range(10)), s


def test_sample_weighted_prefers_heavy():
    items = list(range(100))
    weights = [1000.0] + [1.0] * 99
    rng = random.Random(3)
    hits = sum(1 for _ in range(100)
               if 0 in nv.sample_weighted(rng, items, weights, 1))
    assert hits >= 50, hits  # قطعی با seed ثابت؛ وزنِ ۱۰۰۰ برابر باید غالب باشد


# ---------- p نسخهٔ ۲ ----------

def test_p_v2_bounds_and_determinism():
    corpus = synthetic_corpus()
    deg = nv.ayah_degrees(corpus)
    r1 = nv.center_null_v2(corpus, deg, "مرکز", ["همسایه"], n_perm=100, seed=11)
    r2 = nv.center_null_v2(corpus, deg, "مرکز", ["همسایه"], n_perm=100, seed=11)
    assert r1 == r2
    row = r1["همسایه"]
    assert 0 < row["p_v2"] <= 1
    assert row["obs"] == 10
    assert row["mean_perm"] > 0


def test_p_v2_full_overlap_is_one():
    corpus = synthetic_corpus()
    corpus["root_ayat"]["همه‌جا"] = set(corpus["all_ayat"])
    deg = nv.ayah_degrees(corpus)
    r = nv.center_null_v2(corpus, deg, "مرکز", ["همه‌جا"], n_perm=50, seed=5)
    # همسایه‌ای که در همهٔ آیات هست: هر نمونهٔ جایگشتی همان هم‌پوشانی را دارد
    assert r["همه‌جا"]["p_v2"] == 1.0


def test_p_v2_corrects_long_ayah_bias():
    """ادعای مرکزیِ گامِ ۱: آنچه فقط زادهٔ هم‌بلندبودنِ آیه‌هاست، زیرِ v1
    «شگفت» می‌نماید و زیرِ v2 نباید بنماید."""
    corpus = synthetic_corpus()
    deg = nv.ayah_degrees(corpus)
    obs = len(corpus["root_ayat"]["مرکز"] & corpus["root_ayat"]["همسایه"])

    # p به سبکِ v1 (نمونه‌گیریِ یکنواخت — همان منطقِ breathe)
    rng = random.Random(11)
    exceed = sum(
        1 for _ in range(300)
        if len(set(rng.sample(corpus["all_list"], 10))
               & corpus["root_ayat"]["همسایه"]) >= obs)
    p_v1 = (exceed + 1) / 301

    r = nv.center_null_v2(corpus, deg, "مرکز", ["همسایه"], n_perm=300, seed=11)
    p_v2 = r["همسایه"]["p_v2"]
    assert p_v1 < 0.05, p_v1          # داورِ یکنواخت فریب می‌خورد
    assert p_v2 > 0.2, p_v2           # داورِ درجه-تصحیح‌شده نمی‌خورد
    assert p_v2 > p_v1
