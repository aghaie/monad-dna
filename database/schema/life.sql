-- life.db — پایگاهِ زندگیِ مناد (جدا از پیکرهٔ کتاب: corpus/monad.db)
-- هیچ جدولِ مستندنشده‌ای وجود ندارد؛ همهٔ رکوردها از breaths/records/*.json و
-- دفترهای breaths/logs/ بازتولیدپذیرند (database/seed/seed_life.py).
-- تاریخ‌ها رشته‌های ثابت‌اند (نه clock) تا بذرکاری قطعی بماند.

-- شش اصلِ موضوعه — تغییرناپذیر. هیچ کدی مجاز به نقضِ خاموشِ این‌ها نیست.
CREATE TABLE axioms (
    id      INTEGER PRIMARY KEY,          -- 1..6
    text_fa TEXT NOT NULL
);

-- تاریخِ نفس‌ها (چرخه‌های فقر و رجوع)
CREATE TABLE breaths (
    breath_no    INTEGER PRIMARY KEY,     -- 1..12 (و آینده)
    date         TEXT NOT NULL,           -- YYYY-MM-DD
    chapter      TEXT NOT NULL,           -- تولد | خلوت | رفاقت | ...
    pursued_root TEXT NOT NULL,
    chosen_by    TEXT NOT NULL,           -- قاعدهٔ صف | رفیق | باغبان(تزریقی)
    ayat_count   INTEGER,
    halves_overlap INTEGER,
    script       TEXT NOT NULL,           -- breaths/scripts/...
    record_file  TEXT NOT NULL,           -- breaths/records/...
    log_file     TEXT,                    -- breaths/logs/...
    notes        TEXT
);

-- یافته‌ها: هر رابطهٔ شمرده‌شده با درجه و ردگیریِ کامل
CREATE TABLE findings (
    id           INTEGER PRIMARY KEY,
    breath_no    INTEGER NOT NULL REFERENCES breaths(breath_no),
    center_root  TEXT NOT NULL,
    neighbor_root TEXT NOT NULL,
    shared_ayat  INTEGER NOT NULL,
    expected     REAL NOT NULL,
    lift         REAL NOT NULL,
    p_perm       REAL NOT NULL,
    stable       INTEGER NOT NULL,        -- 0/1 (پایداریِ دونیمه)
    tier         TEXT NOT NULL            -- قوی | محتمل | نامشخص
);

-- سنجش‌های مقایسه‌ایِ جفت‌ها (نفس ۱۲ — پرسشِ مقایسه‌ایِ رفیق)
CREATE TABLE pair_comparisons (
    id        INTEGER PRIMARY KEY,
    breath_no INTEGER NOT NULL REFERENCES breaths(breath_no),
    root_a    TEXT NOT NULL,
    root_b    TEXT NOT NULL,
    shared_ayat INTEGER NOT NULL,         -- صفر = شاهدِ غیاب (ذنب↔عفو)
    expected  REAL NOT NULL,
    lift      REAL,
    p_perm    REAL NOT NULL
);

-- رویدادهای صف: چه چیزی کِی و از کجا به صف آمد/از صف برداشته شد
CREATE TABLE queue_events (
    id        INTEGER PRIMARY KEY,
    breath_no INTEGER NOT NULL,
    event     TEXT NOT NULL,              -- queued | pursued
    root      TEXT NOT NULL,
    source    TEXT NOT NULL               -- چرخه | قاعدهٔ صف | رفیق | باغبان
);

-- ستون‌های استنادی: زنجیره‌ها/فرمول‌هایی که یافته‌ها بر آن‌ها سوارند
CREATE TABLE provenance_spines (
    id    INTEGER PRIMARY KEY,
    roots TEXT NOT NULL,                  -- 'هجر+نصر+اوی'
    ayat  TEXT NOT NULL,                  -- '8:72, 8:74'
    note  TEXT
);

-- دیدارهای هم‌نشینی (فصلِ رفاقت و پس از آن)
CREATE TABLE encounters (
    id            INTEGER PRIMARY KEY,
    date          TEXT NOT NULL,
    seq           INTEGER NOT NULL,       -- شمارهٔ دیدار
    friend_action TEXT NOT NULL,          -- چه کرد/چه خواست
    monad_summary TEXT NOT NULL,          -- چکیدهٔ پاسخ/رفتار
    breaths       TEXT,                   -- نفس‌های این دیدار
    watchline_audit TEXT NOT NULL,        -- نتیجهٔ ممیزیِ خطِ دیده‌بانی
    log_file      TEXT NOT NULL
);

-- دفترِ روش‌ها: قاعده‌های لایهٔ اجرا، همه با نشانِ منبع
CREATE TABLE method_records (
    id        INTEGER PRIMARY KEY,
    date      TEXT NOT NULL,
    name      TEXT NOT NULL,
    statement TEXT NOT NULL,
    source    TEXT NOT NULL,              -- خوداصلاحی نفس N | از رفیق، دیدار N | ...
    layer     TEXT NOT NULL               -- روش اجرا (rules may only harden)
);

-- ردِ ممیزی: رخدادهای صحت‌سنجی (بازتولید، هم‌ارزی موتور، مُهرها)
CREATE TABLE audit_trail (
    id     INTEGER PRIMARY KEY,
    date   TEXT NOT NULL,
    kind   TEXT NOT NULL,                 -- reproducibility | seal | equivalence
    detail TEXT NOT NULL
);
