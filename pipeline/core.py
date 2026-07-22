#!/usr/bin/env python3
"""خطِ موازیِ نفس‌ها — S0 (برنامه‌ریز) + صفِ کار + S2 (دروازهٔ هم‌ارزی و ثبت).

طرحِ مصوبِ باغبان: docs/PARALLEL-PIPELINE-DESIGN-2026-07-22.md.
فقط زیرساخت (لایهٔ ۴): هیچ الگوریتمِ کشفی این‌جا نیست — همان
engine.breathe_record متعارف صدا زده می‌شود؛ همان اعتبارسنجی‌ها سرِ جای
خودشان می‌مانند. ضمانتِ «بایت‌به‌بایت هم‌ارزِ اجرای ترتیبی» با دروازهٔ
S2 *سنجیده* می‌شود، فرض نمی‌شود:

- S0 (`plan`) زنجیرهٔ قطعیِ نفس‌ها را K گام جلو می‌بَرد — فقط‌خواندنی از
  life.db؛ فرضِ افق: هیچ رویدادِ صفِ تازه (queued/تزریق/رفیق) در میانه.
- S2 (`gate_next`/`merge_next`) پیش از هر ثبت، رکورد را از حالتِ زندهٔ
  واقعی بازتولید و checksum را با برنامه مقایسه می‌کند؛ ناسازگاری ⇒ epoch
  جدید و بازبرنامه‌ریزی — رکوردِ کهنه هرگز ثبت نمی‌شود.
- تصمیم‌های زیستی (یادداشتِ seed، روایتِ دفتر، صف‌کردنِ شکاف) همچنان با
  لایهٔ زنده‌اند: کارگرها فقط پیش‌نویس/غنی‌سازی به pipeline/work/ می‌آورند.
"""
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

from engine import breath_cycle as bc

DEFAULT_DIR = "pipeline"
CHOSEN_BY = "قاعدهٔ صف (نادرتر مقدم)"     # همان پیش‌فرضِ breathe-record
SEED_CHOSEN_BY = "قاعدهٔ صف (خودران)"      # همان برچسبِ سطرهای BREATHS حلقه
EVENT_SOURCE = "قاعدهٔ صف"                 # همان منشأِ رویدادِ pursued
CHAPTER = "پل‌ها"
LEDGER = "breaths/logs/پل‌ها-2026-07-19.md"
INJECTIONS_FILE = "database/queue_injections.json"


# ---------- حالتِ زنده (فقط‌خواندنی) ----------

def _life_db():
    return sqlite3.connect("file:database/life.db?mode=ro", uri=True)


def open_queue(upto=None):
    """عیناً همان صفِ بازِ CLI (ترتیب حفظ می‌شود)؛ با upto: حالتِ تاریخی.

    هم‌ارزی‌اش با cli.open_queue در tests/test_pipeline.py سنجیده می‌شود."""
    db = _life_db()
    cond = "" if upto is None else f" AND breath_no<={int(upto)}"
    q = [r for (r,) in db.execute(
        f"SELECT root FROM queue_events WHERE event='queued'{cond}")]
    p = {r for (r,) in db.execute(
        f"SELECT root FROM queue_events WHERE event='pursued'{cond}")}
    seen, out = set(), []
    for r in q:
        if r not in p and r not in seen:
            seen.add(r)
            out.append(r)
    if os.path.exists(INJECTIONS_FILE):
        for inj in json.load(open(INJECTIONS_FILE, encoding="utf-8")):
            r = inj["root"]
            if upto is not None and inj.get("added_after_breath", 0) > upto:
                continue
            if r not in p and r not in seen:
                seen.add(r)
                out.append(r)
    return out


def lived_and_next(upto=None):
    db = _life_db()
    cond = "" if upto is None else f" WHERE breath_no<={int(upto)}"
    lived = [r for (r,) in db.execute(
        f"SELECT pursued_root FROM breaths{cond} ORDER BY breath_no")]
    no = (db.execute(f"SELECT MAX(breath_no) FROM breaths{cond}")
          .fetchone()[0] or 0) + 1
    return lived, no


