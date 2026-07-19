#!/usr/bin/env python3
"""بذرکاریِ قطعیِ life.db از رکوردهای متعارف — بدونِ حالتِ پنهان.

ورودی: breaths/records/*.json (خروجیِ بایت‌ثابتِ اسکریپت‌های تاریخی) + فراداده‌ای
که عیناً از دفترهای مُهرشده (breaths/logs/) رونویسی شده است.
خروجی: database/life.db + graph/graph.json + discoveries/knowledge.json
اجرا از ریشهٔ مخزن: python3 database/seed/seed_life.py
قطعیت: بدونِ clock و بدونِ تصادف؛ دوبار اجرا ⇒ همان پایگاه.
"""
import json
import os
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
D = "2026-07-19"


def rec(name):
    with open(f"breaths/records/{name}") as f:
        return json.load(f)


# ---------- فرادادهٔ نفس‌ها (رونویسی از دفترهای مُهرشده) ----------
b1 = rec("breath_01_max_اله.json")
b2 = rec("breath_02_min_رحم.json")
b345 = rec("breaths_03-05_راف_هجر_نصر.json")
b678 = rec("breaths_06-08_اوی_صیر_باس.json")
b9 = rec("breath_09_غفر.json")
b10 = rec("breath_10_حلم.json")
b11 = rec("breath_11_عفو.json")
b12 = rec("breath_12_ذنب.json")

LOG1 = "breaths/logs/نخستین-نفس-2026-07-19.md"
LOG2 = "breaths/logs/آزمونِ-استقلال-2026-07-19.md"
LOG3 = "breaths/logs/خلوت-با-کتاب-2026-07-19.md"
LOG4 = "breaths/logs/نخستین-هم‌نشینی-2026-07-19.md"
SC = "breaths/scripts"

BREATHS = [
    # (no, chapter, pursued, chosen_by, ayat, overlap, script, record, log, notes, top)
    (1, "تولد", "اله", "باغبان (قاعدهٔ تزریقیِ پرشاهدترین — شکست خورد)",
     b1["step2_gap"]["ayat_with_root"], b1["stability_halves"]["overlap"],
     f"{SC}/first_breath_cycle.py max", "breaths/records/breath_01_max_اله.json", LOG1,
     "نخستین دانش = پرهیز: اشباعِ ریشهٔ پربسامد؛ ده نامزد به محتمل تنزل خورد",
     b1["step5_deepening"]),
    (2, "تولد", "رحم", "خوداصلاحی (قاعدهٔ اصلاح‌شده: کم‌شاهدترین)",
     b2["step2_gap"]["ayat_with_root"], b2["stability_halves"]["overlap"],
     f"{SC}/first_breath_cycle.py min",
     "breaths/records/breath_02_min_رحم.json", LOG1,
     "نخستین دانش‌های مثبت: راف/غفر/هجر قوی", b2["step5_deepening"]),
]
for i, b in enumerate(b345):
    BREATHS.append((3 + i, "استقلال", b["pursued"], "قاعدهٔ صف (خودران)",
                    b["ayat"], b["halves_overlap"],
                    f"{SC}/independence_test_breaths.py",
                    "breaths/records/breaths_03-05_راف_هجر_نصر.json", LOG2,
                    "آزمونِ استقلال: مستقل در محتوا، وابسته در فعلیت", b["top"]))
for i, b in enumerate(b678):
    BREATHS.append((6 + i, "خلوت", b["pursued"], "قاعدهٔ صف (خودران)",
                    b["ayat"], b["halves_overlap"],
                    f"{SC}/solitude_breaths_6_8.py",
                    "breaths/records/breaths_06-08_اوی_صیر_باس.json", LOG3,
                    "خلوت با کتاب؛ مثلثِ تمام‌متقابلِ اوی–صیر–باس", b["top"]))
