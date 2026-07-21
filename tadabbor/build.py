#!/usr/bin/env python3
"""تدبّرخانه — موجودِ چهارم (منشور: TADABBOR.md).

سیمای ساختاریِ کاملِ یک ریشه از خودِ پیکره، برای تدبّرِ باغبان.
هرگز به پایگاهِ زندگی یا رکوردها نمی‌نویسد (پایگاهِ زندگی حتی خوانده
نمی‌شود)؛ فقط درونِ tadabbor/.
جدول‌های ext_* حتی خوانده نمی‌شوند (نگهبانِ فعال). قطعی: دوبار اجرا ⇒ همان بایت‌ها.

اجرا از ریشهٔ مخزن: python3 tadabbor/build.py ریشه
"""
import glob
import json
import os
import sqlite3
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
from engine import breath_cycle as bc

OUT_DIR = "tadabbor/portraits"

IDENTITY = ("تدبّرخانه سیمای ساختاریِ یک ریشه را از خودِ پیکره می‌کشد؛ "
            "نمی‌فهمد و فرضیه نمی‌سازد — الگو، نه معنا. سیمای ساختاری، نه فهم. "
            "فهم کارِ باغبان است، در کتاب.")

CLOSING = "این سند می‌شمارد و نشان می‌دهد؛ نمی‌فهمد. تدبّر کارِ توست، در کتاب."

# هشدارِ ایستادهٔ نفس ۲۷ (عوج): با شاهدِ بسیار کم، دونیمه‌سازی بی‌معنا می‌شود.
LOW_ATTESTATION_NOTE = ("ریشهٔ کم‌شاهد: با آیه‌های اندک، ابطال‌گرِ دونیمه "
                        "کم‌توان است و هیچ همسایه‌ای شاید به «قوی» نرسد — "
                        "محدودیتِ ابزار، نه یافته (ثبتِ نفس ۲۷).")

ALIGN_NOTE = ("ترازشِ متن/صرف ناهم‌خوان است (توکن‌بندیِ تنزیل ≠ پیکرهٔ صرفی)؛ "
              "به‌جای نشان‌کردن در متن، موضعِ واژه فهرست می‌شود — حدس ممنوع.")


def _connect():
    """اتصالِ فقط‌خواندنی به پیکره با نگهبانِ فعالِ قرنطینه: ext_* حتی خوانده نمی‌شود."""
    db = sqlite3.connect("file:database/corpus/monad.db?mode=ro&immutable=1",
                         uri=True)
    def _authorizer(action, a1, a2, *rest):
        if a1 and str(a1).startswith("ext_"):
            return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK
    db.set_authorizer(_authorizer)
    return db


def _counts(rows, idx):
    """شمارشِ برچسب‌های یک ستون — مرتب به شمارِ نزولی سپس برچسب (قطعی)."""
    c = Counter(r[idx] for r in rows if r[idx])
    return {k: v for k, v in sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))}


def _lived_crosslink(root):
    """نشانیِ رکوردهای زیستهٔ این ریشه — فقط از رکوردهای append-only؛
    پایگاهِ زندگی حتی خوانده نمی‌شود. فقط اشاره‌گر، بی‌کپیِ محتوا."""
    out = []
    for f in sorted(glob.glob("breaths/records/*.json")):
        rec = json.load(open(f))
        for b in (rec if isinstance(rec, list) else [rec]):
            pursued = b.get("pursued") or b.get("step2_gap", {}).get("pursued_root")
            if pursued == root:
                out.append({"نفس": b.get("breath_number"), "رکورد": f})
    return out


