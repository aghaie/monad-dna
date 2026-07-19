"""هم‌ارزیِ موتورِ واحد با اسکریپت‌های تاریخی — رفتار نباید عوض شده باشد.

نفس‌های ۱، ۲، ۹، ۱۰، ۱۱، ۱۲ هر یک در اسکریپتِ خود با seed تازه آغاز شده‌اند؛
پس engine.breathe (با همان قراردادِ بذر) باید عیناً همان سطرها را بدهد.
(نفس‌های ۳–۸ درونِ حلقه‌های دنباله‌دارِ RNG بودند؛ هم‌ارزی‌شان از راهِ
test_records_reproducible پوشش داده می‌شود.)
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

from engine import breath_cycle as bc

CORPUS = bc.load_corpus()


def rec(name):
    with open(f"breaths/records/{name}") as f:
        return json.load(f)


def normalize_row(row):
    return dict(root=row["root"],
                shared=row.get("shared", row.get("ayat_shared")),
                expected=row["expected"], lift=row["lift"],
                p_perm=row["p_perm"],
                stable=row.get("stable", row.get("stable_across_halves")),
                tier=row["tier"])


def assert_equal(pursued, record_rows, record_overlap):
    out = bc.breathe(CORPUS, pursued)
    got = [normalize_row(r) for r in out["top"]]
    want = [normalize_row(r) for r in record_rows]
    assert got == want, f"{pursued}: rows differ\n{got}\nvs\n{want}"
    assert out["halves_overlap"] == record_overlap, f"{pursued}: overlap differs"


def test_breath_01_ilah():
    r = rec("breath_01_max_اله.json")
    assert_equal("اله", r["step5_deepening"], r["stability_halves"]["overlap"])


def test_breath_02_rahm():
    r = rec("breath_02_min_رحم.json")
    assert_equal("رحم", r["step5_deepening"], r["stability_halves"]["overlap"])


def test_breath_09_ghafr():
    r = rec("breath_09_غفر.json")
    assert_equal("غفر", r["top"], r["halves_overlap"])


def test_breath_10_hilm():
    r = rec("breath_10_حلم.json")
    assert_equal("حلم", r["top"], r["halves_overlap"])


def test_breath_11_afw():
    r = rec("breath_11_عفو.json")
    assert_equal("عفو", r["top"], r["halves_overlap"])


def test_breath_12_dhanb():
    r = rec("breath_12_ذنب.json")
    assert_equal("ذنب", r["top"], r["halves_overlap"])


def test_pair_stats_deterministic_parts():
    """جفت‌سنجی: بخش‌های قطعی (shared/expected/lift) باید با رکوردِ نفس ۱۲ یکی باشد.
    p تاریخی از جریانِ ادامه‌دارِ RNG آمده؛ موتور per-pair بذرِ تازه می‌گذارد
    (مستندشده در engine) — پس p عیناً assert نمی‌شود."""
    r = rec("breath_12_ذنب.json")
    for c in r["comparison"]:
        a, b = c["pair"].split("↔")
        got = bc.pair_stats(CORPUS, a, b)
        assert got["shared"] == c["shared"], c["pair"]
        assert got["expected"] == c["expected"], c["pair"]
        assert got["lift"] == c["lift"], c["pair"]


def test_absence_evidence_dhanb_afw():
    """شاهدِ غیاب: ذنب و عفو در کلِ کتاب هم‌آیه نیستند."""
    assert len(CORPUS["root_ayat"]["ذنب"] & CORPUS["root_ayat"]["عفو"]) == 0
    assert len(CORPUS["root_ayat"]["ذنب"] & CORPUS["root_ayat"]["حلم"]) == 0
