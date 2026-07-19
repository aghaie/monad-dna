#!/usr/bin/env python3
"""
scripts/build_database.py

Monad Canonical Quran Database Builder.
Reads corpus/quran/ source files and writes generated/monad.db.

Usage:
    python scripts/build_database.py [--db PATH] [--force]

Inputs (in source-priority order):
    corpus/quran/source/qurantexttanzil.csv           Primary text (hafs)
    corpus/quran/source/quranuthmanitanzil.csv         Uthmani text
    corpus/quran/source/quran.csv                     Diacritics, normalized, hash
    corpus/quran/metadata/fahras.csv                  Surah metadata
    corpus/quran/metadata/pages.csv                   Mushaf page layout
    corpus/quran/morphology/quranic-corpus-morphology-0.4.txt  Token morphology

Outputs:
    generated/monad.db                               SQLite database
"""

import argparse
import csv
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS = REPO_ROOT / "corpus" / "quran"
GENERATED = REPO_ROOT / "generated"

SOURCE = {
    "tanzil":    CORPUS / "source"   / "qurantexttanzil.csv",
    "uthmani":   CORPUS / "source"   / "quranuthmanitanzil.csv",
    "quran":     CORPUS / "source"   / "quran.csv",
    "fahras":    CORPUS / "metadata" / "fahras.csv",
    "pages":     CORPUS / "metadata" / "pages.csv",
    "morphology":CORPUS / "morphology"/ "quranic-corpus-morphology-0.4.txt",
}

# ── Expected values (for validation) ──────────────────────────────────────────

EXPECTED_SURAHS  = 114
EXPECTED_AYAHS   = 6236
EXPECTED_TOKENS  = 128219   # morphology corpus v0.4
FAHRAS_ID_OFFSET = 226      # fahras col[0] - 226 = surah_number

# ── Buckwalter → Arabic ───────────────────────────────────────────────────────

_BW = {
    "'": 'ء', '|': 'آ', '>': 'أ', '&': 'ؤ',
    '<': 'إ', '}': 'ئ', 'A': 'ا', 'b': 'ب',
    'p': 'ة', 't': 'ت', 'v': 'ث', 'j': 'ج',
    'H': 'ح', 'x': 'خ', 'd': 'د', '*': 'ذ',
    'r': 'ر', 'z': 'ز', 's': 'س', '$': 'ش',
    'S': 'ص', 'D': 'ض', 'T': 'ط', 'Z': 'ظ',
    'E': 'ع', 'g': 'غ', 'f': 'ف', 'q': 'ق',
    'k': 'ك', 'l': 'ل', 'm': 'م', 'n': 'ن',
    'h': 'ه', 'w': 'و', 'Y': 'ى', 'y': 'ي',
    'F': 'ً', 'N': 'ٌ', 'K': 'ٍ', 'a': 'َ',
    'u': 'ُ', 'i': 'ِ', '~': 'ّ', 'o': 'ْ',
    '`': 'ٰ', '{': 'ٱ',
}
_DIACRITICS = set('ًٌٍَُِّْ'
                  'ٰٕٖٓٔٗ٘')


def bw_to_arabic(s: str) -> str:
    return ''.join(_BW.get(c, c) for c in s)


def strip_diacritics(text: str) -> str:
    return ''.join(c for c in text if c not in _DIACRITICS)


def normalize_name(text: str) -> str:
    """Remove diacritics and normalize alef variants for name matching."""
    t = strip_diacritics(text.strip())
    for variant in 'آأإٱ':   # آ أ إ ٱ → ا
        t = t.replace(variant, 'ا')
    return t


# ── Feature parser ────────────────────────────────────────────────────────────