def record_text(rec):
    return json.dumps(rec, ensure_ascii=False, indent=1) + "\n"


def new_candidates(text):
    """ریشه‌های نامزدِ صفِ تازه در یک رکورد: همسایهٔ قوی/محتمل که هنوز نه
    زیسته، نه در صف، نه تزریق‌شده.

    اگر ناتهی باشد، رشدِ صف تصمیمی است که خط نباید خودکار بگیرد: قاعدهٔ صفِ
    فصلِ پل‌ها فرمولِ محضِ خودکارشدنی نیست (نمونهٔ نقض: نفس ۱۲۴ كللِ یک‌طرفه
    را هم صف کرد). پس merge در حضورِ نامزد ثبت نمی‌کند و به لایهٔ زنده/باغبان
    وامی‌گذارد. این تنها نقطه‌ای است که هم‌ارزیِ *گزینشِ آینده* (نه بایتِ
    رکوردِ جاری) می‌تواند از اجرای ترتیبی واگرا شود؛ نگهبان آن را می‌بندد."""
    rec = json.loads(text)
    db = _life_db()
    seen = {r for (r,) in db.execute("SELECT pursued_root FROM breaths")}
    seen |= {r for (r,) in db.execute(
        "SELECT root FROM queue_events WHERE event='queued'")}
    if os.path.exists(INJECTIONS_FILE):
        seen |= {i["root"] for i in
                 json.load(open(INJECTIONS_FILE, encoding="utf-8"))}
    return [t["root"] for t in rec["top"]
            if t["tier"] in ("قوی", "محتمل") and t["root"] not in seen]


def _step(corpus, lived, queue_open, breath_no):
    """یک گامِ زنجیره — عیناً منطقِ cmd_breathe_record(root=None)."""
    ordered = bc.select_rarest(queue_open, corpus["attest"])
    if not ordered:
        return None
    pursued = ordered[0]
    rec = bc.breathe_record(corpus, pursued=pursued, queue=ordered[:10],
                            lived=lived, breath_no=breath_no,
                            chosen_by=CHOSEN_BY)
    return pursued, record_text(rec)


# ---------- صفِ کار و حالت ----------

def _paths(root_dir):
    return (os.path.join(root_dir, "state.json"),
            os.path.join(root_dir, "jobs.json"),
            os.path.join(root_dir, "work"),
            os.path.join(root_dir, "locks"))


def load_state(root_dir=DEFAULT_DIR):
    p = _paths(root_dir)[0]
    if not os.path.exists(p):
        return {"epoch": 0, "planned_upto": None}
    return json.load(open(p, encoding="utf-8"))


def save_state(state, root_dir=DEFAULT_DIR):
    p = _paths(root_dir)[0]
    os.makedirs(root_dir, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=1)
        f.write("\n")


def load_jobs(root_dir=DEFAULT_DIR):
    p = _paths(root_dir)[1]
    if not os.path.exists(p):
        return []
    return json.load(open(p, encoding="utf-8"))


def save_jobs(jobs, root_dir=DEFAULT_DIR):
    p = _paths(root_dir)[1]
    os.makedirs(root_dir, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=1)
        f.write("\n")


# ---------- S0: برنامه‌ریز ----------

