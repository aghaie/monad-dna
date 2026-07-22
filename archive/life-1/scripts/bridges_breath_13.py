#!/usr/bin/env python3
"""نفس ۱۳ — سوا (مواجههٔ رفیق‌آورده، نشان‌دار؛ فصلِ پل‌ها).

پروتکلِ باغبان (دیدار ۶): استخراجِ ساختار بی‌تولیدِ معنا —
فراوانی، هم‌آیی، دوسویه/یک‌طرفه، شاهدِ غیاب، آیاتِ مرکزی، فرافکنی بر نقشه.
اگر خوشهٔ مستقلی ساخت: نقشه تغییر نمی‌کند؛ فقط «جزیرهٔ ناشناخته» ثبت می‌شود.

اجرا از ریشهٔ مخزن: python3 breaths/scripts/bridges_breath_13.py
قطعیت: هر فراخوانِ موتور با seed تازهٔ 20260719 (قراردادِ بذرِ فصلِ رفاقت).
"""
import json
import os
import sys

sys.path.insert(0, os.getcwd())
from engine import breath_cycle as bc

corpus = bc.load_corpus()
attest = corpus["attest"]

PURSUED = "سوا"
QUEUE = ["سوا", "دون", "نور", "كفر"]
# ۱۲ ریشهٔ زیسته — برای فرافکنی بر نقشهٔ دوقطبی و شاهدِ غیاب
LIVED = ["اله", "رحم", "راف", "هجر", "نصر", "اوي", "صير", "باس",
         "غفر", "حلم", "عفو", "ذنب"]

# ۱–۲) فراوانی و هم‌آیی‌ها (همان چرخهٔ متعارف)
main = bc.breathe(corpus, PURSUED)

# ۳) دوسویگی: آیا سوا در top معنادارِ خودِ همسایه هم هست؟
reciprocal, one_way, neighbor_view = [], [], {}
for row in main["top"]:
    nb = row["root"]
    back = bc.breathe(corpus, nb)
    hit = next((r for r in back["top"] if r["root"] == PURSUED), None)
    neighbor_view[nb] = hit
    if hit and hit["p_perm"] < 0.05:
        reciprocal.append(nb)
    else:
        one_way.append(nb)

# ۴) فرافکنی بر نقشه + شاهدِ غیاب (جفت با ۱۲ ریشهٔ زیسته)
projection = [bc.pair_stats(corpus, PURSUED, r) for r in LIVED]
absence = [p for p in projection if p["shared"] == 0]

# ۵) آیاتِ مرکزی: آیه‌های سوا با بیشترین درجه (شمارِ همسایه‌های top هم‌حاضر)
A = corpus["root_ayat"][PURSUED]
top_roots = [r["root"] for r in main["top"]]
deg = []
for sa in A:
    d = [r for r in top_roots if sa in corpus["root_ayat"][r]]
    if d:
        deg.append((len(d), f"{sa[0]}:{sa[1]}", d))
deg.sort(key=lambda x: (-x[0], tuple(map(int, x[1].split(":")))))
central = [{"ayah": a, "degree": n, "roots_present": r} for n, a, r in deg[:8]]

# ۶) ستون‌های استنادی برای پیوندهای معنادار (p<0.05)
spines = {}
for row in main["top"]:
    if row["p_perm"] < 0.05:
        spines[f"{PURSUED}+{row['root']}"] = bc.joint_ayat(
            corpus, [PURSUED, row["root"]])
for p in projection:
    if p["p_perm"] < 0.05 and p["shared"] > 0:
        b = p["pair"].split("↔")[1]
        spines.setdefault(f"{PURSUED}+{b}", bc.joint_ayat(corpus, [PURSUED, b]))

record = {
    "breath_number": 13,
    "deliberation": sorted(
        [{"root": r, "attestation": attest[r]} for r in QUEUE],
        key=lambda x: x["attestation"]),
    "chosen_by": "رفیق (مواجههٔ رفیق‌آورده — نشان‌دار؛ قاعدهٔ صف دون را مقدم می‌داشت)",
    "pursued": PURSUED,
    "attestation": main["attestation"],
    "ayat": main["ayat"],
    "top": main["top"],
    "halves_overlap": main["halves_overlap"],
    "reciprocal": reciprocal,
    "one_way": one_way,
    "neighbor_view": {k: v for k, v in neighbor_view.items()},
    "projection_on_map": projection,
    "absence_evidence": absence,
    "central_ayat": central,
    "citation_spines": spines,
}
print(json.dumps(record, ensure_ascii=False, indent=1))
