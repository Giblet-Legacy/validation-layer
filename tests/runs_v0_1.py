"""
runs_v0_1.py — synthetic run files for the validation layer's tests (no one's real runs)

Function:
    Builds run files shaped exactly like the page's "Export .json" (keys,
    answers, evidence, modes, screen, jyn, verdict). Every answer is made
    up, so the tests never hold anyone's real or work material. RUNS
    covers each branch of checks(), jflags() and viability(). Not
    collected by pytest (no test_ prefix).

Public API:
    1. blank(method) -> run
    2. make(method, **kw) -> run
    3. runs(method) -> {name: run}

Tier:     P19 Validation, 0.1.0
Spec:     SPEC.md 0.1.0
Version:  0.1.0-dev
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import copy

FORM = {"decision": ["chosen", "rejected", "reason", "downside", "trigger"],
        "redteam": ["reviewer", "found", "changing", "rejected"],
        "kill": ["signal", "checkby", "then"]}


def _blank_answer(q):
    t = q.get("type")
    if t == "whys":
        return {"start": "", "whys": [""] * 5, "branches": [""] * 5}
    if t in FORM:
        return {f: "" for f in FORM[t]}
    return ""


# 1. blank
def blank(method):
    QS = method["QS"]
    return {"id": "synthetic", "name": "", "context": "", "jm": "full", "inv": "", "invWhy": "", "home": False,
            "screen": {}, "screenGo": False, "jyn": {}, "sev": "",
            "verdict": {"v": "", "reason": "", "at": "", "slice": "", "date": "", "trigger": "", "change": ""},
            "modes": {"fun": False, "eng": False, "arch": True}, "keys": [q["k"] for q in QS],
            "answers": [_blank_answer(q) for q in QS], "evidence": [[] for _ in QS],
            "retro": {"result": "", "happened": "", "success": {}, "assumptions": {}, "kill": "", "step": "", "lesson": ""},
            "format": "james-checklist-run", "version": method["VERSION"]}


# 2. make
def make(method, answers=None, evidence=None, **kw):
    r = blank(method)
    keys = r["keys"]
    for k, v in (answers or {}).items():
        i = keys.index(k)
        if isinstance(v, dict):
            r["answers"][i].update(copy.deepcopy(v))
        else:
            r["answers"][i] = v
    for k, ev in (evidence or {}).items():
        r["evidence"][keys.index(k)] = copy.deepcopy(ev)
    for k, v in kw.items():
        r[k] = copy.deepcopy(v)
    return r


def _ev(fig, status="estimate", src="", by="self"):
    return {"fig": fig, "status": status, "src": src, "by": by}


RICH = {
    "PURPOSE": "Stop new layers being added on a first answer, so the stack keeps only parts that earn their place.",
    "PURPOSE — 5 WHYS": {"start": "Stop first answers", "whys": [
        "Because layers pile up without a recorded reason.",
        "Because nobody asks what a layer is worth before it is built.",
        "Because the questions live in one person's head.",
        "Because the method was never written down as part of the stack.",
        "Because the stack had no layer whose job is to judge proposals."], "branches": ["", "", "", "", ""]},
    "NON-GOALS": "No AI inside the engine.\nNo blocking gate in the first slice.\nNo network.",
    "VALUE": "James sees a score and three named gaps for every new layer before code exists.",
    "SUCCESS": "3 new layers each have a recorded run with a verdict by 2027-02-28.",
    "BUSINESS CASE": "Saves rework time; doing nothing costs another layer pile-up like the 14-layer chain.",
    "COMPETITION": "A plain checklist document, a code review, or doing nothing. Could reuse an open-source ADR template instead.",
    "OPTIONS": "1. Port the scoring to Python\n2. Use an open-source ADR template\n3. Don't build it, park it",
    "TRADE-OFFS": "The port costs a day; the ADR template has no scoring.",
    "DECISION": {"chosen": "Port the scoring to Python", "rejected": "ADR template; park it",
                 "reason": "The page already holds the method; a port keeps one source.",
                 "downside": "Two implementations to keep in step",
                 "trigger": "If parity fails on more than 2 runs in a month"},
    "FIRST SLICE": "The engine, the parity tests and one run on the proposal, done in 30 days.",
    "ASSUMPTIONS": "The page's logic can be run under Node.\nThe scores match between page and engine.",
    "VERIFICATION": "Run the page logic under Node and compare the scores between page and engine on every fixture.",
    "OBSERVABILITY": "The parity test fails when the engine and the page disagree on a score.",
    "FAILURE": "The engine and the page disagree on a score.",
    "ROOT CAUSE — 5 WHYS": {"start": "Disagree on a score", "whys": [
        "A regex behaves differently in Python.", "Unicode word boundaries differ.", "", "", ""], "branches": ["", "", "", "", ""]},
    "RECOVERY": "Fix the regex word boundaries in the engine and add a parity fixture for it.",
    "RETIREMENT": {"signal": "Parity fails on more than 2 runs in one month", "checkby": "end of February 2027",
                   "then": "Stop the port and call the page directly."},
    "RED TEAM": {"reviewer": "A fresh AI session that never saw the answers", "found": "Parity only covers synthetic runs.",
                 "changing": "Add more fixtures.", "rejected": ""},
}


# 3. runs
def runs(method):
    m = method
    R = {}
    R["blank-full"] = blank(m)
    R["rich-full"] = make(m, RICH, {"COST": [_ev("Hosting £0 a month", "verified", "runs on the laptop", "self")],
                                    "VERIFICATION": [_ev("Parity on 12 fixtures", "verified", "a reviewer", "external")]},
                          name="validation layer", inv="Governance", screen={"R9": {"r": "pass", "why": "no work material"}})
    R["rich-no-external"] = make(m, {k: v for k, v in RICH.items() if k != "RED TEAM"}, inv="Governance")
    R["quick-severe"] = make(m, {"PURPOSE": "A small tool.", "IMPACT": "Someone loses data.", "COST": "It is free."},
                             jm="quick", sev="severe", inv="Knowledge")
    R["whys-three"] = make(m, {"PURPOSE": "Help people.", "PURPOSE — 5 WHYS": {
        "start": "Help", "whys": ["Because it helps.", "Because helping is good.", "Because yes.", "", ""], "branches": ["", "", "", "", ""]}},
        inv="Emergence")
    R["checks-galore"] = make(m, {
        "PURPOSE": "Make it fast and robust and scalable soon.",
        "VALUE": "Users get a seamless, intuitive experience.",
        "SUCCESS": "It feels good.",
        "COMPETITION": "There is no competition. Nothing else does this.",
        "OPTIONS": "1. Build it",
        "DECISION": {"chosen": "A and B at the same time", "rejected": "", "reason": "", "downside": "", "trigger": "if it feels wrong"},
        "COST": "The API is free.",
        "BUSINESS CASE": "It makes money.",
        "STAKEHOLDERS": "me", "OWNERSHIP": "just me",
        "NON-GOALS": "No mobile app, or payments.",
        "FIRST SLICE": "A mobile app with payments.",
        "ASSUMPTIONS": "Users want it. The market is big.",
        "VERIFICATION": "",
        "FAILURE": "The database fills up.",
        "OBSERVABILITY": "We read the logs weekly.",
        "RETIREMENT": {"signal": "when it feels wrong", "checkby": "", "then": "stop"},
        "DATA & COMPLIANCE": "Some classified notes from a client project.",
    }, context="client", inv="none", jyn={"F6": "no", "F7": "yes", "F8": "no", "J-CAPSULE": "no", "F1": "yes", "F5": "no", "J-REPLACE": "no"})
    R["fun-only"] = make(m, {"PURPOSE": "A toy that draws spirals.", "SUCCESS": "Seeing it draw.", "FIRST SLICE": "One spiral."},
                         modes={"fun": True, "eng": False, "arch": False}, inv="Emergence")
    R["business-screen"] = make(m, {"PURPOSE": "Sell kits.", "OPTIONS": "Sell kits, or don't do it."}, jm="business",
                                inv="Physical Reality", screenGo=True,
                                screen={"R1": {"r": "fail", "why": "stock"}, "R2": {"r": "fail", "why": "rules"},
                                        "R3": {"r": "fail", "why": "selling"}, "R4": {"r": "pass", "why": ""}, "R9": {"r": "risk", "why": ""}})
    R["evidence-mix"] = make(m, {"PURPOSE": "Measure it.", "COST": "£5 a month, verified."},
                             {"COST": [_ev("£5 a month", "verified", "invoice", "self"), _ev("£0 setup", "verified", "", "self"),
                                       _ev("2 hours a week", "assumption", "", "self")],
                              "SCALE": [_ev("100 users", "estimate", "my guess", "self")],
                              "VALUE": [_ev("A buyer said yes", "estimate", "Pat, a buyer", "external")]},
                             inv="Prediction")
    R["eng-only"] = make(m, RICH, modes={"fun": False, "eng": True, "arch": False}, inv="Knowledge")
    R["echo"] = make(m, {"PURPOSE": "PURPOSE\nWhy does this exist? What problem goes away?",
                         "VALUE": "Who benefits, and how would they notice?"}, inv="Knowledge")
    R["kill-checkable"] = make(m, {"RETIREMENT": {"signal": "No reply from the client by 1 March", "checkby": "", "then": ""}},
                               inv="Knowledge")
    return R
