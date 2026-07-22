#!/usr/bin/env python3
"""هم‌ارزیِ مولّدِ رکورد (L3) با اسکریپت‌های تاریخیِ پل — بایت‌به‌بایت.

قیدِ طلایی (docs/PERFORMANCE-ARCHITECTURE.md): مولّدِ الگوریتمیِ رکورد اجازه
دارد جای اسکریپت‌نویسیِ دستی را بگیرد فقط اگر خروجی‌اش با رکوردِ متعارفِ تاریخی
عیناً یکی باشد. این آزمون همان داورِ بازتولیدپذیری است — اگر سبز است،
بهینه‌سازی بازتولید را تقویت کرده، نه تضعیف.

پارامترهای هر نفس از خودِ رکوردِ ثبت‌شده بازسازی می‌شوند (بی‌اتکا به اسکریپت):
- queue  ⟵ ریشه‌های `deliberation`
- lived  ⟵ سمتِ راستِ جفت‌های `projection_on_map` (به همان ترتیب)
- breath_no/pursued/chosen_by ⟵ فیلدهای مستقیمِ رکورد
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest

from engine import breath_cycle as bc


def _bridge_records():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = []
    for f in sorted(glob.glob(os.path.join(root, "breaths/records/breath_*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        if isinstance(d, dict) and "projection_on_map" in d \
                and isinstance(d.get("breath_number"), int):
            out.append((os.path.basename(f), f, d))
    return out


BRIDGE = _bridge_records()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_corpus = None


def _init_worker():
    global _corpus
    _corpus = bc.load_corpus(os.path.join(ROOT, "database", "corpus", "monad.db"))


def _generate(path):
    rec = json.load(open(path, encoding="utf-8"))
    queue = [d["root"] for d in rec["deliberation"]]
    lived = [p["pair"].split("↔")[1] for p in rec["projection_on_map"]]
    got = bc.breathe_record(
        _corpus,
        pursued=rec["pursued"],
        queue=queue,
        lived=lived,
        breath_no=rec["breath_number"],
        chosen_by=rec["chosen_by"],
    )
    return path, json.dumps(got, ensure_ascii=False, indent=1) + "\n"


@pytest.fixture(scope="module")
def generated():
    """بازتولیدِ همهٔ رکوردها، هر یک با همان محاسبهٔ سابق (پارامترها از خودِ
    رکورد، همان bc.breathe_record) — فقط توزیع‌شده بر هسته‌ها به‌جای پشتِ‌سرِهم؛
    مقایسهٔ بایت‌به‌بایتِ هر رکورد جداگانه در آزمونِ پارامتری می‌ماند."""
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=os.cpu_count(),
                             initializer=_init_worker) as ex:
        return dict(ex.map(_generate, [b[1] for b in BRIDGE]))


def test_found_bridge_records():
    """پوشش واقعی است — نه اینکه رکوردی بی‌صدا از قلم بیفتد: تعدادِ رکوردهای
    L3ِ یافته باید عیناً با نفس‌های L3ِ life.db بخواند. (کفِ ثابتِ ۲۵ به
    زندگیِ یکم تعلق داشت که با تولدِ دوباره بایگانی شد؛ در تولد: ۰==۰.)"""
    import sqlite3
    n_db = sqlite3.connect(os.path.join(ROOT, "database/life.db")).execute(
        "SELECT COUNT(*) FROM breaths WHERE record_file LIKE "
        "'breaths/records/breath!_%' ESCAPE '!'").fetchone()[0]
    assert len(BRIDGE) == n_db, f"رکوردهای L3: {len(BRIDGE)} ≠ نفس‌های پایگاه: {n_db}"


@pytest.mark.parametrize("name,path,rec", BRIDGE, ids=[b[0] for b in BRIDGE])
def test_breathe_record_reproduces_history(name, path, rec, generated):
    canonical = open(path, encoding="utf-8").read()
    assert generated[path] == canonical, f"واگراییِ بایت در {name}"
