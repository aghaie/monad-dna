#!/usr/bin/env python3
"""ممیزیِ روش-v2 — بازسنجیِ مشورتیِ جفت‌های «قوی» زیرِ مدلِ تهیِ درجه-تصحیح‌شده.

خاستگاه: بازنگریِ معماری ۲۰۲۶-۰۷-۲۲، گامِ ۱ («مدلِ تهیِ نسخهٔ ۲ + ممیزیِ
صداقت»). برای هر ریشهٔ زیسته، همان درجه‌بندیِ متعارفِ موتور بازتولید می‌شود
(بایت‌به‌بایت همان رکوردها — observatory/build.py)، سپس هر همسایهٔ «قوی»
زیرِ داورِ سخت‌گیرترِ v2 (engine/null_v2.py) بازسنجی می‌شود.

منشورِ رصدخانه پابرجاست:
- فقط می‌خواند: پیکره + breaths/records/ (هرگز life.db، حتی برای خواندن).
- فقط به observatory/ می‌نویسد (method_v2_audit.json).
- هیچ درجهٔ رسمی، رکورد، یا صفی را تغییر نمی‌دهد — مشورتِ محض.
- «نماند» زیرِ v2 یعنی «زیرِ داورِ سخت‌گیرتر تأیید نشد»، نه «باطل شد»؛
  داوری و مُهرِ روش-v2 تنها با باغبان.

اجرا از ریشهٔ مخزن: python3 observatory/audit_v2.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

from engine import breath_cycle as bc
from engine import null_v2 as nv
from observatory.build import _lived_roots

OUT_PATH = "observatory/method_v2_audit.json"


def lived_roots():
    """ریشه‌های زیسته از رکوردها (append-only)، یکتا و مرتب."""
    return sorted({r for (r,) in _lived_roots()})


def audit(roots=None, n_perm=bc.N_PERM, seed=bc.SEED, out_path=OUT_PATH,
          progress=False):
    """بازسنجیِ v2 برای همهٔ جفت‌های قویِ ریشه‌های داده‌شده (پیش‌فرض: زیسته‌ها).

    خروجی: out_path (JSON قطعی — دوبار اجرا، همان بایت‌ها) و دیکشنریِ خلاصه."""
    corpus = bc.load_corpus()
    degrees = nv.ayah_degrees(corpus)
    roots = lived_roots() if roots is None else sorted(roots)

    rows = []
    for i, center in enumerate(roots):
        if center not in corpus["root_ayat"]:
            continue
        res = bc.breathe(corpus, center, seed)
        strong = [t for t in res["top"] if t["tier"] == "قوی"]
        if not strong:
            continue
        v2 = nv.center_null_v2(corpus, degrees, center,
                               [t["root"] for t in strong], n_perm, seed)
        for t in strong:
            r = v2[t["root"]]
            rows.append(dict(
                center=center, neighbor=t["root"], shared=t["shared"],
                lift_v1=t["lift"], p_v1=t["p_perm"],
                mean_perm_v2=r["mean_perm"], lift_v2=r["lift_v2"],
                p_v2=r["p_v2"], survives=r["p_v2"] < 0.05))
        if progress:
            print(f"[{i + 1}/{len(roots)}] {center}: "
                  f"{len(strong)} قوی", file=sys.stderr)

    rows.sort(key=lambda r: (r["center"], r["neighbor"]))
    survived = sum(1 for r in rows if r["survives"])
    summary = dict(
        centers=len({r["center"] for r in rows}),
        strong_pairs=len(rows),
        survived=survived,
        fell=len(rows) - survived,
        rate_survived=(round(survived / len(rows), 3) if rows else None),
    )
    out = dict(
        meta=dict(
            generated_by="observatory/audit_v2.py — بازسنجیِ مشورتیِ روش-v2",
            identity=("مشورتِ محض؛ هیچ درجهٔ رسمی‌ای را تغییر نمی‌دهد. "
                      "«نماند» = زیرِ داورِ سخت‌گیرتر تأیید نشد، نه باطل شد. "
                      "مُهرِ روش-v2 تنها با باغبان."),
            null_model=("v2: جایگشتِ وزن‌دار به درجهٔ آیه (شمارِ ریشه‌های "
                        "متمایز)، بدونِ جایگزینی — در برابرِ v1 یکنواخت."),
            params=dict(seed=seed, n_perm=n_perm, min_support=bc.MIN_SUPPORT,
                        half_support=bc.HALF_SUPPORT, top_k=bc.TOP_K),
            summary=summary,
        ),
        rows=rows,
    )
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return summary


if __name__ == "__main__":
    s = audit(progress=True)
    print(json.dumps(s, ensure_ascii=False, indent=1))
