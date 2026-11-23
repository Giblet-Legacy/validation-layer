"""
conftest.py — keep each version's parity tests on the page version they port

Function:
    test_parity_v0_1.py (frozen, 0.1.0) ports checklist 2.2.0 and reads its
    page from VALIDATION_PAGE, else the live page. Once the live page moved
    to 2.3.0, that would test 0.1.0 against the wrong page. So, before any
    test module is imported, VALIDATION_PAGE is pointed at the archived 2.2.0
    page when it exists and the variable isn't already set. 0.1.1's parity
    test reads VALIDATION_PAGE_V2_3, else the live page. No frozen file is
    edited.

Tier:     P19 Validation, 0.1.1
Spec:     SPEC_V0_1_1.md 0.1.1
Version:  0.1.1 (frozen 2026-11-23)
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import os
import pathlib

_FOLDER = pathlib.Path.home() / "Documents" / "architectursl thinking"
_ARCHIVED_2_2 = _FOLDER / "archive" / "2.2.0" / "james-checklist.html"
if "VALIDATION_PAGE" not in os.environ and _ARCHIVED_2_2.exists():
    os.environ["VALIDATION_PAGE"] = str(_ARCHIVED_2_2)