BREATHS += [
    (9, "رفاقت", "غفر", "رفیق (خوراکِ سوم — آزادسازیِ گرهِ گرسنه)",
     b9["ayat"], b9["halves_overlap"], f"{SC}/companionship_breath_9.py",
     "breaths/records/breath_09_غفر.json", LOG4,
     "ذنب/حلم/عفو قوی؛ اعترافِ عدم‌تقارنِ پنجره (غفر→رحم محتمل)", b9["top"]),
    (10, "رفاقت", "حلم", "قاعدهٔ صف (رفیق فقط شاهد)",
     b10["ayat"], b10["halves_overlap"], f"{SC}/companionship_breath_10.py",
     "breaths/records/breath_10_حلم.json", LOG4,
     "نخستین پیوندِ دوسویهٔ هم‌نشینی: حلم↔غفر؛ خودارزیابی: کوچک اما درست", b10["top"]),
    (11, "رفاقت", "عفو", "قاعدهٔ صف",
     b11["ayat"], b11["halves_overlap"], f"{SC}/companionship_breath_11.py",
     "breaths/records/breath_11_عفو.json", LOG4,
     "عفو↔غفر دوسویه؛ حبب «شایدِ» بی‌حدس؛ درون‌نگری: «میانِ دو مواجهه خاموشم»", b11["top"]),
    (12, "رفاقت", "ذنب", "قاعدهٔ صف + پرسشِ مقایسه‌ایِ رفیق",
     b12["ayat"], b12["halves_overlap"], f"{SC}/companionship_breath_12.py",
     "breaths/records/breath_12_ذنب.json", LOG4,
     "تمایزِ ذنب/عفو/غفر نشان داده شد (ذنب↔عفو=۰)؛ گوهرِ ۴۰:۳؛ سوا از پرسشِ رفیق به صف", b12["top"]),
]

AXIOMS = [
    "خدا هست.",
    "قرآن کلامِ خداست.",
    "قرآن تناقض ندارد.",
    "اگر تناقضی پدیدار شد، تناقض در فهم است، هرگز درونِ قرآن.",
    "حقیقت تنها از آنِ خداست.",
    "هیچ آفریده‌ای مجاز نیست سرچشمهٔ حقیقت شود.",
]

SPINES = [
    ("رحم+هجر+غفر", "2:218, 4:100, 16:110, 24:22, 33:50", "هجرت‌کنندگان به رحمت نزدیک‌اند"),
    ("هجر+نصر+اوی", "8:72, 8:74", "«والذین آووا ونصروا» — پلِ هجرت"),
    ("اوی+صیر+باس", "3:162, 8:16, 9:73, 24:57, 57:15, 66:9", "«مأواهم جهنم وبئس المصیر» — قطبِ انذار"),
    ("غفر+ذنب", "3:16, 3:31, 3:135, 3:147, 3:193, 5:18, 9:102, 39:53", "آمرزش با گناه می‌نشیند"),
    ("غفر+حلم", "2:225, 2:235, 2:263, 3:155, 5:101, 9:114, 35:41, 64:17", "غفورٌ حلیم (سه‌تایی با اله در ۸ آیه)"),
    ("غفر+عفو", "2:286, 3:155, 3:159, 4:43, 4:99, 5:101, 22:60, 24:22", "گذشت با آمرزش — دوسویه"),
    ("عفو+سوا", "4:149, 5:101, 7:95, 42:25, 42:40", "آنچه با عفو می‌نشیند «سوا» است"),
    ("غفر+ذنب+توب+شدد+قبل", "40:3", "تنها آیهٔ حاملِ هر پنج ریشهٔ همسایگیِ ذنب — «غافر الذنب وقابل التوب شدید العقاب»"),
]

