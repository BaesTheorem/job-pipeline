"""resume/factcheck.py: numbers block, JD acronyms are a review list."""

from conftest import load_script

fc = load_script("resume/factcheck.py")
SOURCES = "IT Analyst. Supported 400 users across 3 offices. Microsoft Intune, Entra ID. Cut ticket backlog 30%."
JD = "We need SOC 2 and ISO 27001 experience. Team of 12. Splunk preferred."


def kinds(text, ok=frozenset()):
    return {(k, w) for k, w in fc.check(text, SOURCES, JD, set(ok))}


def test_sourced_numbers_pass_and_invented_ones_block():
    assert ("NUMBER", "400") not in kinds("I supported 400 users.")
    assert ("NUMBER", "12") not in kinds("Your team of 12 matches my experience.")  # stated in the JD
    assert ("NUMBER", "73") in kinds("I cut incidents 73%.")


def test_years_are_not_claims():
    assert not any(k == "NUMBER" for k, _ in kinds("In 2024 I moved teams."))


def test_jd_acronym_without_source_is_claimed():
    found = kinds("I ran SOC 2 evidence collection with Intune data.")
    assert ("CLAIMED", "SOC") in found
    assert not any(w == "Intune" for _, w in found)


def test_greeting_company_and_roman_numerals_skipped():
    found = kinds("Dear Acme Hiring Team,\nThe Analyst II role at Acme fits.", ok={"acme"})
    assert not any(w in ("Acme", "II", "Dear Acme Hiring Team") for _, w in found)


def test_em_dash_is_style():
    assert ("STYLE", "em dash") in kinds("I fixed it — fast.")