def parse_features(raw: str) -> dict:
    """Parse morphology FEATURES field into a structured dict."""
    parts = raw.strip().split('|')
    r = {k: None for k in ('segment_type', 'pos', 'lemma_bw', 'root_bw',
                            'gender', 'number_feature', 'case_feature', 'state',
                            'aspect', 'voice', 'mood', 'person')}
    if parts and parts[0] in ('STEM', 'PREFIX', 'SUFFIX'):
        r['segment_type'] = parts[0]
        parts = parts[1:]
    for p in parts:
        if not p:
            continue
        if   p.startswith('POS:'):  r['pos']            = p[4:]
        elif p.startswith('LEM:'):  r['lemma_bw']       = p[4:]
        elif p.startswith('ROOT:'): r['root_bw']        = p[5:]
        elif p in ('M', 'F'):       r['gender']         = p
        elif p in ('S', 'D', 'P'):  r['number_feature'] = p
        elif p in ('NOM','ACC','GEN'): r['case_feature']= p
        elif p in ('DEF','INDEF','NA'): r['state']      = p
        elif p in ('PERF','IMPF','IMPV'): r['aspect']   = p
        elif p in ('ACT','PASS'):   r['voice']          = p
        elif p in ('IND','JUSS','SUBJ'): r['mood']      = p
        elif p in ('1','2','3'):    r['person']         = p
    return r


# ── Schema ────────────────────────────────────────────────────────────────────

SCHEMA = """
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS surahs (
    surah_number            INTEGER PRIMARY KEY,      -- 1..114
    name_arabic             TEXT    NOT NULL,          -- normalized, no diacritics
    name_arabic_diacritics  TEXT,                     -- full diacritics form
    ayah_count              INTEGER NOT NULL,
    revelation_type         TEXT,                     -- 'meccan' | 'medinan'
    start_page              INTEGER,                  -- mushaf page where surah begins
    source_id_fahras        INTEGER                   -- raw col[0] from fahras.csv
);

CREATE TABLE IF NOT EXISTS ayahs (
    surah_number    INTEGER NOT NULL REFERENCES surahs(surah_number),
    ayah_number     INTEGER NOT NULL,
    text_hafs       TEXT    NOT NULL,   -- qurantexttanzil.csv (authoritative)
    text_uthmani    TEXT,               -- quranuthmanitanzil.csv
    text_diacritics TEXT,               -- quran.csv col[2]
    text_normalized TEXT,               -- quran.csv col[3]
    text_hash       TEXT,               -- SHA-256 from quran.csv
    ayah_sequential INTEGER,            -- global sequence 1..6236
    PRIMARY KEY (surah_number, ayah_number)
);

CREATE TABLE IF NOT EXISTS roots (
    root_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    root_buckwalter TEXT    NOT NULL UNIQUE,
    root_arabic     TEXT    NOT NULL,
    token_count     INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS lemmas (
    lemma_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    lemma_buckwalter TEXT   NOT NULL UNIQUE,
    lemma_arabic    TEXT    NOT NULL,
    root_id         INTEGER REFERENCES roots(root_id)
);

CREATE TABLE IF NOT EXISTS words (
    word_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    surah_number    INTEGER NOT NULL,
    ayah_number     INTEGER NOT NULL,
    word_position   INTEGER NOT NULL,   -- 1-based within ayah
    form_buckwalter TEXT    NOT NULL,   -- STEM token FORM field
    form_arabic     TEXT    NOT NULL,
    lemma_id        INTEGER REFERENCES lemmas(lemma_id),
    root_id         INTEGER REFERENCES roots(root_id),
    FOREIGN KEY (surah_number, ayah_number) REFERENCES ayahs(surah_number, ayah_number),
    UNIQUE (surah_number, ayah_number, word_position)
);

CREATE TABLE IF NOT EXISTS morphology (
    token_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    surah_number    INTEGER NOT NULL,
    ayah_number     INTEGER NOT NULL,
    word_position   INTEGER NOT NULL,
    token_position  INTEGER NOT NULL,   -- 1-based within word
    form_buckwalter TEXT    NOT NULL,
    tag             TEXT    NOT NULL,   -- grammatical tag (N, V, P, PN, ...)
    features_raw    TEXT    NOT NULL,   -- full raw feature string
    segment_type    TEXT,               -- STEM | PREFIX | SUFFIX
    pos             TEXT,               -- part of speech
    lemma_id        INTEGER REFERENCES lemmas(lemma_id),
    root_id         INTEGER REFERENCES roots(root_id),
    gender          TEXT,               -- M | F
    number_feature  TEXT,               -- S | D | P
    case_feature    TEXT,               -- NOM | ACC | GEN
    state           TEXT,               -- DEF | INDEF | NA
    aspect          TEXT,               -- PERF | IMPF | IMPV
    voice           TEXT,               -- ACT | PASS
    mood            TEXT,               -- IND | JUSS | SUBJ
    person          TEXT,               -- 1 | 2 | 3
    FOREIGN KEY (surah_number, ayah_number) REFERENCES ayahs(surah_number, ayah_number)
);

CREATE TABLE IF NOT EXISTS pages (
    page_number         INTEGER PRIMARY KEY,   -- 1..604
    ayah_count_on_page  INTEGER NOT NULL       -- ayahs completing on this page
);

-- Indexes for common joins
CREATE INDEX IF NOT EXISTS idx_ayahs_surah          ON ayahs(surah_number);
CREATE INDEX IF NOT EXISTS idx_words_position        ON words(surah_number, ayah_number, word_position);
CREATE INDEX IF NOT EXISTS idx_words_lemma           ON words(lemma_id);
CREATE INDEX IF NOT EXISTS idx_words_root            ON words(root_id);
CREATE INDEX IF NOT EXISTS idx_morphology_position   ON morphology(surah_number, ayah_number, word_position, token_position);
CREATE INDEX IF NOT EXISTS idx_morphology_lemma      ON morphology(lemma_id);
CREATE INDEX IF NOT EXISTS idx_morphology_root       ON morphology(root_id);
CREATE INDEX IF NOT EXISTS idx_lemmas_root           ON lemmas(root_id);
"""