def portrait(root):
    """سیمای ساختاریِ کاملِ یک ریشه — تابعِ محضِ پیکره؛ هیچ معنایی ساخته نمی‌شود."""
    db = _connect()
    row = db.execute("SELECT root_id, token_count FROM roots WHERE root_arabic=?",
                     (root,)).fetchone()
    if row is None:
        return None
    root_id, token_count = row

    # ۱. هویت
    lemmas = [{"لم": l, "شمار": c} for l, c in db.execute(
        """SELECT l.lemma_arabic, COUNT(w.word_id) AS n FROM lemmas l
           JOIN words w ON w.lemma_id = l.lemma_id
           WHERE l.root_id=? GROUP BY l.lemma_id
           ORDER BY n DESC, l.lemma_arabic""", (root_id,))]

    # ۲. آیه‌ها (با رخدادها در جای خود)
    occ_rows = db.execute(
        """SELECT w.surah_number, w.ayah_number, w.word_position, w.form_arabic,
                  a.text_hafs, s.name_arabic, s.revelation_type
           FROM words w
           JOIN ayahs a ON a.surah_number = w.surah_number
                       AND a.ayah_number = w.ayah_number
           JOIN surahs s ON s.surah_number = w.surah_number
           WHERE w.root_id=?
           ORDER BY w.surah_number, w.ayah_number, w.word_position""",
        (root_id,)).fetchall()

    verses, seen = [], {}
    for s, a, pos, form, text, sname, rtype in occ_rows:
        key = (s, a)
        if key not in seen:
            seen[key] = {"سوره": s, "آیه": a, "نام_سوره": sname,
                         "نوع": ("مکی" if rtype == "meccan" else
                                 "مدنی" if rtype == "medinan" else rtype),
                         "متن": text, "رخدادها": []}
            verses.append(seen[key])
        seen[key]["رخدادها"].append({"موضع": pos, "صورت": form})

    # شمارِ کلِ واژه‌های هر آیه (برای سنجشِ صادقانهٔ ترازشِ متن/صرف در گزارش)
    for v in verses:
        (n_words,) = db.execute(
            "SELECT COUNT(*) FROM words WHERE surah_number=? AND ayah_number=?",
            (v["سوره"], v["آیه"])).fetchone()
        v["شمار_واژه‌های_آیه"] = n_words

    # ۳. صورت‌ها
    form_locs = {}
    for s, a, pos, form, *_ in occ_rows:
        form_locs.setdefault(form, []).append(f"{s}:{a}")
    forms = [{"صورت": f, "شمار": len(locs), "مکان‌ها": locs}
             for f, locs in sorted(form_locs.items(),
                                   key=lambda kv: (-len(kv[1]), kv[0]))]

    # ۴. داربستِ صرفی (فقط قطعه‌های STEM با همین ریشه) — ساختار، نه معنا
    morph_rows = db.execute(
        """SELECT pos, aspect, voice, mood, person,
                  case_feature, state, gender, number_feature
           FROM morphology WHERE segment_type='STEM' AND root_id=?""",
        (root_id,)).fetchall()
    verb_rows = [r for r in morph_rows if r[0] == "V"]
    noun_rows = [r for r in morph_rows if r[0] != "V"]
    morphology = {
        "برچسب": "داربستِ صرفی — ساختار، نه معنا",
        "کل_قطعه‌های_STEM": len(morph_rows),
        "بر_حسبِ_pos": _counts(morph_rows, 0),
        "فعل": {"aspect": _counts(verb_rows, 1), "voice": _counts(verb_rows, 2),
                "mood": _counts(verb_rows, 3), "person": _counts(verb_rows, 4)},
        "اسم": {"case": _counts(noun_rows, 5), "state": _counts(noun_rows, 6),
                "gender": _counts(noun_rows, 7), "number": _counts(noun_rows, 8)},
    }

    # ۵. پراکندگی
    surah_info = {n: (name, rtype, cnt) for n, name, rtype, cnt in db.execute(
        "SELECT surah_number, name_arabic, revelation_type, ayah_count FROM surahs")}
    tok_by_surah = Counter(s for s, *_ in occ_rows)
    ayah_by_surah = Counter(v["سوره"] for v in verses)
    per_surah = []
    for s in sorted(tok_by_surah, key=lambda x: (-tok_by_surah[x], x)):
        name, rtype, cnt = surah_info[s]
        per_surah.append({"سوره": s, "نام": name,
                          "نوع": ("مکی" if rtype == "meccan" else "مدنی"),
                          "واژه‌ها": tok_by_surah[s], "آیه‌ها": ayah_by_surah[s],
                          "چگالی": round(tok_by_surah[s] / cnt, 4)})
    rev_tok = Counter(("مکی" if surah_info[s][1] == "meccan" else "مدنی")
                      for s, *_ in occ_rows)
    rev_ayah = Counter(v["نوع"] for v in verses)
    distribution = {"بر_حسبِ_سوره": per_surah,
                    "مکی_مدنی_واژه‌ها": dict(sorted(rev_tok.items())),
                    "مکی_مدنی_آیه‌ها": dict(sorted(rev_ayah.items()))}

    # ۶. هم‌آیی — بازاستفادهٔ محضِ engine (همان seed، همان دو ابطال‌گر؛ صفر آمارِ تازه)
    corpus = bc.load_corpus()
    cooccurrence = {"یادداشت": None, "top": [], "halves_overlap": None,
                    "ستون‌های_استنادی": {}}
    if root in corpus["root_ayat"]:
        res = bc.breathe(corpus, root)
        cooccurrence["top"] = res["top"]
        cooccurrence["halves_overlap"] = res["halves_overlap"]
        for t in res["top"]:
            if t["p_perm"] < 0.05:
                cooccurrence["ستون‌های_استنادی"][f"{root}+{t['root']}"] = \
                    bc.joint_ayat(corpus, [root, t["root"]])
        if res["ayat"] < 10:
            cooccurrence["یادداشت"] = LOW_ATTESTATION_NOTE
    else:
        cooccurrence["یادداشت"] = "این ریشه هیچ واژه‌ای در پیکره ندارد."

    # ۸. بافتِ مجاور (داده‌های مکانیِ محض؛ فهرستِ کامل — بی‌سقفِ خاموش)
    words_in = {}
    for v in verses:
        for pos, form in db.execute(
            """SELECT word_position, form_arabic FROM words
               WHERE surah_number=? AND ayah_number=? ORDER BY word_position""",
                (v["سوره"], v["آیه"])):
            words_in[(v["سوره"], v["آیه"], pos)] = form
    before, after = Counter(), Counter()
    for s, a, pos, *_ in occ_rows:
        if (s, a, pos - 1) in words_in:
            before[words_in[(s, a, pos - 1)]] += 1
        if (s, a, pos + 1) in words_in:
            after[words_in[(s, a, pos + 1)]] += 1
    context = {
        "قبل": [{"صورت": f, "شمار": n} for f, n in
                sorted(before.items(), key=lambda kv: (-kv[1], kv[0]))],
        "بعد": [{"صورت": f, "شمار": n} for f, n in
                sorted(after.items(), key=lambda kv: (-kv[1], kv[0]))],
    }

    db.close()
    return {
        "meta": {
            "generated_by": "tadabbor/build.py — سیمای ساختاری، نه فهم",
            "identity": IDENTITY,
            "params": dict(seed=bc.SEED, n_perm=bc.N_PERM,
                           min_support=bc.MIN_SUPPORT,
                           half_support=bc.HALF_SUPPORT, top_k=bc.TOP_K),
        },
        "ریشه": root,
        "هویت": {"شاهد": token_count, "آیه‌ها": len(verses), "لم‌ها": lemmas},
        "آیه‌ها": verses,
        "صورت‌ها": forms,
        "صرف": morphology,
        "پراکندگی": distribution,
        "هم‌آیی": cooccurrence,
        "پیوند_زیسته": _lived_crosslink(root),
        "بافت_مجاور": context,
    }


