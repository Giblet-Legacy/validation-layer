# NEXT CLAIMS (draft) — "why it exists" for the six unreached layers

NEXT_CLAIMS_DRAFT.md — claims for the six repositories the first dry run found on no real path.

Function:
    James, 2026-11-24: "draft the claims for the next 6 layers". The
    first dry run (relevance_v0_2.py, 407494d) reached none of
    forge-gate, forge-time, keystone_gate, mediator-layer, seed and
    self-layer from a real entry point. Each gets its "why it exists"
    claim, drafted from its own SPEC, README or header and marked
    **Assumption** until James confirms it. On confirmation each also
    gets the standard CONFORMS claim (the wording in claims v2), as the
    first five did.

Status:   all six CONFIRMED by James 2026-11-24 ("yas all commit"), kinds as drafted;
          the confirmed claims are claims/<repo>.claims_v1.json. This draft is kept as the record.
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)

---

## How to answer

As for the first five, one of these for each claim:
- **confirm**: the claim stands as written;
- **reword**: give the new words, and the reworded claim is confirmed;
- **reject**: the layer exists for another reason (say which).

Each layer also asks a question the first five did not. Once its claim is
confirmed it will read **unknown**, so it gets asked "why is this here?".
What you answer then is its first real evidence: **keep** (and why),
**consolidate**, **park**, or **retire** to the archive. Nothing is
removed automatically.

## The six claims

### 1. `forge-time/PURPOSE`: P16 Time, primitive (365 days), 1.0.1

> **The stack signs one timestamp format (ISO 8601 UTC to the second,
> with a literal Z) and one scp_id rule, kept in one tested copy so that
> no layer or consumer needs its own regex.**

- Source: forge-time/SPEC.md Function and §1–2.
- Found by the dry run: only P17 Mediator imports it
  (`mediator_v1_1.py`: `import forge_time`). ai-gate adds the folder to
  its path but imports nothing from it.
- Expected dry run: **unknown.** It is reached only through Mediator,
  and nothing reaches Mediator.

### 2. `mediator-layer/PURPOSE`: P17 Mediator, primitive (365 days), 1.1.0

> **The stack grows without changing itself: it reads the digests that
> consumers export, judges how mature each reported field is, and
> proposes an unsigned spine update to HAL and James for any field that
> has become Fact. It never merges, signs or edits a layer.**

- Source: mediator-layer/SPEC.md Function and §1.
- Expected dry run: **unknown.** Its input is consumer digests, and no
  consumer is built yet. It will stay unknown until the consumer runtime
  writes its first usage digest.

### 3. `forge-gate/PURPOSE`: The Gate (Tier 4), tool (120 days), 1.0.0

> **Devices sync through one append-only, hash-chained ledger on a relay
> rather than a shared database. Each device pushes signed entries,
> pulls the ones it is missing, verifies them with P6, and replays them
> into its own SQLite.**

- Source: forge-gate/README.md Function and "Why not SQLite over the
  network?"; SPEC.md 1.0.0.
- Expected dry run: **unknown, and a real question.** The README says it
  "does not establish that the gate is deployed or running". The VPS
  today is fed by `sync_legacy_to_vps.py`, which copies whole
  databases, not by the Gate. So the Gate is either the future
  multi-device path or overtaken by the sync script. Its other tie is
  P20: the checkpoint witnesses also want a ledger held off the laptop.

### 4. `keystone_gate/PURPOSE`: Keystone Gate, tool (120 days), 1.1.0

> **Semantic capsules are validated, mutated (merged, split) and their
> lineage tracked under governance, from a capsule primitives registry
> and a cache.**

- Source: keystone_gate/README.md ("A governed semantic-capsule
  validation, mutation, and lineage-tracking system"; "Current
  repository (1.1.0)").
- Expected dry run: **unknown, and a real question.** Its own README
  says that similarity and several mutations are placeholders, and that
  `lineage` and `list` are placeholder commands. It came over from
  the-full-stack, which is now reference only. Nothing on a real path
  loads it (the one apparent link, a `"__main__"` string, was a false
  edge and has been removed).

### 5. `seed/PURPOSE`: the seed, tool (120 days), no VERSION

> **The first claims about James and his repositories, drafted from the
> repositories' own files, are signed into his own Forge one yes at a
> time. Each one goes through the Cockpit's commit path and is sealed
> with HAL, and the passphrase is never stored.**

- Source: seed/sign_seed.py header (there is no README, SPEC or VERSION).
- Expected dry run: **unknown.** It is a one-off bootstrap that you run
  by hand. When every claim in `seed_claims.json` is signed, its job is
  done, so this is the most likely of the six to be **retired** to the
  archive, unless it is kept as the way to sign future seed files.

### 6. `self-layer/PURPOSE`: P18 Self, primitive (365 days), 0.0.0-dev

> **Each repository can explain itself: it finds and cites its own
> files, hands a question about something else to the repository that
> owns it ("not mine, ask X"), and passes the explaining to a model
> through ai-gate, so the answer is an assumption, not a fact.**

- Source: self-layer/DESIGN.md Function and §1 (proposed; the roadmap
  has no P18 yet).
- Expected dry run: **unknown.** It is a design only, waiting on your
  sign-off, with no code and nothing to reach. Like consumer, it is a
  claim about something not yet built.

## Open points for James

1. **Kinds.** forge-time, mediator-layer and self-layer are drafted as
   primitives (P16, P17, P18). forge-gate, keystone_gate and seed are
   drafted as tools. Is that right? keystone_gate could also count as a
   consumer.
2. **P18's number and name.** These are still open from 2026-11-18. The
   claim uses "P18 Self" as the design does.
3. **seed has no VERSION or SPEC.** The claim is drafted from the
   script's header. If you keep seed, it would need a VERSION file at
   least.
4. **The keep/retire questions.** Three of the six look like real
   decisions: forge-gate (overtaken?), keystone_gate (placeholders, from
   the-full-stack) and seed (job done?). Confirming a claim does not
   decide them. The dry run will ask, and you answer then.

---

## Document control

- 2026-11-24: drafted by the VS Code AI from each repository's own files,
  on James's "draft the claims for the next 6 layers". All six are
  Assumptions.
- 2026-11-24: James, "yas all commit": all six confirmed as written, kinds
  as drafted (keystone_gate stays a tool); each with the standard CONFORMS claim.