# ── Import report ─────────────────────────────────────────────────────────────

class Report:
    def __init__(self):
        self.tables   = {}   # table → {imported, skipped, conflicts, notes}
        self.skipped  = []   # (filename, reason)
        self.assumptions = []
        self.warnings    = []
        self.validation  = []

    def table(self, name, imported=0, skipped=0, conflicts=0, notes=None):
        self.tables[name] = {
            'imported': imported, 'skipped': skipped,
            'conflicts': conflicts, 'notes': notes or []
        }

    def skip(self, f, reason):
        self.skipped.append((f, reason))

    def assume(self, text):
        self.assumptions.append(text)

    def warn(self, text):
        self.warnings.append(text)
        print(f"  [WARN] {text}")

    def validate(self, check, passed, detail=''):
        self.validation.append({'check': check, 'passed': passed, 'detail': detail})
        status = 'PASS' if passed else 'FAIL'
        print(f"  [{status}] {check}" + (f" — {detail}" if detail else ''))


# ── Builder ───────────────────────────────────────────────────────────────────

class Builder:
    def __init__(self, db_path: Path, force: bool = False):
        if db_path.exists():
            if force:
                db_path.unlink()
            else:
                print(f"Database already exists: {db_path}")
                print("Use --force to overwrite.")
                sys.exit(1)
        self.db_path = db_path
        self.con = sqlite3.connect(db_path)
        self.con.row_factory = sqlite3.Row
        self.report = Report()

        # In-memory caches keyed by buckwalter string → row_id
        self._roots:  dict[str, int] = {}
        self._lemmas: dict[str, int] = {}

    def _exec(self, sql: str):
        for stmt in sql.split(';'):
            s = stmt.strip()
            if s:
                self.con.execute(s)

    # ── Schema ────────────────────────────────────────────────────────────────

    def create_schema(self):
        print("Creating schema...")
        self._exec(SCHEMA)
        self.con.commit()

    # ── Surahs ────────────────────────────────────────────────────────────────

    def import_surahs(self):
        print("Importing surahs...")

        # Step 1: canonical surah names from quran.csv header rows (aya_index=0)
        # Take first occurrence of each surah_number to avoid duplicates.
        name_diacritics: dict[int, str] = {}
        name_normalized: dict[int, str] = {}
        with open(SOURCE["quran"], encoding='utf-8') as f:
            for row in csv.reader(f):
                sn = int(row[0])
                if row[1] == '0' and sn not in name_diacritics:
                    # Strip "سورة " (with/without diacritics) prefix
                    d = row[9].strip()
                    n = row[10].strip()
                    for prefix in ('سُورَةُ ', 'سورة '):
                        if d.startswith(prefix): d = d[len(prefix):]
                        if n.startswith(prefix): n = n[len(prefix):]
                    name_diacritics[sn] = d
                    name_normalized[sn] = n

        self.report.assume(
            "Surah names sourced from quran.csv sura-header rows (aya_index=0), "
            "first occurrence per surah_number taken (224 header rows → 114 unique)."
        )

        # Step 2: ayah counts from qurantexttanzil.csv (authoritative)
        ayah_counts: dict[int, int] = defaultdict(int)
        with open(SOURCE["tanzil"], encoding='utf-8') as f:
            for row in csv.reader(f):
                ayah_counts[int(row[0])] += 1

        # Step 3: metadata from fahras.csv
        # surah_number = col[0] - FAHRAS_ID_OFFSET  (verified: correct for 113/114 surahs;
        # surah 9 has a 1-ayah counting variant — tanzil count is authoritative)
        fahras_meta: dict[int, dict] = {}
        with open(SOURCE["fahras"], encoding='utf-8') as f:
            for row in csv.reader(f):
                sn = int(row[0]) - FAHRAS_ID_OFFSET
                rev_raw = row[4].strip()
                if 'مكي' in rev_raw:
                    rev = 'meccan'
                elif 'مدني' in rev_raw:
                    rev = 'medinan'
                else:
                    rev = None
                fahras_meta[sn] = {
                    'start_page':   int(row[2]),
                    'revelation':   rev,
                    'source_id':    int(row[0]),
                    'fahras_ayahs': int(row[3]),
                }

        self.report.assume(
            "fahras.csv surah_number derived as col[0] - 226 "
            "(col[0] range 227–340 maps exactly to surahs 1–114). "
            "Surah 9 ayah count in fahras (128) differs from tanzil (129); "
            "tanzil is used as authoritative count."
        )

        # Step 4: Insert
        rows = []
        conflicts = 0
        for sn in range(1, EXPECTED_SURAHS + 1):
            meta = fahras_meta.get(sn, {})
            ac   = ayah_counts.get(sn, 0)
            fa   = meta.get('fahras_ayahs')
            if fa is not None and fa != ac:
                self.report.warn(
                    f"Surah {sn} ayah count conflict: fahras={fa}, tanzil={ac}. "
                    "Using tanzil."
                )
                conflicts += 1
            rows.append((
                sn,
                name_normalized.get(sn),
                name_diacritics.get(sn),
                ac,
                meta.get('revelation'),
                meta.get('start_page'),
                meta.get('source_id'),
            ))

        self.con.executemany(
            "INSERT INTO surahs VALUES (?,?,?,?,?,?,?)", rows
        )
        self.con.commit()
        self.report.table('surahs', imported=len(rows), conflicts=conflicts,
                          notes=["1 ayah-count conflict (surah 9); tanzil used"])

    # ── Ayahs ─────────────────────────────────────────────────────────────────

    def import_ayahs(self):
        print("Importing ayahs...")

        # Primary: qurantexttanzil.csv → text_hafs, ayah_sequential
        hafs: dict[tuple, tuple] = {}
        with open(SOURCE["tanzil"], encoding='utf-8') as f:
            for row in csv.reader(f):
                sn, an = int(row[0]), int(row[1])
                hafs[(sn, an)] = (row[2], int(row[3]) if row[3].strip() else None)

        # Secondary: quranuthmanitanzil.csv → text_uthmani
        uthmani: dict[tuple, str] = {}
        with open(SOURCE["uthmani"], encoding='utf-8') as f:
            for row in csv.reader(f):
                uthmani[(int(row[0]), int(row[1]))] = row[2]

        # Tertiary: quran.csv → text_diacritics, text_normalized, text_hash
        # filter to aya_index >= 1 (canonical ayah rows)
        quran_extra: dict[tuple, tuple] = {}
        with open(SOURCE["quran"], encoding='utf-8') as f:
            for row in csv.reader(f):
                if row[1] == '0':
                    continue
                sn, an = int(row[0]), int(row[1])
                if (sn, an) not in quran_extra:
                    quran_extra[(sn, an)] = (row[2], row[3], row[4])

        rows     = []
        skipped  = 0
        conflicts = 0
        for (sn, an), (text_h, seq) in sorted(hafs.items()):
            text_u  = uthmani.get((sn, an))
            extra   = quran_extra.get((sn, an), (None, None, None))
            rows.append((sn, an, text_h, text_u, extra[0], extra[1], extra[2], seq))

        self.con.executemany(
            "INSERT INTO ayahs VALUES (?,?,?,?,?,?,?,?)", rows
        )
        self.con.commit()

        miss_uthmani = sum(1 for r in rows if r[3] is None)
        miss_extra   = sum(1 for r in rows if r[4] is None)
        notes = []
        if miss_uthmani:
            notes.append(f"{miss_uthmani} ayahs missing uthmani text")
        if miss_extra:
            notes.append(f"{miss_extra} ayahs missing diacritics/normalized/hash from quran.csv")
        self.report.table('ayahs', imported=len(rows), skipped=skipped,
                          conflicts=conflicts, notes=notes)
        self.report.assume(
            "qurantexttanzil.csv is the authoritative text source. "
            "quranuthmanitanzil.csv and quran.csv are merged by (surah_number, ayah_number). "
            "quran.csv rows with aya_index=0 (sura headers) are excluded. "
            "First matching row taken when quran.csv has duplicates for same key."
        )

    # ── Roots / Lemmas / Words / Morphology ───────────────────────────────────

    def _get_or_create_root(self, root_bw: str) -> int:
        if root_bw in self._roots:
            return self._roots[root_bw]
        root_ar = bw_to_arabic(root_bw)
        cur = self.con.execute(
            "INSERT OR IGNORE INTO roots(root_buckwalter, root_arabic) VALUES (?,?)",
            (root_bw, root_ar)
        )
        if cur.lastrowid == 0:
            cur = self.con.execute(
                "SELECT root_id FROM roots WHERE root_buckwalter=?", (root_bw,)
            )
            rid = cur.fetchone()[0]
        else:
            rid = cur.lastrowid
        self._roots[root_bw] = rid
        return rid

    def _get_or_create_lemma(self, lemma_bw: str, root_id=None) -> int:
        if lemma_bw in self._lemmas:
            return self._lemmas[lemma_bw]
        lemma_ar = bw_to_arabic(lemma_bw)
        cur = self.con.execute(
            "INSERT OR IGNORE INTO lemmas(lemma_buckwalter, lemma_arabic, root_id) VALUES (?,?,?)",
            (lemma_bw, lemma_ar, root_id)
        )
        if cur.lastrowid == 0:
            cur = self.con.execute(
                "SELECT lemma_id FROM lemmas WHERE lemma_buckwalter=?", (lemma_bw,)
            )
            lid = cur.fetchone()[0]
        else:
            lid = cur.lastrowid
        self._lemmas[lemma_bw] = lid
        return lid

    def import_morphology(self):
        print("Importing morphology, roots, lemmas, words...")

        # Parse entire morphology corpus into memory first for efficiency
        # Structure: words[(s,a,w)] = {stem_form, stem_lemma, stem_root, tokens=[]}
        words_map: dict[tuple, dict] = {}
        token_rows  = []   # for bulk insert
        parse_errors = 0
        loc_re = re.compile(r'\((\d+):(\d+):(\d+):(\d+)\)')

        with open(SOURCE["morphology"], encoding='utf-8') as f:
            for line in f:
                line = line.rstrip('\n')
                # Skip comment and header lines
                if line.startswith('#') or not line.strip():
                    continue
                if line.startswith('LOCATION'):
                    continue

                parts = line.split('\t')
                if len(parts) < 4:
                    parse_errors += 1
                    continue

                loc_str, form_bw, tag, feat_raw = parts[0], parts[1], parts[2], parts[3]
                m = loc_re.match(loc_str)
                if not m:
                    parse_errors += 1
                    continue
                s, a, w, t = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))

                feat = parse_features(feat_raw)
                root_bw  = feat['root_bw']
                lemma_bw = feat['lemma_bw']

                token_rows.append({
                    'loc': (s, a, w, t),
                    'form_bw': form_bw,
                    'tag': tag,
                    'feat_raw': feat_raw,
                    'feat': feat,
                    'root_bw': root_bw,
                    'lemma_bw': lemma_bw,
                })

                wkey = (s, a, w)
                if wkey not in words_map:
                    words_map[wkey] = {
                        'stem_form': None, 'stem_lemma': None, 'stem_root': None
                    }
                if feat['segment_type'] == 'STEM':
                    words_map[wkey]['stem_form']  = form_bw
                    words_map[wkey]['stem_lemma'] = lemma_bw
                    words_map[wkey]['stem_root']  = root_bw

        # ── Insert roots and lemmas (batch) ──────────────────────────────────

        print("  Inserting roots...")
        all_roots = set()
        for tok in token_rows:
            if tok['root_bw']:
                all_roots.add(tok['root_bw'])
        self.con.executemany(
            "INSERT OR IGNORE INTO roots(root_buckwalter, root_arabic) VALUES (?,?)",
            [(r, bw_to_arabic(r)) for r in sorted(all_roots)]
        )
        self.con.commit()

        # Build root cache
        for row in self.con.execute("SELECT root_id, root_buckwalter FROM roots"):
            self._roots[row['root_buckwalter']] = row['root_id']

        print("  Inserting lemmas...")
        # Collect unique (lemma_bw, root_bw) pairs
        lemma_root: dict[str, str | None] = {}
        for tok in token_rows:
            if tok['lemma_bw'] and tok['lemma_bw'] not in lemma_root:
                lemma_root[tok['lemma_bw']] = tok['root_bw']
        self.con.executemany(
            "INSERT OR IGNORE INTO lemmas(lemma_buckwalter, lemma_arabic, root_id) VALUES (?,?,?)",
            [
                (lbw, bw_to_arabic(lbw), self._roots.get(rbw))
                for lbw, rbw in sorted(lemma_root.items())
            ]
        )
        self.con.commit()

        # Build lemma cache
        for row in self.con.execute("SELECT lemma_id, lemma_buckwalter FROM lemmas"):
            self._lemmas[row['lemma_buckwalter']] = row['lemma_id']

        # ── Insert words ──────────────────────────────────────────────────────

        print("  Inserting words...")
        word_rows = []
        words_skipped = 0
        for (s, a, w), wdata in sorted(words_map.items()):
            form_bw = wdata['stem_form']
            if form_bw is None:
                # No STEM token: use the first token's form (should be rare)
                # Find minimum token_position for this word
                for tok in token_rows:
                    if tok['loc'][:3] == (s, a, w):
                        form_bw = tok['form_bw']
                        break
            if form_bw is None:
                words_skipped += 1
                continue

            root_id  = self._roots.get(wdata['stem_root'])  if wdata['stem_root']  else None
            lemma_id = self._lemmas.get(wdata['stem_lemma']) if wdata['stem_lemma'] else None
            word_rows.append((
                None, s, a, w,
                form_bw, bw_to_arabic(form_bw),
                lemma_id, root_id
            ))

        self.con.executemany(
            "INSERT OR IGNORE INTO words(word_id, surah_number, ayah_number, word_position, "
            "form_buckwalter, form_arabic, lemma_id, root_id) VALUES (?,?,?,?,?,?,?,?)",
            word_rows
        )
        self.con.commit()

        # Build word_id cache: (s,a,w) → word_id  (not needed for morphology FK — we use position)

        # ── Insert morphology tokens ──────────────────────────────────────────

        print("  Inserting morphology tokens...")
        morph_rows = []
        for tok in token_rows:
            s, a, w, t = tok['loc']
            feat = tok['feat']
            root_id  = self._roots.get(tok['root_bw'])   if tok['root_bw']  else None
            lemma_id = self._lemmas.get(tok['lemma_bw']) if tok['lemma_bw'] else None
            morph_rows.append((
                None, s, a, w, t,
                tok['form_bw'], tok['tag'], tok['feat_raw'],
                feat['segment_type'], feat['pos'],
                lemma_id, root_id,
                feat['gender'], feat['number_feature'], feat['case_feature'],
                feat['state'], feat['aspect'], feat['voice'],
                feat['mood'], feat['person']
            ))

        BATCH = 5000
        for i in range(0, len(morph_rows), BATCH):
            self.con.executemany(
                "INSERT INTO morphology VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                morph_rows[i:i+BATCH]
            )
        self.con.commit()

        # ── Update root token_counts ──────────────────────────────────────────

        self.con.execute("""
            UPDATE roots SET token_count = (
                SELECT COUNT(*) FROM morphology WHERE morphology.root_id = roots.root_id
            )
        """)
        self.con.commit()

        n_roots  = self.con.execute("SELECT COUNT(*) FROM roots").fetchone()[0]
        n_lemmas = self.con.execute("SELECT COUNT(*) FROM lemmas").fetchone()[0]
        n_words  = self.con.execute("SELECT COUNT(*) FROM words").fetchone()[0]
        n_tokens = self.con.execute("SELECT COUNT(*) FROM morphology").fetchone()[0]

        self.report.table('roots',     imported=n_roots,  notes=[f"Derived from ROOT: fields in morphology corpus"])
        self.report.table('lemmas',    imported=n_lemmas, notes=[f"Derived from LEM: fields in morphology corpus"])
        self.report.table('words',     imported=n_words,  skipped=words_skipped,
                          notes=["One row per (surah, ayah, word_position); STEM token used as representative form"])
        self.report.table('morphology',imported=n_tokens, skipped=parse_errors,
                          notes=[f"{parse_errors} lines skipped (parse errors)"])

        self.report.assume(
            "Words table represents one entry per morphological word position. "
            "The STEM token's FORM, LEM, and ROOT fields are used as the canonical word representation. "
            "If a word has no STEM token (extremely rare), the first token in the word is used."
        )
        self.report.assume(
            "Buckwalter transliteration is stored verbatim in *_buckwalter columns; "
            "Arabic Unicode conversion via standard Buckwalter table is stored in *_arabic columns."
        )

    # ── Pages ─────────────────────────────────────────────────────────────────

    def import_pages(self):
        print("Importing pages...")
        rows = []
        with open(SOURCE["pages"], encoding='utf-8') as f:
            for i, row in enumerate(csv.reader(f), start=1):
                rows.append((i, int(row[1])))   # col[0] = page number (== i), col[1] = ayah count

        self.con.executemany(
            "INSERT INTO pages(page_number, ayah_count_on_page) VALUES (?,?)", rows
        )
        self.con.commit()

        total_ayahs = sum(r[1] for r in rows)
        self.report.table('pages', imported=len(rows),
                          notes=[f"Sum of ayah_count_on_page = {total_ayahs} (expected {EXPECTED_AYAHS})"])
        self.report.assume(
            "pages.csv col[0] is a sequential page number (== row index); "
            "col[1] is the count of ayahs on that page. "
            "No surah_number is stored in pages because pages.csv does not contain "
            "that mapping — surah assignment per page must be computed from the ayahs table."
        )
        self.report.skip(
            "corpus/quran/source/quranbylines.csv",
            "No corresponding schema table (quranbylines represents printed-line layout, "
            "not needed for canonical data layer; import in a future 'layout' schema extension)."
        )
        self.report.skip(
            "corpus/quran/metadata/unicode.csv",
            "Unicode character inventory — informational only, not part of relational schema."
        )
        self.report.skip(
            "corpus/quran/lexical/stemming.csv",
            "Stemming table is a cross-reference aid; roots and lemmas are imported "
            "directly from the morphology corpus which is more authoritative."
        )
        self.report.skip(
            "corpus/quran/lexical/words.csv",
            "Word-type frequency table; frequencies can be computed from morphology table. "
            "Import if a dedicated word_frequencies table is added to the schema."
        )

    # ── Validation ────────────────────────────────────────────────────────────

    def validate(self):
        print("\nValidating...")
        r = self.report
        con = self.con

        n_surahs = con.execute("SELECT COUNT(*) FROM surahs").fetchone()[0]
        r.validate("Surah count = 114", n_surahs == EXPECTED_SURAHS,
                   f"got {n_surahs}")

        n_ayahs = con.execute("SELECT COUNT(*) FROM ayahs").fetchone()[0]
        r.validate("Ayah count = 6236", n_ayahs == EXPECTED_AYAHS,
                   f"got {n_ayahs}")

        n_tokens = con.execute("SELECT COUNT(*) FROM morphology").fetchone()[0]
        r.validate("Morphology token count = 128219", n_tokens == EXPECTED_TOKENS,
                   f"got {n_tokens}")

        n_pages = con.execute("SELECT COUNT(*) FROM pages").fetchone()[0]
        r.validate("Page count = 604", n_pages == 604, f"got {n_pages}")

        page_sum = con.execute("SELECT SUM(ayah_count_on_page) FROM pages").fetchone()[0]
        r.validate("Sum of page ayah counts = 6236", page_sum == EXPECTED_AYAHS,
                   f"got {page_sum}")

        # Every ayah has hafs text
        no_hafs = con.execute("SELECT COUNT(*) FROM ayahs WHERE text_hafs IS NULL OR text_hafs=''").fetchone()[0]
        r.validate("All ayahs have hafs text", no_hafs == 0, f"{no_hafs} missing")

        # Every word links to a valid (surah, ayah)
        orphan_words = con.execute(
            "SELECT COUNT(*) FROM words w "
            "WHERE NOT EXISTS (SELECT 1 FROM ayahs a WHERE a.surah_number=w.surah_number AND a.ayah_number=w.ayah_number)"
        ).fetchone()[0]
        r.validate("No orphan words (FK integrity)", orphan_words == 0,
                   f"{orphan_words} orphans")

        # Every morphology token links to a valid (surah, ayah)
        orphan_tokens = con.execute(
            "SELECT COUNT(*) FROM morphology m "
            "WHERE NOT EXISTS (SELECT 1 FROM ayahs a WHERE a.surah_number=m.surah_number AND a.ayah_number=m.ayah_number)"
        ).fetchone()[0]
        r.validate("No orphan morphology tokens (FK integrity)", orphan_tokens == 0,
                   f"{orphan_tokens} orphans")

        # Root consistency: all morphology root_ids exist in roots table
        bad_roots = con.execute(
            "SELECT COUNT(*) FROM morphology WHERE root_id IS NOT NULL "
            "AND root_id NOT IN (SELECT root_id FROM roots)"
        ).fetchone()[0]
        r.validate("Root FK consistency", bad_roots == 0, f"{bad_roots} broken FKs")

        # Lemma consistency
        bad_lemmas = con.execute(
            "SELECT COUNT(*) FROM morphology WHERE lemma_id IS NOT NULL "
            "AND lemma_id NOT IN (SELECT lemma_id FROM lemmas)"
        ).fetchone()[0]
        r.validate("Lemma FK consistency", bad_lemmas == 0, f"{bad_lemmas} broken FKs")

        # Surah ayah counts consistent with actual ayah rows
        bad_counts = con.execute("""
            SELECT COUNT(*) FROM surahs s
            WHERE s.ayah_count != (
                SELECT COUNT(*) FROM ayahs a WHERE a.surah_number = s.surah_number
            )
        """).fetchone()[0]
        r.validate("Surah ayah counts consistent with ayahs table", bad_counts == 0,
                   f"{bad_counts} surahs with count mismatch")

        # Unique root buckwalter strings
        dup_roots = con.execute(
            "SELECT COUNT(*) FROM roots GROUP BY root_buckwalter HAVING COUNT(*)>1"
        ).fetchone()
        r.validate("Root buckwalter strings unique", dup_roots is None, "duplicates found" if dup_roots else "")

        # Unique lemma buckwalter strings
        dup_lemmas = con.execute(
            "SELECT COUNT(*) FROM lemmas GROUP BY lemma_buckwalter HAVING COUNT(*)>1"
        ).fetchone()
        r.validate("Lemma buckwalter strings unique", dup_lemmas is None, "duplicates found" if dup_lemmas else "")

        # Print summary stats
        n_roots  = con.execute("SELECT COUNT(*) FROM roots").fetchone()[0]
        n_lemmas = con.execute("SELECT COUNT(*) FROM lemmas").fetchone()[0]
        n_words  = con.execute("SELECT COUNT(*) FROM words").fetchone()[0]
        print(f"\n  Roots:  {n_roots}")
        print(f"  Lemmas: {n_lemmas}")
        print(f"  Words:  {n_words}")
        print(f"  Tokens: {n_tokens}")

    # ── Build ─────────────────────────────────────────────────────────────────

    def build(self):
        print(f"\nBuilding {self.db_path} …\n")
        self.create_schema()
        self.import_surahs()
        self.import_ayahs()
        self.import_morphology()
        self.import_pages()
        self.validate()
        self.con.close()
        size_mb = self.db_path.stat().st_size / 1_048_576
        print(f"\nDatabase written: {self.db_path} ({size_mb:.1f} MB)")
        return self.report


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--db',    default=str(GENERATED / "monad.db"),
                    help="Output database path (default: generated/monad.db)")
    ap.add_argument('--force', action='store_true',
                    help="Overwrite existing database")
    args = ap.parse_args()

    GENERATED.mkdir(exist_ok=True)
    db_path = Path(args.db)
    builder = Builder(db_path, force=args.force)
    report  = builder.build()
    return report


if __name__ == '__main__':
    main()
