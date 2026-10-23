# Prior art

Before this repo was published (2026-10-23), we searched GitHub for other Claude-powered and LLM-powered job-search tools, cloned the eleven most relevant ones, and read their code. We also tested the two most promising data sources against their live APIs. This file records what each project does better than this one, and which ideas this repo took from them.

## The projects

| Project | Shape | License |
|---|---|---|
| [career-ops](https://github.com/career-ops-hq/career-ops) | The largest (approximately 77k stars). Paste a job, get an A-H evaluation, a tailored CV and a tracker row. Works in many AI CLIs. 120 providers. | MIT |
| [Seekter](https://github.com/selfishprimate/seekter) | The closest to this repo: a daily Claude Code run, rules-based filters, a markdown tracker. Fills forms in your own Chrome. | MIT |
| [idotsuk/claude-job-search](https://github.com/idotsuk/claude-job-search) | A Claude Code sweep with a source registry that promotes and demotes sources by yield. LinkedIn, Gmail and WhatsApp status sync. | MIT |
| [OfferOS](https://github.com/averatec0773/offeros) | A local app and Chrome side panel for after you apply: per-field form records, and an answer bank. | Apache-2.0 |
| [openroles](https://github.com/datascry/openroles) | A static job board over 51 ATSes (approximately 1.5M postings), rebuilt nightly, with its tenant lists in the repo. | MIT |
| [job-board-aggregator](https://github.com/Riley-Dorrington/job-board-aggregator) | The daily dataset that `aggregator.py` reads: seven ATSes, approximately 1.4M postings. | MIT |
| [amt](https://github.com/fabkho/amt) | A CLI and MCP server for German and EU job APIs, with a seen-ledger and profile suggestions from your cut reasons. | MIT |
| [mcp-job-search](https://github.com/michalper/mcp-job-search) | An MCP server with a configurable CV linter (banned phrases, required clauses). | MIT |
| [JobAppAgent](https://github.com/vaibhavarora14/job-application-agent), [Joku](https://github.com/wbohanw/joku) | Form-filling agents for Greenhouse, Lever, Ashby and Workday that stop before submit. | MIT / none stated |

## What they do better, and what we took

| Idea | Where | Status here |
|---|---|---|
| API-first liveness ladder: per-job ATS endpoints first, a browser only when the API cannot answer; Workday `403 S22` means withdrawn | career-ops `liveness-api.mjs` | **Taken**: `pipeline/liveness.py`. Tested on 10 real postings with open and closed controls. |
| A fact check on generated documents, in code | career-ops `verify-cv-facts`, Seekter `claims.mjs`, OfferOS quote checks | **Taken**: `resume/factcheck.py`, connected to the builder. |
| Per-source yield, and promotion or demotion of sources | idotsuk source registry, Seekter `stats --by` | **Taken**: `pipeline/runlog.py` and `runlog.py yield`. |
| freehire.me: a free API over many ATSes, with parsed requirements and ghost-posting signals | Seekter source notes | **Taken**: `pipeline/freehire.py`. |
| Many more ATS providers (iCIMS, Taleo, UKG, SuccessFactors, ADP, Paycom, BambooHR, Dayforce, Oracle HCM, Phenom, Eightfold, NEOGOV) | career-ops `providers/` | Not yet. freehire.me covers part of it. The career-ops providers are MIT and in Node; a port is the next step for wide ATS coverage. |
| Tenant lists: which employers use which ATS | openroles `data/tenants/`, Riley-Dorrington company lists | Not yet. Useful to resolve a warm-connection employer to its board. |
| Resolve a company list to scannable ATS boards with no tokens | career-ops `discover-ats.mjs` | Not yet. Here, the watchlists build themselves from notes. |
| Recently funded companies as a discovery lane | career-ops `company-funded.mjs` (TechCrunch, PR Newswire and HN feeds) | Not yet. |
| Calibrate scores against outcomes, continuously | career-ops `calibrate.mjs` | Partial: the 0.65 line was calibrated one time on 30 applications. A continuous check needs more outcomes than one search produces. |
| A golden set to test whether a cheaper model gives the same verdicts | career-ops `eval-golden.mjs` | Not yet. |
| An answer bank for screening questions | OfferOS | Not yet. freehire.me's `/apply-form` endpoint returns the questions before you open the form. |
| Repost and mass-posting detection as ghost-job signals | career-ops `detect-reposts.mjs`, freehire `reality` | Partial: freehire flags print on its rows; `workday.py` flags reposts as re-apply signals. |

## What this repo does that we did not find elsewhere

- All four gates in code, with a pay **band rule** (a range passes when the floor falls inside it), separate remote and office floors, and a home-metro pass on every lane.
- A verb-level fit scorecard that a script decides, calibrated on real outcomes.
- Unlisted pay that fails unless an inference from the employer's own posted bands is recorded (`comp-infer.py`).
- Workday board diffs with crawl bounds, server-side facet filters from a pasted board URL, and repost detection.
- A full-page posting image with a pay check as its positive control (`jd-snapshot.py`).
- Status-aware dedup with re-apply rules and cooldowns.
- Lane flags that make an interactive session run the lanes an unattended run could not reach.

## Data sources checked

- **freehire.me** (probe 2026-10-23): one remote US query for an analyst title gave 8,348 results; the top 100 came from 20 source systems; approximately 3 rows in 10 had a structured pay band.
- **openroles** (probe 2026-10-23): 1.53M rows, newest first in 77 chunks, approximately 20,000 new rows a day. Three days held 48 rows that matched an entry-level remote-US security search, mostly Ashby and Lever, and 1 of them had pay data. Not added as a lane: it mostly repeats `aggregator.py` and the ATS watchlists for that search. It can be worth a lane for searches in other fields.
