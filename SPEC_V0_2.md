# SPEC V0.2 — P19 Validation 0.2.0, first slice: relevance (dry run)

SPEC_V0_2.md — the contract for relevance_v0_2.py, the first slice of validation over a lifetime.

Function:
    PROPOSAL_V0_2_1.md §8.4 and §10 made concrete for the first slice:
    the import graph and "reached on a real path", the confirmed claims,
    λ through Leighton V3, all as a DRY RUN that James checks by hand on
    the five claimed layers before anything reaches the daily report.
    0.1.x (validate_v0_1*.py, the checklist engine) is unchanged.

Status:   draft (0.2.0-dev); written 2026-11-24 on James's "validation 0.2.0"
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)

---

## 1. Inputs (all read only)

| Input | What |
|---|---|
| `weights_v0_2.json` | The one weights file (§10.4): kinds and half-lives, the evidence table, the reading thresholds, the entry points, what is skipped. Every number in it is a DRAFT. |
| `claims/<repo>.claims_vN.json` | The confirmed claims, one file per layer and version, never edited; the highest N is used. v1: PURPOSE; v2 adds CONFORMS (James, 2026-11-24). |
| The sibling repositories | `--root`, else `FORGE_LEGACY_ROOT`, else this layer's parent. |
| `the-saboteur/known_gaps_v1_1.json`, `threats_v1/` | Which layer each attack targets and which attacks are known gaps. |
| `leighton-engine-layer/leighton_engine_v3.py` | P14 V3, loaded from the sibling layer, not copied. |

## 2. The import graph

- **Files:** every `.py` in every top-level repository, skipping folders
  matching `skip_dirs_matching` (archives, tests, fixtures, caches) and
  files matching `skip_files_matching` (`test_*`, `conftest.py`). Tests
  are never a real path.
- **Edges**, read with `ast` (nothing is run):
  - `import` and `from … import`, including relative imports;
  - **dynamic:** in a file that uses `importlib` or `__import__`, any
    string literal that is a module name;
  - **script:** any string literal ending in `.py` (a sibling started by
    `subprocess`).
- **Resolution** of a name, in order: the file's own folder; its own
  repository; repositories the file names in any string (a
  `sys.path.insert`, a `FORGE_LEGACY_ROOT` join, a `"<name>-layer"`); any
  repository if exactly one has the name. A name held by several
  repositories, none named, is **ambiguous**: no edge is drawn, and it is
  listed. `__main__`-style names are never edges.
- **Reached** = some file of the repository is reachable from an entry
  point. The shortest chain is printed, each step labelled with how it
  was resolved, so a person can check it.

## 3. Evidence in this slice

| Evidence | When | Bears on |
|---|---|---|
| `reached_on_real_path` | one observation, at the run's time | PURPOSE |
| `saboteur_gap` | one per (attacked module, known gap class), at the gap list's commit time | CONFORMS |
| `saboteur_no_gap` | one per attacked module with no known gap | CONFORMS |

Not in this slice: VPS test results, agent checks, success tests, kill
signals, outside checks, HAL keep seals (their weights are in the file,
unused). A module's repository is found by its name in the graph.

## 4. λ and the reading

- One Leighton domain per kind, `k = ln 2 / half_life_days`, through
  `compute_lambda_for_domain(..., time_unit="days")`. λ is never stored.
- A claim with no evidence is **unknown** at λ 1.00, without calling
  Leighton (it refuses an empty stream).
- **holds** at λ ≥ 1.05; **doubted** at λ ≤ 0.95; otherwise **unknown**.
  Anything not holding is **asked**.
- A claimed layer without a confirmed CONFORMS claim gets a
  **provisional** one, so the Saboteur's evidence is visible. Since claims
  v2 all five layers have a confirmed one.

## 5. Output and exit codes

`python relevance_v0_2.py [--root DIR] [--now ISO] [--json]` prints the
claims (λ, reading, the prediction written before the slice, the
evidence), every repository's reach and chain, and any ambiguous names.
It writes nothing. 0 printed; 2 bad input (an entry point missing or
skipped, a missing file, Leighton not found).

## 6. Tests

`tests/test_relevance_v0_2.py` on a synthetic workspace, with the real
Leighton V3: each wiring kind followed; tests, archives, ambiguity and
`__main__` are not paths; a missing entry point refuses; no evidence is
unknown, not distrusted; reached holds and gaps doubt CONFORMS; the same
inputs give the same result; CLI exit codes; the real weights and claims
load; the latest claims version wins.

## 7. Not yet (later slices, after James has checked the dry run)

The Relevance section in the daily Saboteur report; VPS test evidence; HAL keep seals as answers; the Field view;
entities that are not code.

---

## Document control

- 2026-11-24: drafted with the code by the VS Code AI, on James's
  "validation 0.2.0". Weights, thresholds and entry points are drafts for
  James's review with the first dry run.
- 2026-11-24: James, "yes all commit" after the first dry run: the hand
  check of the five layers accepted; CONFORMS claims confirmed (claims v2);
  weights, thresholds and entry points kept as drafts; committed.