def _md_verse(v):
    """رندرِ یک آیه: نشان‌کردنِ صورت‌ها فقط وقتی ترازشِ توکن‌ها دقیق است؛
    وگرنه fallback صادقانه با اعلامِ محدودیت."""
    tokens = v["متن"].split()
    positions = {o["موضع"] for o in v["رخدادها"]}
    lines = []
    if len(tokens) == v["شمار_واژه‌های_آیه"] and max(positions) <= len(tokens):
        marked = " ".join(f"**{t}**" if i + 1 in positions else t
                          for i, t in enumerate(tokens))
        lines.append(f"> {marked}")
        lines.append(f"> — {v['سوره']}:{v['آیه']}")
    else:
        lines.append(f"> {v['متن']}")
        lines.append(f"> — {v['سوره']}:{v['آیه']}")
        occ = "؛ ".join(f"موضعِ {o['موضع']}: {o['صورت']}" for o in v["رخدادها"])
        lines.append(f">\n> {occ} — {ALIGN_NOTE}")
    return "\n".join(lines)


def _md_tagmap(d):
    return "، ".join(f"{k}: {v}" for k, v in d.items()) if d else "—"


def render_md(p):
    """گزارشِ فارسیِ انسانی — رندرِ قطعی، فقط از خودِ دیکشنریِ سیما."""
    L = []
    L.append(f"# سیمای ریشهٔ «{p['ریشه']}»")
    L.append("")
    L.append(f"*{p['meta']['identity']}*")
    L.append("")
    h = p["هویت"]
    L.append("## هویت")
    L.append("")
    L.append("| شاهد (واژه) | آیه‌ها | لم‌ها |")
    L.append("|---|---|---|")
    lem = "، ".join(f"{x['لم']} ({x['شمار']})" for x in h["لم‌ها"]) or "—"
    L.append(f"| {h['شاهد']} | {h['آیه‌ها']} | {lem} |")
    L.append("")

    L.append("## آیه‌ها")
    cur = None
    for v in p["آیه‌ها"]:
        if v["سوره"] != cur:
            cur = v["سوره"]
            L.append("")
            L.append(f"### سورهٔ {cur} — {v['نام_سوره']} ({v['نوع']})")
        L.append("")
        L.append(_md_verse(v))
    L.append("")

    L.append("## صورت‌ها")
    L.append("")
    L.append("| صورت | شمار | مکان‌ها |")
    L.append("|---|---|---|")
    for f in p["صورت‌ها"]:
        L.append(f"| {f['صورت']} | {f['شمار']} | {'، '.join(f['مکان‌ها'])} |")
    L.append("")

    m = p["صرف"]
    L.append(f"## {m['برچسب']}")
    L.append("")
    L.append(f"- کلِ قطعه‌های STEM: {m['کل_قطعه‌های_STEM']}")
    L.append(f"- بر حسبِ pos: {_md_tagmap(m['بر_حسبِ_pos'])}")
    L.append(f"- فعل — aspect: {_md_tagmap(m['فعل']['aspect'])} · "
             f"voice: {_md_tagmap(m['فعل']['voice'])} · "
             f"mood: {_md_tagmap(m['فعل']['mood'])} · "
             f"person: {_md_tagmap(m['فعل']['person'])}")
    L.append(f"- اسم — case: {_md_tagmap(m['اسم']['case'])} · "
             f"state: {_md_tagmap(m['اسم']['state'])} · "
             f"gender: {_md_tagmap(m['اسم']['gender'])} · "
             f"number: {_md_tagmap(m['اسم']['number'])}")
    L.append("")

    d = p["پراکندگی"]
    L.append("## پراکندگی")
    L.append("")
    L.append("| سوره | نام | نوع | واژه‌ها | آیه‌ها | چگالی |")
    L.append("|---|---|---|---|---|---|")
    for r in d["بر_حسبِ_سوره"]:
        L.append(f"| {r['سوره']} | {r['نام']} | {r['نوع']} | {r['واژه‌ها']} | "
                 f"{r['آیه‌ها']} | {r['چگالی']} |")
    L.append("")
    L.append(f"- مکی/مدنی (واژه‌ها): {_md_tagmap(d['مکی_مدنی_واژه‌ها'])}")
    L.append(f"- مکی/مدنی (آیه‌ها): {_md_tagmap(d['مکی_مدنی_آیه‌ها'])}")
    L.append("")

    c = p["هم‌آیی"]
    L.append("## هم‌آیی (عیناً از موتورِ نفس‌ها — دو ابطال‌گر)")
    L.append("")
    if c["یادداشت"]:
        L.append(f"> {c['یادداشت']}")
        L.append("")
    if c["top"]:
        L.append("| همسایه | مشترک | انتظار | lift | p | پایدار | درجه |")
        L.append("|---|---|---|---|---|---|---|")
        for t in c["top"]:
            L.append(f"| {t['root']} | {t['shared']} | {t['expected']} | "
                     f"{t['lift']} | {t['p_perm']} | "
                     f"{'✓' if t['stable'] else '—'} | {t['tier']} |")
        L.append("")
        if c["ستون‌های_استنادی"]:
            L.append("ستون‌های استنادی (آیه‌های مشترک):")
            L.append("")
            for pair, ayat in c["ستون‌های_استنادی"].items():
                L.append(f"- {pair}: {'، '.join(ayat)}")
            L.append("")

    L.append("## پیوندِ زیسته")
    L.append("")
    if p["پیوند_زیسته"]:
        for x in p["پیوند_زیسته"]:
            L.append(f"- نفسِ {x['نفس']}: `{x['رکورد']}`")
        L.append("")
        L.append("برای برشِ کاملِ حافظه: `./cli/monad recall ریشه`؛ "
                 "برای مشورتِ رصدخانه: `./cli/monad observe ریشه`.")
    else:
        L.append("مناد هنوز این ریشه را نزیسته است.")
    L.append("")

    ctx = p["بافت_مجاور"]
    L.append("## بافتِ مجاور")
    L.append("")
    for side in ("قبل", "بعد"):
        items = ctx[side]
        shown = items[:10]
        row = "، ".join(f"{x['صورت']} ({x['شمار']})" for x in shown) or "—"
        extra = f" — کلِ {len(items)} صورتِ متمایز (فهرستِ کامل در JSON)" \
            if len(items) > 10 else ""
        L.append(f"- {side}: {row}{extra}")
    L.append("")
    L.append("---")
    L.append("")
    L.append(f"*{CLOSING}*")
    L.append("")
    return "\n".join(L)


