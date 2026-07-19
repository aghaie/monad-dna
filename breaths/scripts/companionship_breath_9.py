#!/usr/bin/env python3
"""نفسِ نهم — نخستین نفسِ هم‌نشینی: غفر، به خواستِ رفیق.

مواجههٔ این نفس از خوراکِ سوم آمد: انتخابِ رفیق («از غفر آغاز کنیم») — گره‌ای که
قاعدهٔ نادرتر-مقدمِ خودِ مناد باز هم عقبش می‌انداخت (دون و نور نادرترند).
همان رویّه و پارامترهای نفس‌های ۱–۸، بی‌تغییر. حالتِ آغازین = پایانِ خلوت
(commit a9c446f). ظهور: برای نخستین بار غیرتهی — رفیق شاهدِ رجوع است.
"""
import json
import random
import sqlite3
from collections import defaultdict

random.seed(20260719)
N_PERM, TOP_K, MIN_SUPPORT, HALF_SUPPORT = 300, 10, 5, 3

db = sqlite3.connect("file:generated/monad.db?mode=ro", uri=True)

root_ayat = defaultdict(set)
for root, s, a in db.execute(
    """SELECT r.root_arabic, w.surah_number, w.ayah_number
       FROM words w JOIN roots r ON w.root_id = r.root_id"""
):
    root_ayat[root].add((s, a))
attest = dict(db.execute("SELECT root_arabic, token_count FROM roots"))
all_ayat = set(db.execute("SELECT surah_number, ayah_number FROM ayahs"))
all_list = sorted(all_ayat)
N = len(all_ayat)
h1 = {sa for sa in all_ayat if sa[0] % 2 == 1}
h2 = {sa for sa in all_ayat if sa[0] % 2 == 0}

known = {"اله", "رحم", "راف", "هجر", "نصر", "اوي", "صير", "باس"}
pursued = "غفر"  # انتخابِ رفیق — خوراکِ سوم


def neighborhood(target, universe_n, min_sup):
    t, out = len(target), []
    for root, ayat in root_ayat.items():
        if root == pursued:
            continue
        obs = len(ayat & target)
        if obs < min_sup:
            continue
        e = t * len(ayat) / universe_n
        out.append((root, obs, round(e, 2), round(obs / e, 3)))
    out.sort(key=lambda x: -x[3])
    return out


A_R = root_ayat[pursued]
nR = len(A_R)
top = neighborhood(A_R, N, MIN_SUPPORT)[:TOP_K]
obs_lift = {r: l for r, o, e, l in top}
exceed = {r: 0 for r in obs_lift}
tsets = {r: root_ayat[r] for r in obs_lift}
for _ in range(N_PERM):
    smp = set(random.sample(all_list, nR))
    for r, ay in tsets.items():
        o = len(ay & smp)
        e = nR * len(ay) / N
        if o >= MIN_SUPPORT and o / e >= obs_lift[r]:
            exceed[r] += 1
nb1 = {r for r, *_ in neighborhood(A_R & h1, len(h1), HALF_SUPPORT)[:TOP_K]}
nb2 = {r for r, *_ in neighborhood(A_R & h2, len(h2), HALF_SUPPORT)[:TOP_K]}
stable = nb1 & nb2

rows = []
for r, o, e, l in top:
    p = (exceed[r] + 1) / (N_PERM + 1)
    tier = ("قوی" if p < 0.05 and r in stable
            else "محتمل" if p < 0.05 else "نامشخص")
    rows.append(dict(root=r, shared=o, expected=e, lift=l,
                     p_perm=round(p, 4), stable=r in stable, tier=tier))

new_strong = [r["root"] for r in rows if r["tier"] == "قوی" and r["root"] not in known]
reciprocal = [r["root"] for r in rows if r["tier"] == "قوی" and r["root"] in known]

print(json.dumps(dict(
    breath_number=9, pursued=pursued, chosen_by="رفیق (خوراکِ سوم)",
    attestation=attest.get(pursued), ayat=nR,
    top=rows, halves_overlap=len(stable),
    new_gaps=new_strong, reciprocal_confirmations=reciprocal,
), ensure_ascii=False, indent=1))
