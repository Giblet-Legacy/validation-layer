"""
test_validate_v0_1_1.py — 0.1.1: a red team's findings must be decided before they lift the score

Function:
    SPEC_V0_1_1.md. The engine against checklist 2.3.0. Everywhere: the
    method is 2.3.0, the undecided cap, and the red-team item's three states.
    On James's laptop (the private page and Node): parity with the 2.3.0 page
    on every synthetic run, the red-team states and the three real runs.

Functions in this file (pytest-collected):
    1. test_method_is_checklist_2_3
    2. test_red_team_states
    3. test_decided_review_lifts_the_cap
    4. test_engine_matches_the_2_3_page (one per run; laptop only)
    5. test_committed_2_3_method_matches_the_page (laptop only)

Helpers:
    6. _with_rt — a synthetic run with a given RED TEAM answer

Tier:     P19 Validation, 0.1.1
Spec:     SPEC_V0_1_1.md 0.1.1
Version:  0.1.1 (frozen 2026-11-23)
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
import validate_v0_1_1 as v  # noqa: E402

M = v.load_method()
NEUTRAL = v.load_profile(LAYER / "profile_neutral_v2_3.json")
PAGE = pathlib.Path(os.environ.get("VALIDATION_PAGE_V2_3") or
                    pathlib.Path.home() / "Documents" / "architectursl thinking" / "james-checklist.html")
on_laptop = pytest.mark.skipif(not PAGE.exists() or shutil.which("node") is None,
                               reason="needs James's private checklist page (2.3.0) and Node")
UNDECIDED = {"reviewer": "A fresh reviewer", "found": "The witness is not independent.", "changing": "", "rejected": ""}
DECIDED = dict(UNDECIDED, changing="Three witnesses.")


# 6. _with_rt
def _with_rt(rt, base="rich-full"):
    run = runs_v0_1.runs(M)[base]
    run["answers"][run["keys"].index("RED TEAM")] = dict(rt)
    return run


# 1.
def test_method_is_checklist_2_3():
    assert M["VERSION"].startswith("2.3.0")
    assert M["VIA"]["caps"]["undecided"] == 65
    assert {k: M["VIA"]["caps"][k] for k in ("noWhy", "screen3", "noExternal")} == {"noWhy": 30, "screen3": 40, "noExternal": 65}


# 2.
def test_red_team_states():
    def rt_item(run):
        return next(x for x in v.evaluate(run, profile=NEUTRAL)["viability"]["items"] if x["key"] == "redteam")
    empty = {"reviewer": "", "found": "", "changing": "", "rejected": ""}
    assert rt_item(_with_rt(empty))["got"] == 0
    assert rt_item(_with_rt(UNDECIDED))["got"] == M["VIA"]["w"]["redteam"] * 0.5
    assert rt_item(_with_rt(DECIDED))["got"] == M["VIA"]["w"]["redteam"]


# 3.
def test_decided_review_lifts_the_cap():
    undecided = v.evaluate(_with_rt(UNDECIDED), profile=NEUTRAL)["viability"]
    assert undecided["score"] == 65 and "haven't decided" in undecided["capWhy"]
    decided = v.evaluate(_with_rt(DECIDED), profile=NEUTRAL)["viability"]
    assert decided["score"] > 65 and not decided["capWhy"]


def _runs():
    R = dict(runs_v0_1.runs(M))
    R["rt-undecided"] = _with_rt(UNDECIDED)
    R["rt-decided"] = _with_rt(DECIDED)
    R["rt-undecided-no-external"] = _with_rt(UNDECIDED, "rich-no-external")
    for f in sorted((LAYER / "runs").glob("*.run.json")):
        R["real-" + f.name[:4]] = json.loads(f.read_text(encoding="utf-8"))
    return R


@pytest.fixture(scope="module")
def page():
    return extract_v0_1.split(extract_v0_1.page_data(PAGE))


def _page_score(run):
    r = subprocess.run(["node", str(LAYER / "tools" / "page_harness_v0_1.js"), str(PAGE)],
                       input=json.dumps({"cmd": "score", "run": run}), capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


# 4.
@on_laptop
@pytest.mark.parametrize("name", sorted(_runs()))
def test_engine_matches_the_2_3_page(page, name):
    from test_parity_v0_1 import _same
    method, profile = page
    run = _runs()[name]
    _same(_page_score(run), json.loads(json.dumps(v.evaluate(run, json.loads(json.dumps(method)), profile))), name)


# 5.
@on_laptop
def test_committed_2_3_method_matches_the_page(page):
    method, _ = page
    committed = v.load_method()
    committed.pop("generated", None)
    assert committed == method, "method_v2_3.json differs from the page: run tools/extract_v0_1.py"
