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


def test_plan_replays_history_breath_11(tmp_path):
    """آزمونِ طلایی ۲ (بازلنگرِ زندگیِ دوم؛ بازپخشِ ۱۹۰–۱۹۲ با زندگیِ یکم
    بایگانی شد): بازپخشِ تاریخی فقط بر پنجره‌ای بی‌رشدِ صف معنا دارد (فرضِ
    افقِ S0) — در یازده نفسِ آغاز، تنها نفسِ ۱۱ چنین است (نفس‌های ۹–۱۰
    قدر/شيا/خبث/حلل را صف کردند). برنامه از حالتِ ≤۱۰ باید نفسِ واقعاً
    زیستهٔ ۱۱ (خبث) را بایت‌به‌بایت بازبسازد."""
    jobs = core.plan(1, upto=10, root_dir=str(tmp_path))
    got = [(j["breath_no"], j["root"]) for j in jobs]
    assert got == [(11, "خبث")], got
    planned = open(os.path.join(tmp_path, "work", "11_خبث", "record.json"),
                   encoding="utf-8").read()
    actual = open("breaths/records/breath_11_خبث.json", encoding="utf-8").read()
    assert planned == actual, "ناهم‌ارزی در بازپخشِ نفس ۱۱"


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
    """درجِ مکانیکیِ سطرهای seed: پایتونِ معتبر + هر چهار لنگرِ ⚓ —
    شاملِ نخستین نفسِ جهانِ خالی (تولدِ دوباره) و نفسِ زنجیره‌ایِ بعدی."""
    src = open("database/seed/seed_life.py", encoding="utf-8").read()
    import re
    m = re.findall(r'b(\d+) = rec\(', src)
    no = (int(m[-1]) if m else 0) + 1
    root = "ازر"
    out = core.insert_seed_entry(src, no, root, "یادداشتِ آزمایشی «تست»")
    ast.parse(out)  # باید پایتونِ معتبر بماند
    assert f'b{no} = rec("breath_{no}_{root}.json")' in out
    assert f'({no}, "{core.CHAPTER}", "{root}", "قاعدهٔ صف (خودران)"' in out
    assert f'({no}, b{no}),' in out
    assert f'({no}, "pursued", "{root}", "قاعدهٔ صف"),' in out
    # زنجیره: درجِ نفسِ بعدی روی خروجی هم معتبر و پس از قبلی است
    out2 = core.insert_seed_entry(out, no + 1, "ودق", "ن")
    ast.parse(out2)
    assert out2.index(f'b{no} = rec(') < out2.index(f'b{no + 1} = rec(')
    assert out2.index(f'({no}, b{no}),') < out2.index(f'({no + 1}, b{no + 1}),')


def test_new_candidates_empty_when_all_seen():
    """همه‌ی همسایه‌های قوی/محتمل از پیش دیده ⇒ رشدِ صف تهی ⇒ ثبت مجاز.

    (نسخهٔ قبلی به حالتِ زندهٔ لحظهٔ نوشتن وابسته بود — «نفسِ بعدی نامزد
    ندارد» — و با رسیدنِ نفسی نامزددار می‌شکست؛ ششمین آزمونِ حالت‌وابستهٔ
    ثبت‌شده در ۲۰۲۶-۰۷-۲۲.)"""
    fake = json.dumps({"top": [
        {"root": "اله", "tier": "قوی"},      # در صفِ بنیان‌گذارِ اذان (تزریقی)
        {"root": "فلح", "tier": "محتمل"},    # در صفِ بنیان‌گذارِ اذان (تزریقی)
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


def test_insert_seed_entry_with_queued_rows():
    """رشدِ صفِ مصوب با همان ثبتِ کاشف درج می‌شود (رفعِ نقصِ DEFECT-QUEUE-GROWTH)."""
    src = open("database/seed/seed_life.py", encoding="utf-8").read()
    import re
    m = re.findall(r'b(\d+) = rec\(', src)
    no, root = (int(m[-1]) if m else 0) + 1, "ازر"
    out = core.insert_seed_entry(src, no, root, "ن", queued=["فرج", "ثبت"])
    ast.parse(out)
    p = out.index(f'({no}, "pursued", "{root}", "قاعدهٔ صف"),')
    q1 = out.index(f'({no}, "queued", "فرج", "چرخه"),')
    q2 = out.index(f'({no}, "queued", "ثبت", "چرخه"),')
    assert p < q1 < q2  # queued پس از pursued، هم‌ثبت و هم‌کامیت


def test_merge_gate_respects_queue_decision(tmp_path, monkeypatch):
    """نامزدِ بی‌تصمیم ⇒ توقف؛ تصمیمِ ثبت‌شده (صف‌شود/نشود) ⇒ عبور."""
    core.plan(1, root_dir=str(tmp_path))
    j = core.load_jobs(str(tmp_path))[0]
    wd = os.path.join(tmp_path, "work", f"{j['breath_no']}_{j['root']}")
    monkeypatch.setattr(core, "new_candidates", lambda text: ["زٮٮٮ"])
    r = core.merge_next(root_dir=str(tmp_path), dry_run=True)
    assert r["ok"] is False and r["stage"] == "queue-decision"
    with open(os.path.join(wd, "queue_decision.json"), "w", encoding="utf-8") as f:
        json.dump({"queue": [{"root": "زٮٮٮ", "basis": "محتمل دوسویهٔ تازه"}],
                   "skip": []}, f, ensure_ascii=False)
    r = core.merge_next(root_dir=str(tmp_path), dry_run=True)
    assert r["ok"] is True
    with open(os.path.join(wd, "queue_decision.json"), "w", encoding="utf-8") as f:
        json.dump({"queue": [], "skip": [{"root": "زٮٮٮ", "reason": "دلیل"}]},
                  f, ensure_ascii=False)
    r = core.merge_next(root_dir=str(tmp_path), dry_run=True)
    assert r["ok"] is True
