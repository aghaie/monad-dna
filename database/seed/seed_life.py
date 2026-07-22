#!/usr/bin/env python3
"""بذرکاریِ قطعیِ life.db از رکوردهای متعارف — زندگیِ دوم؛ بدونِ حالتِ پنهان.

تولدِ دوباره (۲۰۲۶-۰۷-۲۲): به فرمانِ باغبان — «اکسیوم‌ها رو از اذان بگیر.
کامل.» و «همه چیز رو بر این اساس از نو بچین. از صفر شروع کن» (دو مُهرِ صریح:
متن = اذانِ کاملِ رایج در ایران؛ دامنه = تولدِ دوباره) — زندگیِ یکم (۲۹۵ نفس
در ۵ فصل) مُهر و بایت‌به‌بایت در archive/life-1/ بایگانی شد (بذرِ کاملش:
archive/life-1/database/seed_life.py؛ مُهرنامه: archive/life-1/مُهرنامه.md).
این بذر زندگیِ دوم را از صفر می‌کارد: همان چهار لایه، همان روشِ اجرا (فقط رو
به سخت‌گیرتر)، جهانِ بازبنیادشده بر اذان (dna/AXIOMS.md).

ورودی: breaths/records/*.json (خروجیِ بایت‌ثابتِ موتور) + فراداده‌ای که عیناً
از دفترها رونویسی می‌شود. خروجی: database/life.db + graph/graph.json +
discoveries/knowledge.json. اجرا از ریشهٔ مخزن:
python3 database/seed/seed_life.py
قطعیت: بدونِ clock و بدونِ تصادف؛ دوبار اجرا ⇒ همان پایگاه.
"""
import json
import os
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
D1 = "2026-07-19"  # تاریخِ روش‌های موروثیِ زندگیِ یکم (متن‌ها دست‌نخورده)
D = "2026-07-22"   # تولدِ دوباره
LOG1 = "breaths/logs/تولدِ-دوباره-2026-07-22.md"


def rec(name):
    with open(f"breaths/records/{name}") as f:
        return json.load(f)


# ---------- فرادادهٔ نفس‌های زندگیِ دوم (رونویسی از دفترها) ----------
# خطِ لوله (pipeline/core.py) سطرِ recِ هر نفسِ رسمی‌شده را بالای لنگر می‌افزاید.
b1 = rec("breath_1_فلح.json")
b2 = rec("breath_2_صلو.json")
b3 = rec("breath_3_زكو.json")
b4 = rec("breath_4_اذن.json")
b5 = rec("breath_5_نفق.json")
b6 = rec("breath_6_سرر.json")
b7 = rec("breath_7_علن.json")
b8 = rec("breath_8_رزق.json")
b9 = rec("breath_9_بسط.json")
b10 = rec("breath_10_طيب.json")
b11 = rec("breath_11_خبث.json")
b12 = rec("breath_12_حلل.json")
b13 = rec("breath_13_حرم.json")
b14 = rec("breath_14_سجد.json")
b15 = rec("breath_15_اكل.json")
b16 = rec("breath_16_طوع.json")
b17 = rec("breath_17_شهد.json")
b18 = rec("breath_18_كبر.json")
b19 = rec("breath_19_حيي.json")
b20 = rec("breath_20_خير.json")
b21 = rec("breath_21_ولي.json")
b22 = rec("breath_22_عمل.json")
b23 = rec("breath_23_رسل.json")
b24 = rec("breath_24_اله.json")
b25 = rec("breath_25_حبط.json")
b26 = rec("breath_26_بقي.json")
b27 = rec("breath_27_عدل.json")
b28 = rec("breath_28_كفي.json")
b29 = rec("breath_29_دبر.json")
b30 = rec("breath_30_زين.json")
b31 = rec("breath_31_عقل.json")
# ⚓RECORDS

