"""
validate_v0_1_1.py — P19 Validation 0.1.1: score a checklist run (checklist 2.3.0), offline and the same way every time

Function:
    The layer over validate_v0_1.py (SPEC_V0_1_1.md): the same engine,
    carrying checklist 2.3.0, where a red team's findings must be decided
    before they lift the score. validate_v0_1.py is frozen and unchanged.

    The validation layer's engine (SPEC.md §2). It takes a run file, the
    JSON the James Checklist page writes with "Export .json", and returns
    what the page would show:

      - the checks between answers, and vague words;
      - the James flags (F1–F9, WHY3, J-*, R9, INV, SCREEN, QUICK);
      - viability: score, cap, band, the four parts and the three
        biggest gains;
      - the evidence summary and who outside checked anything;
      - the Screen fails;
      - what the verdict still needs.

    It is a line-by-line port of the page's checks(), jflags(), viability(),
    evSummary() and externals() (checklist 2.3.0). It reads the method from
    method_v2_3.json and the rules from a profile: James's private one in
    ~/.forge/validation/, or the neutral one in this layer. There is no AI
    in it and no network. The same run gives the same result. Parity with
    the page is tested by running the page's own script under Node
    (tests/test_parity_v0_1.py).

    python validate_v0_1_1.py RUN.json [--profile PATH] [--json]

    Exit codes: 0 scored; 2 not a run file.

Public API:
    1. load_method(path=None) -> dict
    2. load_profile(path=None) -> dict   (James's if present, else neutral)
    3. Run(run, method, profile)         .checks() .jflags() .viability() .ev_summary()
                                         .externals() .screen_fails() .active()
    4. evaluate(run, method=None, profile=None) -> dict
    5. verdict_needs(run, method=None, profile=None) -> [str]
    6. main(argv=None) -> int

Tier:     P19 Validation, 0.1.0
Depends:  method_v2_3.json; a profile (profile_neutral_v2_3.json, or James's)
Spec:     SPEC_V0_1_1.md 0.1.1
Version:  0.1.1 (frozen 2026-11-23)
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import argparse
import json
import math
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
METHOD = HERE / "method_v2_3.json"
NEUTRAL = HERE / "profile_neutral_v2_3.json"
A = re.ASCII  # JavaScript regexes without the u flag: \b, \d and \w are ASCII-only.
AI = re.ASCII | re.IGNORECASE


def _home_profile():
    home = pathlib.Path(os.environ.get("FORGE_HOME") or pathlib.Path.home() / ".forge")
    return home / "validation" / "profile_v2_3.json"


# 1. load_method
def load_method(path=None):
    return json.loads(pathlib.Path(path or METHOD).read_text(encoding="utf-8"))


# 2. load_profile
def load_profile(path=None):
    p = pathlib.Path(path) if path else (_home_profile() if _home_profile().exists() else NEUTRAL)
    return json.loads(p.read_text(encoding="utf-8"))


def js_round(x):
    return math.floor(x + 0.5)


def _jsre(spec):
    flags = A | (re.I if "i" in spec["flags"] else 0)
    return re.compile(spec["source"], flags)


# Regexes and word lists from the page's logic (not its data block), checklist 2.2.0.
STOP = set(("the and but then than that this these those with without from into onto for are was were been being its it's "
            "our you your they them their not yes does did done can could will would should may might must have has had such any "
            "all each every one two three more most less very just only also about over under again what which who whom when where "
            "why how there here use used using make made get gets via per out off new way ways it's don't doesn't isn't won't").split(" "))
MARK = re.compile(r"^\s*(\(?\d+\)|\(?[A-Za-z]\)|\d+[.:]|[-•*])\s*", A)
VAGUE_RE = re.compile(r"\b(fast(er)?|quick(ly)?|slow|scalab\w*|robust|reliabl[ey]|secure(ly)?|user[- ]friendly|intuitive|seamless(ly)?|"
                      r"efficient(ly)?|performant|cheap(ly)?|affordable|low[- ]cost|soon|asap|significant(ly)?|high[- ]quality|"
                      r"world[- ]class|enterprise[- ]grade|best[- ]in[- ]class|lots of|easy to|as needed)\b", AI)
BUY = re.compile(r"\b(buy|bought|borrow|reuse|re-use|off[- ]the[- ]shelf|existing (tool|product|library|service|app)|saas|vendor|"
                 r"licen[cs]e|open[- ]source|library|libraries|sdk|template|fork|plugin|package)\b", AI)
CHECKABLE = re.compile(r"\d|%|£|\$|€|\b(fails?|exceeds?|more than|less than|fewer than|over|under|drops?|stops?|runs? out|blocked|"
                       r"deprecated|removed|no longer|doesn't|isn't|can't|cannot|breaks?|no (reply|response|users?|customers?|sales?|"
                       r"interest|takers?)|nobody|zero|jan(uary)?|feb(ruary)?|mar(ch)?|apr(il)?|june?|july?|aug(ust)?|sep(tember)?|"
                       r"oct(ober)?|nov(ember)?|dec(ember)?|week|month|quarter|year|deadline|decision)\b", AI)
DATE_RE = re.compile(r"\b(19|20)\d{2}\b|\b\d{1,2}[\/.-]\d{1,2}([\/.-]\d{2,4})?\b|\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)"
                     r"[a-z]*\.?\s+\d{1,4}\b|\b\d{1,2}(st|nd|rd|th)?\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)|\bQ[1-4]\b|"
                     r"\b(within|in|after|for)\s+\d+\s+(days?|weeks?|months?|years?)\b|\bby\s+(the\s+)?end\s+of\b", AI)
PARK_RE = re.compile(r"\b(don'?t (build|do)|do nothing|park|not build|skip it|status quo|stay (as is|in|put|where)|as a hobby|"
                     r"leave it)\b", AI)
NO_COMP = re.compile(r"\b(no (real |direct |obvious )?(competition|competitors?|alternatives?)|nothing (else )?(like|does) (this|it)|"
                     r"there is none)\b", AI)
NONE_ONLY = re.compile(r"^\s*(none|nothing|n\/a)\W*$", AI)
SUCCESS_TEST = re.compile(r"\d|%|\b(pass(es)?|fails?|exit|yes\/no|zero|none|every|all|within|under|at least|at most|only if)\b", AI)
DOING_NOTHING = re.compile(r"\b(nothing|ignored?|status quo|without (it|this)|otherwise|inaction|if we don't|if i don't)\b", AI)
FREE = re.compile(r"(\bfree\b|\bno cost\b|\bcosts? nothing\b|[$£€]0\b)", AI)
JUST_ME = re.compile(r"^(me|just me|myself|only me|me only|i do|i will|i would)$", A)
LETTER = {"fun": "f", "eng": "e", "arch": "a"}
DF = ["chosen", "rejected", "reason", "downside", "trigger"]
RF = ["reviewer", "found", "changing", "rejected"]
KF = ["signal", "checkby", "then"]
FORM_FIELDS = {"decision": DF, "redteam": RF, "kill": KF}


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def stem(w):
    return w[:5] if len(w) > 5 else w


def words(t):
    out = []
    for w in norm(t).split(" "):
        if len(w) >= 3 and w not in STOP:
            s = stem(w)
            if s not in out:
                out.append(s)
    return out


def overlap(a, b):
    B = set(words(b))
    return [w for w in words(a) if w in B]


def items(t):
    parts = re.split(r"\n+|(?<=[.;?!])\s+(?=[A-Z(])", t, flags=A)
    return [s for s in (MARK.sub("", p, count=1).strip() for p in parts) if words(s)]


def listed(t):
    return len([l for l in re.split(r"\n+", t) if MARK.search(l) and MARK.sub("", l, count=1).strip()])


def short(s):
    s = re.sub(r"[.;:]+$", "", s)
    return s[:67].strip() + "…" if len(s) > 70 else s


def vague_in(t):
    out = []
    for s in re.split(r"\n+|(?<=[.;!?])\s+", t, flags=A):
        if re.search(r"\d", s, A):
            continue
        for m in VAGUE_RE.finditer(s):
            w = m.group(0).lower()
            if w not in out:
                out.append(w)
    return out


def dec_warn(a):
    return "Nothing rejected — a design with only one option was assumed, not chosen." if a["chosen"].strip() and not a["rejected"].strip() else ""


def kill_warn(a):
    if not a["signal"].strip():
        return "No kill signal. What, specifically, would tell you to stop?" if a["checkby"].strip() or a["then"].strip() else ""
    if not CHECKABLE.search(a["signal"]):
        return "Not checkable yet. Make it a number, date or event someone else could check."
    if not a["checkby"].strip():
        return "When will you look? A kill signal nobody checks never fires."
    return ""


def multi_chosen(c):
    return bool(re.search(r"\b(both|all three|all of them|at the same time|in parallel|simultaneously)\b", c, AI)
                or re.search(r"(^|[^A-Za-z])[A-D]\s*(,|and|\+|&)\s*[A-D](?![A-Za-z])", c, A))


def ev_warn(e):
    return "Marked verified but no source — where did this figure come from?" if e.get("status") == "verified" and not e.get("src", "").strip() else ""


# 3. Run
class Run:
    """One run file, read the way the page's migrate() reads it, scored the way the page scores it."""

    def __init__(self, run, method, profile):
        if not isinstance(run, dict) or not isinstance(run.get("answers"), list):
            raise ValueError("not a run file: no answers")
        self.M, self.P = method, profile
        self.QS = method["QS"]
        for q in self.QS:
            q.setdefault("m", method["MODE_TAGS"][q["k"]])
        self.keys = [q["k"] for q in self.QS]
        keys = run.get("keys") if isinstance(run.get("keys"), list) else None
        if not keys or len(keys) != len(run["answers"]):
            raise ValueError("not a run file this engine reads: keys and answers do not line up")
        self.answers, self.evidence = [], []
        for q in self.QS:
            j = keys.index(q["k"]) if q["k"] in keys else -1
            old = run["answers"][j] if j >= 0 else None
            self.answers.append(self._blank_like(q, old))
            ev = run.get("evidence", [])
            self.evidence.append(ev[j] if j >= 0 and j < len(ev) and isinstance(ev[j], list) else [])
        self.jm = run.get("jm") if run.get("jm") in [m[0] for m in method["JMODES"]] else "full"
        self.modes = {m: (run.get("modes") or {}).get(m) is True for m in LETTER} if any(
            (run.get("modes") or {}).get(m) is True for m in LETTER) else {"fun": False, "eng": False, "arch": True}
        self.screen = run.get("screen") if isinstance(run.get("screen"), dict) else {}
        self.jyn = run.get("jyn") if isinstance(run.get("jyn"), dict) else {}
        self.sev = run.get("sev", "") if isinstance(run.get("sev"), str) else ""
        self.inv = run.get("inv", "") if isinstance(run.get("inv"), str) else ""
        self.inv_why = run.get("invWhy", "") if isinstance(run.get("invWhy"), str) else ""
        self.name = run.get("name", "") or ""
        self.context = run.get("context", "") if run.get("context") in ("personal", "client") else ""
        self.home = run.get("home") is True
        self.screen_go = run.get("screenGo") is True
        self.imported = run.get("imported") is True
        self.from_v1 = run.get("fromV1") is True
        v = run.get("verdict") if isinstance(run.get("verdict"), dict) else {}
        self.verdict = {f: (v.get(f) if isinstance(v.get(f), str) else "") for f in ("v", "reason", "at", "slice", "date", "trigger", "change")}
        self.r9 = _jsre(profile["R9_RE"])

    @staticmethod
    def _blank_like(q, old):
        t = q.get("type")
        if t == "whys":
            five = lambda arr: [arr[k] if isinstance(arr, list) and k < len(arr) and isinstance(arr[k], str) else "" for k in range(5)]
            if isinstance(old, dict) and isinstance(old.get("whys"), list):
                return {"start": old.get("start", "") if isinstance(old.get("start"), str) else "", "whys": five(old["whys"]),
                        "branches": five(old.get("branches"))}
            return {"start": "", "whys": [""] * 5, "branches": [""] * 5}
        if t in FORM_FIELDS:
            out = {f: "" for f in FORM_FIELDS[t]}
            if isinstance(old, dict):
                out.update({f: old[f] for f in FORM_FIELDS[t] if isinstance(old.get(f), str)})
            elif isinstance(old, str) and t == "redteam":
                out["found"] = old
            elif isinstance(old, str) and t == "kill":
                out["then"] = old
            return out
        return old if isinstance(old, str) else ""

    # -- the page's helpers --
    def idx(self, k):
        return self.keys.index(k)

    def is_on(self, i):
        if self.jm == "quick":
            return self.QS[i]["k"] in self.M["QUICK"]
        return any(self.modes[m] and LETTER[m] in self.QS[i]["m"] for m in LETTER)

    def active(self):
        return [self.QS[i]["k"] for i in range(len(self.QS)) if self.is_on(i)]

    def on(self, k):
        return self.is_on(self.idx(k))

    def fun_only(self):
        return self.jm != "quick" and self.modes["fun"] and not self.modes["eng"] and not self.modes["arch"]

    def echo_warn(self, q, t):
        a = norm(t)
        lines = [s.strip() for s in re.split(r"\n+", t.strip()) if s.strip()]
        key_then_q = len(lines) == 2 and norm(lines[0]) == norm(q["k"]) and lines[1].endswith("?") and len(lines[1]) < 160
        qs = [norm(x) for x in (q["q"], self.M["FUNQ"].get(q["k"])) if x]
        echoes = any(a == qq or (qq in a and len(a) < len(qq) + 40) for qq in qs)
        return "This looks like the question pasted back, not an answer." if a and (echoes or a == norm(q["k"]) or key_then_q) else ""

    def answered(self, i):
        q, a = self.QS[i], self.answers[i]
        if q.get("type") == "whys":
            return any(w.strip() for w in a["whys"])
        if q.get("type") in FORM_FIELDS:
            return any(a[f].strip() for f in FORM_FIELDS[q["type"]])
        return bool(a.strip()) and not self.echo_warn(q, a)

    def txt(self, k):
        i = self.idx(k)
        if not self.is_on(i):
            return ""
        q, a = self.QS[i], self.answers[i]
        if q.get("type") == "whys":
            return "\n".join([a["start"], *a["whys"], *a["branches"]])
        if q.get("type") in FORM_FIELDS:
            return "\n".join(a[f] for f in FORM_FIELDS[q["type"]])
        return "" if self.echo_warn(q, a) else a

    def has(self, k):
        return bool(self.txt(k).strip())

    @staticmethod
    def root_of(w):
        for i in range(4, -1, -1):
            if w["whys"][i].strip():
                b = w["branches"][i].strip()
                return w["whys"][i].strip() + ("  |  also: " + b if b else "")
        return ""

    # -- checks() --
    def checks(self):
        out = []
        add = lambda k, msg, kind="cross": out.append({"k": k, "msg": msg, "kind": kind})
        d = self.answers[self.idx("DECISION")]
        if self.on("DECISION") and self.has("OPTIONS"):
            if d["chosen"].strip() and not overlap(d["chosen"], self.txt("OPTIONS")):
                add("DECISION", "Chosen doesn't match anything in OPTIONS. Was it one of the options you actually compared?")
            if listed(self.txt("OPTIONS")) == 1:
                add("OPTIONS", "Only one option listed. A design with only one option was assumed, not chosen.")
        if d["trigger"].strip() and self.on("DECISION") and not CHECKABLE.search(d["trigger"]):
            add("DECISION", "\"What would change your mind\" isn't checkable yet. Make it a threshold, an event or a figure.")
        if self.has("COMPETITION"):
            c = self.txt("COMPETITION")
            if NO_COMP.search(c) or NONE_ONLY.search(c):
                add("COMPETITION", "\"No competition\" is never true. There's always an alternative, even if it's doing nothing or a spreadsheet.")
            if BUY.search(c) and self.has("OPTIONS") and not BUY.search(self.txt("OPTIONS")) and not BUY.search(self.txt("TRADE-OFFS")):
                add("OPTIONS", "COMPETITION mentions something you could buy, borrow or reuse, but OPTIONS doesn't include that route or say why it's ruled out.")
        if self.has("ASSUMPTIONS") and self.on("VERIFICATION"):
            V = self.txt("VERIFICATION")
            if not V.strip():
                add("VERIFICATION", "ASSUMPTIONS lists what must be true, but nothing here says how you'll check it.")
            else:
                un = [s for s in items(self.txt("ASSUMPTIONS")) if not overlap(s, V)]
                if un:
                    add("VERIFICATION", "No check for: " + "; ".join('"' + short(s) + '"' for s in un) + ".")
        rc = self.root_of(self.answers[self.idx("ROOT CAUSE — 5 WHYS")]) if self.on("ROOT CAUSE — 5 WHYS") else ""
        plan = self.txt("FIRST SLICE") + "\n" + self.txt("RECOVERY")
        if rc and plan.strip() and len(overlap(rc, plan)) < min(2, len(words(rc))):
            add("RECOVERY" if self.on("RECOVERY") else "FIRST SLICE",
                "The root cause you found doesn't show up in FIRST SLICE or RECOVERY. Where's the fix for it?")
        if self.has("FAILURE") and self.has("OBSERVABILITY") and not overlap(self.txt("FAILURE"), self.txt("OBSERVABILITY")):
            add("OBSERVABILITY", "Nothing here would show you the FAILURE you named. How would you see that one happening?")
        if self.has("NON-GOALS") and self.has("FIRST SLICE"):
            fs = set(words(self.txt("FIRST SLICE")))
            parts = [x for s in items(self.txt("NON-GOALS")) for x in re.split(r",|\bor\b|\band\b", s, flags=A)]
            hits = []
            for s in (re.sub(r"[.;:]+$", "", x.strip()) for x in parts):
                w = words(s)
                if w and len(w) <= 3 and all(x in fs for x in w):
                    hits.append(s)
            if hits:
                add("FIRST SLICE", "Includes things NON-GOALS ruled out: " + ", ".join('"' + short(s) + '"' for s in hits) + ".")
        if self.has("SUCCESS") and not self.fun_only() and not SUCCESS_TEST.search(self.txt("SUCCESS")):
            add("SUCCESS", "No number, threshold or pass/fail test. How would someone else check that it worked?")
        if self.has("BUSINESS CASE") and not DOING_NOTHING.search(self.txt("BUSINESS CASE")):
            add("BUSINESS CASE", "Doesn't say what doing nothing costs.")
        if self.has("COST") and FREE.search(self.txt("COST")) and not any(
                FREE.search(e.get("fig", "")) and e.get("status") == "verified" and e.get("src", "").strip()
                for e in self.evidence[self.idx("COST")]):
            add("COST", "Says something is free, with no verified source. \"Free\" usually comes with limits: rate caps, quotas, terms.")
        if self.context == "client":
            for k in ("STAKEHOLDERS", "OWNERSHIP", "OPERATIONS", "CONTINUITY"):
                if JUST_ME.search(norm(self.txt(k))):
                    add(k, "Just \"me\" is a gap for client work. Who approves, takes over or gets the call if you can't?")
        if not self.fun_only():
            for i, q in enumerate(self.QS):
                if not self.is_on(i) or q["k"] == "NON-GOALS" or q.get("type") == "redteam":
                    continue
                v = vague_in(self.txt(q["k"]))
                if v:
                    add(q["k"], "Vague: " + ", ".join('"' + w + '"' for w in v) + ". Add a number, a threshold or a source.", "vague")
        return sorted(out, key=lambda c: self.idx(c["k"]))

    def rules_on(self):
        return [r for r in self.P["RULES"] if self.jm in r["modes"]]

    def externals(self):
        out = []
        for i, q in enumerate(self.QS):
            if not self.is_on(i):
                continue
            for e in self.evidence[i]:
                if e.get("by") == "external" and e.get("fig", "").strip():
                    out.append({"who": e.get("src", "").strip() or "someone else (unnamed)", "k": q["k"],
                                "what": e["fig"].strip(), "verified": e.get("status") == "verified"})
        rt = self.answers[self.idx("RED TEAM")] if self.on("RED TEAM") else None
        if rt and rt["reviewer"].strip() and rt["found"].strip():
            out.append({"who": rt["reviewer"].strip(), "k": "RED TEAM", "what": "attacked the plan", "verified": False})
        return out

    def screen_fails(self):
        return [r["id"] for r in self.rules_on() if (self.screen.get(r["id"]) or {}).get("r") == "fail"]

    # -- jflags() --
    def jflags(self):
        out = []

        def add(code, k, msg):
            if not k or self.on(k):
                out.append({"code": code, "k": k, "msg": msg})
        for k, j in self.P["JQ"].items():
            for y in j.get("yn", []):
                if y.get("bad") and self.jyn.get(y["id"]) == y["bad"]:
                    add(y["id"], k, y["msg"])
        d = self.answers[self.idx("DECISION")]
        if self.jm != "quick" and (not d["chosen"].strip() or not d["rejected"].strip() or not d["reason"].strip()):
            add("F2", "DECISION", "Decision not fully recorded: Chosen, Rejected and Reason are required in this mode.")
        if d["chosen"].strip() and multi_chosen(d["chosen"]):
            add("F3", "DECISION", "More than one option is Chosen. Running every option means none is chosen.")
        sc = self.txt("SUCCESS").strip()
        if not sc:
            add("F4", "SUCCESS", "No success test.")
        elif not re.search(r"\d", sc, A) or not DATE_RE.search(sc):
            add("F4", "SUCCESS", "No number in the success test." if not re.search(r"\d", sc, A) else "No date in the success test.")
        pw = self.answers[self.idx("PURPOSE — 5 WHYS")]
        nw = len([w for w in pw["whys"] if w.strip()])
        if 0 < nw <= 3:
            add("WHY3", "PURPOSE — 5 WHYS", f"Stops at Why {nw}: no real need underneath.")
        if self.has("OPTIONS") and not PARK_RE.search(self.txt("OPTIONS")):
            add("J-PARK", "OPTIONS", "No \"don't build it / park it\" option.")
        if self.r9.search("\n".join(self.txt(q["k"]) for q in self.QS) + " " + self.name) and self.jyn.get("R9") != "yes":
            out.append({"code": "R9", "k": "", "msg": "Mentions work or cleared material. Offline only: never the AI prompt or a public repo."})
        if self.inv == "none" and not self.inv_why.strip():
            out.append({"code": "INV", "k": "", "msg": "No Investigation, and no answer to \"why build it?\"."})
        if not self.inv and not self.imported and not self.from_v1:
            out.append({"code": "INV", "k": "", "msg": "Investigation not set."})
        sf = self.screen_fails()
        if len(sf) >= 3 and self.screen_go:
            out.append({"code": "SCREEN", "k": "", "msg": f"Fails {len(sf)} of your own rules ({', '.join(sf)}); continued anyway."})
        if self.jm == "quick" and {"annoying": 0, "serious": 1, "severe": 2}.get(self.sev, -1) > 0:
            add("QUICK", "IMPACT", "Impact is above annoying, but this is still a Quick run.")
        if self.jm != "quick" and not self.externals() and any(self.answered(i) for i in range(len(self.QS)) if self.is_on(i)):
            add("F9", "VERIFICATION" if self.on("VERIFICATION") else "",
                "Only self-validated: nobody outside you has checked any of this. Which conclusion has survived contact with someone else?")
        return out

    # -- evSummary() --
    def ev_summary(self):
        S = {"verified": 0, "estimate": 0, "assumption": 0, "external": 0, "nosrc": [], "todo": []}
        for i, q in enumerate(self.QS):
            if not self.is_on(i):
                continue
            for e in self.evidence[i]:
                if not e.get("fig", "").strip():
                    continue
                if e.get("status") in ("verified", "estimate", "assumption"):
                    S[e["status"]] += 1
                if e.get("by") == "external":
                    S["external"] += 1
                if ev_warn(e):
                    S["nosrc"].append({"k": q["k"], "e": e})
                if e.get("status") != "verified" or ev_warn(e):
                    S["todo"].append({"k": q["k"], "e": e})
        return S

    # -- viability() --
    def viability(self):
        W, X, JF, P = self.M["VIA"]["w"], self.checks(), self.jflags(), []
        cf = lambda k: any(c["k"] == k and c["kind"] != "vague" for c in X)
        vg = lambda k: any(c["k"] == k and c["kind"] == "vague" for c in X)
        fl = lambda code: any(f["code"] == code for f in JF)

        def item(pil, key, label, step, frac, tip):
            if step and not self.on(step):
                return
            P.append({"pil": pil, "key": key, "label": label, "step": step, "max": W[key],
                      "got": W[key] * max(0, min(1, frac)), "tip": tip})
        pw = self.answers[self.idx("PURPOSE — 5 WHYS")]
        nw = len([w for w in pw["whys"] if w.strip()])
        has = self.has
        item("Why", "purpose", "Purpose stated", "PURPOSE", 1 if has("PURPOSE") else 0, "Say what problem goes away, and for whom.")
        item("Why", "whys", "5 Whys reach the real need", "PURPOSE — 5 WHYS", 1 if nw >= 4 else 0.5 if nw == 3 else 0.2 if nw else 0,
             "Keep asking why. Get to Why 4 or 5, where the real need is." if nw else "Drill the 5 Whys from the purpose to the real need.")
        item("Why", "nongoals", "Non-goals drawn", "NON-GOALS", 1 if has("NON-GOALS") else 0, "Say what it deliberately won't do.")
        item("Why", "value", "Value someone would notice", "VALUE", 0 if not has("VALUE") else 0.6 if vg("VALUE") else 1,
             "Replace the vague words in VALUE with something a person would notice." if has("VALUE") else "Say who benefits, and how they'd notice.")
        sc = self.txt("SUCCESS").strip()
        item("Why", "success", "Success test with a number and a date", "SUCCESS", 0 if not sc else 0.4 if fl("F4") else 1,
             "Write a success test with a number and a date." if not sc else "Give the success test " + ("a number." if not re.search(r"\d", sc, A) else "a date."))
        item("Worth", "bizcase", "Business case, including what doing nothing costs", "BUSINESS CASE",
             0 if not has("BUSINESS CASE") else 0.5 if cf("BUSINESS CASE") else 1,
             "Say what doing nothing costs." if has("BUSINESS CASE") else "Say how this makes or saves money, time or risk.")
        comp_gap = cf("COMPETITION") or any(c["k"] == "OPTIONS" and "COMPETITION" in c["msg"] for c in X)
        item("Worth", "competition", "Competition faced honestly", "COMPETITION", 0 if not has("COMPETITION") else 0.5 if comp_gap else 1,
             "Fix the COMPETITION check: name the real alternatives, and the buy or reuse route." if has("COMPETITION") else "Name what already solves this, including doing nothing.")
        RS = self.rules_on()
        ans = len([r for r in RS if (self.screen.get(r["id"]) or {}).get("r")])
        nf = len(self.screen_fails())
        item("Worth", "screen", "Passes your own rules", "", 0 if not ans else (0 if nf >= 3 else 0.5 if nf else 1) * ans / len(RS),
             "Run The Screen against your own rules." if not ans else f"It fails {nf} of your rules. Change the idea, or accept it knowingly." if nf else "Answer the rest of The Screen.")
        ex = len(self.externals())
        item("Proof", "external", "Checked by someone outside you", "", 1 if ex else 0,
             "Get one person outside you to check one thing: a buyer, a reviewer, an expert. Log it as evidence checked by someone else.")
        S = self.ev_summary()
        tot = S["verified"] + S["estimate"] + S["assumption"]
        okv = S["verified"] - len(S["nosrc"])
        item("Proof", "verified", "Key figures verified", "", okv / max(1, math.ceil(tot / 2)) if tot else 0,
             "Verify more of your figures, each with a source. Half of them gets full marks." if tot else "Log your key figures as evidence, and verify at least one.")
        nA = len(items(self.txt("ASSUMPTIONS"))) if has("ASSUMPTIONS") else 0
        unc = next((c for c in X if c["k"] == "VERIFICATION"), None)
        unN = 0 if not unc else len(re.findall(r'"[^"]*"', unc["msg"])) if "No check for" in unc["msg"] else nA
        item("Proof", "assumptions", "Every assumption has a check", "ASSUMPTIONS", (nA - unN) / nA if nA else 0,
             "Add a check in VERIFICATION for each assumption." if nA else "List what must be true for this to work.")
        rt = self.answers[self.idx("RED TEAM")]
        rt_done = bool(rt["reviewer"].strip() and rt["found"].strip())
        rt_decided = bool(rt["changing"].strip() or rt["rejected"].strip())
        item("Proof", "redteam", "Attacked by someone else, findings decided", "RED TEAM", 0 if not rt_done else 1 if rt_decided else 0.5,
             "Decide on each finding: what you're changing, and what you're rejecting and why." if rt_done else "Hand it to someone else to attack, and log what they found.")
        d = self.answers[self.idx("DECISION")]
        item("Commit", "decision", "Decision recorded, one option chosen", "DECISION",
             0 if not d["chosen"].strip() else 0.5 if (fl("F2") or fl("F3") or dec_warn(d)) else 1,
             "Finish the decision: one Chosen, what's Rejected, and the Reason." if d["chosen"].strip() else "Commit: choose one option and reject the others.")
        kl = self.answers[self.idx("RETIREMENT")]
        item("Commit", "kill", "Kill signal you can check", "RETIREMENT", 0 if not kl["signal"].strip() else 0.5 if kill_warn(kl) else 1,
             "Make the kill signal checkable, with a check-by date." if kl["signal"].strip() else "Set a kill signal: what would tell you to stop?")
        item("Commit", "slice", "First slice defined", "FIRST SLICE", 1 if has("FIRST SLICE") else 0, "Name the smallest thing worth shipping first.")
        mx = sum(x["max"] for x in P)
        got = sum(x["got"] for x in P)
        raw = js_round(100 * got / mx) if mx else 0
        caps, C = [], self.M["VIA"]["caps"]
        if not has("PURPOSE") or (self.on("PURPOSE — 5 WHYS") and nw < 3):
            caps.append([C["noWhy"], "The why isn't there yet: no stated purpose, or the 5 Whys stop before Why 3."])
        if nf >= 3:
            caps.append([C["screen3"], "It fails 3 or more of your own rules."])
        if self.jm != "quick" and not ex:
            caps.append([C["noExternal"], "Nobody outside you has checked any of it."])
        if self.on("RED TEAM") and rt_done and not rt_decided:
            caps.append([C["undecided"], "A reviewer found problems you haven't decided on yet."])
        cap = min(c[0] for c in caps) if caps else 100
        score = min(raw, cap)
        cap_why = " ".join(c[1] for c in caps if c[0] == cap) if caps and raw > cap else ""
        pillars = []
        for n in ("Why", "Worth", "Proof", "Commit"):
            ps = [x for x in P if x["pil"] == n]
            m = sum(x["max"] for x in ps)
            if m:
                pillars.append({"n": n, "got": js_round(sum(x["got"] for x in ps) * 10) / 10, "max": m})
        gains = sorted([x for x in P if x["max"] - x["got"] >= 0.5], key=lambda x: -(x["max"] - x["got"]))[:3]
        gains = [{"pts": max(1, js_round((x["max"] - x["got"]) * 100 / mx)), "tip": x["tip"], "step": x["step"]} for x in gains]
        band = next(b[1] for b in self.M["VIA"]["bands"] if score >= b[0])
        return {"score": score, "raw": raw, "cap": cap, "capWhy": cap_why, "band": band, "pillars": pillars, "gains": gains, "items": P}


