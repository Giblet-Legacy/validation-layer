"""
test_parity_v0_1.py — the engine agrees with the checklist page, run by run

Function:
    SPEC.md §4. The page (James's james-checklist.html) is the source of
    truth; validate_v0_1.py is a port. This runs every synthetic run
    through both and requires the same result:

      - the page's own script under Node (tools/page_harness_v0_1.js);
      - the Python engine, given the method and profile extracted from
        the same page.

    It also checks that the committed method_v2_2.json is still what the
    page holds (drift).

    The page is private, so these tests run only where it is: on James's
    laptop, at VALIDATION_PAGE, or by default at
    ~/Documents/architectursl thinking/james-checklist.html, and with
    Node installed. Elsewhere (the VPS) they are skipped, and they say
    so.

Functions in this file (pytest-collected):
    1. test_committed_method_matches_the_page
    2. test_engine_matches_the_page (one per synthetic run)

Tier:     P19 Validation, 0.1.0
Spec:     SPEC.md 0.1.0
Version:  0.1.0-dev
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import json
import os
import pathlib
import shutil
import subprocess
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
LAYER = HERE.parent
sys.path.insert(0, str(LAYER))
sys.path.insert(0, str(LAYER / "tools"))
sys.path.insert(0, str(HERE))

import extract_v0_1  # noqa: E402
import runs_v0_1  # noqa: E402
import validate_v0_1  # noqa: E402

PAGE = pathlib.Path(os.environ.get("VALIDATION_PAGE") or
                    pathlib.Path.home() / "Documents" / "architectursl thinking" / "james-checklist.html")
pytestmark = pytest.mark.skipif(not PAGE.exists() or shutil.which("node") is None,
                                reason="needs James's private checklist page and Node (parity runs on the laptop only)")


@pytest.fixture(scope="module")
def page():
    method, profile = extract_v0_1.split(extract_v0_1.page_data(PAGE))
    return method, profile


def _page_score(run):
    r = subprocess.run(["node", str(LAYER / "tools" / "page_harness_v0_1.js"), str(PAGE)],
                       input=json.dumps({"cmd": "score", "run": run}), capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def _same(a, b, path="result"):
    """Equal, with floats compared to 1e-9 (both sides do the same float sums)."""
    if isinstance(a, float) or isinstance(b, float):
        assert abs(float(a) - float(b)) < 1e-9, f"{path}: page {a!r} != engine {b!r}"
    elif isinstance(a, dict):
        assert set(a) == set(b), f"{path}: keys differ {sorted(set(a) ^ set(b))}"
        for k in a:
            _same(a[k], b[k], f"{path}.{k}")
    elif isinstance(a, list):
        assert len(a) == len(b), f"{path}: page has {len(a)}, engine {len(b)}: {a!r} vs {b!r}"
        for i, (x, y) in enumerate(zip(a, b)):
            _same(x, y, f"{path}[{i}]")
    else:
        assert a == b, f"{path}: page {a!r} != engine {b!r}"


# 1.
def test_committed_method_matches_the_page(page):
    method, _ = page
    committed = validate_v0_1.load_method()
    committed.pop("generated", None)
    assert committed == method, "method_v2_2.json differs from the page: run tools/extract_v0_1.py"


# 2.
@pytest.mark.parametrize("name", sorted(runs_v0_1.runs(validate_v0_1.load_method())))
def test_engine_matches_the_page(page, name):
    method, profile = page
    run = runs_v0_1.runs(method)[name]
    want = _page_score(run)
    got = validate_v0_1.evaluate(run, json.loads(json.dumps(method)), profile)
    _same(want, json.loads(json.dumps(got)), name)
