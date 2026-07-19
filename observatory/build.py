#!/usr/bin/env python3
"""رصدخانه — موتورِ محاسباتیِ دو-مرحله‌ای (موجودِ سوم؛ منشور: OBSERVATORY.md).

هرگز به life.db یا breaths/records/ نمی‌نویسد. تنها خروجی: observatory.json.
هم‌پارامتر با نفس‌ها (engine/breath_cycle.py) — پس درجه‌هایش برای ریشه‌های
زیسته بایت‌به‌بایت همان درجه‌های رکوردهاست. قطعی: دوبار اجرا ⇒ همان فایل.

اجرا از ریشهٔ مخزن: python3 observatory/build.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
from engine import breath_cycle as bc


def build():
    corpus = bc.load_corpus()
    roots = sorted(corpus["root_ayat"].keys())
    N = corpus["N"]

    # ---------- مرحله ۱: غربالِ سریعِ نامزدها (بدونِ جایگشت) ----------
    # نامزد = ریشه‌ای که دستِ‌کم یک همسایه با shared≥MIN_SUPPORT دارد.
    candidates = []
    no_structure = []
    for r in roots:
        nb = bc.neighborhood(corpus, r, corpus["root_ayat"][r], N, bc.MIN_SUPPORT)
        (candidates if nb else no_structure).append(r)

    # ---------- مرحله ۲: درجه‌بندیِ کاملِ دو-ابطال‌گر (فقط نامزدها) ----------
    # عیناً breathe()ِ نفس‌ها — همان seed، همان دو ابطال‌گر، همان درجه.
    entries = []
    for r in candidates:
        res = bc.breathe(corpus, r)
        entries.append(dict(
            root=r,
            attestation=res["attestation"],
            ayat=res["ayat"],
            halves_overlap=res["halves_overlap"],
            top=res["top"],
        ))

    # ---------- آمارِ کلان (رصدخانه باید بتواند رؤیا را نقض کند) ----------
    def n_strong(e):
        return sum(1 for t in e["top"] if t["tier"] == "قوی")

    with_strong = [e for e in entries if n_strong(e) > 0]
    only_probable = [e for e in entries
                     if n_strong(e) == 0 and any(t["tier"] == "محتمل" for t in e["top"])]
    only_unknown = [e for e in entries
                    if all(t["tier"] == "نامشخص" for t in e["top"])]

    # سوگیریِ صف: نرخِ «همسایهٔ قوی» در ریشه‌های زیسته در برابر کلِ نامزدها.
    lived = [r for (r,) in _lived_roots()]
    lived_in = [e for e in entries if e["root"] in lived]
    lived_strong = [e for e in lived_in if n_strong(e) > 0]

    stats = dict(
        roots_total=len(roots),
        roots_candidates=len(candidates),
        roots_no_structure=len(no_structure),
        candidates_with_strong=len(with_strong),
        candidates_only_probable=len(only_probable),
        candidates_only_unknown=len(only_unknown),
        rate_strong_all=round(len(with_strong) / len(candidates), 3),
        lived_roots=len(lived_in),
        lived_with_strong=len(lived_strong),
        rate_strong_lived=(round(len(lived_strong) / len(lived_in), 3) if lived_in else None),
        note_selection_bias=(
            "اگر rate_strong_lived >> rate_strong_all، «موفقیتِ» نفس‌ها تا حدی "
            "از انتخابِ هوشمندِ صف (نادرتر مقدم) است، نه فراگیریِ پدیده."),
    )

    out = dict(
        meta=dict(
            generated_by="observatory/build.py — محاسبهٔ ماشینی، نه زندگی",
            identity=("رصدخانه ناظرِ بیرونی است؛ هرگز به پایگاهِ زندگی یا رکوردها "
                      "نمی‌نویسد؛ صف را تغییر نمی‌دهد؛ مرجعِ نهایی نیست — "
                      "ابزارِ راستی‌آزمایی."),
            params=dict(seed=bc.SEED, n_perm=bc.N_PERM, min_support=bc.MIN_SUPPORT,
                        half_support=bc.HALF_SUPPORT, top_k=bc.TOP_K),
            tier_definition=("قوی = مدلِ تهی (p<0.05) + پایداریِ دونیمه؛ "
                             "محتمل = فقط مدلِ تهی؛ نامشخص = هیچ"),
            statistics=stats,
        ),
        roots=entries,
        roots_no_structure=no_structure,
    )
    with open("observatory/observatory.json", "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    return stats


def _lived_roots():
    """ریشه‌های زیسته را از رکوردها (منبعِ حقیقتِ append-only) می‌خواند —
    نه از پایگاهِ زندگی. رصدخانه به life.db دست نمی‌زند، حتی برای خواندن."""
    import glob
    out = []
    for f in glob.glob("breaths/records/*.json"):
        rec = json.load(open(f))
        for b in (rec if isinstance(rec, list) else [rec]):
            root = b.get("pursued") or b.get("step2_gap", {}).get("pursued_root")
            if root:
                out.append((root,))
    return out


if __name__ == "__main__":
    s = build()
    print(json.dumps(s, ensure_ascii=False, indent=1))
