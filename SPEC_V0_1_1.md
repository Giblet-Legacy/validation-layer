# SPEC V0.1.1 — P19 Validation: checklist 2.3.0, decided findings

SPEC_V0_1_1.md — what validate_v0_1_1.py changes over the frozen 0.1.0.

Function:
    James, 2026-11-23: "fix scoring". In checklist 2.2.0, logging any red
    team scored RED TEAM in full and lifted the outside-check cap, whatever
    the review said. Three runs on the stack's own designs went from 65 to
    100 the moment a review saying "don't build this as planned" was logged.
    Checklist 2.3.0-draft fixes it; 0.1.1 carries 2.3.0. SPEC.md stays
    authoritative for everything else. validate_v0_1.py and method_v2_2.json
    are frozen and unchanged.

Version:   SPEC V0.1.1 0.1.1, carrying checklist 2.3.0
Licence:   MSL-1.0
Author:    James Gilbert (Giblets Forge)

---

## 1. The change (checklist 2.3.0)

**RED TEAM** has three states:

| State | Score |
|---|---|
| no reviewer, or no findings | 0 |
| findings logged, but no decision on any (neither "I'm changing" nor "I'm rejecting") | **half** |
| findings with a decision | full |

**A new cap, `undecided` (65):** while a reviewer's findings are
undecided, viability can't go above 65. The reason shown: "A reviewer found
problems you haven't decided on yet."

The outside check still counts, because someone did review it. A review
lifts the score only once its findings are answered.

## 2. Files

| File | What |
|---|---|
| `validate_v0_1_1.py` | 0.1.0's engine with §1. It reads `method_v2_3.json` and `profile_v2_3.json` (private), else `profile_neutral_v2_3.json`. |
| `method_v2_3.json` | Generated from the 2.3.0-draft page by `tools/extract_v0_1.py`. |
| `profile_neutral_v2_3.json` | The neutral profile. Its structure is unchanged from 2.2. |
| `tests/conftest.py` | Points 0.1.0's frozen parity tests at the archived 2.2.0 page, so each version is tested against the page it ports. |
| `tests/test_validate_v0_1_1.py` | 3 tests everywhere; 19 on the laptop. |

The laptop tests are parity with the 2.3.0 page on:
- the 12 synthetic runs;
- 3 red-team states;
- the 3 real runs.

## 3. The real runs under 2.3.0

| Run | 2.2.0 | 2.3.0 | Why |
|---|---|---|---|
| 0001 the layer | 100 | **65** | review logged, findings undecided |
| 0002 lifetime | 100 | **65** | review logged, findings undecided |
| 0003 checkpoints | 100 | 100 | findings decided, verdict PARK |

---

## Document control

- **SPEC V0.1.1 0.1.1**: 2026-11-23, by the VS Code AI on James's "fix
  scoring". Frozen with checklist 2.3.0 the same day (James: "freeze
  commit and push").
