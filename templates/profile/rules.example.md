# My job-search rules

The skill reads this file at the start of every session and every scan. When a
rule here conflicts with the skill, the rule here wins. Copy to profile/rules.md
(gitignored). Delete the sections you do not need.

## Target

- Weekly goal: 10 applications. The week starts on Sunday.
- Level: entry and associate titles. "II" titles only when the JD asks for under 4 years.
- Out of field, never recommend: sales engineering, data analyst, help desk Tier 1.

## Hard disqualifiers (beyond profile.yaml)

- Employers that require employees to share a religion.
- "Remote" seats locked to a region or time zone outside mine.

## Warm-connection lane

Scan these employers' boards on every pass. A referral path is worth more than
cold volume. Workday boards: pin with `pipeline/workday.py --add "<url>" --warm`.

| Employer | Board URL | Contact and context | Gate exceptions |
|---|---|---|---|
| Example Co | https://example.wd1.myworkdayjobs.com/External | a former coworker, IT | hybrid in my metro is OK |

## Extra lanes

- (example) A paid-fellowship lane on the gate variant in the skill: any
  location, fixed term, floor X if remote and Y if it needs a move.

## Writing

- Voice for cover letters: direct, plain, specific. No comp in letters.
- Never name a gap in a letter unless it works around a knockout.
- Resume summary always opens with total years and years in the target field.

## Scan log

- Append each daily scan entry to: ~/JobSearch/Job Search Log.md
