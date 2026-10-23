# Customize the pipeline for your search

This guide tells you how to make the pipeline search for your roles, in your place, at your pay. Do the steps in order. Step 1 to step 4 are necessary. The others are optional.

## 1. Write your profile

```bash
cp profile.example.yaml profile.yaml
```

`profile.yaml` is gitignored. Every lane and gate reads it. Edit each section:

| Section | What to set | Notes |
|---|---|---|
| `comp` | `remote_floor`, `onsite_floor` (annual USD) | The band rule passes a range when your floor falls inside it. Set the onsite floor higher if an office day costs you time and money. |
| `location.metro` | `search`, `search_long`, `radius_mi`, `tag`, `cities` | Leave `metro` out for a remote-only search. `cities` is a list of regex fragments matched anywhere in a location string. Include suburbs, and state abbreviations where a city name is ambiguous ("independence, mo"). |
| `titles.keep` | words a title must contain | Fragments inside word boundaries. Keep it broad: the JD read and the scorecard do the fine work. |
| `titles.drop` | seniority above your level, platforms you do not have, sales shapes | This filter runs before any JD read, so it saves the most time. |
| `titles.off_lane` | full regexes for titles that pass `keep` on a generic word | For example "financial ... analyst" when you search for security analysts. |
| `knockouts` | `degree_required`, `max_years`, `clearance` | Used on boards with structured fields (hiring.cafe, freehire). |
| `angles` | `titles` and `phrases` | The daily rotation takes 3 titles and 2 phrases, least recently used first. Use duty phrases from your real work ("access provisioning", "month-end close"). They find roles with titles you would not search. |
| `paths` | `listings`, `archive`, `state` | The listings folder holds one note per posting. An Obsidian vault folder works well. |
| `lanes` | per-lane settings | Employers on Jibe or Oracle HCM near you; freehire categories. |
| `notify` | a command | Called by the daily scan with a message and a title, for example a `terminal-notifier` or `ntfy` call. |

Check it:

```bash
python3 pipeline/doctor.py --live
```

## 2. Write your capability table

```bash
mkdir -p profile
cp templates/profile/capabilities.example.md profile/capabilities.md
```

This table is what gate 4 scores against. Write one row per area of your work, with the highest verb level that is true: Own/Build, Administer, Operate, Support, Exposure or None. See [docs/fit-scorecard.md](docs/fit-scorecard.md) for the method and for how to calibrate the 0.65 pass line on your own past applications.

Be strict. A level that is too high passes roles where you cannot answer the interview questions.

## 3. Write your rules (optional, recommended)

```bash
cp templates/profile/rules.example.md profile/rules.md
```

Rules are for things the profile cannot hold: a weekly goal, employers where you have a referral path, per-firm exceptions, extra lanes with their own gates, your writing voice, where the scan log goes. The skill reads this file first, and a rule here wins over the skill.

## 4. Add your resume data

```bash
cp resume/data/resume_data.example.json resume/data/resume_data.json
```

Fill in every field. This file is the source of truth for every resume and the fact check. Put true facts that are not on every resume (an exam code, a number you can prove, a tool you used once) in `resume/data/facts.md`. Then the fact check accepts them in a letter.

## 5. Install the skill and run one audit

```bash
mkdir -p .claude/skills && ln -s ../../skill/job-search .claude/skills/job-search
claude
> /job-search audit <a posting URL>
```

Read the note it writes. If the scorecard rows look wrong, fix your capability table and run the audit again.

## 6. Pick your lanes

Run each lane one time by hand with today's angles (`python3 pipeline/angles.py next` prints the commands). Then remove the lanes that do not suit your field:

- **Remote-only tech roles:** all lanes are useful.
- **Non-tech roles:** Dice, ClearanceJobs and the HN thread give little. freehire.me, hiring.cafe, Indeed, the aggregator dataset and the ATS watchlists are general.
- **Outside the US:** USAJOBS does not apply. freehire.me takes a `country` (set `lanes.freehire.country`), and the career-ops project has providers for many national boards (see docs/prior-art.md).

To remove a lane from the daily scan, delete it from `scheduler/scan-prompt.md` step 3.

After two weeks, run `python3 pipeline/runlog.py yield`. It shows rows, survivors and leads per lane, and the tracker funnel by `source`. Remove lanes with many runs and no applied notes.

## 7. Add a local lane

Most cities, counties, states, universities and hospital systems post jobs on their own boards, and many of those postings appear nowhere else. `pipeline/regional/` has two worked examples:

- `kcmo.py`: a city board on PeopleSoft Candidate Gateway, read with headless Chrome (patchright under uv), with a WATCH list of titles that always print.
- `talify.py`: a state board on a Rails app with a JSON endpoint and Ransack filter parameters.

To make your own:

1. Find the data path. Open the board in a browser with the developer tools open, search, and look for a JSON or HTML request that returns the results. Try it with `curl`. If `curl` gets a 403 or a challenge page, use `curl_cffi` with `impersonate="chrome"`, then headless Chrome.
2. Copy the regional example that is closest. Keep its output shape: one `== query N rows` line per query, then SURVIVORS, LEADS and a summary line with counts. `runlog.py` reads the counts.
3. Gate with the profile: `P.title_re("keep")`, `P.title_re("drop")`, `P.metro_re()`, `comp_floor()`, `onsite_floor()`.
4. Make it say when it did not run: print `NOT RUN` or `~ COVERAGE` lines, and compare your parsed count with the board's own total when it shows one.
5. Add it to `scheduler/scan-prompt.md` and to your `profile/rules.md`.

Many employers use one ATS. For a Workday employer, pin its filtered board: `python3 pipeline/workday.py --add "<board URL with filters>" --why "..."`. For Greenhouse, Lever or Ashby employers, add `{"<ats>:<board>": {"why": "..."}}` to `state/watchlist-extra.json`. Both lanes also find every employer that already has a note.

## 8. Set up the tracker view

The notes are the tracker. [docs/tracker.md](docs/tracker.md) has an Obsidian Bases file with Active, Applied and Re-apply views, and the `reconcile.py` rules. Run `tracker/reconcile.py` from the scheduler or from a file watcher.

## 9. Schedule the daily scan

```bash
cp .env.example .env                       # optional API keys
bash scheduler/run-scan.sh                 # one run by hand first; logs go to ~/.job-pipeline/logs
```

Then install `scheduler/launchd.plist.template` (macOS) or `scheduler/crontab.example`. The scan uses Claude Code with `--dangerously-skip-permissions`, because an unattended run cannot answer permission prompts. Job postings and emails are third-party text. Run the scan as a user account that holds nothing you would not risk, and keep secrets out of the repo folder.

A full scan takes 20 to 50 minutes. Set `JOB_SCAN_MODEL` to choose a model.

## Privacy

These files are gitignored: `profile.yaml`, `profile/`, `.env`, `state/` (except the examples), `resume/data/resume_data.json`, `resume/data/facts.md`, `resume/tailoring/` (except the examples). The state folder shows where you apply. If you fork the repo, keep it that way. CI fails if one of the personal files is tracked.
