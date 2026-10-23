"""The profile is the only home of personal values; floors and filters come from it."""

import pytest
from conftest import SYNTHETIC_ENV, load_script

P = load_script("pipeline/jobprofile.py")
cf = load_script("pipeline/comp_floors.py")


def test_env_overrides_profile_floor(monkeypatch):
    assert cf.comp_floor() == int(SYNTHETIC_ENV["JOB_COMP_FLOOR"])
    monkeypatch.setenv("JOB_COMP_FLOOR", "12,345")
    assert P.comp_floor() == 12345


def test_profile_floor_when_env_unset(monkeypatch):
    monkeypatch.delenv("JOB_ONSITE_FLOOR", raising=False)
    assert P.onsite_floor() == P.get("comp.onsite_floor")


def test_non_numeric_floor_raises(monkeypatch):
    monkeypatch.setenv("JOB_COMP_FLOOR", "lots")
    with pytest.raises(P.ProfileError):
        P.comp_floor()


def test_missing_required_key_names_it():
    with pytest.raises(P.ProfileError, match="nope.missing"):
        P.get("nope.missing")


def test_title_filters_are_word_bounded():
    keep, drop = P.title_re("keep"), P.title_re("drop")
    assert keep.search("IT Security Analyst I")
    assert drop.search("Sr. Security Analyst") and drop.search("Senior Analyst")
    assert not drop.search("Leadership Analyst")  # "lead" must not match inside a word


def test_off_lane_catches_other_fields():
    assert P.off_lane_re().search("Financial Planning Analyst")
    assert not P.off_lane_re().search("Information Security Analyst")


def test_metro_and_local_passes():
    assert P.metro_re().search("Overland Park, KS - Corporate")
    assert P.with_local("remote", lambda: "local") == ["remote", "local"]


def test_remote_only_profile_skips_local(monkeypatch):
    monkeypatch.setattr(P, "has_metro", lambda: False)
    assert P.with_local("remote", lambda: 1 / 0) == ["remote"]  # local pass never evaluated
