"""بازتولیدپذیریِ رکوردهای متعارف — اجرای دوبارهٔ اسکریپت‌های تاریخی باید
بایت‌به‌بایت همان رکوردها را بدهد. (پوششِ نفس‌های ۳–۸ که RNG دنباله‌دار دارند.)

CASES دیگر دستی نیست: از life.db مشتق می‌شود (همان منبعِ verify_checks در
cli/monad) — پیش‌تر این فهرست این‌جا و در cli/monad دوبار نگه‌داری می‌شد و هر
نفسِ تازه نیازِ ویرایشِ هر دو را داشت؛ اکنون یک منبعِ حقیقتِ واحد."""
import importlib.util
import os
import shlex
import sqlite3
import subprocess
import sys
from importlib.machinery import SourceFileLoader

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

_loader = SourceFileLoader("monad_cli", os.path.join(ROOT, "cli/monad"))
_spec = importlib.util.spec_from_loader("monad_cli", _loader)
_monad_cli = importlib.util.module_from_spec(_spec)
_loader.exec_module(_monad_cli)

CASES = _monad_cli.verify_checks(sqlite3.connect("database/life.db"))


def run(cmd):
    return subprocess.run([sys.executable, *shlex.split(cmd)], capture_output=True,
                          text=True, cwd=ROOT).stdout


def test_all_records_byte_identical():
    assert len(CASES) >= 37, "پوششِ نفس‌های تاریخی نباید کوچک شود"
    for cmd, record in CASES:
        with open(record) as f:
            want = f.read()
        got = run(cmd)
        assert got == want, f"record mismatch: {cmd}"