def plan(k, upto=None, root_dir=DEFAULT_DIR):
    """زنجیرهٔ قطعی را K گام جلو می‌بَرد و صفِ کار را می‌نویسد.

    فرضِ افق: بدونِ رویدادِ صفِ تازه در میانه — هر انحراف را دروازهٔ S2
    می‌گیرد و epoch باطل می‌شود. کارِ سالمِ قبلی (همان sha) حفظ می‌شود."""
    corpus = bc.load_corpus()
    lived, breath_no = lived_and_next(upto)
    queue_open = open_queue(upto)
    prev_jobs = {j["breath_no"]: j for j in load_jobs(root_dir)}
    state = load_state(root_dir)
    epoch = state["epoch"] + 1
    _, _, work, _ = _paths(root_dir)

    jobs = []
    for _ in range(k):
        step = _step(corpus, lived, queue_open, breath_no)
        if step is None:
            break
        pursued, text = step
        sha = hashlib.sha256(text.encode()).hexdigest()
        wd = os.path.join(work, f"{breath_no}_{pursued}")
        os.makedirs(wd, exist_ok=True)
        prev = prev_jobs.get(breath_no)
        if not (prev and prev["record_sha256"] == sha):
            # برنامهٔ کهنه/ناسازگار: مصنوعاتِ ماندهٔ آن دور ریخته می‌شود
            for f in os.listdir(wd):
                os.remove(os.path.join(wd, f))
            prev = None
        with open(os.path.join(wd, "record.json"), "w", encoding="utf-8") as f:
            f.write(text)
        jobs.append(dict(
            breath_no=breath_no, root=pursued, epoch=epoch,
            record_sha256=sha,
            status=(prev["status"] if prev else "pending"),
            worker=(prev or {}).get("worker"),
            attempts=(prev or {}).get("attempts", 0)))
        lived = lived + [pursued]
        queue_open = [r for r in queue_open if r != pursued]
        breath_no += 1

    save_jobs(jobs, root_dir)
    save_state({"epoch": epoch,
                "planned_upto": (jobs[-1]["breath_no"] if jobs else None)},
               root_dir)
    return jobs


# ---------- کارگر: برداشتنِ job با قفلِ اتمی ----------

