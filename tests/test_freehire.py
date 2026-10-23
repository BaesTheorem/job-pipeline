"""Gates in pipeline/freehire.py, on planted rows shaped like the API's."""

from conftest import load_script

fh = load_script("pipeline/freehire.py")
FLOOR, ONSITE = 50000, 60000


def row(**kw):
    base = {"title": "Security Analyst", "location": "United States", "work_mode": "remote",
            "countries": ["us"], "closed_at": None,
            "enrichment": {"employment_type": "full_time", "salary_min": 70000, "salary_max": 90000,
                           "salary_period": "year", "salary_currency": "USD"},
            "reality": {"repost_count": 1, "mass_posting_count": 1, "fake_freshness": False}}
    base.update(kw)
    return base


def test_remote_band_passes():
    assert fh.gate(row(), FLOOR, ONSITE)[0] == "survivor"


def test_band_rule_straddle_and_top_under_floor():
    e = dict(row()["enrichment"], salary_min=40000, salary_max=55000)
    bucket, why = fh.gate(row(enrichment=e), FLOOR, ONSITE)
    assert bucket == "survivor" and "BAND-STRADDLE" in why
    e = dict(e, salary_max=45000)
    assert fh.gate(row(enrichment=e), FLOOR, ONSITE)[0] == "decline"


def test_hourly_is_annualized():
    e = dict(row()["enrichment"], salary_min=30, salary_max=40, salary_period="hour")
    assert fh.gate(row(enrichment=e), FLOOR, ONSITE)[0] == "survivor"  # 40 x 2080 = 83,200


def test_unlisted_pay_is_a_lead():
    e = {"employment_type": "full_time"}
    assert fh.gate(row(enrichment=e), FLOOR, ONSITE)[0] == "lead"


def test_onsite_outside_metro_declines_and_inside_uses_onsite_floor():
    assert fh.gate(row(work_mode="onsite", location="Denver, CO"), FLOOR, ONSITE)[0] == "decline"
    bucket, why = fh.gate(row(work_mode="hybrid", location="Lenexa, KS"), FLOOR, ONSITE)
    assert bucket == "survivor" and "onsite floor" in why


def test_title_closed_contract_and_years():
    assert fh.gate(row(title="Senior Security Analyst"), FLOOR, ONSITE)[0] == "drop"
    assert fh.gate(row(closed_at="2026-10-01"), FLOOR, ONSITE)[0] == "drop"
    assert fh.gate(row(title="Seasonal Security Analyst I"), FLOOR, ONSITE)[0] == "decline"
    e = dict(row()["enrichment"], employment_type="contract")
    assert fh.gate(row(enrichment=e), FLOOR, ONSITE)[0] == "decline"
    e = dict(row()["enrichment"], experience_years_min=12)
    assert fh.gate(row(enrichment=e), FLOOR, ONSITE)[0] == "decline"


def test_reality_flags():
    r = row(reality={"repost_count": 3, "mass_posting_count": 5, "fake_freshness": True})
    flags = fh.reality_flags(r)
    assert "MASS-POSTED x5" in flags and "FAKE-FRESH" in flags and "REPOSTED x3" in flags
    assert fh.reality_flags(row()) == ""


def test_required_lines():
    e = {"requirements": [{"text": "SOC 2 audits", "priority": "required"},
                          {"text": "Python", "priority": "preferred"}]}
    assert fh.required_lines(row(enrichment=e)) == ["SOC 2 audits"]
