#!/usr/bin/env python3
"""گواهیِ افزایشی — مدلِ اعتمادِ نو (docs/VALIDATION-PARADIGM-2026-07-22.md).

پارادایم: به‌جای اثباتِ دوبارهٔ گذشتهٔ تغییرناپذیر در هر نفس (O(N²) در کل)،
اعتماد از سه چیز می‌آید:
  ۱. **اثرِ انگشتِ موتور** — هشِ همهٔ ورودی‌هایی که بایتِ رکوردها را تعیین
     می‌کنند. تا نخورده، بازتولیدپذیریِ گذشته ناوردای برهانی است (ورودیِ
     ثابت + تابعِ قطعی ⇒ خروجیِ ثابت). خورد ⇒ مسیرِ سرد اجباری.
  ۲. **ریشهٔ رکوردها** — هشِ مرتبِ رکوردهای منجمد؛ هر لغزشِ خاموشِ فایل را
     رسوا می‌کند بی‌بازاجرا.
  ۳. **verify تک‌رکورد + ناوردای دلتا** — تنها بازاجرای هر نفس: خودِ رکوردِ
     تازه؛ به‌علاوه چک‌های O(1) روی ردیف‌های تازهٔ life.db.

مسیرِ سرد (verify کامل + کلِ pytest) حذف نمی‌شود — به نقطهٔ درست می‌رود:
تغییرِ اثرِ انگشت، یا اجرای دستی/شبانه. صدقِ سنجش (قاعدهٔ ۴) حفظ و صریح‌تر
می‌شود؛ آنچه حذف می‌شود فقط تکرارِ بی‌اطلاعِ سنجش است.
"""
import glob
import hashlib
import json
import os
import sqlite3
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

STATE_PATH = "database/validation_state.json"
RECORDS_DIR = "breaths/records"

# ورودی‌های تعیین‌کنندهٔ بایتِ رکوردها — مشتق‌ها (life.db، records، گراف) عمداً
# نیستند: آن‌ها معلول‌اند و لغزششان را records_root/ناورداها می‌گیرند.
_DETERMINANTS = (
    ["database/corpus/monad.db", "cli/monad", "database/seed/seed_life.py"]
)
_DETERMINANT_GLOBS = ["engine/*.py", "breaths/scripts/*.py"]


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def determinant_files():
    files = [p for p in _DETERMINANTS if os.path.exists(p)]
    for g in _DETERMINANT_GLOBS:
        files += sorted(glob.glob(g))
    # seed_life.py با هر نفس رشد می‌کند؛ در اثرِ انگشت نیست (دادهٔ append-only
    # است، نه منطق) — منطقِ seed در بدنهٔ ثابتش است و لغزشش را ناورداها و
    # بازساختِ seed-db در همان نفس می‌گیرند.
    return [f for f in files if f != "database/seed/seed_life.py"]


def fingerprint(files=None):
    """هشِ تک‌تکِ ورودی‌های تعیین‌کننده — نقشهٔ فایل←sha256."""
    return {f: _sha(f) for f in (files or determinant_files())}


def records_root(records_dir=RECORDS_DIR):
    """ریشهٔ رکوردها: هشِ زنجیرهٔ مرتبِ (نام، هش) همهٔ رکوردهای منجمد."""
    h = hashlib.sha256()
    for p in sorted(glob.glob(os.path.join(records_dir, "*.json"))):
        h.update(os.path.basename(p).encode())
        h.update(_sha(p).encode())
    return h.hexdigest()


def load_state(path=STATE_PATH):
    if not os.path.exists(path):
        return None
    return json.load(open(path, encoding="utf-8"))


def save_state(state, path=STATE_PATH):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")


def fingerprint_changed(state):
    """فهرستِ ورودی‌هایی که از آخرین گواهیِ سرد تغییر کرده‌اند (تهی = هیچ)."""
    if not state or "fingerprint" not in state:
        return ["<بدونِ گواهیِ پیشین>"]
    old, new = state["fingerprint"], fingerprint()
    return sorted(set(k for k in set(old) | set(new)
                      if old.get(k) != new.get(k)))


def verify_new_record(path):
    """تنها بازاجرای مسیرِ داغ: خودِ رکوردِ تازه، بایت‌به‌بایت."""
    r = subprocess.run(["./cli/monad", "breathe-record-from", path],
                       capture_output=True, text=True)
    frozen = open(path, encoding="utf-8").read()
    if r.stdout != frozen:
        return False, f"رکوردِ {path} بایت‌به‌بایت بازتولید نشد"
    return True, "ok"


def delta_invariants(breath_no, db_path="database/life.db"):
    """ناورداهای O(1) روی ردیف‌های همین نفس — نه کلِ تاریخ."""
    db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    n, mn, mx = db.execute(
        "SELECT COUNT(*), MIN(breath_no), MAX(breath_no) FROM breaths").fetchone()
    if not (mn == 1 and mx == n == breath_no):
        return False, f"پیوستگیِ نفس‌ها شکست: min={mn} max={mx} n={n} انتظار={breath_no}"
    rows = db.execute(
        "SELECT center_root, neighbor_root, p_perm, stable, tier "
        "FROM findings WHERE breath_no=?", (breath_no,)).fetchall()
    for c, nb, p, stable, tier in rows:
        if c == nb:
            return False, f"خود-حلقه: {c}"
        want = ("قوی" if p < 0.05 and stable else
                "محتمل" if p < 0.05 else "نامشخص")
        if tier != want:
            return False, f"درجهٔ ناسازگار {c}→{nb}: {tier}≠{want} (p={p}, stable={stable})"
    (pc,) = db.execute(
        "SELECT COUNT(*) FROM pair_comparisons WHERE breath_no=?",
        (breath_no,)).fetchone()
    if pc == 0:
        return False, f"فرافکنیِ نفس {breath_no} در pair_comparisons نیست (لغزشِ نوعِ نفس ۱۹۳)"
    orphan = db.execute(
        "SELECT root, breath_no FROM queue_events WHERE event='queued' "
        "AND breath_no NOT IN (SELECT breath_no FROM breaths)").fetchall()
    if orphan:
        return False, f"queuedِ منسوب به نفسِ نزیسته: {orphan}"
    q = {r for (r,) in db.execute(
        "SELECT root FROM queue_events WHERE event='queued'")}
    p_ = {r for (r,) in db.execute(
        "SELECT root FROM queue_events WHERE event='pursued'")}
    (rec_file,) = db.execute(
        "SELECT record_file FROM breaths WHERE breath_no=?", (breath_no,)).fetchone()
    if not os.path.exists(rec_file):
        return False, f"فایلِ رکورد نیست: {rec_file}"
    if not p_ <= {r for (r,) in db.execute("SELECT pursued_root FROM breaths")}:
        return False, "رویدادِ pursued بدونِ نفسِ متناظر"
    return True, "ok"
