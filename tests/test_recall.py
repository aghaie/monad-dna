"""L4 — حافظهٔ انتخابی (Selective Retrieval): `./cli/monad recall ROOT`.

هدف: به‌جای بارگذاریِ کاملِ تاریخ (دفترها/knowledge.json) در هر جلسه، فقط
برشِ مرتبط با یک ریشه را الگوریتمی بیرون بکش. سه ضمانت:
۱. کامل‌بودن: هیچ سطرِ مرتبط با ریشه از قلم نیفتد (زیرمجموعه‌سازی، نه نمونه‌گیری).
۲. صداقتِ گزینش: کوچک‌تر از کل بودنِ برش، صریح در coverage اعلام شود.
۳. بی‌نویسی: recall فقط می‌خواند؛ هیچ فایلی تغییر نمی‌کند.
"""
import json
import os
import sqlite3
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)


def _recall(root):
    out = subprocess.run([sys.executable, "cli/monad", "recall", root],
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def test_recall_findings_are_exact_subset_touching_root():
    """هر سطرِ findings که root در آن center یا neighbor است — نه کم، نه زیاد."""
    root = "رحم"
    db = sqlite3.connect("database/life.db")
    expected = sorted(db.execute(
        "SELECT breath_no, center_root, neighbor_root, tier FROM findings "
        "WHERE center_root=? OR neighbor_root=?", (root, root)).fetchall())
    got = sorted((f["breath_no"], f["center"], f["neighbor"], f["tier"])
                for f in _recall(root)["findings"])
    assert got == expected
    assert len(expected) > 0, "ریشهٔ آزمون باید یافتهٔ واقعی داشته باشد"


def test_recall_graph_edges_touch_root_only():
    root = "بدو"
    graph = json.load(open("graph/graph.json"))
    expected = sorted(
        (e["a"], e["b"]) for e in graph["edges"] if root in (e["a"], e["b"]))
    got = sorted((e["a"], e["b"]) for e in _recall(root)["graph_edges"])
    assert got == expected
    assert len(expected) > 0


def test_recall_knowledge_slices_touch_root_only():
    root = "غفر"
    know = json.load(open("discoveries/knowledge.json"))
    exp_strong = sorted(
        (f["breath"], f["center"], f["neighbor"]) for f in know["strong_findings"]
        if root in (f["center"], f["neighbor"]))
    exp_absence = sorted(
        p["pair"] for p in know["absence_evidence"] if root in p["pair"].split("↔"))
    r = _recall(root)
    got_strong = sorted(
        (f["breath"], f["center"], f["neighbor"]) for f in r["knowledge"]["strong_findings"])
    got_absence = sorted(p["pair"] for p in r["knowledge"]["absence_evidence"])
    assert got_strong == exp_strong
    assert got_absence == exp_absence


def test_recall_coverage_is_honest_about_selection():
    """هرچه بار نشد باید در coverage قابلِ محاسبه باشد — سقفِ خاموش ممنوع."""
    r = _recall("رحم")
    c = r["coverage"]
    know = json.load(open("discoveries/knowledge.json"))
    db = sqlite3.connect("database/life.db")
    assert c["life_db_findings_total"] == db.execute("SELECT COUNT(*) FROM findings").fetchone()[0]
    assert c["life_db_findings_for_root"] == len(r["findings"])
    assert c["knowledge_strong_total"] == len(know["strong_findings"])
    assert c["knowledge_strong_for_root"] == len(r["knowledge"]["strong_findings"])
    # این ریشه باید واقعاً برشِ کوچک‌تری از کل باشد — وگرنه recall چیزی صرفه‌جویی نکرده
    assert c["life_db_findings_for_root"] < c["life_db_findings_total"]


def test_recall_never_seen_root_does_not_crash():
    """ریشه‌ای بی‌هیچ یافته — نه خطا، نه سقفِ خاموش؛ فهرست‌های تهی + coverage صادق."""
    r = _recall("__nonexistent_root__")
    assert r["findings"] == []
    assert r["graph_edges"] == []
    assert r["coverage"]["life_db_findings_for_root"] == 0


def test_recall_is_read_only():
    """مرزِ سخت: recall نباید هیچ فایلی را تغییر دهد."""
    import hashlib

    def snapshot():
        h = {}
        for f in ("database/life.db", "graph/graph.json", "discoveries/knowledge.json"):
            h[f] = hashlib.sha256(open(f, "rb").read()).hexdigest()
        return h

    before = snapshot()
    _recall("رحم")
    after = snapshot()
    assert before == after
