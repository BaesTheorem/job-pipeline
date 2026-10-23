"""Compensation floors for the lanes. A thin shim over jobprofile.py.

    comp_floor()     remote / standard-lane floor, annual USD (comp.remote_floor)
    onsite_floor()   floor for any seat with an office requirement (comp.onsite_floor)

The environment variables JOB_COMP_FLOOR and JOB_ONSITE_FLOOR override the
profile; the test suite uses them. There is no numeric default, so a fresh
clone fails loudly instead of gating on somebody else's number.
"""

from __future__ import annotations

from jobprofile import ProfileError as FloorConfigError  # noqa: F401  (old name, kept for callers)
from jobprofile import comp_floor, onsite_floor  # noqa: F401