# 4. evaluate
def evaluate(run, method=None, profile=None):
    r = Run(run, method or load_method(), profile or load_profile())
    return {"checks": r.checks(), "jflags": r.jflags(), "viability": r.viability(), "evSummary": r.ev_summary(),
            "externals": r.externals(), "screenFails": r.screen_fails(), "active": r.active()}


# 5. verdict_needs
def verdict_needs(run, method=None, profile=None):
    """What the page would refuse to finish without (the Verdict rules, README "Verdict")."""
    r = Run(run, method or load_method(), profile or load_profile())
    v, need = r.verdict, []
    if v["v"] == "build":
        if not v["slice"].strip() or not v["date"].strip():
            need.append("BUILD needs a first slice and a date.")
        d = r.answers[r.idx("DECISION")]
        if r.jm != "quick" and not (d["chosen"].strip() and d["rejected"].strip() and d["reason"].strip()):
            need.append("BUILD outside Quick needs the decision recorded: Chosen, Rejected and Reason.")
    elif v["v"] == "park":
        if not v["trigger"].strip() or not v["change"].strip():
            need.append("PARK needs a revisit trigger and what would have to change.")
    elif v["v"] == "kill":
        if not v["reason"].strip():
            need.append("KILL needs a reason.")
    else:
        need.append("No verdict: BUILD, PARK or KILL.")
    return need