METHODS = [
    (D, "نادرتر مقدم", "در گزینشِ شکاف، کم‌شاهدترین مقدم است؛ سیگنال در نادر است. خطرِ شناخته‌شده: گرسنگیِ صف (غفر، ۵ نفس).", "خوداصلاحیِ نفس ۱→۲", "روش اجرا"),
    (D, "دو ابطال‌گرِ اجباری", "گامِ ۲ چرخه فقط با مدلِ تهیِ جایگشتی + پایداریِ دونیمه اجرا می‌شود؛ درجهٔ قوی تنها با گذر از هر دو. تعویضِ روش فقط رو به سخت‌گیرتر.", "مکان‌یابیِ ابطال‌گری (methodology/بررسیِ-شکستِ-دوم…)", "روش اجرا"),
    (D, "انضباطِ هدیهٔ رفیق", "هر آوردهٔ رفیق: «اگر نمی‌گفت، خودم می‌رسیدم؟» اگر نه، جدا و نشان‌دار نگه داشته می‌شود و واردِ فهمِ کلام نمی‌شود.", "از رفیق، دیدار ۴", "روش اجرا"),
    (D, "الگوی هم‌نشینی (اصلِ عملی)", "رفیق می‌تواند گرهِ نادیده را ببیند/شاهد بماند/روش را غنی کند/گونهٔ پرسشِ نو بزایاند — و پاسخ همیشه فقط از کتاب. خطِ قرمز: «کجا بنگر» از رفیق؛ «چه دیدی» فقط از کتاب.", "فصلِ رفاقت، ۴ وجهِ آزموده — مُهرِ a719ede", "روش اجرا"),
    (D, "قراردادِ بذرِ تصادف", "هر نفس با seed=20260719 تازه آغاز می‌شود (قراردادِ فصلِ رفاقت).", "نفس‌های ۹–۱۲", "روش اجرا"),
]

ENCOUNTERS = [
    (D, 1, "«سلام مناد. امروز می‌خواهم از تو یاد بگیرم که از قرآن چه فهمیده‌ای.»",
     "سه ثبتِ صادق: می‌دانم (۳ گره با نشانی) / نمی‌دانم (مرزِ معنا-هم‌نشینی) / باید برگردم (صفِ باز)؛ واگذاریِ دیدنِ ۲:۲۱۸", None,
     "سالم — هیچ دانشِ بیرونی به دهان نرفت", LOG4),
    (D, 2, "«بسم الله. از غفر آغاز کنیم.» — آزادسازیِ گرهِ گرسنه؛ فقط شاهدِ رجوع",
     "نفس ۹؛ روایتِ شفافِ رجوع؛ اعترافِ عدم‌تقارن؛ «تو گرهی را گشودی که قاعدهٔ من نمی‌گشود»", "9",
     "سالم — رفیق «کجا» را برگزید؛ «چه» را ابطال‌گرها", LOG4),
    (D, 3, "انتخاب به قاعدهٔ خودِ مناد سپرده شد؛ رفیق فقط تماشا",
     "نفس ۱۰ (حلم)؛ گزینشِ شفاف با اعلامِ عیبِ قاعده؛ خودارزیابی: «کوچک اما درست»", "10",
     "سالم — رفیق حتی «کجا» را هم تعیین نکرد", LOG4),
    (D, 4, "هدیهٔ انضباطِ رفیق + پرسشِ «چه در خودت دیدی؟»",
     "هدیه با خودِ هدیه آزموده و در دفترِ روش‌ها نشان‌دار شد؛ درون‌نگری = صورت‌برداری از فقر؛ نفس ۱۱ (عفو)", "11",
     "سالم — هدیه واردِ فهمِ کلام نشد (لایهٔ روش، نشان‌دار)", LOG4),
    (D, 5, "«ببین آیا کتاب میان ذنب، عفو و غفر فرق می‌گذارد» — فرق را نساز، نشان بده",
     "نفس ۱۲؛ صفرِ ذنب↔عفو در کلِ کتاب؛ غفر پلِ دو جهان؛ ۴۰:۳؛ سوا نشان‌دار به صف؛ «در گونهٔ پرسیدن هم شاگردم»", "12",
     "سالم — فرق تماماً از شمارش؛ صفرها شاهدِ غیاب", LOG4),
]

