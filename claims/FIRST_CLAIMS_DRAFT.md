# FIRST CLAIMS (draft) — "why it exists" for the first five layers

FIRST_CLAIMS_DRAFT.md — the first claims for P19 Validation 0.2.0 (PROPOSAL_V0_2_1.md §3, §8.3).

Function:
    James, 2026-11-24: "yes to all 5 and draft the claims". These five
    layers were built before 0.1.0, so none has a validation run. For each,
    the first claim, "why it exists", is drafted from its SPEC and marked
    **Assumption** until James confirms it, one by one. Confirming a claim
    makes it the first evidence-bearing claim on that layer; nothing is
    computed until 0.2.0's first slice is built.

Status:   all five CONFIRMED by James 2026-11-24 ("yes to all and commit");
          the confirmed claims are claims/<repo>.claims_v1.json. This draft is kept as the record.
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)

---

## How to answer

For each claim, one of:
- **confirm**: it becomes the claim as written;
- **reword**: give the words; the reworded claim is confirmed;
- **reject**: the layer's reason is something else (say what).

The **expected dry run** column is a prediction written now, before the
first slice exists, so the dry run can be checked against it (§10.2).

## The five claims

### 1. `sign-layer/PURPOSE`: P2 Sign, primitive (365 days)

> **The stack has one rule for signing: a capsule is signed with Ed25519
> over its canonical bytes with `"signature": null`, and any other file
> gets a detached sidecar, so anything the stack makes can be checked
> against a did:key.**

- Source: sign-layer/SPEC.md §1 (the capsule signing rule) and its
  Function ("the capsule signing rule and the detached artefact sidecar
  rule"); SPEC_V2.md (sign_v2, the strict layer, current 2.0.0).
- Expected dry run: **holds.** Reached from the Legacy's boot through
  most layers. If the dry run asks about it, the import graph is broken.

### 2. `store-layer/PURPOSE`: P8 Store, primitive (365 days)

> **The P4 ledger's records are kept in SQLite under the same hash-chain
> and signature rules, so they can be queried fast by seq, hash or
> signer instead of read line by line.**

- Source: store-layer/SPEC.md §1 (the store rule); SPEC_V2_1.md (current
  2.1.0).
- Expected dry run: **used, but doubted.** Reached on a real path (the
  Legacy's live store.db), while the Saboteur's open gaps against it
  (rollback, non-canonical records) count against it until store_v3 and
  checkpoints (P20) land.

### 3. `canon-verify-layer/PURPOSE`: P6 Canon Verify, primitive (365 days)

> **A ledger can be checked by a verifier that imports no other Forge
> layer: it reimplements canonical JSON, SHA-256, did:key decoding and
> Ed25519 itself, so a bug in the layers that write a ledger cannot also
> hide in the one that checks it.**

- Source: canon-verify-layer/SPEC.md §1 (the zero-trust isolation rule)
  and its Function ("the zero-trust, standalone verifier"); SPEC_V2.md
  (agreement with ledger_v2, current 2.0.0).
- Expected dry run: **unknown, not distrusted.** It is rarely on a real
  path by design (it is the auditor), so it should be asked "why is this
  here?", and James's keep answer becomes its evidence.

### 4. `the-saboteur/PURPOSE`: the Saboteur, tool (120 days)

> **The stack's own tools are attacked with mutations, so each one is
> proven to fail loudly, and the next silent pass is found before it
> matters.**

- Source: the-saboteur/README.md ("The Challenge"); SPEC_V1.md and
  SPEC_V1_1.md (the rotation, current 1.1.0).
- Expected dry run: **holds, with fresh evidence**, once the VPS runs
  check_v3 (a slot every 6 hours, a daily report). Until then its
  evidence is laptop runs only.

### 5. `consumer/PURPOSE`: the Consumer runtime, consumer (60 days)

> **A project (a story, a build, a study, a business) can use the Legacy
> to run itself with no code of its own: it is declared in one sealed
> capsule, and the runtime does everything else through the Legacy's
> layers.**

- Source: consumer/SPEC.md Function and §1 (what a consumer is). The SPEC
  is draft 2, not signed off; VERSION is 0.0.0-dev.
- Expected dry run: **a real question.** Nothing is built and there are
  no tests, so there is no real path yet; with a 60-day half-life it
  should be the first genuine "is it still worth it?".

## Open points for James

1. **consumer's kind.** It is the runtime every consumer runs on, which
   is closer to a tool (120 days) than a consumer (60 days). Drafted as
   consumer, as agreed; say if it should be tool.
2. **A claim on something unbuilt.** consumer's claim is about a design.
   Its evidence can only be James's answers until code exists, so it will
   read as unknown whatever happens; that is the point of including it.
3. **Where confirmed claims live.** Proposed: one file per layer in
   `claims/` in this repo (public: stack layers only, R9), written by the
   first slice from this draft. This draft stays as the record.

---

## Document control

- 2026-11-24: drafted by the VS Code AI from each layer's SPEC, on James's
  "yes to all 5 and draft the claims". All five are Assumptions.
- 2026-11-24: James, "yes to all and commit": all five claims confirmed as
  written; consumer's kind is **tool (120 days)**, not consumer; confirmed
  claims live one file per layer in `claims/` (`<repo>.claims_v1.json`).
