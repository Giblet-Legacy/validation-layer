# SPEC — P19 Validation (validation-layer)

SPEC.md — the validation layer: the James Checklist's method as part of the stack, judging proposals before they are built.

Function:
    James, 2026-11-21: "i think this needs to go in validation layer and be
    a part of the stack ... it could determine if new layers should be
    added, evaluate decisions and responses, help guide ai models, evaluate
    the stack." Then "yes to all 6" to PROPOSAL.md.

    The layer carries the checklist's method (2.2.0, frozen 2026-11-21)
    and a deterministic engine that scores a run the way the checklist
    page does. James's own rules, guard words and runs stay private
    (§3).

Number:    P19 (P1–P17 built; P18 Self proposed)
Version:   SPEC 0.1.0, carrying checklist 2.2.0
Depends:   Python 3 (engine); Node (parity tests and extraction only, on James's laptop)
Licence:   MSL-1.0
Author:    James Gilbert (Giblets Forge)

---

## 1. What the layer does

| Aim (James) | 0.1.0 | Later |
|---|---|---|
| Decide if a new layer should be added | A run is recorded for each new layer or major version, in `runs/`, and kept with its spec. **Advice, not a gate** (PROPOSAL §7.4). | Decide on blocking after 3 recorded runs. |
| Evaluate decisions and responses | `validate_v0_1.py` scores any run: checks, flags, viability and what the verdict still needs. | Other layers call it. |
| Guide AI models | The checklist's generated interviewer prompt is the brief for an AI design session, and an AI's answers enter as Assumption evidence. | A neutral prompt generated from the method. |
| Evaluate the stack | — | Retro runs on existing layers; Patterns across them. |

## 2. The engine: validate_v0_1.py

    python validate_v0_1.py RUN.json [--profile PATH] [--json]

- **Input:** a run file, the JSON the page writes with "Export .json".
  The steps are matched by key, as the page's `migrate()` does.
- **Output, as the page computes it:**
  - `checks`: the cross-checks between answers, and vague words;
  - `jflags`: F1–F9, WHY3, J-PARK, the James checks' J-codes, R9, INV,
    SCREEN and QUICK;
  - `viability`: score, raw, cap, capWhy, band, the four parts, the
    three biggest gains and every scored item;
  - `evSummary`, `externals`, `screenFails` and `active`.

  Plus `verdictNeeds`: what BUILD, PARK or KILL still lacks.
- **How it is built:** a line-by-line port of the page's `checks()`,
  `jflags()`, `viability()`, `evSummary()` and `externals()` from
  checklist 2.2.0.
  - Every regex is ASCII-mode, as JavaScript's are without the `u` flag.
  - `Math.round` is ported exactly (halves round up).
- **Properties:** no AI, no network, deterministic.
- **Exit codes:** 0 scored; 2 not a run file.

## 3. Method public, profile private

| Part | Holds | Where |
|---|---|---|
| **Method** | steps, modes, kinds of build, Quick's steps, Investigations, failure-mode names, viability weights, verdicts, report format | `method_v2_2.json`, committed. Generated from the page by `tools/extract_v0_1.py`; never edited by hand. |
| **James's profile** | his Screen rules, his R9 guard words, his standing constraints, his James checks (JQ), the interviewer's rules | `~/.forge/validation/profile_v2_2.json`. Private, git-ignored, never published (R9). |
| **Neutral profile** | one generic R9 rule and generic guard words; the method's own checks without James's personal wording | `profile_neutral_v2_2.json`, committed, hand-written. |

- The engine uses James's profile when it exists, and the neutral one
  otherwise. `--profile` overrides.
- The extractor refuses to write a method in which James's guard words
  match anything.
- A test refuses any published file holding the generic markers of
  personal or work material.

## 4. One source of truth

- **The source:** the page's data block (james-checklist.html, on
  James's laptop). The method file and James's profile are generated
  from it.
- **The harness:** `tools/page_harness_v0_1.js` runs the page's own
  script, unchanged, under Node with a stand-in browser. The only
  thing removed is its start-up `render()`. That gives three things:
  - the prompt (`genPrompt()`): reproduced byte for byte before the
    freeze;
  - the data block;
  - the page's own scores for a run.
- **Parity** (`tests/test_parity_v0_1.py`):
  - 12 synthetic runs, covering every branch, are scored by the page and
    by the engine, and must agree exactly;
  - the committed method must equal the page's.

  These tests need the private page and Node, so they run on James's
  laptop and are skipped elsewhere, with the reason given.

## 5. Runs kept by the layer

`runs/NNNN-<label>.run.json` holds the runs on proposals for the stack
itself, which contain no private material.

- **0001: the validation layer itself** (PROPOSAL §7.5).
  - Drafted by the AI from the proposal; James answers the gaps.
  - Scores 65/100, capped at 65: nobody outside James has checked it.
  - Flags: F9, J-CAPSULE, J-REPLACE.
  - The verdict is James's.

## 6. Tests

| File | What | Runs on |
|---|---|---|
| `tests/test_validate_v0_1.py` (8) | the method is checklist 2.2.0; published files hold no private markers; the profile is never committed; the extractor refuses a guarded method; the neutral profile scores the runs; the R9 guard; the verdict rules; the command line | everywhere |
| `tests/test_parity_v0_1.py` (13) | the method matches the page; the engine matches the page on 12 runs | James's laptop |

## 7. Not in 0.1.0

- Blocking new layers.
- Agent wiring (`agent_validation_layer.py`).
- Signing runs as capsules.
- A neutral page.
- Patterns across stack runs.
- The checklist's open items: **R8** (one of James's private rules),
  **T13** (the S24 export test) and the real name (after 3 real runs).

---

## Document control

- **SPEC 0.1.0**: 2026-11-21, by the VS Code AI on James's "yes to all
  6". Frozen 2026-11-22 (James: "yes to all and freeze commit and
  push"). Next: 0.2.0, validation over a lifetime (PROPOSAL_V0_2.md,
  agreed).
