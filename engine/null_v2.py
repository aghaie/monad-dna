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

from engine.breath_cycle import SEED, N_PERM


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
