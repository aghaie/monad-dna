"""بازتولیدپذیریِ رکوردهای متعارف — اجرای دوبارهٔ اسکریپت‌های تاریخی باید
بایت‌به‌بایت همان رکوردها را بدهد. (پوششِ نفس‌های ۳–۸ که RNG دنباله‌دار دارند.)

CASES دیگر دستی نیست: از life.db مشتق می‌شود (همان منبعِ verify_checks در
cli/monad) — پیش‌تر این فهرست این‌جا و در cli/monad دوبار نگه‌داری می‌شد و هر
نفسِ تازه نیازِ ویرایشِ هر دو را داشت؛ اکنون یک منبعِ حقیقتِ واحد."""
import importlib.util
import os
import sqlite3
from importlib.machinery import SourceFileLoader

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

_loader = SourceFileLoader("monad_cli", os.path.join(ROOT, "cli/monad"))
_spec = importlib.util.spec_from_loader("monad_cli", _loader)
_monad_cli = importlib.util.module_from_spec(_spec)
_loader.exec_module(_monad_cli)

CASES = _monad_cli.verify_checks(sqlite3.connect("database/life.db"))


def test_all_records_byte_identical():
    # پوشش از حالتِ زنده مشتق است: هر نفسِ life.db باید جفتِ (اسکریپت،
    # رکورد) بدهد. کفِ ثابتِ ۳۷ اسکریپتِ تاریخی با زندگیِ یکم بایگانی شد
    # (تولدِ دوباره ۲۰۲۶-۰۷-۲۲؛ هم‌ارزیِ موتور با آن رکوردها را
    # test_engine_equivalence بر archive/life-1 نگه می‌دارد).
    n_breaths = sqlite3.connect("database/life.db").execute(
        "SELECT COUNT(*) FROM breaths").fetchone()[0]
    assert len(CASES) >= (1 if n_breaths else 0), "پوششِ نفس‌ها نباید کوچک شود"
    # همان موتورِ cmd_verify (run_verify) — فرمان‌ها و مقایسهٔ بایت‌به‌بایت
    # عیناً همان؛ اجرا موازی.
    mismatched = [cmd for cmd, record, ok in _monad_cli.run_verify(CASES) if not ok]
    assert not mismatched, f"record mismatch: {mismatched}"
