# validation-layer — P19 Validation

README.md — the stack's validation layer: ask the architect's questions before a new layer is built.

Function:
    The James Checklist's method (2.2.0) as part of the stack, with an
    offline engine that scores a run exactly as the checklist page does.
    It grew out of a failed AI architecture role, where the problem was
    approached as an engineer and not as a systems architect. It asks
    why, who for, what it's worth, how it fails, what it replaces and
    who else has checked it, before code.

Number:   P19
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
Status:   0.1.0-dev, carrying checklist 2.2.0

## Score a run

    python validate_v0_1.py runs/0001-validation-layer.run.json

You get:

- viability out of 100, with the cap that applies, the four parts and the
  three biggest gains;
- the flags and the checks between answers;
- what the verdict still needs.

A run file is what the checklist page saves with **Export .json**.

## What's here

| File | What |
|---|---|
| `validate_v0_1.py` | The engine: checks, flags, viability and verdict rules. No AI, no network. |
| `method_v2_2.json` | The method: 32 steps, modes, weights. Generated from the page; never edit by hand. |
| `profile_neutral_v2_2.json` | Neutral rules for anyone. James's own profile is private (below). |
| `tools/page_harness_v0_1.js` | Runs the checklist page's own script under Node: its prompt, its data, its scores. |
| `tools/extract_v0_1.py` | Splits the page into the public method and James's private profile. |
| `runs/` | Runs on proposals for the stack itself. 0001 is this layer. |
| `SPEC.md`, `PROPOSAL.md` | What it is, and the design James agreed. |

## Private by design

James's Screen rules, R9 guard words, standing constraints and past runs
never come here (R9: nothing from work goes public). They live in
`~/.forge/validation/profile_v2_2.json`, made by:

    python tools/extract_v0_1.py "<path to james-checklist.html>"

## Tests

    python -m pytest -q tests

- **Everywhere:** 8 tests.
- **On James's laptop:** 13 more, which check the engine against the
  page itself. They need the private page and Node, and skip elsewhere.
