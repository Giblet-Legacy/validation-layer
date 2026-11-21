"""
test_validate_v0_1.py — the validation engine on its own: neutral profile, privacy, verdicts, command line

Function:
    SPEC.md §2, §3 and §5. These need neither Node nor James's private
    page, so they run anywhere, including the VPS. Parity with the page
    is test_parity_v0_1.py.

Functions in this file (pytest-collected):
    1. test_method_is_the_frozen_checklist
    2. test_published_files_hold_no_guarded_words
    3. test_profile_is_never_committed
    4. test_extract_refuses_a_method_with_a_guarded_word
    5. test_neutral_profile_scores_the_synthetic_runs
    6. test_neutral_r9_guard_flags_restricted_material
    7. test_verdict_needs
    8. test_cli_text_json_and_bad_file

Tier:     P19 Validation, 0.1.0
Spec:     SPEC.md 0.1.0
Version:  0.1.0-dev
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import json
import pathlib
import re
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
import validate_v0_1 as v  # noqa: E402

M = v.load_method()
NEUTRAL = v.load_profile(LAYER / "profile_neutral_v2_2.json")
# Words that must never be in a file this layer publishes. Everywhere: two generic markers, so this
# public test names nothing of anyone's. On James's laptop: also his real R9 guard words, read from
# his private profile, never written here.
FORBIDDEN = re.compile(r"\b(clearance|official[- ]sensitive)\b", re.I)
_PRIVATE = pathlib.Path.home() / ".forge" / "validation" / "profile_v2_2.json"
GUARD = v._jsre(json.loads(_PRIVATE.read_text(encoding="utf-8"))["R9_RE"]) if _PRIVATE.exists() else None


def _run(name):
    return runs_v0_1.runs(M)[name]


# 1.
def test_method_is_the_frozen_checklist():
    assert M["VERSION"] == "2.2.0"
    assert len(M["QS"]) == 32 and len(M["QUICK"]) == 10
    assert sum(M["VIA"]["w"].values()) == 100
    assert set(M["FCODES"]) == {f"F{i}" for i in range(1, 10)}


# 2.
def test_published_files_hold_no_guarded_words():
    out = subprocess.run(["git", "ls-files"], cwd=LAYER, capture_output=True, text=True).stdout.split()
    files = out or [str(p.relative_to(LAYER)) for p in LAYER.rglob("*") if p.is_file() and ".git" not in p.parts]
    for f in files:
        if f.endswith(".py") and "test_validate" in f:
            continue  # this file names the markers it forbids
        p = LAYER / f
        if p.suffix in (".py", ".json", ".md", ".js", ".txt", ".ini", ""):
            text = p.read_text(encoding="utf-8", errors="replace")
            own = "profile_neutral" in f or "runs_v0_1" in f  # the neutral guard and its test runs hold generic words
            hit = FORBIDDEN.search(text) or (GUARD.search(text) if GUARD and not own else None)
            assert not hit, f"{f} holds {hit.group(0)!r}"


# 3.
def test_profile_is_never_committed():
    ignore = (LAYER / ".gitignore").read_text(encoding="utf-8")
    assert "profile_v*.json" in ignore
    tracked = subprocess.run(["git", "ls-files"], cwd=LAYER, capture_output=True, text=True).stdout.split()
    assert not [f for f in tracked if re.match(r"profile_v\d", pathlib.Path(f).name)]


# 4.
def test_extract_refuses_a_method_with_a_guarded_word():
    data = {**{k: M[k] for k in extract_v0_1.METHOD_KEYS}, **{k: NEUTRAL[k] for k in extract_v0_1.PROFILE_KEYS}}
    data["QS"] = json.loads(json.dumps(M["QS"]))
    data["QS"][0]["q"] += " Keep confidential notes out."
    with pytest.raises(ValueError, match="guarded word"):
        extract_v0_1.split(data)
    data["QS"] = M["QS"]
    method, profile = extract_v0_1.split(data)
    assert "RULES" not in method and "QS" not in profile


# 5.
def test_neutral_profile_scores_the_synthetic_runs():
    rich = v.evaluate(_run("rich-full"), profile=NEUTRAL)
    assert rich["viability"]["score"] >= 80 and not rich["jflags"]
    no_ext = v.evaluate(_run("rich-no-external"), profile=NEUTRAL)["viability"]
    assert no_ext["cap"] == 65 and no_ext["score"] == 65 and "Nobody outside you" in no_ext["capWhy"]
    blank = v.evaluate(_run("blank-full"), profile=NEUTRAL)
    assert blank["viability"]["score"] == 0 and {f["code"] for f in blank["jflags"]} == {"F2", "F4", "INV"}
    quick = v.evaluate(_run("quick-severe"), profile=NEUTRAL)
    assert "QUICK" in {f["code"] for f in quick["jflags"]} and quick["active"] == M["QUICK"]


# 6.
def test_neutral_r9_guard_flags_restricted_material():
    flags = {f["code"] for f in v.evaluate(_run("checks-galore"), profile=NEUTRAL)["jflags"]}
    assert "R9" in flags  # "classified notes" in DATA & COMPLIANCE
    assert "R9" not in {f["code"] for f in v.evaluate(_run("rich-full"), profile=NEUTRAL)["jflags"]}


# 7.
def test_verdict_needs():
    r = _run("rich-full")
    assert v.verdict_needs(r, profile=NEUTRAL) == ["No verdict: BUILD, PARK or KILL."]
    r["verdict"].update(v="build", slice="the engine", date="2026-12-21")
    assert v.verdict_needs(r, profile=NEUTRAL) == []
    b = _run("blank-full")
    b["verdict"]["v"] = "build"
    assert len(v.verdict_needs(b, profile=NEUTRAL)) == 2
    b["verdict"].update(v="park", trigger="after 3 runs")
    assert v.verdict_needs(b, profile=NEUTRAL) == ["PARK needs a revisit trigger and what would have to change."]
    b["verdict"].update(v="kill", reason="no need underneath")
    assert v.verdict_needs(b, profile=NEUTRAL) == []


# 8.
def test_cli_text_json_and_bad_file(tmp_path):
    good = tmp_path / "run.json"
    good.write_text(json.dumps(_run("rich-full")), encoding="utf-8")
    prof = str(LAYER / "profile_neutral_v2_2.json")
    t = subprocess.run([sys.executable, str(LAYER / "validate_v0_1.py"), str(good), "--profile", prof],
                       capture_output=True, text=True, encoding="utf-8")
    assert t.returncode == 0 and t.stdout.startswith("Viability: ") and "== JAMES FLAGS ==" in t.stdout
    j = subprocess.run([sys.executable, str(LAYER / "validate_v0_1.py"), str(good), "--profile", prof, "--json"],
                       capture_output=True, text=True, encoding="utf-8")
    assert json.loads(j.stdout)["viability"]["band"] == "Strong"
    bad = tmp_path / "bad.json"
    bad.write_text('{"answers": "nope"}', encoding="utf-8")
    b = subprocess.run([sys.executable, str(LAYER / "validate_v0_1.py"), str(bad), "--profile", prof],
                       capture_output=True, text=True, encoding="utf-8")
    assert b.returncode == 2 and "not a run file" in b.stderr
