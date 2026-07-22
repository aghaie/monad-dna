"""گواهیِ افزایشی (attestation) — پیاده‌سازیِ سندِ پارادایم
docs/VALIDATION-PARADIGM-2026-07-22.md (تبرّکِ باغبان، همان روز).

اصل: تغییرناپذیری + هش، همان اعتمادِ بازاجرا را ارزان‌تر و صریح‌تر می‌دهد.
- «اثرِ انگشتِ موتور»: هشِ هر ورودی‌ای که بایتِ رکوردها را تعیین می‌کند
  (موتور، پیکره، اسکریپت‌های تاریخی، CLI). خورد ⇒ مسیرِ سرد (verify کامل +
  کلِ pytest) اجباری.
- «ریشهٔ رکوردها»: هشِ مرتبِ همهٔ رکوردهای منجمد؛ لغزشِ خاموش را رسوا می‌کند.
- «ناوردای دلتا»: چک‌های O(1) فقط روی ردیف‌های نفسِ تازه.
مسیرِ سرد حذف نمی‌شود؛ فقط به نقطهٔ درست می‌رود. صدقِ سنجش صریح‌تر می‌شود.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

from pipeline import attest


def test_fingerprint_covers_record_determinants_and_is_stable():
    fp1 = attest.fingerprint()
    fp2 = attest.fingerprint()
    assert fp1 == fp2
    keys = set(fp1)
    assert "engine/breath_cycle.py" in keys
    assert "cli/monad" in keys
    assert "database/corpus/monad.db" in keys
    assert any(k.startswith("breaths/scripts/") for k in keys)
    # هیچ مشتقی در اثرِ انگشت نیست (مشتق‌ها معلول‌اند، نه علت)
    assert not any("life.db" in k or "records/" in k for k in keys)


def test_fingerprint_changes_when_input_changes(tmp_path):
    f = tmp_path / "fake_engine.py"
    f.write_text("SEED = 1\n")
    h1 = attest.fingerprint(files=[str(f)])
    f.write_text("SEED = 2\n")
    h2 = attest.fingerprint(files=[str(f)])
    assert h1 != h2


def test_records_root_changes_on_new_record(tmp_path):
    d = tmp_path / "records"
    d.mkdir()
    (d / "breath_1_ا.json").write_text('{"a":1}')
    r1 = attest.records_root(str(d))
    r1b = attest.records_root(str(d))
    assert r1 == r1b
    (d / "breath_2_ب.json").write_text('{"b":2}')
    assert attest.records_root(str(d)) != r1


def _last_breath():
    """آخرین نفس از حالتِ زنده — نه عددِ ثابت (درسِ test_counts/test_open_queue:
    snapshot با هر نفسِ تازه می‌شکند و خطِ ثبت را می‌بندد)."""
    import sqlite3
    db = sqlite3.connect("file:database/life.db?mode=ro", uri=True)
    return db.execute(
        "SELECT breath_no, record_file FROM breaths "
        "ORDER BY breath_no DESC LIMIT 1").fetchone()


def test_verify_new_record_passes_on_frozen_record():
    _, rec_file = _last_breath()
    ok, why = attest.verify_new_record(rec_file)
    assert ok, why


def test_verify_new_record_fails_on_tampered_record(tmp_path):
    src = open("breaths/records/breath_207_بطل.json", encoding="utf-8").read()
    # دستکاریِ یک مقدارِ مشتق (پایداریِ دونیمه) — نه پارامترِ ورودی؛ verify
    # فقط مشتق‌ها را می‌گیرد چون ورودی‌ها عیناً بازخورانده می‌شوند.
    assert '"halves_overlap": 3' in src
    bad = tmp_path / "breath_207_بطل.json"
    bad.write_text(src.replace('"halves_overlap": 3',
                               '"halves_overlap": 4', 1), encoding="utf-8")
    ok, _ = attest.verify_new_record(str(bad))
    assert not ok


def test_delta_invariants_pass_for_last_breath():
    no, _ = _last_breath()
    ok, why = attest.delta_invariants(no)
    assert ok, why


def test_state_roundtrip_and_change_detection(tmp_path):
    p = str(tmp_path / "state.json")
    st = {"fingerprint": attest.fingerprint(),
          "records_root": attest.records_root()}
    attest.save_state(st, p)
    assert attest.load_state(p) == st
    assert attest.fingerprint_changed(attest.load_state(p)) == []
    st2 = dict(st, fingerprint=dict(st["fingerprint"],
                                    **{"cli/monad": "0" * 64}))
    changed = attest.fingerprint_changed(st2)
    assert changed == ["cli/monad"]
