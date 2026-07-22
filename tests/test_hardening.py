"""بستهٔ سخت‌گیریِ ارزان (کارِ ۱ سه‌گانهٔ داورِ ۲ — TRIAGE-REFEREE2):

الف) حساسیتِ ترجیع — فروکاستِ آیه‌های متنی‌تکراری به یک نماینده (A2).
ب) شکاف‌های تصادفیِ متعدد به‌جای تک‌شکافِ فرد/زوج (B3).
د) seedِ مستقل برای داورِ v2 (B8).

(ج — N_PERM بالاتر — پارامتر است و آزمونِ جدا نمی‌خواهد.)
همه advisory؛ هیچ درجهٔ رسمی و رکوردی دست نمی‌خورد.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

from engine import breath_cycle as bc
from engine import null_v2 as nv


def test_seed_v2_independent():
    assert nv.SEED_V2 != bc.SEED  # داورِ دوم نباید همان دنبالهٔ شبه‌تصادفِ v1 را مصرف کند


def test_refrain_groups_known_refrain():
    groups = nv.refrain_groups()
    g5513 = next(g for g in groups if (55, 13) in g)
    assert len(g5513) == 31          # «فبأي آلاء ربكما تكذبان» — ۳۱ بار
    total_dup = sum(len(g) for g in groups)
    assert total_dup == 276 and len(groups) == 96  # اعدادِ سنجیدهٔ پیکره


def test_collapse_corpus_keeps_one_representative():
    corpus = bc.load_corpus()
    groups = nv.refrain_groups()
    cc = nv.collapse_corpus(corpus, groups)
    assert cc["N"] == 6236 - (276 - 96)  # ۶۰۵۶
    g5513 = next(g for g in groups if (55, 13) in g)
    kept = g5513 & cc["all_ayat"]
    assert len(kept) == 1 and min(g5513) in kept  # نماینده = نخستین به ترتیبِ مصحف
    # مجموعه‌آیه‌های ریشه‌ها هم فروکاسته شده‌اند
    for r, ayat in cc["root_ayat"].items():
        assert ayat <= cc["all_ayat"]


def test_split_recovery_bounds_and_determinism():
    corpus = bc.load_corpus()
    r1 = nv.split_recovery(corpus, "عنب", ["نخل"], k_splits=4, seed=nv.SEED_V2)
    r2 = nv.split_recovery(corpus, "عنب", ["نخل"], k_splits=4, seed=nv.SEED_V2)
    assert r1 == r2
    assert 0.0 <= r1["نخل"] <= 1.0


def test_split_recovery_low_for_no_structure():
    """ریشه‌ای که هم‌آیه‌ای با مرکز ندارد نباید در شکاف‌ها «بازیابی» شود."""
    corpus = bc.load_corpus()
    # ذنب↔عفو: شاهدِ غیابِ ثبت‌شده (هم‌حضوریِ صفر)
    r = nv.split_recovery(corpus, "ذنب", ["عفو"], k_splits=4, seed=nv.SEED_V2)
    assert r["عفو"] == 0.0