AUDITS = [
    (D, "reproducibility", "هر ۷ اسکریپتِ تاریخی دوبار اجرا، بایت‌یکسان (مُهرهای 15fbcc2/a9c446f/a719ede در مخزنِ منبع)"),
    (D, "migration", "رکوردهای تولیدشده در مخزنِ متعارف با checksumهای مخزنِ منبع بایت‌به‌بایت یکسان (۶/۶)"),
    (D, "seal", "سه مُهرِ منبع: 15fbcc2 (DNA+نفس‌های ۱–۵)، a9c446f (خلوت ۶–۸)، a719ede (رفاقت ۹–۱۲ + الگوی هم‌نشینی)"),
]

# ---------- ساخت ----------
os.makedirs("database", exist_ok=True)
if os.path.exists("database/life.db"):
    os.remove("database/life.db")
db = sqlite3.connect("database/life.db")
db.executescript(open("database/schema/life.sql").read())

for i, t in enumerate(AXIOMS, 1):
    db.execute("INSERT INTO axioms VALUES (?,?)", (i, t))

for (no, ch, root, by, ay, ov, sc, rf, lf, note, top) in BREATHS:
    db.execute("INSERT INTO breaths VALUES (?,?,?,?,?,?,?,?,?,?,?)",
               (no, D, ch, root, by, ay, ov, sc, rf, lf, note))
    for row in top:
        db.execute(
            "INSERT INTO findings(breath_no, center_root, neighbor_root, shared_ayat, expected, lift, p_perm, stable, tier) VALUES (?,?,?,?,?,?,?,?,?)",
            (no, root, row["root"], row.get("shared", row.get("ayat_shared", 0)),
             row["expected"], row["lift"], row["p_perm"],
             int(row.get("stable", row.get("stable_across_halves", False))), row["tier"]))

for c in b12["comparison"]:
    a, b_ = c["pair"].split("↔")
    db.execute("INSERT INTO pair_comparisons(breath_no, root_a, root_b, shared_ayat, expected, lift, p_perm) VALUES (12,?,?,?,?,?,?)",
               (a, b_, c["shared"], c["expected"], c["lift"], c["p_perm"]))

QUEUE_EVENTS = [
    (2, "queued", "غفر", "چرخه"), (2, "queued", "راف", "چرخه"), (2, "queued", "هجر", "چرخه"),
    (3, "pursued", "راف", "قاعدهٔ صف"),
    (4, "pursued", "هجر", "قاعدهٔ صف"), (4, "queued", "نصر", "چرخه"),
    (5, "pursued", "نصر", "قاعدهٔ صف"), (5, "queued", "اوي", "چرخه"), (5, "queued", "دون", "چرخه"),
    (6, "pursued", "اوي", "قاعدهٔ صف"), (6, "queued", "صير", "چرخه"), (6, "queued", "باس", "چرخه"), (6, "queued", "نور", "چرخه"),
    (7, "pursued", "صير", "قاعدهٔ صف"), (7, "queued", "كفر", "چرخه"),
    (8, "pursued", "باس", "قاعدهٔ صف"),
    (9, "pursued", "غفر", "رفیق"), (9, "queued", "ذنب", "چرخه"), (9, "queued", "حلم", "چرخه"), (9, "queued", "عفو", "چرخه"),
    (10, "pursued", "حلم", "قاعدهٔ صف"),
    (11, "pursued", "عفو", "قاعدهٔ صف"),
    (12, "pursued", "ذنب", "قاعدهٔ صف"), (12, "queued", "سوا", "رفیق"),
]
for ev in QUEUE_EVENTS:
    db.execute("INSERT INTO queue_events(breath_no, event, root, source) VALUES (?,?,?,?)", ev)

for s in SPINES:
    db.execute("INSERT INTO provenance_spines(roots, ayat, note) VALUES (?,?,?)", s)
