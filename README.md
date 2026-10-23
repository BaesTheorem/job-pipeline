# job-pipeline

A job-search pipeline that runs inside [Claude Code](https://claude.com/claude-code). Scripts query a broad set of job boards and ATS APIs every day. They apply your rules (location, employment type, pay floor, title level) as code. Claude reads the JDs that pass and scores each one against a capability table. Then it keeps one markdown note per posting and builds resumes and cover letters. A fact check compares each document with your real resume data before the PDF is made.

One person used it for a daily job search from June to October 2026. Every lane note and every rule in it records a failure that occurred. All personal values are in one gitignored file, `profile.yaml`.

## What it does

- Finds postings in many places. There are 11 scripted lanes, plus two regional examples. Together they cover freehire.me, hiring.cafe, Dice, Indeed, Himalayas, Remotive, WeWorkRemotely, BuiltIn, SimplyHired, SmartRecruiters, Workable, ClearanceJobs, Working Nomads, Jobicy, RemoteOK, HigherEdJobs, HN "Who is hiring", Jooble, Adzuna, Glassdoor and ZipRecruiter through JobSpy, an open dataset of approximately 1.4M ATS postings, USAJOBS, and direct diffs of Greenhouse, Lever, Ashby and Workday boards. Claude adds email job alerts, LinkedIn, ATS searches and the 80,000 Hours board when those tools are connected.
- Applies the gates in code. Remote or home metro, full-time, and a pay **band rule**: a range passes when your floor falls inside it. Unlisted pay fails unless `comp-infer.py` finds evidence from the employer's own other postings. The fit check (gate 4) is a verb-level scorecard that `fit-gate.py` scores. A role is not a fit because a paragraph says so.
- Checks that a posting is open before you spend time on it. `liveness.py` asks the ATS API first: Greenhouse and Lever 404s, Ashby board membership, and Workday `canApply` and its `403 S22` "withdrawn" code. It uses a browser only when the API cannot answer.
- Keeps one note per posting with the full JD archived in it. Near-misses get a note too, so the next scan does not read the same JD again. Dedup knows the status of each note: a rejected role that is posted again comes back as a re-apply candidate.
- Builds documents without invented facts. `resume/build.py` makes clean, parseable PDFs from your JSON resume data. `resume/factcheck.py` stops a build when a number is in neither your data nor the JD, and lists JD acronyms that your data never mentions.
- Measures itself. `runlog.py` records every lane run. `runlog.py yield` shows which lanes find the postings that you apply to.

## Quick start

```bash
git clone https://github.com/BaesTheorem/job-pipeline && cd job-pipeline
uv sync                                     # or: pip install pyyaml curl_cffi pypdf playwright
cp profile.example.yaml profile.yaml        # then edit every value in it
mkdir -p profile
cp templates/profile/capabilities.example.md profile/capabilities.md   # your verb-level skill table
cp templates/profile/rules.example.md profile/rules.md                 # your own standing rules
cp resume/data/resume_data.example.json resume/data/resume_data.json
python3 pipeline/doctor.py --live           # every line OK or WARN, no FAIL
```

Then open Claude Code in the repo and install the skill:

```bash
mkdir -p .claude/skills && ln -s ../../skill/job-search .claude/skills/job-search
claude
> /job-search audit https://job-boards.greenhouse.io/acme/jobs/123
```

Run one lane by hand to see what the output looks like:

```bash
python3 pipeline/angles.py next                       # today's keyword angles, as ready command lines
python3 pipeline/freehire.py "security analyst" --days 3
```

For a daily unattended scan, see `scheduler/` (launchd and cron templates).

[CUSTOMIZE.md](CUSTOMIZE.md) is the full set-up and tuning guide: the profile, the capability table, your own lanes, regional boards, and the tracker.

## Layout

| Path | What is in it |
|---|---|
| `profile.example.yaml` | Every personal value: floors, metro, title filters, knockouts, keyword angles, paths. Copy it to `profile.yaml`. |
| `pipeline/` | Lanes (one script per source), gates (`fit-gate.py`, `comp-infer.py`), `liveness.py`, `dedup-lookup.py`, `contact-check.py`, `jd-snapshot.py`, `runlog.py`, `doctor.py`. |
| `pipeline/regional/` | Two worked examples of a local lane: a city PeopleSoft board and a state job board. |
| `skill/job-search/SKILL.md` | The Claude Code skill: gates, lanes, verification, notes, modes. |
| `resume/` | The PDF builder and the fact check. |
| `tracker/reconcile.py` | Keeps note frontmatter consistent (applied, rejected dates). |
| `scheduler/` | The daily scan runner, its prompt, and launchd and cron templates. |
| `docs/` | Prior art, lessons, the fit scorecard, the tracker, the ATS playbook. |

## Requirements

- Python 3.11 or later, and [uv](https://docs.astral.sh/uv/) for the lanes that run a headless browser (Indeed, JobSpy, the regional examples)
- Claude Code for the skill and the daily scan
- Optional: `qpdf` (PDF rewrite), free API keys for USAJOBS, Jooble and Adzuna (`.env.example`), a Gmail and a LinkedIn tool in Claude Code

## Limits

- A lane can stop when a board changes its site. Each lane prints `NOT RUN`, `TRUNCATED` or `COVERAGE` lines when it does not fully run, and `runlog.py` records failed runs. A failed run is a tooling problem, and the record keeps it apart from a lane that found nothing.
- The pipeline does not apply for you, send messages, or touch LinkedIn Easy Apply. You submit every application.
- The fact check catches invented numbers and lists keywords for review. It does not prove that a document is true. Read everything before you send it.
- The defaults reflect a US search for entry-level IT and security roles. Most lanes are general, but the title lists, the keyword angles and the regional examples need your values.

## Related projects

[docs/prior-art.md](docs/prior-art.md) compares this pipeline with career-ops, Seekter, idotsuk/claude-job-search, OfferOS and others. It records what each one does better, and which ideas came from them: the API-first liveness check (career-ops), the output fact check (career-ops, Seekter), the per-lane yield record (idotsuk, Seekter) and the freehire.me lane (Seekter's source notes).

## License

MIT. The lanes read public endpoints. You are responsible for following each site's terms.
