/*
page_harness_v0_1.js — run the James Checklist page's own script under Node, with no browser

Function:
    The validation layer's reference for the page (SPEC.md §4). It reads
    a james-checklist.html, takes its one <script>, and runs it unchanged
    inside a stand-in browser: a DOM where every element absorbs any
    call, and an in-memory localStorage. Then it answers one command on
    stdin (JSON) and prints JSON on stdout:

      {"cmd":"prompt"}                 genPrompt(), the AI interviewer prompt
      {"cmd":"data"}                   the data block's constants (regexes as {source, flags})
      {"cmd":"score", "run": {...}}    checks(), jflags(), viability(), evSummary(), externals()
                                       for one run file, as the page computes them

    Nothing is written; the page is never edited.

    node page_harness_v0_1.js <path to james-checklist.html> < request.json

Tier:     P19 Validation, 0.1.0
Spec:     SPEC.md 0.1.0
Version:  0.1.0-dev
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
*/
"use strict";
const fs = require("fs");

const page = fs.readFileSync(process.argv[2], "utf8");
const open = page.indexOf("<script>"), close = page.lastIndexOf("</script>");
if (open < 0 || close < open) { console.error("no <script> in " + process.argv[2]); process.exit(2); }
let script = page.slice(open + "<script>".length, close);
// The page draws itself on load: its script ends "render();" then the "}" that closes the block the
// whole script sits in. Nothing is drawn here, so that one render(); is removed. If the script no
// longer ends that way, the harness stops rather than guess.
const NL = String.fromCharCode(10);
const TAIL = NL + "render();" + NL + "}";
const body = script.replace(/\r\n/g, NL).trimEnd();
if (!body.endsWith(TAIL)) { console.error("the page's script no longer ends with render(); }"); process.exit(2); }
script = body.slice(0, body.length - TAIL.length) + NL;  // the api below goes in before the block closes

// A DOM element that absorbs any property and any call.
const sink = () => new Proxy(function () {}, {
  get: (t, p) => p === Symbol.toPrimitive ? () => "" : p === "querySelectorAll" ? () => [] :
    p === "value" || p === "textContent" || p === "innerHTML" ? "" : p === "dataset" ? {} : p === "checked" ? false : sink(),
  set: () => true, apply: () => sink(),
});
const store = {};
const env = {
  document: { getElementById: () => sink(), querySelector: () => sink(), querySelectorAll: () => [],
              addEventListener() {}, createElement: () => sink(), body: sink() },
  localStorage: { getItem: k => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = String(v); }, removeItem: k => { delete store[k]; } },
  window: { addEventListener() {}, scrollTo() {} }, navigator: { clipboard: { writeText: () => Promise.resolve() } },
  location: { href: "" }, setTimeout: () => 0, alert() {}, confirm: () => false, Blob: function () {}, URL: { createObjectURL: () => "" },
};
const req = JSON.parse(fs.readFileSync(0, "utf8") || "{}");
const re = r => ({ source: r.source, flags: r.flags });
const api = `
  ;return (req) => {
    if (req.cmd === "prompt") return genPrompt();
    if (req.cmd === "data") return {VERSION, QS, MODES, MODE_TAGS, FUNQ, JMODES, QUICK, RULES, R9_RE: re(R9_RE),
      INVESTIGATIONS, FCODES, CONSTRAINTS_PREFILL, JQ, VIA, VERDICTS, JRULES, REPORT_FORMAT};
    if (req.cmd === "score") { const m = migrate(req.run); if (!m) throw new Error("not a run file");
      state = m; return {checks: checks(), jflags: jflags(), viability: viability(), evSummary: evSummary(),
      externals: externals(), screenFails: screenFails(), active: act().map(i => QS[i].k)}; }
    throw new Error("unknown cmd " + req.cmd);
  };`;
const names = Object.keys(env);
const run = new Function(...names, "re", script + api + NL + "}")(...names.map(n => env[n]), re);
process.stdout.write(JSON.stringify(run(req), null, 2) + "\n");