def _text(res, needs):
    V = res["viability"]
    L = [f"Viability: {V['score']}/100 ({V['band']})" + (f"  [capped at {V['cap']}: {V['capWhy']}]" if V["capWhy"] else ""),
         "  " + " · ".join(f"{p['n']} {js_round(p['got'])}/{p['max']}" for p in V["pillars"])]
    L += [f"  Biggest gain: +{g['pts']} {g['tip']}" + (f" ({g['step']})" if g["step"] else "") for g in V["gains"]]
    L.append(f"External validation: {len(res['externals'])}" + (" — " + "; ".join(f"{e['who']} ({e['k']})" for e in res["externals"]) if res["externals"] else " (none)"))
    L.append("== JAMES FLAGS ==")
    L += [f"  - [{f['code']}] {f['k'] + ': ' if f['k'] else ''}{f['msg']}" for f in res["jflags"]] or ["  (none)"]
    L.append("== CHECKS ==")
    L += [f"  - [{'VAGUE' if c['kind'] == 'vague' else 'CROSS-CHECK'}] {c['k']}: {c['msg']}" for c in res["checks"]] or ["  (none)"]
    L.append("== VERDICT ==")
    L += [f"  - {n}" for n in needs] or ["  complete"]
    return "\n".join(L)


# 6. main
def main(argv=None):
    p = argparse.ArgumentParser(description="P19 Validation 0.1.1: score a checklist run file (checklist 2.3.0).")
    p.add_argument("run")
    p.add_argument("--profile", help="profile JSON (default: ~/.forge/validation/profile_v2_3.json, else the neutral one)")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    try:
        run = json.loads(pathlib.Path(args.run).read_text(encoding="utf-8"))
        res = evaluate(run, profile=load_profile(args.profile))
        needs = verdict_needs(run, profile=load_profile(args.profile))
    except (ValueError, KeyError) as e:
        print(f"not a run file: {e}", file=sys.stderr)
        return 2
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(json.dumps({**res, "verdictNeeds": needs}, indent=1, ensure_ascii=False) if args.json else _text(res, needs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
