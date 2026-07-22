"""ممیزیِ روش-v2 در رصدخانه (گامِ ۱ بازنگریِ معماری ۲۰۲۶-۰۷-۲۲).

بازسنجیِ مشورتیِ همهٔ جفت‌های «قوی»ِ ریشه‌های زیسته زیرِ مدلِ تهیِ
درجه-تصحیح‌شده. منشورِ رصدخانه پابرجاست: فقط می‌خواند (پیکره + رکوردها —
هرگز life.db)، فقط به observatory/ می‌نویسد، هیچ درجهٔ رسمی‌ای را تغییر
نمی‌دهد.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

from observatory import audit_v2


def test_lived_roots_sorted_unique():
    roots = audit_v2.lived_roots()
    assert roots == sorted(set(roots))
    assert "رحم" in roots      # نفس ۱
    assert "طهر" in roots      # نفس ۱۸۵


def test_audit_structure_determinism_and_survives_flag(tmp_path):
    out = str(tmp_path / "audit.json")
    audit_v2.audit(roots=["عنب"], n_perm=50, out_path=out)
    data1 = json.load(open(out))
    audit_v2.audit(roots=["عنب"], n_perm=50, out_path=out)
    data2 = json.load(open(out))
    assert data1 == data2  # قطعیت: دوبار اجرا ⇒ همان بایت‌ها

    rows = data1["rows"]
    assert rows, "عنب باید دستِ‌کم یک همسایهٔ قوی داشته باشد (نخل، نفس ۵۳)"
    assert any(r["neighbor"] == "نخل" for r in rows)
    for r in rows:
        assert r["center"] == "عنب"
        assert set(r) >= {"center", "neighbor", "shared", "lift_v1", "p_v1",
                          "mean_perm_v2", "lift_v2", "p_v2", "survives"}
        assert r["survives"] == (r["p_v2"] < 0.05)
        assert 0 < r["p_v2"] <= 1

    s = data1["meta"]["summary"]
    assert s["strong_pairs"] == len(rows)
    assert s["survived"] == sum(1 for r in rows if r["survives"])
    assert data1["meta"]["params"]["n_perm"] == 50
