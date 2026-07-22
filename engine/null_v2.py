#!/usr/bin/env python3
"""مدلِ تهیِ نسخهٔ ۲ — جایگشتِ درجه-تصحیح‌شده (روش-v2، فقط‌مشورتی).

خاستگاه: بازنگریِ معماری ۲۰۲۶-۰۷-۲۲ (docs/ARCHITECTURE-REVIEW-2026-07-22.md)،
گامِ ۱. نقد: v1 (breath_cycle.breathe) آیات را یکنواخت نمونه می‌گیرد؛ اما
مجموعه‌آیه‌های واقعی به‌سمتِ آیه‌های پرریشه سوگیرند، پس هم‌پوشانی زیرِ داورِ
یکنواخت به‌طورِ سیستماتیک «شگفت‌تر» از واقع می‌نماید.

v2 آیه‌ها را با احتمالِ متناسب با «درجه» (شمارِ ریشه‌های متمایزِ آیه) و بدونِ
جایگزینی نمونه می‌گیرد (Efraimidis–Spirakis) — همان حاشیه‌نگه‌داریِ مدلِ
پیکربندیِ دوبخشی، سخت‌گیرتر از v1.

مرزها (تخطی‌ناپذیر):
- هیچ رفتارِ v1 را تغییر نمی‌دهد؛ رکوردها و درجه‌های رسمی دست‌نخورده.
- خروجی فقط شمارش و p؛ هیچ معنایی ساخته نمی‌شود.
- تا مُهرِ باغبان بر «روش-v2»، مصرفش فقط مشورتی است (رصدخانه).
"""
import heapq
import random
import sqlite3

from engine.breath_cycle import (SEED, N_PERM, TOP_K, HALF_SUPPORT,
                                 CORPUS_DB, neighborhood)

# seedِ مستقلِ داورِ دوم (بستهٔ سخت‌گیری، B8): بازسنجی نباید همان دنبالهٔ
# شبه‌تصادفِ v1 را مصرف کند وگرنه «دو داور» یک نویزِ هم‌بسته‌اند.
SEED_V2 = 20260722


def ayah_degrees(corpus):
    """درجهٔ هر آیه = شمارِ ریشه‌های متمایزش — وارونگیِ دقیقِ root_ayat."""
    deg = {}
    for ayat in corpus["root_ayat"].values():
        for sa in ayat:
            deg[sa] = deg.get(sa, 0) + 1
    return deg


def sample_weighted(rng, items, weights, k):
    """k عضو بدونِ جایگزینی، احتمال متناسب با وزن (Efraimidis–Spirakis).

    قطعی به‌ازای rngِ بذردار و ترتیبِ ثابتِ items؛ وزنِ صفر هرگز برگزیده
    نمی‌شود."""
    keyed = []
    for it, w in zip(items, weights):
        if w <= 0:
            continue
        keyed.append((rng.random() ** (1.0 / w), it))
    if k >= len(keyed):
        return {it for _, it in keyed}
    return {it for _, it in heapq.nlargest(k, keyed)}


def refrain_groups(db_path=CORPUS_DB):
    """گروه‌های آیه‌های متنی‌تکراری (ترجیع‌ها) — A2 بستهٔ سخت‌گیری.

    هر گروه: مجموعهٔ (سوره، آیه)هایی با text_normalized یکسان و شمارِ >۱.
    ترتیبِ خروجی قطعی است (بر حسبِ نخستین آیهٔ هر گروه)."""
    db = sqlite3.connect(f"file:{db_path}?mode=ro&immutable=1", uri=True)
    by_text = {}
    for s, a, t in db.execute(
            "SELECT surah_number, ayah_number, text_normalized FROM ayahs"):
        by_text.setdefault(t, set()).add((s, a))
    return sorted((g for g in by_text.values() if len(g) > 1), key=min)


