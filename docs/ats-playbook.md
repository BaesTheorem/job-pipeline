# ATS and AI-screening playbook

This is a summary of a research pass from June 2026 (two research agents, with cited sources), checked again in August 2026. Its purpose is to separate the real causes of rejection from the feared ones, and to put the inexpensive defenses into `resume/build.py`.

> Source quality: most sources about resumes and AI detectors are vendors with a reason to sound sure. The structural ATS rules, the PDF-engine fingerprints and the "no native AI detection" finding have good support. The exact percentages below are weak, and they are marked as uncertain.

## Main finding

We found no mainstream ATS (Workday, Greenhouse, iCIMS, Taleo, Lever, Ashby, SuccessFactors) with a native "is this AI-written" detector. Their AI does candidate matching and ranking. The real causes of rejection are:

1. **A file the parser cannot read**: a silent auto-fail, and the most common real cause.
2. **Application speed and automation**: platforms lock accounts for it, and this is the most consistent enforcement.
3. **Hidden text and keyword stuffing**: parsers strip color, so screeners see the text. Reported prevalence is approximately 1 to 10% (uncertain).
4. **A person's quick read of generic prose**: the main way that AI-written text is caught, and a classifier is not part of it.

AI text detectors exist, and some sell to recruiters. Few employers connect them, and their precision is poor in published tests (uncertain figures; high false-positive rates on non-native English).

## What the builder does

- Real, selectable, single-column text, checked by extraction. Never an image or a flattened export.
- A filename like `First_Last_Resume.pdf`.
- Metadata like a word processor: author and title set, a normal producer string, empty subject and keywords, the XMP packet removed, and a full rewrite with `qpdf --linearize`. A headless-Chrome print says `Skia/PDF` and `HeadlessChrome`. We found no evidence that an ATS checks this today, but the fix costs nothing. Do not ship `wkhtmltopdf`, `WeasyPrint`, `ReportLab` or `pdfTeX` producer strings, or empty metadata.
- At most 2 pages for a resume and 1 for a letter.

## Layout

- Single column, reverse chronological, standard headings (Professional Summary, Technical Skills, Professional Experience, Education and Certifications).
- Contact information in the body text, not in a header or footer (parsers miss headers and footers often).
- Standard fonts at 10 to 12 pt. No tables, columns, text boxes, graphics, icons or skill bars. Consistent date formats.
- Send DOCX only when the posting asks, or for older parsers (Taleo, some iCIMS, SuccessFactors) that drop content silently.

## Keywords

Use the JD's exact words only for skills you have, in context, inside accomplishment bullets. Do not repeat words for density. Never use hidden or white text, and never put instructions for a model in a resume: both are detected and count against you.

## Language

- Vary sentence length. Use named, specific details and real numbers.
- Leave out stock phrases ("I am writing to express my interest", "proven track record") and stock AI words (delve, leverage, utilize, robust, seamless, showcase, pivotal).
- Personalize every letter with details about the company and the role. Surveys report that most hiring managers reject generic AI output and accept personalized AI-assisted output (uncertain figures).

## Behavior

Apply at a human pace. Do not use auto-apply bots. LinkedIn and Indeed lock accounts for automation, and that enforcement is well documented.

## Claims checked and rejected (August 2026)

- **"Keep white-text keywords as a fallback."** Rejected for the reasons above.
- **"A 2026 study of 197,000 resumes found that 80% of keyword injections manipulate early filtering."** No author, no venue, and a malformed statistic. Zero evidence; do not cite it.

What we kept from the same source: the scorecard simulation in the skill. Predict the screener's rubric (details, qualifications, skills, traits), and mark each JD line as a knockout or a nice-to-have before you tailor. The four categories are a heuristic, not a known vendor rubric.

## Hold loosely

- ATS checks of PDF producer strings: no evidence today.
- Keyword indexing of filenames: possible, not shown.
- Cross-applicant fingerprinting of cover letters: feared, not a shipped feature. ATS dedup works on identity (email, phone).
- The real change in 2025 and 2026 is screening and ranking by language models, and more live interviews, because text detection does not work.
