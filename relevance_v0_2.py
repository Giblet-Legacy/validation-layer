"""
relevance_v0_2.py — P19 Validation 0.2.0 first slice: is each claimed layer reached, and what is its λ (dry run)

Function:
    The first slice of validation over a lifetime (PROPOSAL_V0_2_1.md
    §8.4, §10; SPEC_V0_2.md). It answers, for the stack's confirmed claims
    (claims/<repo>.claims_v1.json):

      1. Is the layer reached on a real path? An import graph is built
         from the real entry points (weights_v0_2.json), across the
         sibling repositories. It follows how the stack is really wired
         (§10.2): plain imports, sibling folders named in sys.path
         inserts and FORGE_LEGACY_ROOT joins, importlib loads by literal
         name, and sibling scripts started by path (subprocess). Tests,
         archives and fixtures are not real paths.
      2. What evidence bears on each claim? In this slice: "reached on a
         real path" (PURPOSE) and the Saboteur's known gaps and clean
         attacks (CONFORMS). The weights are the draft table of
         weights_v0_2.json.
      3. Its λ, computed by P14 Leighton V3 compute_lambda_for_domain,
         one domain per kind (k = ln 2 / half-life, in days). λ is never
         stored. A claim with no evidence is "unknown" (λ 1.00, neutral)
         without calling Leighton, which refuses an empty stream.

    It is a DRY RUN only: it prints, writes nothing, and nothing reaches
    the daily report until James has checked it by hand on the five
    claimed layers (§10.2). CONFORMS is shown as provisional: no layer has
    a confirmed CONFORMS claim yet. No AI, no network, no key.

    python relevance_v0_2.py [--root DIR] [--now ISO] [--json]

    Exit codes: 0 printed; 2 bad input (missing entry point, claims or
    weights file, or Leighton not found).

Public API:
    1. load_weights(path=None) -> dict
    2. load_claims(layer_dir=None) -> [dict]
    3. Graph(root, weights)          .reach(entry_points) -> {repo: [path...]}
                                     .owner(stem) -> repo | None
    4. evidence(root, graph, reached, weights, now) -> {repo: [obs...]}
    5. judge(claims, ev, weights, now) -> [dict]
    6. dry_run(root, weights=None, claims=None, now=None) -> dict
    7. main(argv=None) -> int

Internal helpers:
    8. _scan(path) -> dict, 9. _leighton(root), 10. _git_time(path), 11. _text(result)

Tier:     P19 Validation, 0.2.0 (first slice)
Depends:  weights_v0_2.json, claims/*.claims_vN.json (latest); P14 leighton_engine_v3
          (../leighton-engine-layer, or FORGE_LEGACY_ROOT); the-saboteur's
          known_gaps_v1_1.json and threats_v1/ (read only)
Spec:     SPEC_V0_2.md 0.2.0-dev
Version:  0.2.0-dev
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import argparse
import ast
import collections
import datetime
import importlib.util
import json
import math
import os
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
WEIGHTS = HERE / "weights_v0_2.json"
CLAIMS_DIR = HERE / "claims"
GAPS_FILE = ("the-saboteur", "known_gaps_v1_1.json")
THREATS_DIR = ("the-saboteur", "threats_v1")


# ---------------------------------------------------------------------------
# 1. load_weights — the draft weights file (one file in this layer, §10.4).
# ---------------------------------------------------------------------------
def load_weights(path=None):
    p = pathlib.Path(path) if path else WEIGHTS
    w = json.loads(p.read_text(encoding="utf-8"))
    if w.get("format") != "p19-weights":
        raise ValueError(f"{p}: not a p19-weights file")
    return w


# ---------------------------------------------------------------------------
# 2. load_claims — the confirmed claims, one file per layer and version
#    (claims/<repo>.claims_vN.json, never edited); the highest N per
#    layer is used. Sorted by entity.
# ---------------------------------------------------------------------------
def load_claims(layer_dir=None):
    d = pathlib.Path(layer_dir) / "claims" if layer_dir else CLAIMS_DIR
    latest = {}
    for f in sorted(d.glob("*.claims_v*.json")):
        m = re.fullmatch(r"(.+)\.claims_v(\d+)\.json", f.name)
        if not m:
            continue
        c = json.loads(f.read_text(encoding="utf-8"))
        if c.get("format") != "p19-claims" or c.get("entity") != m.group(1) or c.get("version") != int(m.group(2)):
            raise ValueError(f"{f}: not a p19-claims file for {m.group(1)} version {m.group(2)}")
        if m.group(1) not in latest or c["version"] > latest[m.group(1)]["version"]:
            latest[m.group(1)] = c
    return [latest[k] for k in sorted(latest)]


# ---------------------------------------------------------------------------
# 8. _scan — what one file says about its wiring, read with ast (never run).
# ---------------------------------------------------------------------------
def _scan(path):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    except SyntaxError:
        return {"imports": set(), "relative": set(), "strings": set(), "dynamic": False}
    imports, relative, strings, dynamic = set(), set(), set(), False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                imports.add(a.name.split(".")[0])
                if a.name.split(".")[0] == "importlib":
                    dynamic = True
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                relative.update(a.name for a in node.names)
                if node.module:
                    relative.add(node.module.split(".")[0])
            elif node.module:
                imports.add(node.module.split(".")[0])
                if node.module.split(".")[0] == "importlib":
                    dynamic = True
        elif isinstance(node, ast.Name) and node.id == "__import__":
            dynamic = True
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and len(node.value) < 300:
            strings.add(node.value)
    return {"imports": imports, "relative": relative, "strings": strings, "dynamic": dynamic}


# ---------------------------------------------------------------------------
# 3. Graph — every module in every sibling repository, and the edges
#    between files. A name resolves first in the file's own folder, then
#    its own repository, then the sibling repositories the file names in
#    a string ('../envelope-layer', os.path.join(ROOT, "substrate-layer")),
#    then anywhere if exactly one repository has it. A name held by
#    several repositories, none of them named, is ambiguous: no edge, and
#    it is listed so a missed path can be seen.
# ---------------------------------------------------------------------------
class Graph:
    def __init__(self, root, weights):
        self.root = pathlib.Path(root).resolve()
        sd = [re.compile(x) for x in weights["skip_dirs_matching"]]
        sf = [re.compile(x) for x in weights["skip_files_matching"]]
        self.repos = sorted(p.name for p in self.root.iterdir()
                            if p.is_dir() and not any(r.search(p.name) for r in sd))
        self._repo_set = set(self.repos)
        self.index = collections.defaultdict(list)   # stem -> [path]
        self.files = {}                               # path -> repo
        for repo in self.repos:
            for dirpath, dirnames, filenames in os.walk(self.root / repo):
                dirnames[:] = sorted(d for d in dirnames if not any(r.search(d) for r in sd))
                for fn in sorted(filenames):
                    if fn.endswith(".py") and not any(r.search(fn) for r in sf):
                        p = pathlib.Path(dirpath) / fn
                        self.index[fn[:-3]].append(p)
                        self.files[p] = repo
        self.ambiguous = collections.Counter()
        self._edges = {}

    def owner(self, stem):
        repos = sorted({self.files[p] for p in self.index.get(stem, [])})
        return repos[0] if len(repos) == 1 else None

    def _resolve(self, stem, src, named):
        cands = self.index.get(stem)
        if not cands or (stem.startswith("__") and stem.endswith("__")):  # "__main__" is a name, not a module
            return [], None
        own = [p for p in cands if p.parent == src.parent]
        if own:
            return own, "import"
        mine = [p for p in cands if self.files[p] == self.files[src]]
        if mine:
            return mine, "import"
        sib = [p for p in cands if self.files[p] in named]
        if sib:
            return sib, "sibling-path"
        if len({self.files[p] for p in cands}) == 1:
            return cands, "unique-name"
        self.ambiguous[stem] += 1
        return [], None

    def edges(self, src):
        if src in self._edges:
            return self._edges[src]
        s = _scan(src)
        named = set()
        for text in s["strings"]:
            for part in re.split(r"[\\/]", text):
                if part in self._repo_set:
                    named.add(part)
        out = []
        for stem in sorted(s["imports"] | s["relative"]):
            ps, how = self._resolve(stem, src, named)
            out += [(p, how) for p in ps]
        if s["dynamic"]:
            for text in sorted(s["strings"]):
                if text in self.index and text not in s["imports"]:
                    ps, how = self._resolve(text, src, named)
                    out += [(p, "dynamic:" + how) for p in ps]
        for text in sorted(s["strings"]):
            if text.endswith(".py"):
                stem = re.split(r"[\\/]", text)[-1][:-3]
                ps, how = self._resolve(stem, src, named)
                out += [(p, "script:" + how) for p in ps]
        self._edges[src] = [(p, how) for p, how in out if p != src]
        return self._edges[src]

    def reach(self, entry_points):
        """Breadth first from each entry point; for each repository reached,
        the shortest chain of (file, how) that first reached it."""
        first = {}
        for ep in entry_points:
            start = (self.root / ep).resolve()
            if start not in self.files:
                raise FileNotFoundError(f"entry point not found or skipped: {ep}")
            seen, queue = {start: [(start, "entry")]}, collections.deque([start])
            while queue:
                cur = queue.popleft()
                repo = self.files[cur]
                if repo not in first or len(seen[cur]) < len(first[repo]):
                    first[repo] = seen[cur]
                for nxt, how in self.edges(cur):
                    if nxt not in seen:
                        seen[nxt] = seen[cur] + [(nxt, how)]
                        queue.append(nxt)
        return {repo: [(str(p.relative_to(self.root)).replace("\\", "/"), how) for p, how in chain]
                for repo, chain in sorted(first.items())}


# ---------------------------------------------------------------------------
# 10. _git_time — when a file was last committed (seconds), else its mtime.
# ---------------------------------------------------------------------------
def _git_time(path):
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%ct", "--", path.name], cwd=path.parent,
                             capture_output=True, text=True, timeout=30).stdout.strip()
        if out:
            return float(out)
    except (OSError, subprocess.SubprocessError):
        pass
    return path.stat().st_mtime


# ---------------------------------------------------------------------------
# 4. evidence — Leighton observations per repository, each tagged with the
#    claim key it bears on. Reached: one observation now. The Saboteur:
#    one per (layer, known gap class), at the gap list's commit time; a
#    layer attacked with no known gap gets one clean observation.
# ---------------------------------------------------------------------------
def evidence(root, graph, reached, weights, now):
    root, ev = pathlib.Path(root), collections.defaultdict(list)
    E = weights["evidence"]

    def obs(kind, ts, note):
        e = E[kind]
        return {"kind": kind, "bears_on": e["bears_on"], "timestamp": ts,
                "value": e["value"], "confidence": e["confidence"], "note": note}

    for repo, chain in reached.items():
        ev[repo].append(obs("reached_on_real_path", now, "via " + chain[0][0]))
    gaps_f = root.joinpath(*GAPS_FILE)
    threats_d = root.joinpath(*THREATS_DIR)
    if gaps_f.exists() and threats_d.is_dir():
        gaps = json.loads(gaps_f.read_text(encoding="utf-8"))["gaps"]
        ts = _git_time(gaps_f)
        attacked, gapped = collections.Counter(), collections.Counter()
        for f in sorted(threats_d.glob("*.json")):
            tool = json.loads(f.read_text(encoding="utf-8")).get("tool", "")
            m = re.search(r"--layer\s+(\S+)", tool)
            if not m:
                continue
            attacked[m.group(1)] += 1
            if f.name in gaps:
                gapped[(m.group(1), gaps[f.name])] += 1
        for module in sorted(attacked):
            repo = graph.owner(module)
            if repo is None:
                continue
            mine = sorted((cls, n) for (mod, cls), n in gapped.items() if mod == module)
            for cls, n in mine:
                ev[repo].append(obs("saboteur_gap", ts, f"{module}: {n} known '{cls}' gap(s)"))
            if not mine:
                ev[repo].append(obs("saboteur_no_gap", ts, f"{module}: {attacked[module]} attacks, no known gap"))
    return dict(ev)


# ---------------------------------------------------------------------------
# 9. _leighton — load P14 Leighton V3 from the sibling layer.
# ---------------------------------------------------------------------------
def _leighton(root):
    p = pathlib.Path(root) / "leighton-engine-layer" / "leighton_engine_v3.py"
    if not p.exists():
        raise FileNotFoundError(f"Leighton V3 not found: {p}")
    spec = importlib.util.spec_from_file_location("leighton_engine_v3", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# 5. judge — λ and a reading for each claim (and a provisional CONFORMS).
# ---------------------------------------------------------------------------
def judge(claims, ev, weights, now, leighton):
    reg = leighton.DomainRegistry()
    for kind, k in sorted(weights["kinds"].items()):
        reg.register(kind, math.log(2) / k["half_life_days"])
    R = weights["readings"]
    out = []
    for c in claims:
        repo, kind = c["entity"], c["kind"]
        keys = [(cl["id"], cl["id"].split("/", 1)[1], cl.get("status"), cl.get("says"),
                 cl.get("expected_dry_run")) for cl in c["claims"]]
        if not any(k == "CONFORMS" for _, k, *_ in keys):
            keys.append((f"{repo}/CONFORMS", "CONFORMS", "provisional", "It conforms to the stack's rules.", None))
        for cid, key, status, says, expected in keys:
            mine = [o for o in ev.get(repo, []) if o["bears_on"] in (key, "ANY")]
            if not mine:
                lam, reading, fallback = 1.0, "unknown", "no evidence"
            else:
                res = leighton.compute_lambda_for_domain(
                    reg, kind, [{k: o[k] for k in ("timestamp", "value", "confidence")} for o in mine],
                    now, now, time_unit=weights["time_unit"])
                lam, fallback = res["lambda"], res["fallback"]
                reading = ("holds" if lam >= R["holds_at_or_above"] else
                           "doubted" if lam <= R["doubted_at_or_below"] else "unknown")
            out.append({"id": cid, "entity": repo, "kind": kind, "key": key, "status": status, "says": says,
                        "lambda": round(lam, 4), "reading": reading, "asked": reading != "holds",
                        "fallback": fallback, "expected_dry_run": expected, "evidence": mine})
    return out


# ---------------------------------------------------------------------------
# 6. dry_run — the whole slice, read only.
# ---------------------------------------------------------------------------
def dry_run(root, weights=None, claims=None, now=None):
    weights = weights or load_weights()
    claims = load_claims() if claims is None else claims
    now = float(now if now is not None else datetime.datetime.now(datetime.timezone.utc).timestamp())
    g = Graph(root, weights)
    reached = g.reach([e["path"] for e in weights["entry_points"]])
    ev = evidence(root, g, reached, weights, now)
    return {
        "dry_run": True, "now": datetime.datetime.fromtimestamp(now, datetime.timezone.utc).isoformat(),
        "weights_version": weights["version"],
        "entry_points": [e["path"] for e in weights["entry_points"]],
        "claims": judge(claims, ev, weights, now, _leighton(root)),
        "repos": {r: {"reached": r in reached, "chain": reached.get(r)} for r in g.repos},
        "ambiguous": dict(sorted(g.ambiguous.items())),
    }


# ---------------------------------------------------------------------------
# 11. _text — the dry run for a person to check by hand.
# ---------------------------------------------------------------------------
def _text(r):
    L = [f"P19 Relevance — DRY RUN ({r['now']}, weights {r['weights_version']}). Nothing is written.", ""]
    L.append("== CLAIMS ==")
    for c in r["claims"]:
        mark = "ASK " if c["asked"] else "    "
        L.append(f"{mark}{c['id']:<32} {c['kind']:<9} λ {c['lambda']:.3f}  {c['reading']}"
                 + ("  (provisional: no confirmed claim)" if c["status"] == "provisional" else ""))
        if c["status"] != "provisional":
            L.append(f"      predicted: {c['expected_dry_run']}")
        for o in c["evidence"]:
            L.append(f"      - {o['kind']} ({o['value']}, {o['confidence']}): {o['note']}")
    L += ["", "== REACHED ON A REAL PATH (check by hand) =="]
    for repo, v in r["repos"].items():
        if v["reached"]:
            L.append(f"  yes  {repo:<24} " + " -> ".join(f"{p} [{how}]" for p, how in v["chain"]))
        else:
            L.append(f"  no   {repo}")
    if r["ambiguous"]:
        L += ["", "== AMBIGUOUS NAMES (no edge drawn; each could hide a missed path) =="]
        L += [f"  {stem} ({n} file(s) import it)" for stem, n in r["ambiguous"].items()]
    return "\n".join(L)


# ---------------------------------------------------------------------------
# 7. main
# ---------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description="P19 Relevance, first slice: a dry run.")
    ap.add_argument("--root", default=os.environ.get("FORGE_LEGACY_ROOT") or str(HERE.parent))
    ap.add_argument("--now", help="ISO time to judge at (default: now, UTC)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        now = datetime.datetime.fromisoformat(a.now).timestamp() if a.now else None
        r = dry_run(a.root, now=now)
    except (OSError, ValueError, KeyError) as exc:
        print(f"relevance: {exc}", file=sys.stderr)
        return 2
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # λ on a Windows console
    print(json.dumps(r, indent=1, ensure_ascii=False) if a.json else _text(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
