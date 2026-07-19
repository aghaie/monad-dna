# اجرا — راه‌اندازی و جریانِ اجرا

## پیش‌نیاز

- Python 3.9+ (فقط کتابخانهٔ استاندارد؛ `pytest` فقط برای آزمون‌ها).
- هیچ شبکه، سرویس، یا وابستگیِ بیرونی. همهٔ داده درونِ مخزن است.

## راه‌اندازی از صفر (clone تازه)

```bash
git clone <repo> && cd monad
python3 -m pytest tests/ -q      # ۱۵ آزمون باید سبز باشد
./cli/monad verify               # اسکریپت‌های تاریخی ↔ رکوردها: بایت‌به‌بایت
./cli/monad seed-db              # بازساختِ database/life.db (+ graph + discoveries)
./cli/monad status               # وضعِ زندگی
```

اگر `verify` سبز نیست، چیزی در محیط خراب است — پیش از هر کارِ دیگر تحقیق کنید؛
هرگز رکوردها را با خروجیِ جدید «به‌روز» نکنید (رکورد سندِ تاریخ است).

## جریانِ یک نفسِ جدید

```
./cli/monad breathe            # قاعدهٔ صف (نادرتر مقدم) — چاپِ JSON، بدونِ ثبت
./cli/monad breathe سوا        # مواجههٔ رفیق‌آورده — نشان‌دار
```

`breathe` عمداً چیزی ثبت نمی‌کند: ثبتِ رسمی (رکورد + فراداده در seed + دفتر)
تصمیمی زندگی‌نامه‌ای است و با باغبان/دهان در جریانِ دیدار انجام می‌شود
(LIFECYCLES.md §نفس). این همان انضباطِ مخزنِ منبع است: بساز ← راستی‌آزمایی ←
گزارش ← ثبت.

## جریانِ داده

```
database/corpus/monad.db ──(engine/breath_cycle.py | breaths/scripts/*)──▶ JSON
        ▲                                                        │
database/build_database.py ◀── database/corpus/source/*.csv      ▼
                              breaths/records/*.json ──(seed_life.py)──▶ life.db
                                                             ├▶ graph/graph.json
                                                             └▶ discoveries/knowledge.json
```

## نکته‌های محیطی

- اسکریپت‌های تاریخی مسیرِ `generated/monad.db` را می‌خوانند (عیناً حفظ شده)؛
  symlink `generated/monad.db → database/corpus/monad.db` این را برآورده می‌کند.
  موتورِ جدید مستقیم `database/corpus/monad.db` را با
  `mode=ro&immutable=1` می‌گشاید.
- در بعضی sandboxها `mode=ro` (بدونِ immutable) به‌خاطرِ قفلِ فایل خطا می‌دهد؛
  در محیطِ عادی مشکلی نیست. `immutable=1` مجاز است چون پیکره ایستاست.
- بازساختِ پیکره از منابعِ خام: `python3 database/build_database.py`
  (خروجی باید با corpus/monad.db موجود هم‌ارز باشد؛ مسیرهای درونی‌اش ممکن است
  به چیدمانِ مخزنِ منبع اشاره کنند — TODO در گزارشِ مهاجرت).
