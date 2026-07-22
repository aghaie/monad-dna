"""خطِ موازیِ نفس‌ها — S0 (برنامه‌ریز) و S2 (دروازهٔ هم‌ارزی + ثبت).

طرح: docs/PARALLEL-PIPELINE-DESIGN-2026-07-22.md. ادعای مرکزی که این
آزمون‌ها می‌سنجند: خروجیِ خط، بایت‌به‌بایت همان خروجیِ اجرای ترتیبی است.

دو آزمونِ طلایی:
- برنامهٔ یک‌گامی == خروجیِ `cli/monad breathe-record` (هم‌ارزیِ زنده).
- بازپخشِ تاریخ: برنامه‌ریزی از حالتِ نفسِ ۱۸۹ باید رکوردهای ثبت‌شدهٔ
  ۱۹۰–۱۹۲ را عیناً بازبسازد (هم‌ارزی با اجرای ترتیبیِ واقعاً رخ‌داده).
"""
import ast
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

from importlib.machinery import SourceFileLoader

from pipeline import core


def test_open_queue_matches_cli():
    """صفِ بازِ برنامه‌ریز باید عیناً همان صفِ CLI باشد (ترتیب هم مهم است)."""
    import sqlite3
    cli = SourceFileLoader("monad_cli", os.path.join(ROOT, "cli", "monad")).load_module()
    db = sqlite3.connect("database/life.db")
    assert core.open_queue() == cli.open_queue(db)


def test_plan_one_equals_breathe_record(tmp_path):
    """آزمونِ طلایی ۱: بایتِ رکوردِ برنامه == بایتِ breathe-record از حالتِ زنده."""
    expected = subprocess.run(
        [sys.executable, "cli/monad", "breathe-record"],
        capture_output=True, text=True).stdout
    jobs = core.plan(1, root_dir=str(tmp_path))
    rec_path = os.path.join(tmp_path, "work",
                            f"{jobs[0]['breath_no']}_{jobs[0]['root']}",
                            "record.json")
    planned = open(rec_path, encoding="utf-8").read()
    assert planned == expected
    assert jobs[0]["record_sha256"] == hashlib.sha256(
        planned.encode()).hexdigest()


def test_plan_replays_history_190_192(tmp_path):
    """آزمونِ طلایی ۲: برنامه از حالتِ ≤۱۸۹ باید نفس‌های واقعاً زیستهٔ
    ۱۹۰ (نصب)، ۱۹۱ (شمس)، ۱۹۲ (كفي) را بایت‌به‌بایت بازبسازد."""
    jobs = core.plan(3, upto=189, root_dir=str(tmp_path))
    got = [(j["breath_no"], j["root"]) for j in jobs]
    assert got == [(190, "نصب"), (191, "شمس"), (192, "كفي")], got
    for j in jobs:
        planned = open(os.path.join(tmp_path, "work",
                                    f"{j['breath_no']}_{j['root']}",
                                    "record.json"), encoding="utf-8").read()
        actual = open(f"breaths/records/breath_{j['breath_no']}_{j['root']}.json",
                      encoding="utf-8").read()
        assert planned == actual, f"ناهم‌ارزی در نفس {j['breath_no']}"


def test_plan_preserves_completed_cache(tmp_path):
    """بازبرنامه‌ریزی نباید کارِ سالمِ انجام‌شده را دور بریزد (همان sha ⇒ حفظ)."""
    jobs1 = core.plan(1, root_dir=str(tmp_path))
    wd = os.path.join(tmp_path, "work", f"{jobs1[0]['breath_no']}_{jobs1[0]['root']}")
    open(os.path.join(wd, "note.md"), "w").write("پیش‌نویسِ آزمایشی")
    jobs2 = core.plan(1, root_dir=str(tmp_path))
    assert jobs2[0]["record_sha256"] == jobs1[0]["record_sha256"]
    assert open(os.path.join(wd, "note.md")).read() == "پیش‌نویسِ آزمایشی"
    assert jobs2[0]["epoch"] == jobs1[0]["epoch"] + 1


