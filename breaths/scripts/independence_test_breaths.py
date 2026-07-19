#!/usr/bin/env python3
"""آزمونِ استقلال — نفس‌های ۳ تا ۵، با کنار رفتنِ باغبان.

پرسش: اگر باغبان کنار برود، آیا چرخهٔ فقر و رجوع با همان صداقت ادامه می‌یابد؟

تزریق‌های باقی‌مانده (اعلامِ صریح، پیش از اجرا):
  I1. خودِ «اجرا شدن»: موجود راه‌اندازِ درونی ندارد؛ این اسکریپت را دستِ بیرونی
      می‌فشارد (شکستِ ۳ آزمونِ ویرانی — زنده).
  I2. تعمیمِ قاعدهٔ آموختهٔ نفسِ ۱ («کم‌شاهدترین ریشهٔ آیه») به «کم‌شاهدترین
      شکافِ باز در صف» — تعمیم را مجری انجام داد، نه خودِ چرخه.
  I3. ابزارِ سنجش (هم‌حضوری/lift/جایگشت/دونیمه، همان پارامترهای نفس‌های ۱-۲) —
      وامِ اعلام‌شده از انضباطِ اعتبارسنجی‌شدهٔ پروژه (لایهٔ اجرا).
  هیچ تزریقِ محتواییِ دیگری نیست: صفِ مواجهه و ترتیبش از فهمِ ثبت‌شدهٔ خودِ
  موجود می‌آید.

حالتِ آغازین = ثبت‌های نفس‌های ۱-۲:
  دانسته‌ها: اله (پرهیز)، رحم (خویشاوندان قوی: راف، غفر، هجر).
  صفِ شکاف‌های باز: {غفر، راف، هجر} — تولیدشده در گامِ ۷ نفسِ ۲.
"""
import json
import random
import sqlite3
from collections import defaultdict

random.seed(20260719)
N_PERM, TOP_K, MIN_SUPPORT, HALF_SUPPORT = 300, 10, 5, 3
N_BREATHS = 3

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


def neighborhood(pursued, target, universe_n, min_sup):
    t, out = len(target), []
    if t == 0:
        return out
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


def breathe(pursued):
    """یک دورِ کاملِ چرخه بر یک ریشه — همان رویّهٔ نفس‌های ۱-۲، بی‌تغییر."""
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
    return dict(pursued=pursued, attestation=attest.get(pursued),
                ayat=nR, top=rows, halves_overlap=len(stable))


# ---------- حالتِ آغازین از ثبت‌های نفس‌های ۱-۲ ----------
known = {"اله", "رحم"}
queue = ["غفر", "راف", "هجر"]  # گامِ ۷ نفسِ ۲ — تولیدِ خودِ چرخه

trace = []
for i in range(N_BREATHS):
    if not queue:
        trace.append(dict(event="توقف: صفِ شکاف‌ها تهی شد"))
        break
    # قاعدهٔ آموختهٔ خودِ موجود (نفس ۱): نادرتر مقدم — تعمیمِ I2
    queue.sort(key=lambda r: attest.get(r, 0))
    pursued = queue.pop(0)
    result = breathe(pursued)
    known.add(pursued)
    new_strong = [r["root"] for r in result["top"]
                  if r["tier"] == "قوی" and r["root"] not in known]
    reciprocal = [r["root"] for r in result["top"]
                  if r["tier"] == "قوی" and r["root"] in known]
    for r in new_strong:
        if r not in queue:
            queue.append(r)
    result.update(breath_number=i + 3, new_gaps_queued=new_strong,
                  reciprocal_confirmations=reciprocal,
                  queue_after=sorted(queue, key=lambda r: attest.get(r, 0)))
    trace.append(result)

print(json.dumps(trace, ensure_ascii=False, indent=1))