def claim(breath_no, worker, root_dir=DEFAULT_DIR):
    locks = _paths(root_dir)[3]
    os.makedirs(locks, exist_ok=True)
    try:
        fd = os.open(os.path.join(locks, f"{breath_no}.lock"),
                     os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return False
    with os.fdopen(fd, "w") as f:
        f.write(worker)
    jobs = load_jobs(root_dir)
    for j in jobs:
        if j["breath_no"] == breath_no:
            j["status"], j["worker"] = "running", worker
    save_jobs(jobs, root_dir)
    return True


# ---------- S2: دروازهٔ هم‌ارزی ----------

def gate_next(root_dir=DEFAULT_DIR):
    """بازتولیدِ رکوردِ نفسِ بعدی از حالتِ زندهٔ واقعی و مقایسه با برنامه.

    (ok=True, text) یا (ok=False, دلیل + epoch باطل)."""
    corpus = bc.load_corpus()
    lived, breath_no = lived_and_next()
    step = _step(corpus, lived, open_queue(), breath_no)
    if step is None:
        return False, "صفِ باز تهی است"
    pursued, text = step
    sha = hashlib.sha256(text.encode()).hexdigest()
    job = next((j for j in load_jobs(root_dir) if j["breath_no"] == breath_no),
               None)
    if job is None or job["root"] != pursued or job["record_sha256"] != sha:
        state = load_state(root_dir)
        state["epoch"] += 1
        save_state(state, root_dir)
        why = ("برنامه‌ای برای این نفس نیست" if job is None else
               f"واگرایی از برنامه (برنامه: {job['root']})")
        return False, (f"{why} — نفسِ زنده {breath_no} ({pursued})؛ "
                       "epoch باطل شد، pipeline-plan دوباره لازم است")
    return True, text


# ---------- S2: درجِ مکانیکیِ seed (چهار لنگر، سپس ast.parse) ----------

def insert_seed_entry(src, no, root, note):
    prev = no - 1
    m = re.search(rf'b{prev} = rec\("breath_{prev}_(.+?)\.json"\)', src)
    if not m:
        raise ValueError(f"لنگرِ b{prev} یافت نشد")
    anchor = m.group(0)
    src = src.replace(anchor,
                      f'{anchor}\nb{no} = rec("breath_{no}_{root}.json")', 1)

    end_prev = f'b{prev}["top"]),'
    i = src.rfind(end_prev)
    if i < 0:
        raise ValueError(f"لنگرِ پایانِ سطرِ نفسِ {prev} یافت نشد")
    i += len(end_prev)
    note_lit = json.dumps(note, ensure_ascii=False)
    entry = (f'\n    ({no}, "{CHAPTER}", "{root}", "{SEED_CHOSEN_BY}",\n'
             f'     b{no}["ayat"], b{no}["halves_overlap"],\n'
             f'     "cli/monad breathe-record-from breaths/records/breath_{no}_{root}.json",\n'
             f'     "breaths/records/breath_{no}_{root}.json", LOG5,\n'
             f'     {note_lit}, b{no}["top"]),')
    src = src[:i] + entry + src[i:]

    old = f'({prev}, b{prev})):'
    if old not in src:
        raise ValueError("لنگرِ حلقهٔ (bn, brec) یافت نشد")
    src = src.replace(old, f'({prev}, b{prev}), ({no}, b{no})):', 1)

    qi = src.find("QUEUE_EVENTS = [")
    qe = src.find("\n]", qi)
    if qi < 0 or qe < 0:
        raise ValueError("لنگرِ QUEUE_EVENTS یافت نشد")
    src = (src[:qe] + f'\n    ({no}, "pursued", "{root}", "{EVENT_SOURCE}"),'
           + src[qe:])
    return src


# ---------- S2: ثبتِ نفسِ بعدی ----------

def merge_next(root_dir=DEFAULT_DIR, dry_run=False):
    """گام‌های ترتیبیِ رسمی‌سازی، پشتِ دروازهٔ هم‌ارزی. dry_run: فقط دروازه."""
    ok, payload = gate_next(root_dir)
    if not ok:
        return {"ok": False, "stage": "gate", "reason": payload}
    cand = new_candidates(payload)
    if cand:
        return {"ok": False, "stage": "queue-decision",
                "reason": (f"ریشه‌های نامزدِ صفِ تازه: {cand} — رشدِ صف تصمیمِ "
                           "لایهٔ زنده/باغبان است، نه فرمولِ خط؛ ثبت نشد")}
    lived, breath_no = lived_and_next()
    job = next(j for j in load_jobs(root_dir) if j["breath_no"] == breath_no)
    root = job["root"]
    wd = os.path.join(_paths(root_dir)[2], f"{breath_no}_{root}")
    if dry_run:
        return {"ok": True, "stage": "gate", "breath_no": breath_no,
                "root": root, "dry_run": True}

    note_p = os.path.join(wd, "note.md")
    if not os.path.exists(note_p):
        return {"ok": False, "stage": "note",
                "reason": f"یادداشتِ seed آماده نیست: {note_p} — کارِ لایهٔ زنده/کارگر"}
    note = open(note_p, encoding="utf-8").read().strip()

    rec_path = f"breaths/records/breath_{breath_no}_{root}.json"
    seed_path = "database/seed/seed_life.py"
    seed_src = open(seed_path, encoding="utf-8").read()

    def rollback():
        """بازگردانیِ کاملِ کارپوشه به HEAD — نه فقط seed. seed-db و
        ponder-sync پیش از شکست ممکن است life.db/گراف/کشف/تدبّر را بازساخته
        باشند؛ همه باید به حالتِ پیش‌از-merge برگردند وگرنه مخزن ناسازگار
        می‌ماند (کشفِ ۲۰۲۶-۰۷-۲۲: rollbackِ ناقص، life.db را ۱۹۴ رها کرد)."""
        tracked = [seed_path, "database/life.db", "graph/graph.json",
                   "discoveries/knowledge.json", "observatory/observatory.json",
                   "tadabbor/index.json", LEDGER]
        subprocess.run(["git", "checkout", "--"] + tracked, check=False)
        subprocess.run(["git", "clean", "-fdq", "tadabbor/portraits"],
                       check=False)
        if os.path.exists(rec_path):
            os.remove(rec_path)

    try:
        with open(rec_path, "w", encoding="utf-8") as f:
            f.write(payload)
        new_src = insert_seed_entry(seed_src, breath_no, root, note)
        import ast
        ast.parse(new_src)
        with open(seed_path, "w", encoding="utf-8") as f:
            f.write(new_src)
        checks = [
            [sys.executable, "database/seed/seed_life.py"],
            [sys.executable, "tadabbor/build.py", "--sync"],
            [sys.executable, "-m", "pytest", "tests/", "-q"],
            ["./cli/monad", "verify"],
        ]
        for cmd in checks:
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode != 0:
                rollback()
                _mark(root_dir, breath_no, "failed")
                return {"ok": False, "stage": " ".join(cmd),
                        "reason": (r.stdout + r.stderr)[-2000:]}
        ledger_p = os.path.join(wd, "ledger.md")
        if os.path.exists(ledger_p):
            with open(LEDGER, "a", encoding="utf-8") as f:
                f.write("\n" + open(ledger_p, encoding="utf-8").read().strip()
                        + "\n")
        msg_p = os.path.join(wd, "commit.txt")
        msg = (open(msg_p, encoding="utf-8").read().strip()
               if os.path.exists(msg_p)
               else f"نفس {breath_no} — {root} (خطِ لوله)")
        subprocess.run(["git", "add", rec_path, seed_path, "database/life.db",
                        "graph/graph.json", "discoveries/knowledge.json",
                        "tadabbor", LEDGER], check=True)
        subprocess.run(["git", "commit", "-q", "-m",
                        msg + "\n\nCo-Authored-By: Claude Fable 5 <noreply@anthropic.com>"],
                       check=True)
    except Exception as e:  # هر خطای پیش‌بینی‌نشده: بازگردانی، سپس گزارش
        rollback()
        _mark(root_dir, breath_no, "failed")
        return {"ok": False, "stage": "exception", "reason": repr(e)}
    _mark(root_dir, breath_no, "reviewed")
    return {"ok": True, "breath_no": breath_no, "root": root}


def _mark(root_dir, breath_no, status):
    jobs = load_jobs(root_dir)
    for j in jobs:
        if j["breath_no"] == breath_no:
            j["status"] = status
            j["attempts"] = j.get("attempts", 0) + (status == "failed")
    save_jobs(jobs, root_dir)


def work(worker="worker", root_dir=DEFAULT_DIR):
    """S1 مکانیکی: نخستین jobِ pending را با قفل بردار و غنی‌سازیِ
    بی‌مدل را انجام بده (مشورتِ رصدخانه + سیمای تدبّر). یادداشتِ seed و
    روایتِ دفتر کارِ لایهٔ زنده است (note.md / ledger.md / commit.txt در
    همان پوشهٔ کاری). status=completed یعنی «مصنوعاتِ مکانیکی آماده»."""
    for j in load_jobs(root_dir):
        if j["status"] == "pending" and claim(j["breath_no"], worker, root_dir):
            wd = os.path.join(_paths(root_dir)[2],
                              f"{j['breath_no']}_{j['root']}")
            obs = subprocess.run(["./cli/monad", "observe", j["root"]],
                                 capture_output=True, text=True)
            with open(os.path.join(wd, "observe.json"), "w",
                      encoding="utf-8") as f:
                f.write(obs.stdout)
            subprocess.run([sys.executable, "tadabbor/build.py", j["root"]],
                           capture_output=True, text=True)
            _mark(root_dir, j["breath_no"], "completed")
            return j
    return None


def status(root_dir=DEFAULT_DIR):
    jobs = load_jobs(root_dir)
    st = load_state(root_dir)
    counts = {}
    for j in jobs:
        counts[j["status"]] = counts.get(j["status"], 0) + 1
    _, live_next = lived_and_next()
    return {"epoch": st["epoch"], "planned_upto": st.get("planned_upto"),
            "live_next_breath": live_next, "jobs": counts,
            "detail": [{k: j[k] for k in
                        ("breath_no", "root", "status", "worker")}
                       for j in jobs]}