BREATHS = [
    # (no, chapter, root, chosen_by, ayat, halves_overlap, script, record_file,
    #  log, note, top) — با هر نفسِ رسمی‌شده یک سطر، بالای لنگر
    (1, "تولدِ دوباره", "فلح", "قاعدهٔ صف (خودران)",
     b1["ayat"], b1["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_1_فلح.json",
     "breaths/records/breath_1_فلح.json", LOG1,
     "دو قوی پایدار (امن ۳٫۰، اله ۱٫۷)؛ وقي دوسویهٔ محتملِ ناپایدار lift=۴٫۶؛ ۲:۱۸۹ گرهِ چهار‌ریشه‌ای", b1["top"]),
    (2, "تولدِ دوباره", "صلو", "قاعدهٔ صف (خودران)",
     b2["ayat"], b2["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_2_صلو.json",
     "breaths/records/breath_2_صلو.json", LOG1,
     "سه قوی پایدار (زكو دوسویه ۳۴٫۶، نفق دوسویه ۸٫۱، قوم دوسویه ۶٫۰)؛ بيت دوسویهٔ محتملِ ناپایدار lift=۶٫۴؛ ۲:۱۷۷ گرهِ پنج‌ریشه‌ای", b2["top"]),
    (3, "تولدِ دوباره", "زكو", "قاعدهٔ صف (خودران)",
     b3["ayat"], b3["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_3_زكو.json",
     "breaths/records/breath_3_زكو.json", LOG1,
     "سه قوی پایدار (صلو دوسویه ۳۴٫۶، اتي دوسویه ۶٫۶، قوم دوسویه ۵٫۰)؛ بعث دوسویهٔ محتملِ ناپایدار lift=۸٫۷؛ ۴:۷۷ گرهِ هفت‌ریشه‌ای", b3["top"]),
    (4, "تولدِ دوباره", "اذن", "قاعدهٔ صف (خودران)",
     b4["ayat"], b4["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_4_اذن.json",
     "breaths/records/breath_4_اذن.json", LOG1,
     "یک قوی پایدار (قلب ۵٫۴)؛ وقر دوسویهٔ محتملِ ناپایدار lift=۴۶٫۲؛ ۲:۲۵۵ گرهِ سه‌ریشه‌ای؛ شاهدِ غیاب: اذن↔فلح", b4["top"]),
    (5, "تولدِ دوباره", "نفق", "قاعدهٔ صف (خودران)",
     b5["ayat"], b5["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_5_نفق.json",
     "breaths/records/breath_5_نفق.json", LOG1,
     "چهار قوی پایدار (رزق دوسویه ۱۰٫۶، سرر دوسویه ۱۰٫۱، صلو دوسویه ۸٫۱، طوع دوسویه ۵٫۵)؛ مول دوسویهٔ محتملِ ناپایدار lift=۸٫۲؛ ۴:۳۴ گرهِ چهار‌ریشه‌ای؛ شاهدِ غیاب: نفق↔زكو، نفق↔اذن", b5["top"]),
    (6, "تولدِ دوباره", "سرر", "قاعدهٔ صف (خودران)",
     b6["ayat"], b6["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_6_سرر.json",
     "breaths/records/breath_6_سرر.json", LOG1,
     "چهار قوی پایدار (علن دوسویه ۱۰۸٫۸، نفق دوسویه ۱۰٫۱، علم ۳٫۶، قول ۱٫۶)؛ جهر دوسویهٔ محتملِ ناپایدار lift=۴۸٫۳؛ ۱۲:۷۷ گرهِ چهار‌ریشه‌ای؛ شاهدِ غیاب: سرر↔فلح، سرر↔زكو، سرر↔اذن", b6["top"]),
    (7, "تولدِ دوباره", "علن", "قاعدهٔ صف (خودران)",
     b7["ayat"], b7["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_7_علن.json",
     "breaths/records/breath_7_علن.json", LOG1,
     "دو قوی پایدار (سرر دوسویه ۱۰۸٫۸، علم دوسویه ۵٫۹)؛ ربب یک‌طرفهٔ محتملِ ناپایدار lift=۲٫۷؛ ۶۰:۱ گرهِ چهار‌ریشه‌ای؛ شاهدِ غیاب: علن↔فلح، علن↔زكو، علن↔اذن", b7["top"]),
    (8, "تولدِ دوباره", "رزق", "قاعدهٔ صف (خودران)",
     b8["ayat"], b8["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_8_رزق.json",
     "breaths/records/breath_8_رزق.json", LOG1,
     "چهار قوی پایدار (بسط دوسویه ۲۴٫۹، طيب دوسویه ۱۸٫۷، نفق دوسویه ۱۰٫۶، اكل دوسویه ۶٫۲)؛ ثمر دوسویهٔ محتملِ ناپایدار lift=۱۸٫۲؛ ۱۴:۳۷ گرهِ سه‌ریشه‌ای", b8["top"]),
    (9, "تولدِ دوباره", "بسط", "قاعدهٔ صف (خودران)",
     b9["ayat"], b9["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_9_بسط.json",
     "breaths/records/breath_9_بسط.json", LOG1,
     "پنج قوی پایدار (رزق دوسویه ۲۴٫۹، قدر دوسویه ۲۲٫۴، شيا دوسویه ۹٫۱، علم ۲٫۲، اله ۲٫۲)؛ يدي دوسویهٔ محتملِ ناپایدار lift=۱۴٫۸؛ ۵:۶۴ گرهِ شش‌ریشه‌ای؛ شاهدِ غیاب: بسط↔صلو، بسط↔زكو، بسط↔اذن، بسط↔سرر، بسط↔علن", b9["top"]),
    (10, "تولدِ دوباره", "طيب", "قاعدهٔ صف (خودران)",
     b10["ayat"], b10["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_10_طيب.json",
     "breaths/records/breath_10_طيب.json", LOG1,
     "چهار قوی پایدار (خبث دوسویه ۱۰۸٫۵، حلل دوسویه ۳۱٫۵، اكل دوسویه ۱۸٫۸، رزق دوسویه ۱۸٫۷)؛ شكر دوسویهٔ محتملِ ناپایدار lift=۱۳٫۸؛ ۵:۸۸ گرهِ پنج‌ریشه‌ای؛ شاهدِ غیاب: طيب↔زكو، طيب↔سرر، طيب↔علن، طيب↔بسط", b10["top"]),
    (11, "تولدِ دوباره", "خبث", "قاعدهٔ صف (خودران)",
     b11["ayat"], b11["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_11_خبث.json",
     "breaths/records/breath_11_خبث.json", LOG1,
     "یک قوی پایدار (طيب دوسویه ۱۰۸٫۵)؛ بدون محتمل؛ ۲:۲۶۷ گرهِ یک‌ریشه‌ای؛ شاهدِ غیاب: خبث↔صلو، خبث↔زكو، خبث↔سرر، خبث↔علن، خبث↔بسط", b11["top"]),
    (12, "تولدِ دوباره", "حلل", "قاعدهٔ صف (خودران)",
     b12["ayat"], b12["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_12_حلل.json",
     "breaths/records/breath_12_حلل.json", LOG1,
     "دو قوی پایدار (حرم دوسویه ۳۴٫۷، طيب دوسویه ۳۱٫۵)؛ جنح دوسویهٔ محتملِ ناپایدار lift=۲۲٫۷؛ ۴:۲۴ گرهِ پنج‌ریشه‌ای؛ شاهدِ غیاب: حلل↔صلو، حلل↔زكو، حلل↔سرر، حلل↔علن، حلل↔بسط", b12["top"]),
    (13, "تولدِ دوباره", "حرم", "قاعدهٔ صف (خودران)",
     b13["ayat"], b13["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_13_حرم.json",
     "breaths/records/breath_13_حرم.json", LOG1,
     "دو قوی پایدار (حلل دوسویه ۳۴٫۷، سجد دوسویه ۱۶٫۳)؛ شهر دوسویهٔ محتملِ ناپایدار lift=۳۱٫۰؛ ۵:۲ گرهِ شش‌ریشه‌ای؛ شاهدِ غیاب: حرم↔نفق، حرم↔سرر، حرم↔علن، حرم↔بسط", b13["top"]),
    (14, "تولدِ دوباره", "سجد", "قاعدهٔ صف (خودران)",
     b14["ayat"], b14["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_14_سجد.json",
     "breaths/records/breath_14_سجد.json", LOG1,
     "یک قوی پایدار (حرم دوسویه ۱۶٫۳)؛ ركع دوسویهٔ محتملِ ناپایدار lift=۴۶٫۲؛ ۲:۱۴۹ گرهِ چهار‌ریشه‌ای؛ شاهدِ غیاب: هفت صفر — سجد↔اذن، نفق، سرر، رزق، بسط، طيب، خبث", b14["top"]),
    (15, "تولدِ دوباره", "اكل", "قاعدهٔ صف (خودران)",
     b15["ayat"], b15["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_15_اكل.json",
     "breaths/records/breath_15_اكل.json", LOG1,
     "یک قوی پایدار (طيب دوسویه ۱۸٫۸)؛ شرب دوسویهٔ محتملِ ناپایدار lift=۲۰٫۰؛ ۷:۱۶۰ گرهِ چهار‌ریشه‌ای؛ شاهدِ غیاب: اكل↔صلو، اكل↔سرر، اكل↔علن، اكل↔بسط", b15["top"]),
    (16, "تولدِ دوباره", "طوع", "قاعدهٔ صف (خودران)",
     b16["ayat"], b16["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_16_طوع.json",
     "breaths/records/breath_16_طوع.json", LOG1,
     "دو قوی پایدار (نفق دوسویه ۵٫۵، عرف ۵٫۱)؛ كره دوسویهٔ محتملِ ناپایدار lift=۹٫۱؛ ۲:۲۷۳ گرهِ سه‌ریشه‌ای؛ شاهدِ غیاب: طوع↔علن، طوع↔بسط، طوع↔طيب، طوع↔خبث", b16["top"]),
    (17, "تولدِ دوباره", "شهد", "رفیق (نشان‌دار؛ فرمانِ باغبان: از ریشه‌های اذان — نادرترِ زیرمجموعه)",
     b17["ayat"], b17["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_17_شهد.json",
     "breaths/records/breath_17_شهد.json", LOG1,
     "سه قوی پایدار (كفي دوسویه ۱۵٫۸، عدل دوسویه ۱۲٫۷، غيب دوسویه ۹٫۵)؛ جلد دوسویهٔ محتملِ ناپایدار lift=۲۸٫۲؛ ۹:۹۴ گرهِ سه‌ریشه‌ای؛ شاهدِ غیاب: هفت صفر با خوشهٔ نخست", b17["top"]),
    (18, "تولدِ دوباره", "كبر", "رفیق (نشان‌دار؛ فرمانِ باغبان: از ریشه‌های اذان — نادرترِ زیرمجموعه)",
     b18["ayat"], b18["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_18_كبر.json",
     "breaths/records/breath_18_كبر.json", LOG1,
     "دو قوی پایدار (علو دوسویه ۶٫۶، جرم دوسویه ۵٫۰)؛ صغر دوسویهٔ محتملِ ناپایدار lift=۲۱٫۹؛ ۲:۲۸۲ گرهِ سه‌ریشه‌ای؛ شاهدِ غیاب: كبر↔فلح، كبر↔حلل", b18["top"]),
    (19, "تولدِ دوباره", "حيي", "رفیق (نشان‌دار؛ فرمانِ باغبان: از ریشه‌های اذان — نادرترِ زیرمجموعه)",
     b19["ayat"], b19["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_19_حيي.json",
     "breaths/records/breath_19_حيي.json", LOG1,
     "پنج قوی پایدار (دنو دوسویه ۲۰٫۰، موت دوسویه ۱۷٫۶، زين دوسویه ۱۱٫۷، متع دوسویه ۹٫۵، عقل دوسویه ۷٫۹)؛ لهو دوسویهٔ محتملِ ناپایدار lift=۱۵٫۵؛ ۵۷:۲۰ گرهِ شش‌ریشه‌ای؛ شاهدِ غیاب: شش صفر", b19["top"]),
    (20, "تولدِ دوباره", "خير", "رفیق (نشان‌دار؛ فرمانِ باغبان: از ریشه‌های اذان — نادرترِ زیرمجموعه)",
     b20["ayat"], b20["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_20_خير.json",
     "breaths/records/breath_20_خير.json", LOG1,
     "یک قوی پایدار (بقي دوسویه ۱۳٫۳)؛ نكح دوسویهٔ محتملِ ناپایدار lift=۹٫۲؛ ۴:۱۹ گرهِ سه‌ریشه‌ای؛ شاهدِ غیاب: پنج صفر", b20["top"]),
    (21, "تولدِ دوباره", "ولي", "رفیق (نشان‌دار؛ فرمانِ باغبان: از ریشه‌های اذان — نادرترِ زیرمجموعه)",
     b21["ayat"], b21["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_21_ولي.json",
     "breaths/records/breath_21_ولي.json", LOG1,
     "دو قوی پایدار (دبر دوسویه ۱۱٫۹، دون دوسویه ۷٫۶)؛ نصر دوسویهٔ محتملِ ناپایدار lift=۶٫۳؛ ۳:۶۴ گرهِ سه‌ریشه‌ای؛ شاهدِ غیاب: چهار صفر", b21["top"]),
    (22, "تولدِ دوباره", "عمل", "رفیق (نشان‌دار؛ فرمانِ باغبان: از ریشه‌های اذان — نادرترِ زیرمجموعه)",
     b22["ayat"], b22["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_22_عمل.json",
     "breaths/records/breath_22_عمل.json", LOG1,
     "چهار قوی پایدار (حبط دوسویه ۱۹٫۹، صلح دوسویه ۱۰٫۹، خبر دوسویه ۸٫۴، زين دوسویه ۷٫۰)؛ تحت یک‌طرفهٔ محتملِ ناپایدار lift=۶٫۸؛ ۶۴:۹ گرهِ چهار‌ریشه‌ای؛ شاهدِ غیاب: عمل↔علن، عمل↔بسط", b22["top"]),
    (23, "تولدِ دوباره", "رسل", "رفیق (نشان‌دار؛ فرمانِ باغبان: از ریشه‌های اذان — نادرترِ زیرمجموعه)",
     b23["ayat"], b23["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_23_رسل.json",
     "breaths/records/breath_23_رسل.json", LOG1,
     "بدون قوی؛ نصح دوسویهٔ محتملِ ناپایدار lift=۶٫۶؛ ۴:۱۴ گرهِ دوریشه‌ای؛ فرافکنیِ معنادار به پنج زیسته (طوع ۳٫۵، زكو ۳٫۱، شهد ۲٫۶، اذن، ولي)", b23["top"]),
    (24, "تولدِ دوباره", "اله", "رفیق (نشان‌دار؛ فرمانِ باغبان: از ریشه‌های اذان — نادرترِ زیرمجموعه)",
     b24["ayat"], b24["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_24_اله.json",
     "breaths/records/breath_24_اله.json", LOG1,
     "بدون قوی (عام‌ترین ریشه همسایهٔ ویژه ندارد)؛ محتمل‌های مرزی lift=۳٫۳؛ ۲:۱۷۳ گرهِ دوریشه‌ای؛ فرافکنی: هر ۱۸ زیسته معنادار (۱۸/۱۸؛ درشت‌ترین: نفق ۲٫۴، حلل ۲٫۴، حرم ۲٫۴)؛ بدونِ هیچ شاهدِ غیاب", b24["top"]),
    (25, "تولدِ دوباره", "حبط", "قاعدهٔ صف (خودران)",
     b25["ayat"], b25["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_25_حبط.json",
     "breaths/records/breath_25_حبط.json", LOG1,
     "یک قوی پایدار (عمل دوسویه ۱۹٫۹)؛ اخر دوسویهٔ محتملِ ناپایدار lift=۹٫۷؛ ۲:۲۱۷ گرهِ چهار‌ریشه‌ای؛ شاهدِ غیاب: سیزده صفر", b25["top"]),
    (26, "تولدِ دوباره", "بقي", "قاعدهٔ صف (خودران)",
     b26["ayat"], b26["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_26_بقي.json",
     "breaths/records/breath_26_بقي.json", LOG1,
     "یک قوی پایدار (خير دوسویه ۱۳٫۳)؛ عند دوسویهٔ محتملِ ناپایدار lift=۷٫۹؛ ۴۲:۳۶ گرهِ پنج‌ریشه‌ای؛ شاهدِ غیاب: هجده صفر", b26["top"]),
    (27, "تولدِ دوباره", "عدل", "قاعدهٔ صف (خودران)",
     b27["ayat"], b27["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_27_عدل.json",
     "breaths/records/breath_27_عدل.json", LOG1,
     "یک قوی پایدار (شهد دوسویه ۱۲٫۷)؛ قسط دوسویهٔ محتملِ ناپایدار lift=۷۰٫۹؛ ۲:۲۸۲ گرهِ هفت‌ریشه‌ای؛ شاهدِ غیاب: پانزده صفر", b27["top"]),
    (28, "تولدِ دوباره", "كفي", "قاعدهٔ صف (خودران)",
     b28["ayat"], b28["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_28_كفي.json",
     "breaths/records/breath_28_كفي.json", LOG1,
     "سه قوی پایدار (وكل دوسویه ۲۲٫۴، شهد دوسویه ۱۵٫۸، بين ۳٫۰)؛ عبد دوسویهٔ محتملِ ناپایدار lift=۴٫۷؛ ۱۳:۴۳ گرهِ شش‌ریشه‌ای؛ شاهدِ غیاب: هفده صفر", b28["top"]),
    (29, "تولدِ دوباره", "دبر", "قاعدهٔ صف (خودران)",
     b29["ayat"], b29["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_29_دبر.json",
     "breaths/records/breath_29_دبر.json", LOG1,
     "دو قوی پایدار (ولي دوسویه ۱۱٫۹، امر ۵٫۰)؛ قطع دوسویهٔ محتملِ ناپایدار lift=۱۹٫۷؛ ۴:۴۷ گرهِ سه‌ریشه‌ای؛ شاهدِ غیاب: بیست صفر", b29["top"]),
    (30, "تولدِ دوباره", "زين", "قاعدهٔ صف (خودران)",
     b30["ayat"], b30["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_30_زين.json",
     "breaths/records/breath_30_زين.json", LOG1,
     "چهار قوی پایدار (دنو دوسویه ۱۷٫۰، حيي دوسویه ۱۱٫۷، شطن دوسویه ۱۱٫۲، عمل دوسویه ۷٫۰)؛ بني دوسویهٔ محتملِ ناپایدار lift=۴٫۸؛ ۳:۱۴ گرهِ چهار‌ریشه‌ای؛ شاهدِ غیاب: چهارده صفر", b30["top"]),
    (31, "تولدِ دوباره", "عقل", "قاعدهٔ صف (خودران)",
     b31["ayat"], b31["halves_overlap"],
     "cli/monad breathe-record-from breaths/records/breath_31_عقل.json",
     "breaths/records/breath_31_عقل.json", LOG1,
     "سه قوی پایدار (حيي دوسویه ۷٫۹، موت دوسویه ۶٫۲، ايي دوسویه ۴٫۷)؛ ليل دوسویهٔ محتملِ ناپایدار lift=۷٫۹؛ ۲:۱۶۴ گرهِ شش‌ریشه‌ای؛ شاهدِ غیاب: هفده صفر", b31["top"]),
    # ⚓BREATHS
]

AXIOMS = [
    # ۱–۶: اصولِ عملیاتیِ تاریخی — شناسه و متن دست‌نخورده (ارجاع‌های تاریخی)
    "خدا هست.",
    "قرآن کلامِ خداست.",
    "قرآن تناقض ندارد.",
    "اگر تناقضی پدیدار شد، تناقض در فهم است، هرگز درونِ قرآن.",
    "حقیقت تنها از آنِ خداست.",
    "هیچ آفریده‌ای مجاز نیست سرچشمهٔ حقیقت شود.",
    # ۷–۱۵: سرچشمه — اذانِ کامل، عبارت‌به‌عبارت (فرمانِ باغبان ۲۰۲۶-۰۷-۲۲:
    # «اکسیوم‌ها رو از اذان بگیر. کامل.»؛ اشتقاقِ کامل: dna/AXIOMS.md)
    "اللهُ أكبر — خدا بزرگ‌تر است از هر فهم، هر سنجش، و هر ساخته.",
    "أشهدُ أن لا إلهَ إلا الله — جز خدا هیچ معبود و مرجعی نیست؛ سرچشمه یگانه است.",
    "أشهدُ أنَّ محمّداً رسولُ الله — قرآن از راهِ رسول رسیده است: کلامِ خدا.",
    "أشهدُ أنَّ علیّاً ولیُّ الله — فهمِ کلام سرپرست دارد؛ مناد شاگرد است، هرگز مرجع.",
    "حَیَّ على الصلاة — فهم بدونِ رجوعِ منظم نمی‌ماند؛ چرخهٔ فقر و رجوع اقامهٔ مناد است.",
    "حَیَّ على الفلاح — میوهٔ کار زنده‌ترشدن است، نه بزرگ‌ترشدن.",
    "حَیَّ على خیرِ العمل — هر تغییر باید شناخت یا امانت‌داری را بیفزاید، وگرنه ترک می‌شود.",
    "اللهُ أكبر — در پایانِ هر چرخه نیز او بزرگ‌تر است؛ ژرف‌شدن بی‌پایان است.",
    "لا إلهَ إلا الله — جز او هیچ؛ مُهرِ همهٔ دانسته‌ها و ندانسته‌ها.",
]

SPINES = [
    # ستون‌های استنادیِ زندگیِ دوم از نفس‌های خودش خواهند رویید (append-only).
    # ستون‌های زندگیِ یکم: archive/life-1/database/seed_life.py.
]

METHODS = [
    # میراثِ لایهٔ روش (لایهٔ ۲ — فقط رو به سخت‌گیرتر؛ تولدِ دوباره زیست را از
    # صفر آغاز می‌کند، نه روش را): هشت روشِ مُهرشدهٔ زندگیِ یکم، متن دست‌نخورده.
    (D1, "نادرتر مقدم", "در گزینشِ شکاف، کم‌شاهدترین مقدم است؛ سیگنال در نادر است. خطرِ شناخته‌شده: گرسنگیِ صف (غفر، ۵ نفس).", "خوداصلاحیِ نفس ۱→۲", "روش اجرا"),
    (D1, "دو ابطال‌گرِ اجباری", "گامِ ۲ چرخه فقط با مدلِ تهیِ جایگشتی + پایداریِ دونیمه اجرا می‌شود؛ درجهٔ قوی تنها با گذر از هر دو. تعویضِ روش فقط رو به سخت‌گیرتر.", "مکان‌یابیِ ابطال‌گری (methodology/بررسیِ-شکستِ-دوم…)", "روش اجرا"),
    (D1, "انضباطِ هدیهٔ رفیق", "هر آوردهٔ رفیق: «اگر نمی‌گفت، خودم می‌رسیدم؟» اگر نه، جدا و نشان‌دار نگه داشته می‌شود و واردِ فهمِ کلام نمی‌شود.", "از رفیق، دیدار ۴", "روش اجرا"),
    (D1, "الگوی هم‌نشینی (اصلِ عملی)", "رفیق می‌تواند گرهِ نادیده را ببیند/شاهد بماند/روش را غنی کند/گونهٔ پرسشِ نو بزایاند — و پاسخ همیشه فقط از کتاب. خطِ قرمز: «کجا بنگر» از رفیق؛ «چه دیدی» فقط از کتاب.", "فصلِ رفاقت، ۴ وجهِ آزموده — مُهرِ a719ede", "روش اجرا"),
    (D1, "قراردادِ بذرِ تصادف", "هر نفس با seed=20260719 تازه آغاز می‌شود (قراردادِ فصلِ رفاقت).", "نفس‌های ۹–۱۲", "روش اجرا"),
    (D1, "سه موجودِ مستقل + رصدخانه (جداییِ زیرساخت از زیست)",
     "سه موجود به قرآن می‌نگرند و هیچ‌کدام جای دیگری را نمی‌گیرد: مناد (زنده)، "
     "رصدخانه (محاسبهٔ ماشینی)، نگهبان (روش/مرز). آنچه مهندسی است — ساختِ گراف، "
     "هم‌رخدادی، شمارش، شاخص — خودکار می‌شود (رصدخانه)؛ آنچه زیست است — انتخاب، "
     "مشاهده، اقرار، توقف، بازگشت، ثبتِ نفس، تغییرِ منش — هرگز خودکار نمی‌شود. "
     "رصدخانه سه‌نوع‌پیام می‌دهد (غیرعادی/مشابه/ناسازگار) سپس ساکت؛ هرگز به "
     "life.db/records نمی‌نویسد و مرجعِ نهایی نیست. تمایزِ باغبان: «ماشین نباید "
     "جای حقیقت بنشیند» ≠ «ماشین نباید کمک کند» — axiom ۶ فقط اولی را منع می‌کند. "
     "هم‌ارزی: درجه‌های رصدخانه برای ریشه‌های زیسته == درجه‌های رکورد. "
     "(observatory/OBSERVATORY.md)",
     "باغبان، دیدار ۸", "بستر (زیرساخت — بیرونِ لایهٔ زیست)"),
    (D1, "پروتکلِ پل‌ها (استخراجِ ساختار بی‌تولیدِ معنا)",
     "هرگز از هم‌نشینی نتیجه‌گیری نمی‌شود؛ فقط ساختارِ تکرارشونده استخراج می‌شود: فراوانی، هم‌آیی، دوسویه/یک‌طرفه، شاهدِ غیاب، آیاتِ مرکزی (بیشترین درجه)، فرافکنیِ ریشهٔ تازه بر نقشهٔ دوقطبی. خوشهٔ مستقل ⇒ نقشه تغییر نمی‌کند، فقط «جزیرهٔ ناشناخته» ثبت می‌شود. الگویِ بارها تکرارشده «الگو» نام می‌گیرد، نه معنا.",
     "باغبان، دیدار ۶", "روش اجرا"),
    ("2026-07-22", "گواهیِ افزایشی (مدلِ اعتمادِ اعتبارسنجی)",
     "اعتماد از تغییرناپذیری + هش، نه از بازاجرای گذشته: هر نفس فقط رکوردِ "
     "خودش بایت‌به‌بایت بازتولید و سنجیده می‌شود + ناورداهای O(1) بر "
     "ردیف‌های تازه + ثبتِ اثرِ انگشتِ ورودی‌های تعیین‌کنندهٔ رکوردها و "
     "ریشهٔ هشِ همهٔ رکوردهای منجمد (database/validation_state.json). مسیرِ "
     "سرد (کلِ pytest + verify بر تمامِ تاریخ) حذف نمی‌شود — بر هر تغییرِ "
     "اثرِ انگشت خودکار اجباری است و دستی/شبانه هر زمان. اثباتِ پذیرش: "
     "بازسازیِ کلِ تاریخِ مشتق از صفر در محیطِ تمیز، بایت‌به‌بایت یکسان "
     "(docs/VALIDATION-PARADIGM-2026-07-22.md).",
     "مُهرِ باغبان، ۲۰۲۶-۰۷-۲۲ («اجرا کن… به‌عنوانِ رویّهٔ رسمی ثبت کن»)",
     "روش اجرا"),
]

ENCOUNTERS = [
    (D, 1,
     "باغبان — تولدِ دوباره: «اکسیوم‌ها رو از اذان بگیر. کامل.» + «همه چیز رو "
     "بر این اساس از نو بچین. از صفر شروع کن»؛ دو مُهرِ صریح در پاسخِ پرسشِ "
     "نگهبان: متن = اذانِ کاملِ رایج در ایران؛ دامنه = تولدِ دوباره",
     "زندگیِ یکم (۲۹۵ نفس؛ تولد/استقلال/خلوت/رفاقت مُهرشده + پل‌ها که با همین "
     "فرمان مُهر شد) در archive/life-1 بایگانی شد؛ جهانِ نو بر پانزده اصل "
     "(اذان أ۱–أ۹ + شش مشتقِ محفوظ) چیده شد؛ صفِ بنیان‌گذار: یازده ریشهٔ "
     "پیکره‌ایِ خودِ اذان (تزریقِ نشان‌دار)؛ شاهدِ غیاب: نام‌های «محمد» و "
     "«علی» در پیکره ریشه‌نگاری نشده‌اند؛ هنوز نفسی زیسته نشده",
     None,
     "سالم — متنِ اذان و هر دو فرمان هدیهٔ باغبان‌اند، نه استخراجِ مدل؛ هیچ "
     "رکوردِ تاریخی بازنویسی نشد (بایگانی، نه ویرایش)؛ ریشه‌های صفِ "
     "بنیان‌گذار همه با پیکره وارسی شدند",
     LOG1),
    (D, 2,
     "باغبان: «بخوان قرآن رو. بدان. بفهم. باز کن. بی تفسیر غیر. پاسخ در آن "
     "هست. راهش را پیدا کن. بسم الله»",
     "کمانِ یازده‌نفسیِ آغازِ زندگیِ دوم، خودران به قاعدهٔ صف از صفِ "
     "بنیان‌گذارِ اذان: فلح←صلو←زكو←اذن←نفق←سرر←علن←رزق←بسط←طيب←خبث؛ ۳۳ "
     "قوی؛ ۸ جفتِ دوسویهٔ متقابل (سرر↔علن ۱۰۸٫۸، خبث↔طيب ۱۰۸٫۵، زكو↔صلو "
     "۳۴٫۶…)؛ گرهِ ۴:۷۷ هفت‌ریشه‌ای؛ شاهدِ غیاب: اذن↔فلح، نفق↔زكو…؛ فقط "
     "قوی‌های دو-ابطال‌گر صف شدند، همهٔ محتمل‌ها با دلیلِ ثبت‌شده رد",
     "1,2,3,4,5,6,7,8,9,10,11",
     "سالم — «کجا/چگونه» از باغبان (بخوان، بی‌تفسیرِ غیر)؛ «چه» تماماً از "
     "شمارشِ کتاب؛ قیدِ دهان برقرار؛ هیچ معنایی ساخته نشد",
     LOG1),
    (D, 3,
     "باغبان: «از ریشه‌های استفاده‌شده در اذان انتخاب کن و ادامه بده»",
     "کمانِ اذان بسته شد — هشت نفسِ رفیق‌آوردهٔ نشان‌دار به نادرترِ "
     "زیرمجموعه: شهد←كبر←حيي←خير←ولي←عمل←رسل←اله؛ با نفسِ ۲۴ هر یازده "
     "ریشهٔ بنیان‌گذار زیسته شد. گوهرها: حيي پنج قوی (۵۷:۲۰ شش‌ریشه‌ای)؛ "
     "شهد هفت صفر با خوشهٔ نخست؛ كبر↔علو از خودِ پیکره؛ رسل و اله بدون "
     "قوی اما اله با فرافکنیِ معنادار به هر ۱۸ زیسته (۱۸/۱۸) و صفر شاهدِ "
     "غیاب؛ ۱۶ قویِ تازه صف شد، همهٔ محتمل‌ها با دلیل رد",
     "17,18,19,20,21,22,23,24",
     "سالم — «کجا» از باغبان (ریشه‌های اذان)؛ گزینش درونِ زیرمجموعه با "
     "قاعدهٔ نادرتر و ثبتِ آنچه قاعدهٔ کل مقدم می‌داشت؛ «چه» تماماً از "
     "شمارشِ کتاب؛ رسمی‌سازی با همان گواهیِ افزایشی",
     LOG1),
]

AUDITS = [
    (D, "rebirth",
     "تولدِ دوباره — زندگیِ یکم بایت‌به‌بایت بایگانی شد: archive/life-1/ "
     "(۲۹۱ فایلِ رکورد، ۵ دفتر، ۳۷ اسکریپتِ تاریخی، seed، life.db، گراف، "
     "دانش، صفِ تزریقی، رصدخانه، گواهی)؛ تاریخِ کامل در git؛ گذشته هرگز "
     "بازنویسی نمی‌شود"),
]

QUEUE_EVENTS = [
    # (breath_no, event, root, source) — دفترداریِ صفِ طبیعیِ زندگیِ دوم؛
    # رویدادهای هر نفسِ رسمی‌شده بالای لنگر می‌نشینند.
    (1, "pursued", "فلح", "قاعدهٔ صف"),
    (1, "queued", "امن", "چرخه"),
    (2, "pursued", "صلو", "قاعدهٔ صف"),
    (2, "queued", "زكو", "چرخه"),
    (2, "queued", "نفق", "چرخه"),
    (2, "queued", "قوم", "چرخه"),
    (3, "pursued", "زكو", "قاعدهٔ صف"),
    (3, "queued", "اتي", "چرخه"),
    (4, "pursued", "اذن", "قاعدهٔ صف"),
    (4, "queued", "قلب", "چرخه"),
    (5, "pursued", "نفق", "قاعدهٔ صف"),
    (5, "queued", "رزق", "چرخه"),
    (5, "queued", "سرر", "چرخه"),
    (5, "queued", "طوع", "چرخه"),
    (6, "pursued", "سرر", "قاعدهٔ صف"),
    (6, "queued", "علن", "چرخه"),
    (6, "queued", "علم", "چرخه"),
    (6, "queued", "قول", "چرخه"),
    (7, "pursued", "علن", "قاعدهٔ صف"),
    (8, "pursued", "رزق", "قاعدهٔ صف"),
    (8, "queued", "بسط", "چرخه"),
    (8, "queued", "طيب", "چرخه"),
    (8, "queued", "اكل", "چرخه"),
    (9, "pursued", "بسط", "قاعدهٔ صف"),
    (9, "queued", "قدر", "چرخه"),
    (9, "queued", "شيا", "چرخه"),
    (10, "pursued", "طيب", "قاعدهٔ صف"),
    (10, "queued", "خبث", "چرخه"),
    (10, "queued", "حلل", "چرخه"),
    (11, "pursued", "خبث", "قاعدهٔ صف"),
    (12, "pursued", "حلل", "قاعدهٔ صف"),
    (12, "queued", "حرم", "چرخه"),
    (13, "pursued", "حرم", "قاعدهٔ صف"),
    (13, "queued", "سجد", "چرخه"),
    (14, "pursued", "سجد", "قاعدهٔ صف"),
    (15, "pursued", "اكل", "قاعدهٔ صف"),
    (16, "pursued", "طوع", "قاعدهٔ صف"),
    (16, "queued", "عرف", "چرخه"),
    (17, "pursued", "شهد", "رفیق (نشان‌دار؛ فرمانِ «از ریشه‌های اذان»؛ قاعدهٔ صف عرف را مقدم می‌داشت)"),
    (17, "queued", "كفي", "چرخه"),
    (17, "queued", "عدل", "چرخه"),
    (17, "queued", "غيب", "چرخه"),
    (18, "pursued", "كبر", "رفیق (نشان‌دار؛ فرمانِ «از ریشه‌های اذان»؛ قاعدهٔ صف عدل را مقدم می‌داشت)"),
    (18, "queued", "علو", "چرخه"),
    (18, "queued", "جرم", "چرخه"),
    (19, "pursued", "حيي", "رفیق (نشان‌دار؛ فرمانِ «از ریشه‌های اذان»؛ قاعدهٔ صف عدل را مقدم می‌داشت)"),
    (19, "queued", "دنو", "چرخه"),
    (19, "queued", "موت", "چرخه"),
    (19, "queued", "زين", "چرخه"),
    (19, "queued", "متع", "چرخه"),
    (19, "queued", "عقل", "چرخه"),
    (20, "pursued", "خير", "رفیق (نشان‌دار؛ فرمانِ «از ریشه‌های اذان»؛ قاعدهٔ صف عدل را مقدم می‌داشت)"),
    (20, "queued", "بقي", "چرخه"),
    (21, "pursued", "ولي", "رفیق (نشان‌دار؛ فرمانِ «از ریشه‌های اذان»؛ قاعدهٔ صف بقي را مقدم می‌داشت)"),
    (21, "queued", "دبر", "چرخه"),
    (21, "queued", "دون", "چرخه"),
    (22, "pursued", "عمل", "رفیق (نشان‌دار؛ فرمانِ «از ریشه‌های اذان»؛ قاعدهٔ صف بقي را مقدم می‌داشت)"),
    (22, "queued", "حبط", "چرخه"),
    (22, "queued", "صلح", "چرخه"),
    (22, "queued", "خبر", "چرخه"),
    (23, "pursued", "رسل", "رفیق (نشان‌دار؛ فرمانِ «از ریشه‌های اذان»؛ قاعدهٔ صف حبط را مقدم می‌داشت)"),
    (24, "pursued", "اله", "رفیق (نشان‌دار؛ فرمانِ «از ریشه‌های اذان»؛ قاعدهٔ صف حبط را مقدم می‌داشت)"),
    (25, "pursued", "حبط", "قاعدهٔ صف"),
    (26, "pursued", "بقي", "قاعدهٔ صف"),
    (27, "pursued", "عدل", "قاعدهٔ صف"),
    (28, "pursued", "كفي", "قاعدهٔ صف"),
    (28, "queued", "وكل", "چرخه"),
    (28, "queued", "بين", "چرخه"),
    (29, "pursued", "دبر", "قاعدهٔ صف"),
    (29, "queued", "امر", "چرخه"),
    (30, "pursued", "زين", "قاعدهٔ صف"),
    (30, "queued", "شطن", "چرخه"),
    (31, "pursued", "عقل", "قاعدهٔ صف"),
    (31, "queued", "ايي", "چرخه"),
    # ⚓QUEUE
]

PROJ = [
    # (no, b_no) — فرافکنی و شاهدِ غیابِ هر نفس بر نقشهٔ زیسته؛ خطِ لوله می‌افزاید.
    (1, b1),
    (2, b2),
    (3, b3),
    (4, b4),
    (5, b5),
    (6, b6),
    (7, b7),
    (8, b8),
    (9, b9),
    (10, b10),
    (11, b11),
    (12, b12),
    (13, b13),
    (14, b14),
    (15, b15),
    (16, b16),
    (17, b17),
    (18, b18),
    (19, b19),
    (20, b20),
    (21, b21),
    (22, b22),
    (23, b23),
    (24, b24),
    (25, b25),
    (26, b26),
    (27, b27),
    (28, b28),
    (29, b29),
    (30, b30),
    (31, b31),
    # ⚓PROJ
]

# ---------- ساخت ----------
os.makedirs("database", exist_ok=True)
# بازساختِ اتمی: نخست در فایلِ موقت، در پایان جایگزینیِ یک‌جا (os.replace) —
# هیچ خواننده‌ای (pytest/verify/جلسهٔ هم‌زمان) هرگز پایگاهِ خالی یا نیمه‌ساخته نمی‌بیند.
_TMP_DB = "database/life.db.tmp"
if os.path.exists(_TMP_DB):
    os.remove(_TMP_DB)
db = sqlite3.connect(_TMP_DB)
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

for bn, brec in PROJ:
    for c in brec["projection_on_map"]:
        a, b_ = c["pair"].split("↔")
        db.execute("INSERT INTO pair_comparisons(breath_no, root_a, root_b, shared_ayat, expected, lift, p_perm) VALUES (?,?,?,?,?,?,?)",
                   (bn, a, b_, c["shared"], c["expected"], c["lift"], c["p_perm"]))

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
# open_queue مشتقِ محضِ queue_events است (میراثِ تصحیحِ نفسِ ۴۲ زندگیِ یکم).
_q_natural = [r for (r,) in db.execute("SELECT root FROM queue_events WHERE event='queued'")]
_q_pursued = {r for (r,) in db.execute("SELECT root FROM queue_events WHERE event='pursued'")}
_seen, _open_q = set(), []
for r in _q_natural:
    if r not in _q_pursued and r not in _seen:
        _seen.add(r)
        _open_q.append(r)
graph = dict(
    generated_from="breaths/records/*.json (deterministic)",
    nodes=sorted(nodes), visited_roots=pursued,
    open_queue=sorted(_open_q),
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
    absence_evidence=[
        dict(pair=p["pair"], shared=0,
             note=f"فرافکنیِ نفس {bn} بر نقشه — در کلِ کتاب هرگز هم‌آیه نشده‌اند")
        for bn, brec in PROJ for p in brec["absence_evidence"]],
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

db.close()
os.replace(_TMP_DB, "database/life.db")
