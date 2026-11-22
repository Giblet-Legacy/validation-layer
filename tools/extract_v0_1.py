"""
extract_v0_1.py — split the checklist page's data block into the public method and the private profile

Function:
    SPEC.md §3. The page (james-checklist.html, kept on James's machine)
    is the one source of truth. This asks it for its data block, through
    page_harness_v0_1.js under Node, and writes two files:

      - the METHOD: steps, modes, kinds of build, Quick's steps,
        Investigations, failure-mode names, the viability weights,
        verdicts and the report format. Public: committed as
        method_v<X>_<Y>.json in the layer.
      - the PROFILE: James's Screen rules, his R9 guard words, his
        standing constraints, his James checks (JQ) and the interviewer's
        rules (JRULES, which name his work). Private: written to
        ~/.forge/validation/profile_v<X>_<Y>.json (FORGE_HOME if set),
        and never committed.

    Before writing, it refuses a method file in which the profile's R9
    guard words match anything. Work names must never reach a public
    repo (R9).

    python tools/extract_v0_1.py PAGE [--method-out DIR] [--profile-out DIR]

Public API:
    1. page_data(page) -> dict
    2. split(data) -> (method, profile)
    3. main(argv=None) -> int

Tier:     P19 Validation, 0.1.0
Spec:     SPEC.md 0.1.0
Version:  0.1.0 (frozen 2026-11-22)
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
LAYER = HERE.parent
HARNESS = HERE / "page_harness_v0_1.js"
METHOD_KEYS = ("VERSION", "QS", "MODES", "MODE_TAGS", "FUNQ", "JMODES", "QUICK", "INVESTIGATIONS", "FCODES",
               "VIA", "VERDICTS", "REPORT_FORMAT")
PROFILE_KEYS = ("RULES", "R9_RE", "CONSTRAINTS_PREFILL", "JQ", "JRULES")


# 1. page_data
def page_data(page):
    r = subprocess.run(["node", str(HARNESS), str(page)], input='{"cmd":"data"}', capture_output=True,
                       text=True, encoding="utf-8")
    if r.returncode != 0:
        raise RuntimeError(f"the page harness failed: {r.stderr.strip()}")
    return json.loads(r.stdout)


# 2. split
def split(data):
    method = {k: data[k] for k in METHOD_KEYS}
    profile = {k: data[k] for k in PROFILE_KEYS}
    guard = re.compile(profile["R9_RE"]["source"], re.I if "i" in profile["R9_RE"]["flags"] else 0)
    hit = guard.search(json.dumps(method, ensure_ascii=False))
    if hit:
        raise ValueError(f"the method holds a guarded word ({hit.group(0)!r}); it must not be published")
    return method, profile


def _vtag(version):
    major, minor = version.split("-")[0].split(".")[:2]
    return f"v{major}_{minor}"


def _write(path, doc):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(doc, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))


# 3. main
def main(argv=None):
    p = argparse.ArgumentParser(description="Split the checklist page into the public method and the private profile.")
    p.add_argument("page")
    p.add_argument("--method-out", default=str(LAYER))
    home = pathlib.Path(os.environ.get("FORGE_HOME") or pathlib.Path.home() / ".forge")
    p.add_argument("--profile-out", default=str(home / "validation"))
    args = p.parse_args(argv)
    method, profile = split(page_data(args.page))
    tag = _vtag(method["VERSION"])
    note = "Generated from james-checklist.html by tools/extract_v0_1.py; never edit by hand."
    _write(pathlib.Path(args.method_out) / f"method_{tag}.json", {"generated": note, **method})
    _write(pathlib.Path(args.profile_out) / f"profile_{tag}.json",
           {"generated": note, "private": "James's profile: never commit, never publish (R9).", **profile})
    print(f"method_{tag}.json -> {args.method_out}; profile_{tag}.json -> {args.profile_out} (private)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
