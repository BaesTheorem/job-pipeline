# The fit scorecard (gate 4)

A paragraph that explains why a role fits is easy to write and hard to check. The scorecard turns gate 4 into a table and a number that `pipeline/fit-gate.py` computes.

## The two inputs

1. **Your capability table** (`profile/capabilities.md`): one row per area of your work, with the highest true level from Own/Build > Administer > Operate > Support > Exposure > None. Start from `templates/profile/capabilities.example.md`.
2. **The scorecard on each listing note**: one row per JD line, with the level the JD's verb asks for, your level from the table, and a verdict.

```
## Fit scorecard
| # | JD line | Kind | Asks | Me | Verdict | Evidence |
|---|---|---|---|---|---|---|
| 1 | "Administer MDM compliance policies" | core | Administer | Administer | Met | Boundaries: endpoint management |
| 2 | "Deploy virtual desktop environments" | core | Own/Build | Support | Unmet | Boundaries: virtual desktop |
| 3 | "Bachelor's degree or equivalent experience" | required | n/a | n/a | Met | 6 years in the field |
```

## The rules

- **The verb sets the ask.** deploy, build, architect, design ask Own/Build. configure, manage, maintain, administer ask Administer. use, operate, run, perform ask Operate. support users on, troubleshoot for users ask Support. familiarity, knowledge, exposure ask Exposure. A softener (assist, participate in, help with) lowers the ask by one level.
- **A lower level is never Met.** `fit-gate.py` rejects a Met row whose "Me" level is under its "Asks" level.
- **Kinds:** `knockout` (a bar that cannot be waived: a degree with no equivalent clause, citizenship, clearance, a license), `required` (any stated qualification), `core` (a primary duty), `preferred` (not scored).
- **Score** = (Met + 0.5 x Partial) / (knockout + required + core rows). The note fails on any unmet knockout or a score under the pass line. Fewer than 5 scored rows is INCOMPLETE.

## Calibrate the pass line

The default line is 0.65. It came from a blind calibration on 30 past applications from one search: every role that led to a screen scored 0.66 or higher, and a line at 0.80 would have blocked 3 of the 5 screens.

Do the same with your own history when you have it:

1. Take 20 or more past applications with known outcomes (screen or no screen).
2. Score each one with the scorecard, without looking at the outcome.
3. Find the highest line that keeps all, or almost all, of the screens. Set it as `fit.threshold` in `profile.yaml`.

The line removes roles that do not convert. A pass does not predict a screen.

## Overrides

When you want to apply to a role that failed, record why: `fit_override: "<reason>"` in the frontmatter. The script then reports OVERRIDE, and the tracker shows the exception.
