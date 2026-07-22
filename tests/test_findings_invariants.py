"""نامتغیّرهای علمیِ findings — آزمون‌های تازه برای اعتبارسنجیِ یافته‌ها.

بازتولیدپذیریِ بایت‌به‌بایت (verify) فقط می‌گوید «اسکریپت همان چیزِ قبلی را
داد»؛ این‌ها نامتغیّرهای مستقل‌اند که هیچ‌کدام تاکنون صریح آزموده نشده بودند —
اگر موتور در آینده تغییر کند، این‌ها خطای منطقی/آماری را حتی وقتی
بازتولیدپذیریِ محلی حفظ شده، آشکار می‌کنند.
"""
import json
import os
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

N_PERM = 300  # engine/breath_cycle.py:N_PERM — پارامترِ متعارف


def _findings():
    db = sqlite3.connect("database/life.db")
    return db.execute(
        "SELECT center_root, neighbor_root, shared_ayat, expected, lift, "
        "p_perm, stable, tier FROM findings").fetchall()


def test_no_self_loops():
    """یک ریشه هرگز همسایهٔ خودش نیست."""
    for c, n, *_ in _findings():
        assert c != n, f"self-loop: {c}"


def test_tier_matches_p_and_stability():
    """قوی = p<0.05 و پایدار؛ محتمل = فقط p<0.05؛ نامشخص = هیچ‌کدام
    (تعریفِ engine/breath_cycle.py:breathe، خطِ tier=...)."""
    for c, n, s, e, l, p, st, tier in _findings():
        want = "قوی" if (p < 0.05 and st) else ("محتمل" if p < 0.05 else "نامشخص")
        assert tier == want, f"{c}->{n}: tier={tier} اما انتظار {want} (p={p}, stable={st})"


def test_p_perm_within_permutation_bounds():
    """p_perm = (exceed+1)/(N_PERM+1) — هرگز کمتر از کمینهٔ ممکن یا بیش از ۱.
    تلورانس: p_perm با ۴ رقمِ اعشار گرد شده (round(p,4))."""
    lo = 1 / (N_PERM + 1)
    for c, n, s, e, l, p, st, tier in _findings():
        assert lo - 5e-4 <= p <= 1.0, f"{c}->{n}: p_perm={p} خارج از بازهٔ ممکن"


def test_lift_consistent_with_shared_and_expected():
    """lift ≈ shared/expected، با درنظرگرفتنِ گردکردنِ expected به ۲ رقم
    (خطای بزرگ برای expected‌های خیلی کوچک، خودِ گردکردن است، نه ناسازگاری —
    پس بازهٔ مجاز از رویِ نیم‌واحدِ گردکردن ساخته می‌شود، نه تلورانسِ ثابت)."""
    for c, n, s, e, l, p, st, tier in _findings():
        lo = s / (e + 0.005)
        hi = (s / (e - 0.005)) if e > 0.005 else float("inf")
        assert lo - 1e-3 <= l <= hi + 1e-3, (
            f"{c}->{n}: lift={l} خارج از بازهٔ سازگار [{lo:.3f},{hi:.3f}] "
            f"با shared={s}, expected={e}")


def test_absence_evidence_matches_pair_comparisons():
    """هر شاهدِ غیابِ ثبت‌شده در knowledge.json باید shared_ayat=0 را در
    pair_comparisons داشته باشد — سازگاریِ میانِ لایهٔ کشف و پایگاه."""
    db = sqlite3.connect("database/life.db")
    know = json.load(open("discoveries/knowledge.json"))
    assert len(know["absence_evidence"]) > 0
    for a in know["absence_evidence"]:
        x, y = a["pair"].split("↔")
        row = db.execute(
            "SELECT shared_ayat FROM pair_comparisons WHERE "
            "(root_a=? AND root_b=?) OR (root_a=? AND root_b=?)",
            (x, y, y, x)).fetchone()
        assert row is not None, f"{a['pair']}: در pair_comparisons نیست"
        assert row[0] == 0, f"{a['pair']}: shared_ayat={row[0]} نه ۰"


def test_mutual_strong_graph_matches_findings_both_directions():
    """هر یالِ mutual_strong در graph.json باید در findings از هر دو سو
    tier='قوی' داشته باشد — گراف نباید از پایگاه واگرا شود."""
    db = sqlite3.connect("database/life.db")
    graph = json.load(open("graph/graph.json"))
    mutual = [e for e in graph["edges"] if e.get("mutual_strong")]
    assert len(mutual) > 0

    def tier_of(c, n):
        row = db.execute(
            "SELECT tier FROM findings WHERE center_root=? AND neighbor_root=?",
            (c, n)).fetchone()
        return row[0] if row else None

    for e in mutual:
        a, b = e["a"], e["b"]
        assert tier_of(a, b) == "قوی", f"{a}->{b} در findings قوی نیست"
        assert tier_of(b, a) == "قوی", f"{b}->{a} در findings قوی نیست"


def test_pair_comparisons_cover_every_l3_breath():
    """هر نفسِ L3 (۱۲ به بعد) باید فرافکنی‌اش در pair_comparisons باشد —
    ناوردایی که غیبتش در نفس ۱۹۳ (جاافتادنِ حلقهٔ (bn, brec) در seed) را
    هیچ آزمونی نمی‌گرفت؛ کشفِ ۲۰۲۶-۰۷-۲۲ هنگامِ ساختِ خطِ لوله."""
    db = sqlite3.connect("database/life.db")
    breaths = {b for (b,) in db.execute(
        "SELECT breath_no FROM breaths WHERE breath_no >= 12")}
    covered = {b for (b,) in db.execute(
        "SELECT DISTINCT breath_no FROM pair_comparisons")}
    missing = sorted(breaths - covered)
    assert not missing, f"نفس‌های بی‌فرافکنی در pair_comparisons: {missing}"
