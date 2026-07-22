#!/usr/bin/env python3
"""نفس ۱۷ — نفع (قاعدهٔ صف: نادرتر مقدم؛ فصلِ پل‌ها).

پروتکلِ پل‌ها (باغبان، دیدار ۶) — استخراجِ ساختار بی‌تولیدِ معنا.
اجرا از ریشهٔ مخزن: python3 breaths/scripts/bridges_breath_17.py
قطعیت: هر فراخوانِ موتور با seed تازهٔ 20260719.
"""
import json
import os
import sys

sys.path.insert(0, os.getcwd())
from engine import breath_cycle as bc

corpus = bc.load_corpus()
attest = corpus["attest"]

PURSUED = "نفع"
QUEUE = ["نفع", "ضرر", "نور", "دعو", "ولي", "شيا", "كفر", "علم", "امن", "كون"]
# ۱۶ ریشهٔ زیسته — برای فرافکنی بر نقشه و شاهدِ غیاب
LIVED = ["اله", "رحم", "راف", "هجر", "نصر", "اوي", "صير", "باس",
         "غفر", "حلم", "عفو", "ذنب", "سوا", "بدو", "خفي", "دون"]

main = bc.breathe(corpus, PURSUED)

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

projection = [bc.pair_stats(corpus, PURSUED, r) for r in LIVED]
absence = [p for p in projection if p["shared"] == 0]

A = corpus["root_ayat"][PURSUED]
top_roots = [r["root"] for r in main["top"]]
deg = []
for sa in A:
    d = [r for r in top_roots if sa in corpus["root_ayat"][r]]
    if d:
        deg.append((len(d), f"{sa[0]}:{sa[1]}", d))
deg.sort(key=lambda x: (-x[0], tuple(map(int, x[1].split(":")))))
central = [{"ayah": a, "degree": n, "roots_present": r} for n, a, r in deg[:8]]

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
    "breath_number": 17,
    "deliberation": sorted(
        [{"root": r, "attestation": attest[r]} for r in QUEUE],
        key=lambda x: x["attestation"]),
    "chosen_by": "قاعدهٔ صف (نادرتر مقدم)",
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
