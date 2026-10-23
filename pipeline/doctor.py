#!/usr/bin/env python3
"""Check that this clone is ready to run: profile, paths, tools, keys.

    python3 pipeline/doctor.py           # offline checks
    python3 pipeline/doctor.py --live    # also one small request to each keyless API lane

Each line is OK, WARN (a lane or feature will skip) or FAIL (the pipeline
cannot run). Exit 1 on any FAIL.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import sys
import urllib.request

import jobprofile as P

UA = "job-pipeline/0.1 (+https://github.com/BaesTheorem/job-pipeline)"
results: list[tuple[str, str]] = []


def say(level: str, msg: str) -> None:
    results.append((level, msg))
    print(f"{level:5} {msg}")


def env_key(name: str) -> bool:
    if os.environ.get(name):
        return True
    env = P.REPO / ".env"
    return env.exists() and any(line.split("=", 1)[0].strip() == name and line.split("=", 1)[1].strip()
                                for line in env.read_text().splitlines() if "=" in line)


def check_profile() -> bool:
    try:
        P.load()
    except P.ProfileError as e:
        say("FAIL", str(e))
        return False
    say("OK", f"profile: {P.profile_path()}")
    for key in ("comp.remote_floor", "comp.onsite_floor", "titles.keep", "angles.titles", "paths.listings"):
        try:
            P.get(key)
        except P.ProfileError as e:
            say("FAIL", str(e))
    try:
        floor, onsite = P.comp_floor(), P.onsite_floor()
        say("OK", f"floors: remote ${floor:,}, onsite ${onsite:,}")
    except P.ProfileError as e:
        say("FAIL", str(e))
    for kind in ("keep", "drop", "strong"):
        try:
            P.title_re(kind)
        except Exception as e:  # noqa: BLE001  a bad regex in the profile
            say("FAIL", f"titles.{kind} does not compile: {e}")
    try:
        P.off_lane_re()
    except Exception as e:  # noqa: BLE001
        say("FAIL", f"titles.off_lane does not compile: {e}")
    if P.has_metro():
        say("OK", f"home metro: {P.metro_name()} ({P.metro_search()}, {P.metro_radius()} mi)")
    else:
        say("OK", "no home metro: remote-only search, local passes skip")
    return True


def check_paths() -> None:
    lst = P.listings_dir()
    say("OK" if lst.is_dir() else "WARN", f"listings folder: {lst}" + ("" if lst.is_dir() else " (missing; create it)"))
    for a in P.archive_dirs():
        if not a.is_dir():
            say("WARN", f"archive folder missing: {a}")
    cap = P.capabilities_file()
    if not cap or not cap.exists():
        say("WARN", f"capabilities file missing ({cap}); gate 4 has nothing to score against")
    data = P.REPO / "resume" / "data" / "resume_data.json"
    say("OK" if data.exists() else "WARN", f"resume data: {data}" + ("" if data.exists() else " (missing)"))


def check_tools() -> None:
    py = {"yaml": "FAIL", "curl_cffi": "WARN", "pypdf": "WARN", "playwright": "WARN"}
    for mod, level in py.items():
        ok = importlib.util.find_spec(mod) is not None
        say("OK" if ok else level, f"python module {mod}" + ("" if ok else " missing (uv sync)"))
    for exe, why in (("claude", "the daily scan and comp-infer agent"), ("uv", "indeed.py, jobspy_lane.py, kcmo.py"),
                     ("qpdf", "PDF linearize in resume/build.py")):
        say("OK" if shutil.which(exe) else "WARN", f"{exe}: " + ("found" if shutil.which(exe) else f"missing ({why})"))
    for name, lane in (("USAJOBS_API_KEY", "usajobs.py"), ("JOOBLE_API_KEY", "moreboards jooble"),
                       ("ADZUNA_APP_ID", "moreboards adzuna")):
        say("OK" if env_key(name) else "WARN", f"{name}: " + ("set" if env_key(name) else f"not set ({lane} skips)"))


def check_live() -> None:
    probes = {
        "freehire": "https://freehire.me/api/v1/jobs/search?q=analyst&limit=1",
        "greenhouse api": "https://boards-api.greenhouse.io/v1/boards/gitlab/jobs",
        "himalayas": "https://himalayas.app/jobs/api?limit=1",
        "remotive": "https://remotive.com/api/remote-jobs?limit=1",
        "aggregator dataset": "https://riley-dorrington.github.io/job-board-data/data/chunks/jobs_manifest.json",
    }
    for name, url in probes.items():
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=20) as r:
                say("OK", f"{name}: HTTP {r.status}")
        except Exception as e:  # noqa: BLE001  report, keep checking
            say("WARN", f"{name}: {str(e)[:80]}")


def main() -> int:
    ap = argparse.ArgumentParser(description="check this clone is ready to run")
    ap.add_argument("--live", action="store_true", help="probe the keyless API lanes")
    a = ap.parse_args()
    if check_profile():
        check_paths()
    check_tools()
    if a.live:
        check_live()
    fails = sum(1 for lvl, _ in results if lvl == "FAIL")
    warns = sum(1 for lvl, _ in results if lvl == "WARN")
    print(f"\n{fails} FAIL, {warns} WARN")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
