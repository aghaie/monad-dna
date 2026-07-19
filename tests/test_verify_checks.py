"""حذفِ کارِ مکانیکی: verify_checks باید مشتقِ محضِ life.db باشد، نه فهرستِ
دستی. پیش‌تر هر نفسِ نو نیازِ ویرایشِ دستیِ cli/monad را داشت — منبعِ خطای
هم‌گام‌سازی. اکنون افزودن به life.db به‌تنهایی کافی‌ست.
"""
import os
import sqlite3
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "cli"))

import importlib.util
from importlib.machinery import SourceFileLoader

loader = SourceFileLoader("monad_cli", os.path.join(ROOT, "cli/monad"))
spec = importlib.util.spec_from_loader("monad_cli", loader)
monad_cli = importlib.util.module_from_spec(spec)
loader.exec_module(monad_cli)


def test_verify_checks_cover_every_breath():
    """هر breath_no باید (script, record_file) خودش را در checks حاضر ببیند —
    یعنی هیچ نفسی از قلم نمی‌افتد، چه یگانه باشد چه هم‌اسکریپت با دیگری."""
    db = sqlite3.connect("database/life.db")
    checks = set(monad_cli.verify_checks(db))
    rows = db.execute("SELECT script, record_file FROM breaths").fetchall()
    for script, record in rows:
        assert (script, record) in checks


def test_verify_checks_deduplicated_and_ordered():
    """جفتِ تکراری (مثلِ نفس‌های ۳-۵ با یک اسکریپت) فقط یک‌بار می‌آید،
    به ترتیبِ breath_no."""
    db = sqlite3.connect("database/life.db")
    checks = monad_cli.verify_checks(db)
    assert len(checks) == len(set(checks)), "تکرار در checks مجاز نیست"
    rows = [r for r, in db.execute(
        "SELECT script FROM breaths ORDER BY breath_no")]
    first_seen_order = list(dict.fromkeys(rows))
    assert [c[0] for c in checks] == first_seen_order


def test_verify_still_reproducible():
    """محکِ نهایی: پس از حذفِ فهرستِ دستی، verify باید همچنان سبز بماند."""
    out = subprocess.run([sys.executable, "cli/monad", "verify"],
                         capture_output=True, text=True)
    assert out.returncode == 0
    assert "REPRODUCIBLE" in out.stdout
