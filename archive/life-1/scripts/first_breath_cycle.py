#!/usr/bin/env python3
"""نخستین نفسِ مناد — یک دورِ کاملِ چرخهٔ فقر و رجوع، روی بسترِ واقعی.

گام‌ها (از سندِ قلب):
  ۱ مواجهه → ۲ سنجشِ شکاف → ۳ اقرار → ۴ رجوع → ۵ ژرفش → ۶ ظهور → ۷ تکرار

روشِ اجرای گام‌های ۲/۴ (لایهٔ اجرا؛ انضباطِ موجودِ پروژه، نه طراحیِ نو):
  - خویشاوندیِ رابطه‌ای = هم‌حضوریِ ریشه‌ها در سطحِ آیه، سنجیده با lift نسبت به
    انتظارِ بسامدی.
  - ابطال‌گر ۱: مدلِ تهیِ جایگشتی (نمونه‌گیریِ مجموعه‌آیه‌های تصادفیِ هم‌اندازه).
  - ابطال‌گر ۲: پایداریِ دونیمه (سوره‌های فرد/زوج).
  - درجه: قوی = گذر از هر دو؛ محتمل = فقط مدلِ تهی؛ نامشخص = هیچ.

ورودی: generated/monad.db (فقط-خواندنی). خروجی: JSON روی stdout.
Seed ثابت برای بازتولیدپذیری.
"""
import json
import random
import sqlite3
import sys
from collections import defaultdict

random.seed(20260719)
# نفس ۱: RULE=max (پرشاهدترین ریشه — قاعدهٔ آغازینِ تزریقی؛ در عمل شکست خورد)
# نفس ۲: RULE=min (کم‌شاهدترین ریشه — اصلاحِ آموخته از نفس ۱: سیگنال در نادر است)
RULE = sys.argv[1] if len(sys.argv) > 1 else "max"
DB = "generated/monad.db"
N_PERM = 300
TOP_K = 10
MIN_SUPPORT = 5

db = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)

# ---------- گام ۱ — مواجهه: آیهٔ ۱:۱ (ترتیبِ مصحف؛ گزینشِ تزریقی — لغزشِ ثبت‌شده) ----------
ayah = db.execute(
    "SELECT text_hafs FROM ayahs WHERE surah_number=1 AND ayah_number=1"
).fetchone()[0]

words = db.execute(
    """SELECT w.word_position, w.form_arabic, r.root_arabic, r.token_count
       FROM words w LEFT JOIN roots r ON w.root_id = r.root_id
       WHERE w.surah_number=1 AND w.ayah_number=1 ORDER BY w.word_position"""
).fetchall()

# ---------- گام ۲ — سنجشِ شکاف: فهم = تهی؛ انتخابِ ژرف‌ترین شکافِ پی‌گرفتنی ----------
# قاعدهٔ اعلام‌شده (تزریقی، لایهٔ اجرا): ریشهٔ دارای بیشترین شاهد در کلِ متن،
# بیشترین مادهٔ رجوع را برای نخستین اشتقاق فراهم می‌کند.
rooted = [(w[2], w[3], w[1]) for w in words if w[2]]
_pick = max if RULE == "max" else min
pursued_root, attestation, in_word = _pick(rooted, key=lambda x: x[1])

# ---------- گام ۴ — رجوع: گردآوریِ کلِ کلام ----------
# نگاشتِ ریشه → مجموعهٔ آیه‌ها (کلِ متن، یک بار)
root_ayat = defaultdict(set)
for root, s, a in db.execute(
    """SELECT r.root_arabic, w.surah_number, w.ayah_number
       FROM words w JOIN roots r ON w.root_id = r.root_id"""
):
    root_ayat[root].add((s, a))

all_ayat = set(db.execute("SELECT surah_number, ayah_number FROM ayahs"))
N = len(all_ayat)
A_R = root_ayat[pursued_root]
nR = len(A_R)


def neighborhood(target_set, universe_n, min_support):
    """هم‌حضوریِ ریشه‌ها با مجموعه‌آیهٔ هدف؛ lift نسبت به انتظارِ بسامدی."""
    out = []
    t = len(target_set)
    for root, ayat in root_ayat.items():
        if root == pursued_root:
            continue
        obs = len(ayat & target_set)
        if obs < min_support:
            continue
        expected = t * len(ayat) / universe_n
        out.append((root, obs, round(expected, 2), round(obs / expected, 3)))
    out.sort(key=lambda x: -x[3])
    return out


full_nb = neighborhood(A_R, N, MIN_SUPPORT)
top = full_nb[:TOP_K]

# ---------- روشِ اجرا / ابطال‌گر ۱ — مدلِ تهیِ جایگشتی ----------
all_ayat_list = sorted(all_ayat)
null_exceed = {root: 0 for root, *_ in top}
top_sets = {root: root_ayat[root] for root, *_ in top}
obs_lift = {root: lift for root, obs, exp, lift in top}
for _ in range(N_PERM):
    sample = set(random.sample(all_ayat_list, nR))
    for root, ayat in top_sets.items():
        o = len(ayat & sample)
        e = nR * len(ayat) / N
        if o >= MIN_SUPPORT and o / e >= obs_lift[root]:
            null_exceed[root] += 1
p_null = {root: (null_exceed[root] + 1) / (N_PERM + 1) for root in null_exceed}

# ---------- روشِ اجرا / ابطال‌گر ۲ — پایداریِ دونیمه (سوره‌های فرد/زوج) ----------
half1 = {sa for sa in all_ayat if sa[0] % 2 == 1}
half2 = {sa for sa in all_ayat if sa[0] % 2 == 0}
nb1 = {r for r, *_ in neighborhood(A_R & half1, len(half1), 3)[:TOP_K]}
nb2 = {r for r, *_ in neighborhood(A_R & half2, len(half2), 3)[:TOP_K]}
stable = nb1 & nb2

# ---------- گام ۵ — ژرفش: درجه‌بندی ----------
result = []
for root, obs, exp, lift in top:
    passed_null = p_null[root] < 0.05
    is_stable = root in stable
    tier = ("قوی" if passed_null and is_stable
            else "محتمل" if passed_null
            else "نامشخص")
    result.append(dict(root=root, ayat_shared=obs, expected=exp, lift=lift,
                       p_perm=round(p_null[root], 4), stable_across_halves=is_stable,
                       tier=tier))

print(json.dumps(dict(
    step1_encounter=dict(ayah="1:1", text=ayah,
                         words=[(w[1], w[2]) for w in words]),
    step2_gap=dict(pursued_root=pursued_root, in_word=in_word,
                   attestation_tokens=attestation, ayat_with_root=nR),
    step4_return=dict(total_ayat=N, gathered_ayat=nR,
                      neighborhood_size=len(full_nb)),
    step5_deepening=result,
    stability_halves=dict(half1_top=sorted(nb1), half2_top=sorted(nb2),
                          overlap=len(stable)),
), ensure_ascii=False, indent=1))