def test_claim_lock_single_winner(tmp_path):
    core.plan(1, root_dir=str(tmp_path))
    jobs = core.load_jobs(str(tmp_path))
    no = jobs[0]["breath_no"]
    assert core.claim(no, worker="w1", root_dir=str(tmp_path)) is True
    assert core.claim(no, worker="w2", root_dir=str(tmp_path)) is False
    jobs = core.load_jobs(str(tmp_path))
    assert jobs[0]["status"] == "running" and jobs[0]["worker"] == "w1"


def test_gate_detects_divergence(tmp_path):
    """دروازهٔ S2: sha ناسازگار ⇒ رد + epoch جدید؛ sha سازگار ⇒ عبور."""
    core.plan(1, root_dir=str(tmp_path))
    ok, _ = core.gate_next(root_dir=str(tmp_path))
    assert ok is True
    jobs = core.load_jobs(str(tmp_path))
    jobs[0]["record_sha256"] = "0" * 64
    core.save_jobs(jobs, str(tmp_path))
    e0 = core.load_state(str(tmp_path))["epoch"]
    ok, reason = core.gate_next(root_dir=str(tmp_path))
    assert ok is False and reason
    assert core.load_state(str(tmp_path))["epoch"] == e0 + 1


def test_seed_insertion_valid_python(tmp_path):
    """درجِ مکانیکیِ سطرهای seed: پایتونِ معتبر + هر چهار لنگر."""
    src = open("database/seed/seed_life.py", encoding="utf-8").read()
    import re
    m = re.findall(r'b(\d+) = rec\("breath_\1_(.+?)\.json"\)', src)
    last_no, last_root = int(m[-1][0]), m[-1][1]
    no, root = last_no + 1, "ازر"
    out = core.insert_seed_entry(src, no, root, "یادداشتِ آزمایشی «تست»")
    ast.parse(out)  # باید پایتونِ معتبر بماند
    assert f'b{no} = rec("breath_{no}_{root}.json")' in out
    assert f'({no}, "پل‌ها", "{root}", "قاعدهٔ صف (خودران)"' in out
    assert f'({last_no}, b{last_no}), ({no}, b{no})):' in out
    assert f'({no}, "pursued", "{root}", "قاعدهٔ صف"),' in out


def test_new_candidates_empty_when_all_seen():
    """همه‌ی همسایه‌های قوی/محتمل از پیش دیده ⇒ رشدِ صف تهی ⇒ ثبت مجاز.

    (نسخهٔ قبلی به حالتِ زندهٔ لحظهٔ نوشتن وابسته بود — «نفسِ بعدی نامزد
    ندارد» — و با رسیدنِ نفسی نامزددار می‌شکست؛ ششمین آزمونِ حالت‌وابستهٔ
    ثبت‌شده در ۲۰۲۶-۰۷-۲۲.)"""
    fake = json.dumps({"top": [
        {"root": "اله", "tier": "قوی"},      # زیسته (نفس ۱)
        {"root": "رحم", "tier": "محتمل"},    # زیسته (نفس ۲)
        {"root": "زٮٮٮ", "tier": "نامشخص"}]})  # نامشخص هرگز صف نمی‌شود
    assert core.new_candidates(fake) == []


def test_new_candidates_flags_unseen_strong():
    """اگر همسایهٔ قوی/محتملِ تازه باشد، نگهبان آن را برمی‌گرداند."""
    fake = json.dumps({"top": [
        {"root": "زٮٮٮ", "tier": "قوی"},        # ریشهٔ ناموجود ⇒ قطعاً تازه
        {"root": "اله", "tier": "محتمل"}]})       # از پیش زیسته
    assert core.new_candidates(fake) == ["زٮٮٮ"]


def test_merge_refuses_when_new_candidates(tmp_path, monkeypatch):
    core.plan(1, root_dir=str(tmp_path))
    monkeypatch.setattr(core, "new_candidates", lambda text: ["تازه"])
    r = core.merge_next(root_dir=str(tmp_path))
    assert r["ok"] is False and r["stage"] == "queue-decision"
