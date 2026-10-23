# resume

`build.py` makes resume and cover-letter PDFs from one JSON file of your real resume content. Each application gets a small tailoring file with surgical changes only. `factcheck.py` checks each tailoring file or letter against your data before the PDF is made.

## Set up

```bash
cp data/resume_data.example.json data/resume_data.json   # then fill it in
uv run --with playwright python -m playwright install chromium
brew install qpdf                                         # or apt install qpdf
```

`data/resume_data.json`, `data/facts.md` and every file in `tailoring/` except the two examples are gitignored.

## Make a PDF

```bash
# canonical resume -> ~/Downloads/First_Last_Resume.pdf
python3 resume/build.py resume

# tailored resume, fact-checked against the JD first
python3 resume/build.py resume --tailor resume/tailoring/acme.json \
    --jd jd.txt --role "GRC Analyst" \
    --out "<listing folder>/First_Last_Resume_ACME.pdf"

# cover letter (markdown from the date line down; the letterhead is automatic)
python3 resume/build.py cover --md resume/tailoring/acme_cover.md \
    --company "Acme Corp" --tag ACME --jd jd.txt --role "GRC Analyst"
```

The builder:

- prints real, selectable, single-column text with standard headings
- replaces the headless-Chrome PDF metadata with a normal word-processor set, and removes the XMP packet
- names the file `First_Last_Resume[_Tag].pdf`
- stops when a resume is more than 2 pages or a letter is more than 1 page

End the letter with your name only. The letterhead already has your contact line, so a contact line in the signature prints it two times.

## Tailoring file (`tailoring/<company>.json`, all keys optional)

```json
{
  "tag": "ACME",
  "summary": "role-tailored summary",
  "skills_append": { "Security": "Additional focus on <truthful ATS keywords>." },
  "experience_bullets": { "job1": ["reordered or reworded bullet", "..."] },
  "title_suffix": { "job1": " (contract ended)" },
  "leadership_include": ["volunteer_org"]
}
```

- Job ids are the `id` fields in `data/resume_data.json`.
- `leadership_include` shows an entry marked `"optional": true`. It adds nothing new.
- `title_suffix` is for true context only, for example why a role ended, and only when the form has no cover-letter field.
- Do not add a skill, tool or certification that your data does not support. Do not change titles, dates or employers.

## Fact check

`factcheck.py` compares the text with `data/resume_data.json`, the optional fact bank `data/facts.md`, and the JD:

| Finding | Meaning | Effect |
| --- | --- | --- |
| NUMBER | a figure that is in neither your data nor the JD | stops the build |
| CLAIMED | an acronym or product name from the JD that your data never mentions | review list (`--strict` stops the build) |
| UNSOURCED | another term your data does not mention | warning |
| STYLE | an em dash, or a phrase from `writing.banned` in `profile.yaml` | warning |

Put true facts that are not on every resume (an exam code, a tool you used once, a number you can prove) in `data/facts.md`. Then the check accepts them.

On five real letters, the check found two figures that were in the letter but not in the data, and approximately three JD acronyms for each letter to review. A clean result does not prove that the text is true. Read every document before you send it.

## What the builder does not do

The prose is your work. Read each summary, bullet and letter for invented claims and for text that sounds generated.
