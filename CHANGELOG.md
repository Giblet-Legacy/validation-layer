# CHANGELOG — validation-layer (P19 Validation)

CHANGELOG.md — build history for the validation layer, latest entry at top.

## [v0.1.0-dev] — 2026-11-21 — the checklist joins the stack

### Good
- James: "i think this needs to go in validation layer and be a part of
  the stack", then "yes to all 6" to PROPOSAL.md:
  - the method public and the profile private;
  - the name `validation-layer`;
  - the number P19;
  - advise first;
  - first slice: the engine, parity and one run;
  - freeze the checklist first.
- **The checklist is frozen at 2.2.0** in James's private folder: F9, the
  viability weights and R4's rewording. The draft files are archived
  there, and the prompt was regenerated from the page.
- **`tools/page_harness_v0_1.js`** runs the page's own script under
  Node. Before the freeze it reproduced the existing prompt byte for
  byte.
- **`tools/extract_v0_1.py`** splits the page into `method_v2_2.json`
  (public) and James's profile (`~/.forge/validation/`, private). It
  refuses a method that holds a guarded word.
- **`validate_v0_1.py`**, the engine: a line-by-line port of the page's
  checks, flags, viability and evidence summary, plus the verdict rules.
  Deterministic, with no AI and no network.
- **Parity:** 12 synthetic runs, covering every branch, are scored the
  same by the page and the engine, and the method matches the page.
  Scores range 0–98 and caps 30/65/100; one run trips 14 flags and 14
  checks.
- **Run 0001**, the checklist on this layer: 65/100, capped because
  nobody outside James has checked it. Flags: F9, J-CAPSULE, J-REPLACE.
  The page and the engine agree on it.
- Tests: 21/21 on the laptop (8 run everywhere, 13 need the private page
  and Node).

### Bad
- Parity can only be tested on James's laptop, where the private page
  is. On the VPS those 13 tests are skipped, and say why.
- Run 0001 was drafted by the AI from the proposal. Its outside check,
  red team and verdict are James's to give.
- The neutral profile is hand-written. Only the method is generated.

### Ugly
- The first neutral profile stored its guard regex with backspace
  characters where `\b` belonged, so it matched nothing. The tests caught
  it and it was fixed before any commit.
