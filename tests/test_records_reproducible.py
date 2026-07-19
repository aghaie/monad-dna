"""بازتولیدپذیریِ رکوردهای متعارف — اجرای دوبارهٔ اسکریپت‌های تاریخی باید
بایت‌به‌بایت همان رکوردها را بدهد. (پوششِ نفس‌های ۳–۸ که RNG دنباله‌دار دارند.)"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

CASES = [
    (["breaths/scripts/first_breath_cycle.py", "max"], "breaths/records/breath_01_max_اله.json"),
    (["breaths/scripts/first_breath_cycle.py", "min"], "breaths/records/breath_02_min_رحم.json"),
    (["breaths/scripts/independence_test_breaths.py"], "breaths/records/breaths_03-05_راف_هجر_نصر.json"),
    (["breaths/scripts/solitude_breaths_6_8.py"], "breaths/records/breaths_06-08_اوی_صیر_باس.json"),
    (["breaths/scripts/companionship_breath_9.py"], "breaths/records/breath_09_غفر.json"),
    (["breaths/scripts/companionship_breath_10.py"], "breaths/records/breath_10_حلم.json"),
    (["breaths/scripts/companionship_breath_11.py"], "breaths/records/breath_11_عفو.json"),
    (["breaths/scripts/companionship_breath_12.py"], "breaths/records/breath_12_ذنب.json"),
]


def run(cmd):
    return subprocess.run([sys.executable, *cmd], capture_output=True,
                          text=True, cwd=ROOT).stdout


def test_all_records_byte_identical():
    for cmd, record in CASES:
        with open(record) as f:
            want = f.read()
        got = run(cmd)
        assert got == want, f"record mismatch: {' '.join(cmd)}"