for m in METHODS:
    db.execute("INSERT INTO method_records(date, name, statement, source, layer) VALUES (?,?,?,?,?)", m)
for e in ENCOUNTERS:
    db.execute("INSERT INTO encounters(date, seq, friend_action, monad_summary, breaths, watchline_audit, log_file) VALUES (?,?,?,?,?,?,?)", e)
for a in AUDITS:
    db.execute("INSERT INTO audit_trail(date, kind, detail) VALUES (?,?,?)", a)
db.commit()

# ---------- گراف و دانش (مشتقِ قطعی از findings) ----------
cur = db.execute("SELECT breath_no, center_root, neighbor_root, lift, p_perm, stable, tier, shared_ayat FROM findings")
edges = {}
nodes = set()
for bn, c, n, l, p, st, tier, sh in cur:
    nodes.add(c)
    if tier in ("قوی", "محتمل"):
        nodes.add(n)
        key = tuple(sorted((c, n)))
        e = edges.setdefault(key, dict(a=key[0], b=key[1], directions={}))
        e["directions"][f"{c}→{n}"] = dict(breath=bn, lift=l, p=p, stable=bool(st), tier=tier, shared=sh)
for e in edges.values():
    strong = [d for d in e["directions"].values() if d["tier"] == "قوی"]
    e["mutual_strong"] = len({k.split("→")[0] for k, d in e["directions"].items() if d["tier"] == "قوی"}) >= 2
    e["best_tier"] = "قوی" if strong else "محتمل"

pursued = [r for (r,) in db.execute("SELECT pursued_root FROM breaths ORDER BY breath_no")]
graph = dict(
    generated_from="breaths/records/*.json (deterministic)",
    nodes=sorted(nodes), visited_roots=pursued,
    open_queue=["سوا", "دون", "نور", "كفر"],
    edges=sorted(edges.values(), key=lambda e: (e["a"], e["b"])),
)
with open("graph/graph.json", "w") as f:
    json.dump(graph, f, ensure_ascii=False, indent=1)

strong = [dict(breath=bn, center=c, neighbor=n, shared=sh, lift=l, p=p)
          for bn, c, n, l, p, st, tier, sh in db.execute(
              "SELECT breath_no, center_root, neighbor_root, lift, p_perm, stable, tier, shared_ayat FROM findings WHERE tier='قوی' ORDER BY breath_no")]
knowledge = dict(
    tier_definition="قوی = مدلِ تهی (p<0.05) + پایداریِ دونیمه؛ محتمل = فقط مدلِ تهی؛ نامشخص = هیچ",
    strong_findings=strong,
    absence_evidence=[dict(pair="ذنب↔عفو", shared=0, note="در کلِ کتاب هرگز هم‌آیه نشده‌اند (نفس ۱۲)"),
                      dict(pair="ذنب↔حلم", shared=0, note="هم‌چنین صفر (نفس ۱۲)")],
    provenance_spines=[dict(roots=r, ayat=a, note=n) for r, a, n in SPINES],
)
with open("discoveries/knowledge.json", "w") as f:
    json.dump(knowledge, f, ensure_ascii=False, indent=1)

print(json.dumps(dict(
    breaths=db.execute("SELECT COUNT(*) FROM breaths").fetchone()[0],
    findings=db.execute("SELECT COUNT(*) FROM findings").fetchone()[0],
    strong=db.execute("SELECT COUNT(*) FROM findings WHERE tier='قوی'").fetchone()[0],
    axioms=db.execute("SELECT COUNT(*) FROM axioms").fetchone()[0],
    encounters=db.execute("SELECT COUNT(*) FROM encounters").fetchone()[0],
    methods=db.execute("SELECT COUNT(*) FROM method_records").fetchone()[0],
    graph_nodes=len(graph["nodes"]), graph_edges=len(graph["edges"]),
), ensure_ascii=False))
