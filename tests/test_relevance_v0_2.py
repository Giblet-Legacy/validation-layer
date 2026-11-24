"""
test_relevance_v0_2.py — tests for relevance_v0_2.py (P19 0.2.0 first slice), on a synthetic workspace

Function:
    Builds a throwaway workspace in tmp_path with one repository per kind
    of wiring the stack uses, and checks the graph, the evidence, λ and
    the readings. Leighton V3 is the real one, copied from the sibling
    layers, so λ is P14's own. No private material, no network.

    1. test_each_kind_of_wiring_is_followed
    2. test_tests_archives_and_unnamed_ambiguity_are_not_paths
    3. test_dunder_name_is_not_an_edge
    4. test_missing_entry_point_refuses
    5. test_no_evidence_is_unknown_not_distrusted
    6. test_reached_holds_and_gaps_doubt_conforms
    7. test_same_inputs_same_result
    8. test_cli_exit_codes
    9. test_real_weights_and_claims_load
    10. test_latest_claims_version_wins

Tier:     P19 Validation, 0.2.0 (first slice)
Spec:     SPEC_V0_2.md 0.2.0-dev
Version:  0.2.0-dev
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import json
import pathlib
import shutil
import sys

import pytest

LAYER = pathlib.Path(__file__).resolve().parent.parent
REAL_ROOT = LAYER.parent
sys.path.insert(0, str(LAYER))
import relevance_v0_2 as rv  # noqa: E402

NOW = 1_800_000_000.0
PY = {
    # entry: plain import, a sibling folder named in a string, importlib by literal, a script by path
    "a-layer/entry.py": "import os, sys, importlib, subprocess\nsys.path.insert(0, os.path.join('..', 'b-layer'))\n"
                        "import b_mod\nimportlib.import_module('c_mod')\nsubprocess.Popen(['python', '../d-layer/d_serve.py'])\n"
                        "import local_helper\nimport amb\nprint('__main__')\n",
    "a-layer/local_helper.py": "X = 1\n",
    "b-layer/b_mod.py": "import os\n",
    "c-layer/c_mod.py": "import os\n",
    "d-layer/d_serve.py": "import os\n",
    "e-layer/e_mod.py": "import os\n",                 # only tests reach it
    "e-layer/test_e.py": "import e_mod\n",
    "e-layer/archive/old.py": "import os\n",
    "f-layer/amb.py": "X = 1\n",                         # amb exists twice, unnamed: ambiguous
    "g-layer/amb.py": "X = 1\n",
    "k-layer/__main__.py": "X = 1\n",
}


def _weights(entry="a-layer/entry.py"):
    w = json.loads((LAYER / "weights_v0_2.json").read_text(encoding="utf-8"))
    w["entry_points"] = [{"path": entry, "why": "test"}]
    return w


def _claim(repo, kind="primitive"):
    return {"format": "p19-claims", "version": 1, "entity": repo, "kind": kind, "name": repo,
            "claims": [{"id": f"{repo}/PURPOSE", "says": "x", "status": "confirmed", "expected_dry_run": "holds"}]}


@pytest.fixture
def ws(tmp_path):
    for rel, text in PY.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    for layer in ("leighton-engine-layer", "trust-layer", "weight-layer"):
        dst = tmp_path / layer
        dst.mkdir()
        for f in (REAL_ROOT / layer).glob("*.py"):
            if not f.name.startswith(("test_", "agent_", "conftest")):
                shutil.copy(f, dst / f.name)
    sab = tmp_path / "the-saboteur"
    (sab / "threats_v1").mkdir(parents=True)
    for n, mod in (("0001-b-x.json", "b_mod"), ("0002-c-y.json", "c_mod")):
        (sab / "threats_v1" / n).write_text(json.dumps({"tool": f"python legacy_check_v1.py --layer {mod}"}), encoding="utf-8")
    (sab / "known_gaps_v1_1.json").write_text(json.dumps({"gaps": {"0001-b-x.json": "rollback"}}), encoding="utf-8")
    return tmp_path


# 1.
def test_each_kind_of_wiring_is_followed(ws):
    reached = rv.Graph(ws, _weights()).reach(["a-layer/entry.py"])
    how = {repo: chain[-1][1] for repo, chain in reached.items()}
    assert how["b-layer"] == "sibling-path"
    assert how["c-layer"].startswith("dynamic:")
    assert how["d-layer"].startswith("script:")
    assert how["a-layer"] == "entry"
    assert any(p.endswith("local_helper.py") for p, _ in rv.Graph(ws, _weights()).reach(["a-layer/local_helper.py"])["a-layer"])


# 2.
def test_tests_archives_and_unnamed_ambiguity_are_not_paths(ws):
    g = rv.Graph(ws, _weights())
    reached = g.reach(["a-layer/entry.py"])
    assert "e-layer" not in reached
    assert "f-layer" not in reached and "g-layer" not in reached
    assert g.ambiguous["amb"] >= 1
    assert not any("archive" in p.relative_to(g.root).parts or p.name.startswith("test_") for p in g.files)


# 3.
def test_dunder_name_is_not_an_edge(ws):
    assert "k-layer" not in rv.Graph(ws, _weights()).reach(["a-layer/entry.py"])


# 4.
def test_missing_entry_point_refuses(ws):
    with pytest.raises(FileNotFoundError):
        rv.Graph(ws, _weights()).reach(["a-layer/nope.py"])


# 5.
def test_no_evidence_is_unknown_not_distrusted(ws):
    r = rv.dry_run(ws, _weights(), [_claim("e-layer", "tool")], now=NOW)
    purpose = next(c for c in r["claims"] if c["key"] == "PURPOSE")
    assert (purpose["lambda"], purpose["reading"], purpose["asked"]) == (1.0, "unknown", True)


# 6.
def test_reached_holds_and_gaps_doubt_conforms(ws):
    r = rv.dry_run(ws, _weights(), [_claim("b-layer"), _claim("c-layer", "tool")], now=NOW)
    got = {c["id"]: c for c in r["claims"]}
    assert got["b-layer/PURPOSE"]["reading"] == "holds" and got["b-layer/PURPOSE"]["lambda"] == pytest.approx(1.2)
    assert got["b-layer/CONFORMS"]["status"] == "provisional"
    assert got["b-layer/CONFORMS"]["reading"] == "doubted"
    assert got["c-layer/CONFORMS"]["evidence"][0]["kind"] == "saboteur_no_gap"
    assert got["c-layer/CONFORMS"]["lambda"] > 1.0


# 7.
def test_same_inputs_same_result(ws):
    a = rv.dry_run(ws, _weights(), [_claim("b-layer")], now=NOW)
    b = rv.dry_run(ws, _weights(), [_claim("b-layer")], now=NOW)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


# 8.
def test_cli_exit_codes(ws, capsys, monkeypatch):
    monkeypatch.setattr(rv, "load_weights", lambda path=None: _weights("a-layer/nope.py"))
    assert rv.main(["--root", str(ws), "--now", "2027-01-01T00:00:00+00:00"]) == 2
    monkeypatch.setattr(rv, "load_weights", lambda path=None: _weights())
    monkeypatch.setattr(rv, "load_claims", lambda layer_dir=None: [_claim("b-layer")])
    assert rv.main(["--root", str(ws), "--now", "2027-01-01T00:00:00+00:00", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["dry_run"] is True


# 9.
def test_real_weights_and_claims_load():
    w = rv.load_weights()
    claims = rv.load_claims()
    assert {c["entity"] for c in claims} == {"sign-layer", "store-layer", "canon-verify-layer", "the-saboteur", "consumer"}
    assert all(c["kind"] in w["kinds"] for c in claims)
    assert all(c["version"] == 2 and {x["id"].split("/")[1] for x in c["claims"]} == {"PURPOSE", "CONFORMS"}
               for c in claims)
    for e in w["evidence"].values():
        assert 0 < e["value"] and 0 <= e["confidence"] <= 1


# 10.
def test_latest_claims_version_wins(tmp_path):
    (tmp_path / "claims").mkdir()
    for v in (1, 2):
        c = _claim("b-layer")
        c["version"] = v
        c["claims"][0]["says"] = f"v{v}"
        (tmp_path / "claims" / f"b-layer.claims_v{v}.json").write_text(json.dumps(c), encoding="utf-8")
    got = rv.load_claims(tmp_path)
    assert len(got) == 1 and got[0]["claims"][0]["says"] == "v2"
    bad = _claim("x-layer")
    (tmp_path / "claims" / "x-layer.claims_v3.json").write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ValueError):
        rv.load_claims(tmp_path)
