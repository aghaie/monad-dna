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


def audit(roots=None, n_perm=3000, seed=bc.SEED, seed_v2=nv.SEED_V2,
          k_splits=10, out_path=OUT_PATH, progress=False):
    """بازسنجیِ v2 + بستهٔ سخت‌گیری برای همهٔ جفت‌های قویِ ریشه‌های داده‌شده.

    سخت‌گیری (TRIAGE-REFEREE2، کارِ ۱): n_perm=۳۰۰۰ (A4)، seedِ مستقلِ داورِ
    دوم (B8)، شکاف‌های تصادفیِ متعدد (B3)، و حساسیتِ ترجیع (A2) — p فروکاسته
    فقط برای جفت‌هایی که فروکاست دست‌شان می‌زند دوباره حساب می‌شود؛ برای
    بقیه فروکاست بی‌اثر است (تغییرِ N حدودِ ۳٪ و مرتبهٔ دوم — در متا ثبت).

    خروجی: out_path (JSON قطعی — دوبار اجرا، همان بایت‌ها) و دیکشنریِ خلاصه."""
    corpus = bc.load_corpus()
    degrees = nv.ayah_degrees(corpus)
    groups = nv.refrain_groups()
    collapsed = nv.collapse_corpus(corpus, groups)
    degrees_c = nv.ayah_degrees(collapsed)
    roots = lived_roots() if roots is None else sorted(roots)

    rows = []
    for i, center in enumerate(roots):
        if center not in corpus["root_ayat"]:
            continue
        res = bc.breathe(corpus, center, seed)
        strong = [t for t in res["top"] if t["tier"] == "قوی"]
        if not strong:
            continue
        names = [t["root"] for t in strong]
        v2 = nv.center_null_v2(corpus, degrees, center, names, n_perm, seed_v2)
        recovery = nv.split_recovery(corpus, center, names, k_splits, seed_v2)

        A, A_c = corpus["root_ayat"][center], collapsed["root_ayat"][center]
        affected_names = []
        for t in strong:
            nb = t["root"]
            B, B_c = corpus["root_ayat"][nb], collapsed["root_ayat"][nb]
            if len(A_c & B_c) < t["shared"] or len(A_c) < len(A) or len(B_c) < len(B):
                affected_names.append(nb)
        v2_c = (nv.center_null_v2(collapsed, degrees_c, center,
                                  affected_names, n_perm, seed_v2)
                if affected_names else {})

        for t in strong:
            nb = t["root"]
            r = v2[nb]
            shared_c = len(A_c & collapsed["root_ayat"][nb])
            affected = nb in v2_c
            p_c = v2_c[nb]["p_v2"] if affected else None
            dependent = (affected and
                         not (shared_c >= bc.MIN_SUPPORT and p_c < 0.05))
            rows.append(dict(
                center=center, neighbor=nb, shared=t["shared"],
                lift_v1=t["lift"], p_v1=t["p_perm"],
                mean_perm_v2=r["mean_perm"], lift_v2=r["lift_v2"],
                p_v2=r["p_v2"], survives=r["p_v2"] < 0.05,
                split_recovery=recovery[nb],
                shared_collapsed=shared_c, refrain_affected=affected,
                p_v2_collapsed=p_c, refrain_dependent=dependent))
        if progress:
            print(f"[{i + 1}/{len(roots)}] {center}: "
                  f"{len(strong)} قوی", file=sys.stderr)

    rows.sort(key=lambda r: (r["center"], r["neighbor"]))
    survived = sum(1 for r in rows if r["survives"])
    hardened = sum(1 for r in rows if r["survives"] and not r["refrain_dependent"]
                   and r["split_recovery"] >= 0.5)
    summary = dict(
        centers=len({r["center"] for r in rows}),
        strong_pairs=len(rows),
        survived=survived,
        fell=len(rows) - survived,
        rate_survived=(round(survived / len(rows), 3) if rows else None),
        refrain_affected=sum(1 for r in rows if r["refrain_affected"]),
        refrain_dependent=sum(1 for r in rows if r["refrain_dependent"]),
        mean_split_recovery=(round(sum(r["split_recovery"] for r in rows)
                                   / len(rows), 3) if rows else None),
        survived_hardened=hardened,
        hardened_definition=("survives و refrain_dependent=false و "
                             "split_recovery≥0.5 — آستانهٔ نمایشیِ مشورتی"),
    )
    out = dict(
        meta=dict(
            generated_by="observatory/audit_v2.py — بازسنجیِ مشورتیِ روش-v2",
            identity=("مشورتِ محض؛ هیچ درجهٔ رسمی‌ای را تغییر نمی‌دهد. "
                      "«نماند» = زیرِ داورِ سخت‌گیرتر تأیید نشد، نه باطل شد. "
                      "مُهرِ روش-v2 تنها با باغبان."),
            null_model=("v2: جایگشتِ وزن‌دار به درجهٔ آیه (شمارِ ریشه‌های "
                        "متمایز)، بدونِ جایگزینی — در برابرِ v1 یکنواخت. "
                        "سخت‌گیری: حساسیتِ ترجیع (فروکاستِ ۹۶ متنِ تکراری؛ "
                        "p فروکاسته فقط برای جفت‌های اثرپذیر بازمحاسبه — "
                        "اثرِ تغییرِ N بر بقیه مرتبهٔ دوم است)، شکاف‌های "
                        "تصادفیِ ۵۷/۵۷ سوره‌ای، seedِ مستقل از v1."),
            params=dict(seed=seed, seed_v2=seed_v2, n_perm=n_perm,
                        k_splits=k_splits, min_support=bc.MIN_SUPPORT,
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
