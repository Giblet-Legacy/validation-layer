# PROPOSAL — the validation layer: the James Checklist as part of the stack

PROPOSAL.md — how the James Checklist (v2.2.0-draft) could become the stack's validation layer. Design only; nothing built.

Function:
    James, 2026-11-21: "i think this needs to go in validation layer and be
    a part of the stack ... it could determine if new layers should be
    added, evaluate decisions and responses, help guide ai models, evaluate
    the stack."

    The checklist came out of a failed AI architecture role, where the
    problem was approached as an engineer rather than as a systems
    architect. It asks the architect's questions before anything is built.
    This proposal says what would move into the stack, what must stay
    private, and what the layer would do there. The decisions in §7 are
    James's.

Status:   agreed (James 2026-11-21: "yes to all 6"); built as 0.1.0-dev (SPEC.md)
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)

---

## 1. Why it fits the stack

The checklist already holds the stack's own rules, as questions:

- **Verification first:** the evidence model, F9 ("only self-validated"),
  and VERIFICATION, which can't be skipped.
- **A named human signs off:** OWNERSHIP, GOVERNANCE and the HAL value.
- **Freeze, version, archive:** F8 ("version and naming sprawl") and
  GOVERNANCE's freeze rule.
- **AI answers are assumptions, not facts:** RED TEAM treats a reviewer's
  findings as claims, and evidence starts as Assumption. That is the same
  stance as ai-gate (AI through the gate).
- **Parked on purpose, not abandoned:** the PARK verdict with a revisit
  trigger.
- **One source of truth:** the data block in the HTML, from which the AI
  prompt is generated.

Its own spec already looks ahead to the stack. Run files are keyed by step
"so they can later be wrapped as an sc capsule" (§8.2, deferred to v2.1).

## 2. What must stay private (R9, and personal)

The stack's repositories are public on GitHub. **R9 says nothing from work
goes public.** Today:

| File | Holds | Where it belongs |
|---|---|---|
| `james-checklist.html` | the method, **and** the employer's name in R9's guard words and some wording | the method public; the guard words and personal rules private |
| `architecture-library.json`, `career-move-checklist.txt` and the other past runs | personal and work material (22 mentions in each of the two) | private, never committed |
| `SPEC_james_checklist_v2.md` | names the employer, and James's career direction | private. The layer gets its own SPEC, written without it. |

**The split:**

- **Public, in the layer: the method.**
  - the 32 steps, the modes and the kinds of build;
  - the checks between answers, the flag logic, the viability score and
    the verdict;
  - the report and run-file formats.
- **Private, on James's machine only: a profile.**
  - his Screen rules (R1–R9 wording), his R9 guard words and his standing
    constraints;
  - his past runs and lessons.
  - It would live in `~/.forge/validation/`, beside the agent's turns.
    That is **not** the key folder's contents, just the same home. It is
    never committed.
- Without a profile, the layer runs with neutral rules, so a stranger or
  an AI can use it. With James's profile, it is the James Checklist.

## 3. What the layer would do (James's four aims)

| Aim | How |
|---|---|
| **Decide if a new layer should be added** | Before a new layer or a new major version is built, a run is made: an Architecture kind of build, Full mode. Its report and verdict are kept with the layer's spec. BUILD needs a first slice and a recorded decision; PARK and KILL are answers too. Whether this **advises** or **blocks** is §7.4. |
| **Evaluate decisions and responses** | A small offline engine, `validate_v1.py`, takes a run file (JSON) and returns the Screen, flags, checks, viability and verdict checks. It is deterministic and has no AI in it, so any layer can call it, and the same answers always give the same score. |
| **Guide AI models** | The generated interviewer prompt becomes the stack's standard brief for an AI session working on a design. Its rules (evidence has a source; findings are claims; one option chosen; a kill signal) are the ones the stack already wants. An AI's answers enter as Assumption evidence, the same as ai-gate. |
| **Evaluate the stack** | Retro runs on what exists, the Saboteur, the-legacy and the layers, feed Patterns: which failure modes keep coming back across the stack. Calibrating the viability weights against real outcomes needs exactly these retros. |

## 4. One source of truth, two front ends

- **The HTML stays the tool James uses:** offline, a single file,
  phone-first.
- **Its data block (steps, rules, checks and weights) stays the single
  source of truth.** The Python engine reads it from the HTML, the same way
  the AI prompt is generated from it. There is no second copy to drift.
- **Parity:** tests run the same synthetic runs through the page's logic
  and the Python engine, and the scores and flags must agree. The fixtures
  are synthetic, never James's private runs.

## 5. Where it sits

- **A layer, with a number.** P1–P17 are built, and P18 (Self) is
  proposed. This would be **P19: Validation**. The alternative is a
  consumer; but it judges proposals and does not run on the Legacy's data,
  so it is a layer.
- **Name:** the stack's layer repositories are `<name>-layer`
  (sign-layer, hal-layer and so on). The empty folder is
  `validation_layer`. To keep F8 happy it would be
  `validation-layer` (§7.2).
- **Version:** the checklist is at 2.2.0-draft. The layer starts at
  **0.1.0** and records that it carries checklist 2.2.0. Both freeze on
  James's word.

## 6. Before it can judge the stack

The checklist itself has open items. A gate built on unfrozen rules is F8
in the gate:

- **Awaiting James's freeze:** F9, the viability weights, R4's rewording.
- **R8:** one of James's private rules, still to be redrawn. It goes
  in the profile.
- **T13:** the S24 export test has not been run.
- **The real name:** "after 3 real runs". The validation layer itself
  could be one of the three.

## 7. Decisions for James

1. **The split (§2):** the method public in the layer; the rules, guard
   words and runs private, in `~/.forge/validation/`. Recommended: yes.
2. **The name:** `validation-layer`, to match the other layer
   repositories. Recommended. The empty `validation_layer/` would be
   removed.
3. **The number:** P19 Validation. Recommended.
4. **Advise or block:** does a new layer need a BUILD verdict to be built
   (a gate the agents check), or is the run advice that is recorded but
   never blocks? Recommended: **advise first.** Record a run for each new
   layer for 3 runs, then decide on blocking with evidence. That would be
   the checklist's own rule ("decide when to stop before you start").
5. **First slice:**
   - the engine (`validate_v1.py`), reading the HTML's data block;
   - parity tests;
   - one real run: the checklist on this proposal itself.

   Not in the first slice: blocking, capsule signing, or wiring into the
   agents.
6. **The checklist's open items (§6):** freeze F9, the weights and R4
   before the layer uses them, or carry them as 2.2.0-draft and say so in
   every report.

James, 2026-11-21: "yes to all 6". In 0.1.0 the engine is `validate_v0_1.py`, named for the layer's version; §3 called it validate_v1.
