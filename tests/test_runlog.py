"""pipeline/runlog.py parses lane summaries and appends one line per run."""

import json
import sys

from conftest import load_script

rl = load_script("pipeline/runlog.py")


def test_parse_counts_from_lane_summaries():
    assert rl.parse_counts("12 unique | 3 survivors | 5 leads | 2 declined | 2 title-dropped") == {
        "unique": 12, "survivor": 3, "lead": 5, "declined": 2, "title-dropped": 2}
    assert rl.parse_counts("1 new verified survivor")["survivor"] == 1


def test_wrap_records_exit_and_counts(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(rl, "runs_file", lambda: tmp_path / "runs.jsonl")
    code = rl.wrap("demo", [sys.executable, "-c", "print('4 survivors | 1 leads'); print('== x NOT RUN: 403')"])
    assert code == 0
    rec = json.loads((tmp_path / "runs.jsonl").read_text())
    assert rec["lane"] == "demo" and rec["counts"]["survivor"] == 4 and rec["counts"]["lead"] == 1
    assert any("NOT RUN" in n for n in rec["notes"])
    assert "4 survivors" in capsys.readouterr().out  # output passes through


def test_wrap_keeps_the_exit_code(monkeypatch, tmp_path):
    monkeypatch.setattr(rl, "runs_file", lambda: tmp_path / "runs.jsonl")
    assert rl.wrap("bad", [sys.executable, "-c", "raise SystemExit(3)"]) == 3


def test_self_counting_lane_is_recorded_once(monkeypatch, tmp_path):
    monkeypatch.setattr(rl, "runs_file", lambda: tmp_path / "runs.jsonl")
    child = ("import json; print('RUNLOG-COUNTS ' + json.dumps({'counts': {'survivor': 2, 'rows': 9}, 'notes': []}));"
             "print('99 survivors')")
    rl.wrap("self", [sys.executable, "-c", child])
    lines = (tmp_path / "runs.jsonl").read_text().splitlines()
    assert len(lines) == 1 and json.loads(lines[0])["counts"] == {"survivor": 2, "rows": 9}
