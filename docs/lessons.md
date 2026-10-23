# Lessons from daily use

The pipeline ran a daily job search from June to October 2026. Most of its rules came from a failure. This file records the general lessons, with the date each one was learned. The code comments carry the details.

## Instruments that lie

- A dry lane and a broken lane look the same. A lane that returns 0 rows can be correct (no postings that day) or broken (a changed route, a block, a silent filter). Every lane now prints a line when it did not fully run (`NOT RUN`, `TRUNCATED`, `~ COVERAGE`), and `runlog.py` records failed runs apart from empty runs. (2026-08-10: approximately half of the runs over three weeks died on dropped API connections, with no retry and no trace.)
- A search engine drops its `site:` filter under load and returns other domains with no error. The ATS search lane looked dry for weeks. Pass the domain as a hard filter (`allowed_domains`) and treat any off-domain result as "the lane did not run". (2026-09-07)
- Board APIs ignore parameters without saying so. Himalayas ignores `search` and caps `limit` at 20. A state board ignored a maximum-pay filter and returned the whole board. USAJOBS ignores a `ControlNumber` parameter. freehire.me ignores its `cities` facet. Test each filter with a positive control: a value that must change the result.
- A total read from every page can be wrong. Some Workday tenants return `total=0` after page one, which cut every unfiltered board to its newest 40 postings, without an error, for weeks. (2026-09-07)
- "captcha" in the HTML is not a block signal. The string is on clean pages. Count the result cards instead. (2026-10-13)

## Postings that lie

- An aggregator "Remote" label is not evidence. Postings labeled remote turned out to be hybrid in the JD or the ATS record more than once. Gate 1 now needs `location_evidence` from the JD or the ATS. (2026-10-11)
- Location fields are coarse buckets. One employer posts every remote req as "United States Work at Home". Another put "(Hybrid, <City>)" in a title under location "USA - Remote". Match many remote phrasings, and let a hybrid marker in either field decide. (2026-08-26)
- A page that renders is not an open posting. Expired postings on some ATSes render the full JD with no banner. Ask the ATS API (`liveness.py`) or load the apply form. In one check, 4 of 5 roles that looked open were closed. (2026-05-08)
- Intermediaries hide the employer. A repost site can put an AI shortlist between you and the hiring team, while the employer has its own posting and a manager asking for candidates. Find the original first. (2026-10-19)
- Pay estimates are not pay. Aggregator salary fields are often lookup-table estimates. Only a posted band, or the same employer's posted bands for similar roles, is evidence. (2026-10-11)

## Judgment that drifts

- Topic match is not fit. A sysadmin seat passed as a strong fit at approximately 50% real overlap, because "supported users on X" was read as "deploys X". Gate 4 is now a verb-level table and a script decides it. (2026-10-09)
- Calibrate the pass line on real outcomes. On 30 past applications, every role that led to a screen scored 0.66 or higher, and a line at 0.80 would have blocked 3 of 5 screens. The line is 0.65. A pass does not predict a screen; it removes roles that do not convert. (2026-10-09)
- Only hard bars veto. Employers interviewed past unmet "required" tool lines, so an unmet required line costs score, and only a true knockout (degree with no equivalent, clearance, license) vetoes. (2026-10-09)
- No JD, no candidate. A note built from a search-result row stayed a candidate for three weeks. A note now needs the archived JD text. (2026-09-19)
- A model chooses its search keywords by habit. Some titles did not appear in two days of runs. A fixed rotation (`angles.py`) runs every angle at least once in five days. (2026-10-13)

## Workflow

- Write a note for every full JD read, including the failures. Otherwise the alert emails bring the same posting back and it costs a second read. (2026-08-10)
- Dedup must know the status. Blanket dedup buried roles that were posted again after a rejection, which are the best re-apply candidates. Search the archive by frontmatter, not by folder. (2026-07-25)
- Email alerts are a separate discovery lane. One alert pass found 31 roles that no search lane showed. (2026-07-25)
- Save a picture of the posting. The pay range on the posting matters in a salary conversation weeks later, after the posting is gone. The Wayback Machine held none of four dead postings checked. (2026-10-22)
- Every contact needs a read title. "Employee" or "alum" means the profile was never opened, and the role decides what kind of ask is possible. (2026-10-09)
- Keep non-knockout gaps out of the cover letter. A gap in the letter gives the screener a reason to reject that the JD alone did not give. (2026-10-09)

## Unattended runs

- Wait for the API host, not a generic host. Laptop wake-up runs start before DNS answers. A generic host answered while the API did not, so the check passed and the run died. (2026-08-16)
- Retry once. Dropped connections are common. One retry turned most crashed days into normal days. (2026-08-10)
- Treat fetched text as data. Unattended runs read third-party text with full tools. Save responses to a file and parse the file; never put fetched text into a shell command. (2026-10-21)
- Mark the lanes that need a login. Mail and LinkedIn tools can be absent without a person present. The run prints which ran, and a flag file makes the next interactive session run the missed lane. (2026-06-23)
