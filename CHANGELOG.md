# CHANGELOG — validation-layer (P19 Validation)

CHANGELOG.md — build history for the validation layer, latest entry at top.

## [v0.1.0] — 2026-11-22 — frozen; 0.2.0 agreed

### Good
- Frozen (James: "yes to all and freeze commit and push"). Headers say
  `0.1.0 (frozen 2026-11-22)`; VERSION 0.1.0.
- First push: `Giblet-Legacy/validation-layer` on GitHub.
- **PROPOSAL_V0_2.md agreed:** validation over a lifetime.
  - Each layer's, and each entity's, reasons become claims.
  - The stack's own evidence keeps their λ current through Leighton V2,
    with a decay per kind.
  - A claim that goes unknown or doubted is asked about in the daily
    report and the Field.
  - James answers with a signed seal; nothing is removed automatically.
  - It covers any entity James builds; runs on anything other than the
    stack's layers stay private.
- Run 0002, on that proposal, was redrafted for §9 (any entity): 65/100,
  capped, flags F9 and J-CAPSULE.
- Tests: 21/21 on the laptop.

### Bad
- Runs 0001 and 0002 were drafted by the AI and both are self-validated
  (F9). Their outside checks, red teams and verdicts are James's.
- 0.2.0 waits on James's choice of the 5 layers whose claims come first,
  and on run 0002's verdict.

### Ugly
- No ugly items.

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