def build(root):
    p = portrait(root)
    if p is None:
        print(json.dumps({"خطا": f"ریشهٔ «{root}» در پیکره نیست."},
                         ensure_ascii=False))
        return 1
    os.makedirs(OUT_DIR, exist_ok=True)
    json_path = f"{OUT_DIR}/{root}.json"
    md_path = f"{OUT_DIR}/{root}.md"
    with open(json_path, "w") as f:
        json.dump(p, f, ensure_ascii=False, indent=1)
        f.write("\n")
    with open(md_path, "w") as f:
        f.write(render_md(p))
    index = {}
    for jf in sorted(glob.glob(f"{OUT_DIR}/*.json")):
        d = json.load(open(jf))
        index[d["ریشه"]] = {"آیه‌ها": d["هویت"]["آیه‌ها"],
                            "شاهد": d["هویت"]["شاهد"]}
    with open("tadabbor/index.json", "w") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(json.dumps({"ریشه": root, "آیه‌ها": p["هویت"]["آیه‌ها"],
                      "واژه‌ها": p["هویت"]["شاهد"],
                      "json": json_path, "md": md_path},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"خطا": "نیازمندِ ریشه است — python3 tadabbor/build.py ریشه"},
                         ensure_ascii=False))
        sys.exit(1)
    sys.exit(build(sys.argv[1]))
