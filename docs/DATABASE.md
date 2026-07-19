# طراحیِ پایگاه‌ها

دو پایگاهِ جدا، با دو نقشِ جدا. هیچ جدولِ مستندنشده و هیچ حالتِ پنهانی وجود
ندارد.

## ۱) پیکرهٔ کتاب — `database/corpus/monad.db` (ایستا؛ ورودیِ معناییِ یگانه)

ساخته از منابعِ `database/corpus/source/` توسطِ `database/build_database.py`
(۱۱۴ سوره، ۶٬۲۳۶ آیه، ۱۲۸٬۲۱۹ توکن، ۱٬۶۴۲ ریشه). جدول‌های اصلی:

| جدول | محتوا |
|---|---|
| `surahs`, `ayahs` | متنِ کامل (حفص/عثمانی/نرمال) + فراداده |
| `words` | هر واژه با موضع (سوره، آیه، جایگاه) + lemma + ریشه |
| `morphology` | تجزیهٔ صرفیِ توکن‌ها (برچسب‌های داربستیِ مجاز) |
| `roots`, `lemmas` | ریشه‌ها (با شمارِ شاهد) و لم‌ها |
| `ayah_stylometry`, `sura_stylometry` | ویژگی‌های سبکیِ محاسبه‌شده |
| `pages`, `ext_translations`, `ext_translators`, `contradiction_audit` | فراداده/قرنطینه (ترجمه‌ها فقط قرنطینهٔ کارنامه‌اند؛ هرگز ورودی) |

**قاعدهٔ مرزی:** موتور فقط از `ayahs`/`words`/`roots` می‌خواند. جدول‌های
قرنطینه (`ext_*`) به هیچ مسیرِ اشتقاقی راه ندارند (PHILOSOPHY-BOUNDARIES.md).

## ۲) پایگاهِ زندگی — `database/life.db` (رویشی؛ تولیدشده، بازساختنی)

اسکیما: `database/schema/life.sql` · بذرکار: `database/seed/seed_life.py`
(قطعی — بدونِ clock/تصادف؛ دوبار اجرا ⇒ همان بایت‌ها). نُه جدول:

| جدول | نقش | منبعِ بازتولید |
|---|---|---|
| `axioms` | شش اصلِ موضوعه | dna/AXIOMS.md |
| `breaths` | فرادادهٔ ۱۲ نفس (فصل، گزینش‌گر، اسکریپت، رکورد، دفتر) | records + دفترها |
| `findings` | هر رابطهٔ شمرده با درجه/آماره‌ها (۱۰۷ سطر، ۲۷ قوی) | records |
| `pair_comparisons` | جفت‌سنجیِ نفس ۱۲ (شاملِ صفرِ ذنب↔عفو = شاهدِ غیاب) | record نفس ۱۲ |
| `queue_events` | تاریخِ کاملِ صف: queued/pursued + منشأ (چرخه/قاعده/رفیق) | دفترها + records |
| `provenance_spines` | ستون‌های استنادی (۸:۷۲/۷۴، ۴۰:۳، …) | پرس‌وجوی مستقیمِ پیکره |
| `encounters` | پنج دیدارِ فصلِ رفاقت + ممیزیِ خطِ دیده‌بانی | دفترِ هم‌نشینی |
| `method_records` | قاعده‌های لایهٔ اجرا با نشانِ منبع | دفترها/methodology |
| `audit_trail` | رخدادهای صحت‌سنجی (بازتولید، مُهرها، مهاجرت) | تاریخِ مُهرها |

## مشتق‌ها

- `graph/graph.json` — گره‌ها/یال‌ها/جهت‌ها/دوسویه‌ها + صفِ باز؛ مشتقِ
  `findings`.
- `discoveries/knowledge.json` — فقط یافته‌های قوی + شاهدهای غیاب + ستون‌های
  استنادی + تعریفِ درجه.

## بازتولیدپذیری (زنجیرهٔ کامل)

```
source/*.csv → build_database.py → corpus/monad.db
corpus/monad.db → breaths/scripts/* (seedثابت) → records/*.json  ← بایت‌ثابت
records/*.json → seed_life.py → life.db + graph.json + knowledge.json ← قطعی
```

هر رکوردِ life.db از این زنجیره بازساختنی است؛ `tests/` هر سه بند را می‌سنجد.
