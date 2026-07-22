#!/usr/bin/env python3
"""نفسِ دوازدهم — ذنب؛ و خواهشِ رفیق: «ببین آیا کتاب میان ذنب، عفو و غفر فرق می‌گذارد.»

بخش ۱: همان چرخهٔ همیشگی بر «ذنب» (گزینشِ قاعدهٔ خودِ صف).
بخش ۲: سنجشِ مقایسه‌ایِ صرفاً شمارشی — هم‌حضوریِ دوبه‌دوی {ذنب، عفو، غفر} و
        همسایه‌های نامزدِ تمایز (سوا، حبب، حلم، توب) — هیچ معنایی ساخته نمی‌شود؛
        فقط شمارش و ابطال. (روشِ اجرا: همان ابزار، بر جفت‌ها.)
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

known = {"اله", "رحم", "راف", "هجر", "نصر", "اوي", "صير", "باس", "غفر", "حلم", "عفو"}
queue = ["ذنب", "دون", "نور", "كفر"]
deliberation = sorted(((r, attest.get(r, 0)) for r in queue), key=lambda x: x[1])
pursued = deliberation[0][0]


def neighborhood(center, target, universe_n, min_sup):
    t, out = len(target), []
    for root, ayat in root_ayat.items():
        if root == center:
            continue
        obs = len(ayat & target)
        if obs < min_sup:
            continue
        e = t * len(ayat) / universe_n
        out.append((root, obs, round(e, 2), round(obs / e, 3)))
    out.sort(key=lambda x: -x[3])
    return out


# ---------- بخش ۱: چرخه بر ذنب ----------
A_R = root_ayat[pursued]
nR = len(A_R)
top = neighborhood(pursued, A_R, N, MIN_SUPPORT)[:TOP_K]
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
nb1 = {r for r, *_ in neighborhood(pursued, A_R & h1, len(h1), HALF_SUPPORT)[:TOP_K]}
nb2 = {r for r, *_ in neighborhood(pursued, A_R & h2, len(h2), HALF_SUPPORT)[:TOP_K]}
stable = nb1 & nb2
rows = []
for r, o, e, l in top:
    p = (exceed[r] + 1) / (N_PERM + 1)
    tier = ("قوی" if p < 0.05 and r in stable
            else "محتمل" if p < 0.05 else "نامشخص")
    rows.append(dict(root=r, shared=o, expected=e, lift=l,
                     p_perm=round(p, 4), stable=r in stable, tier=tier))

# ---------- بخش ۲: سنجشِ مقایسه‌ای (فقط شمارش) ----------
def pair(a, b):
    Aa, Ab = root_ayat[a], root_ayat[b]
    obs = len(Aa & Ab)
    e = len(Aa) * len(Ab) / N
    exceed_p = 0
    for _ in range(N_PERM):
        smp = set(random.sample(all_list, len(Aa)))
        if len(smp & Ab) >= obs:
            exceed_p += 1
    return dict(pair=f"{a}↔{b}", shared=obs, expected=round(e, 2),
                lift=round(obs / e, 2) if e else None,
                p_perm=round((exceed_p + 1) / (N_PERM + 1), 4))

trio = ["ذنب", "عفو", "غفر"]
candidates = ["سوا", "حبب", "حلم", "توب"]
pairs = []
for i in range(len(trio)):
    for j in range(i + 1, len(trio)):
        pairs.append(pair(trio[i], trio[j]))
for t in trio:
    for c in candidates:
        pairs.append(pair(t, c))

print(json.dumps(dict(
    breath_number=12,
    deliberation=[dict(root=r, attestation=a) for r, a in deliberation],
    pursued=pursued, ayat=nR,
    top=rows, halves_overlap=len(stable),
    new_gaps=[r["root"] for r in rows if r["tier"] == "قوی" and r["root"] not in known],
    reciprocal=[r["root"] for r in rows if r["tier"] == "قوی" and r["root"] in known],
    comparison=pairs,
), ensure_ascii=False, indent=1))