def collapse_corpus(corpus, groups):
    """فروکاستِ هر گروهِ ترجیع به یک نماینده (نخستین به ترتیبِ مصحف).

    پیکرهٔ تازه همان ساختارِ load_corpus را دارد؛ برای اجرای حساسیتِ
    advisory — پیکرهٔ متعارفِ نفس‌ها دست نمی‌خورد."""
    dropped = set()
    for g in groups:
        dropped |= g - {min(g)}
    all_ayat = corpus["all_ayat"] - dropped
    return dict(
        root_ayat={r: ayat - dropped for r, ayat in corpus["root_ayat"].items()},
        all_ayat=all_ayat, all_list=sorted(all_ayat), N=len(all_ayat),
        h1={sa for sa in all_ayat if sa[0] % 2 == 1},
        h2={sa for sa in all_ayat if sa[0] % 2 == 0},
    )


def split_recovery(corpus, center, neighbors, k_splits=10, seed=SEED_V2):
    """پایداری با شکاف‌های تصادفیِ متعدد — B3 بستهٔ سخت‌گیری.

    همان منطقِ دونیمهٔ breathe (top-K روی هر نیمه با HALF_SUPPORT)، اما
    نیمه‌ها افرازِ تصادفیِ ۵۷/۵۷ سوره‌ها هستند نه فرد/زوجِ یگانه. خروجی:
    سهمِ شکاف‌هایی که همسایه در هر دو نیمه بازیابی می‌شود (۰..۱)."""
    rng = random.Random(seed)
    surahs = sorted({s for s, _ in corpus["all_ayat"]})
    A = corpus["root_ayat"][center]
    hits = {r: 0 for r in neighbors}
    for _ in range(k_splits):
        shuffled = surahs[:]
        rng.shuffle(shuffled)
        half1 = set(shuffled[:len(shuffled) // 2])
        ay1 = {sa for sa in corpus["all_ayat"] if sa[0] in half1}
        ay2 = corpus["all_ayat"] - ay1
        nb1 = {r for r, *_ in neighborhood(corpus, center, A & ay1,
                                           len(ay1), HALF_SUPPORT)[:TOP_K]}
        nb2 = {r for r, *_ in neighborhood(corpus, center, A & ay2,
                                           len(ay2), HALF_SUPPORT)[:TOP_K]}
        for r in neighbors:
            if r in nb1 and r in nb2:
                hits[r] += 1
    return {r: hits[r] / k_splits for r in neighbors}


def center_null_v2(corpus, degrees, center, neighbors, n_perm=N_PERM, seed=SEED):
    """p درجه-تصحیح‌شده برای هم‌پوشانیِ مرکز با هر همسایه.

    آینهٔ breathe: مجموعهٔ مرکز جایگشت می‌شود (این‌بار وزن‌دار به درجهٔ
    آیه)، مجموعهٔ همسایه ثابت می‌ماند؛ p = سهمِ جایگشت‌هایی که هم‌پوشانی‌شان
    به مشاهده می‌رسد (تصحیحِ +۱)."""
    rng = random.Random(seed)
    all_list = corpus["all_list"]
    weights = [float(degrees.get(sa, 0)) for sa in all_list]
    A = corpus["root_ayat"][center]
    nR = len(A)
    nb_sets = {r: corpus["root_ayat"][r] for r in neighbors}
    obs = {r: len(A & s) for r, s in nb_sets.items()}
    exceed = {r: 0 for r in neighbors}
    total = {r: 0 for r in neighbors}
    for _ in range(n_perm):
        smp = sample_weighted(rng, all_list, weights, nR)
        for r, s in nb_sets.items():
            o = len(smp & s)
            total[r] += o
            if o >= obs[r]:
                exceed[r] += 1
    out = {}
    for r in neighbors:
        mean = total[r] / n_perm
        out[r] = dict(
            obs=obs[r],
            mean_perm=round(mean, 3),
            lift_v2=(round(obs[r] / mean, 2) if mean else None),
            p_v2=round((exceed[r] + 1) / (n_perm + 1), 4),
        )
    return out
