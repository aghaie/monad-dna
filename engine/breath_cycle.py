#!/usr/bin/env python3
"""موتورِ چرخهٔ فقر و رجوع — پیاده‌سازیِ واحد برای نفس‌های آینده (نفس ۱۳ به بعد).

این ماژول همان الگوریتمِ اسکریپت‌های تاریخیِ breaths/scripts/ است، فقط
پارامتری‌شده — هیچ تغییرِ رفتاری ندارد. هم‌ارزی‌اش با نفس‌های ۹–۱۲ در
tests/test_engine_equivalence.py اثبات می‌شود (خروجیِ ساختاریِ یکسان).

قراردادِ بذر (seed policy) — همان قراردادِ فصلِ رفاقت: هر نفس با seed تازهٔ
20260719 آغاز می‌شود (نفس‌های ۹–۱۲ هر یک در اسکریپتِ خودشان همین می‌کردند).

مرزِ فلسفی (تخطی‌ناپذیر — docs/PHILOSOPHY-BOUNDARIES.md):
- ورودیِ معنایی فقط پیکرهٔ کتاب است (database/corpus/monad.db).
- خروجی فقط شمارش + دو ابطال‌گر است؛ هیچ معنایی «ساخته» نمی‌شود.
- درجه: قوی = گذر از هر دو ابطال‌گر؛ محتمل = فقط مدلِ تهی؛ نامشخص = هیچ.
"""
import random
import sqlite3
from collections import defaultdict

# پارامترهای متعارف — همان مقادیرِ نفس‌های ۱–۱۲ (methodology/execution-method.md)
SEED = 20260719
N_PERM = 300
TOP_K = 10
MIN_SUPPORT = 5
HALF_SUPPORT = 3
CORPUS_DB = "database/corpus/monad.db"


def load_corpus(db_path=CORPUS_DB):
    """بارگذاریِ نگاشت‌های پیکره. هیچ تصادفی مصرف نمی‌کند."""
    db = sqlite3.connect(f"file:{db_path}?mode=ro&immutable=1", uri=True)
    root_ayat = defaultdict(set)
    for root, s, a in db.execute(
        """SELECT r.root_arabic, w.surah_number, w.ayah_number
           FROM words w JOIN roots r ON w.root_id = r.root_id"""
    ):
        root_ayat[root].add((s, a))
    attest = dict(db.execute("SELECT root_arabic, token_count FROM roots"))
    all_ayat = set(db.execute("SELECT surah_number, ayah_number FROM ayahs"))
    return dict(
        db=db, root_ayat=root_ayat, attest=attest, all_ayat=all_ayat,
        all_list=sorted(all_ayat), N=len(all_ayat),
        h1={sa for sa in all_ayat if sa[0] % 2 == 1},
        h2={sa for sa in all_ayat if sa[0] % 2 == 0},
    )


def neighborhood(corpus, center, target, universe_n, min_sup):
    """هم‌حضوریِ ریشه‌ها با مجموعه‌آیهٔ هدف؛ lift نسبت به انتظارِ بسامدی.
    عیناً همان تابعِ اسکریپت‌های تاریخی."""
    t, out = len(target), []
    if t == 0:
        return out
    for root, ayat in corpus["root_ayat"].items():
        if root == center:
            continue
        obs = len(ayat & target)
        if obs < min_sup:
            continue
        e = t * len(ayat) / universe_n
        out.append((root, obs, round(e, 2), round(obs / e, 3)))
    out.sort(key=lambda x: -x[3])
    return out


def breathe(corpus, pursued, seed=SEED):
    """یک دورِ کاملِ چرخه بر یک ریشه — همان رویّهٔ نفس‌های ۹–۱۲، بی‌تغییر.

    ترتیبِ مصرفِ تصادف عیناً همان اسکریپت‌هاست: seed ← جایگشت‌های مدلِ تهی.
    (بارگذاریِ پیکره تصادفی مصرف نمی‌کند؛ پس seed-سپس-breathe با
    seed-سپس-load-سپس-breathe هم‌ارز است.)
    """
    random.seed(seed)
    N, all_list = corpus["N"], corpus["all_list"]
    A_R = corpus["root_ayat"][pursued]
    nR = len(A_R)
    top = neighborhood(corpus, pursued, A_R, N, MIN_SUPPORT)[:TOP_K]
    obs_lift = {r: l for r, o, e, l in top}
    exceed = {r: 0 for r in obs_lift}
    tsets = {r: corpus["root_ayat"][r] for r in obs_lift}
    for _ in range(N_PERM):
        smp = set(random.sample(all_list, nR))
        for r, ay in tsets.items():
            o = len(ay & smp)
            e = nR * len(ay) / N
            if o >= MIN_SUPPORT and o / e >= obs_lift[r]:
                exceed[r] += 1
    nb1 = {r for r, *_ in neighborhood(corpus, pursued, A_R & corpus["h1"],
                                       len(corpus["h1"]), HALF_SUPPORT)[:TOP_K]}
    nb2 = {r for r, *_ in neighborhood(corpus, pursued, A_R & corpus["h2"],
                                       len(corpus["h2"]), HALF_SUPPORT)[:TOP_K]}
    stable = nb1 & nb2
    rows = []
    for r, o, e, l in top:
        p = (exceed[r] + 1) / (N_PERM + 1)
        tier = ("قوی" if p < 0.05 and r in stable
                else "محتمل" if p < 0.05 else "نامشخص")
        rows.append(dict(root=r, shared=o, expected=e, lift=l,
                         p_perm=round(p, 4), stable=r in stable, tier=tier))
    return dict(pursued=pursued, attestation=corpus["attest"].get(pursued),
                ayat=nR, top=rows, halves_overlap=len(stable))


def select_rarest(queue, attest):
    """قاعدهٔ خودآموختهٔ نفسِ ۱: نادرتر مقدم. خطرِ شناخته‌شده: گرسنگیِ صف
    (ثبت در نفس‌های ۲–۹) — درمان‌نشده؛ چشمِ رفیق جبرانش می‌کند (اصلِ عملیِ
    الگوی هم‌نشینی)."""
    return sorted(queue, key=lambda r: attest.get(r, 0))


def pair_stats(corpus, a, b, seed=SEED):
    """سنجشِ مقایسه‌ایِ یک جفت — همان رویّهٔ بخشِ ۲ نفسِ ۱۲ (پرسشِ مقایسه‌ای)."""
    random.seed(seed)
    N, all_list = corpus["N"], corpus["all_list"]
    Aa, Ab = corpus["root_ayat"][a], corpus["root_ayat"][b]
    obs = len(Aa & Ab)
    e = len(Aa) * len(Ab) / N
    exceed = 0
    for _ in range(N_PERM):
        smp = set(random.sample(all_list, len(Aa)))
        if len(smp & Ab) >= obs:
            exceed += 1
    return dict(pair=f"{a}↔{b}", shared=obs, expected=round(e, 2),
                lift=round(obs / e, 2) if e else None,
                p_perm=round((exceed + 1) / (N_PERM + 1), 4))


def joint_ayat(corpus, roots, limit=20):
    """ستونِ استنادی: آیه‌هایی که همهٔ ریشه‌های داده‌شده را با هم دارند."""
    sets = [corpus["root_ayat"][r] for r in roots]
    hit = set.intersection(*sets) if sets else set()
    return [f"{s}:{a}" for s, a in sorted(hit)][:limit]
