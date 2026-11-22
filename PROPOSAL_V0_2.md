# PROPOSAL V0.2 — validation over a lifetime: is it still used, does it still conform, why is it here

PROPOSAL_V0_2.md — the addendum to PROPOSAL.md for P19 Validation 0.2.0. Design only; nothing built.

Function:
    James, 2026-11-21: "it feels more powerful than this ... it has part to
    do with leighton weight and on the program itself: is this being used,
    does it still conform, why is it here, why is it relevant." 0.1.0
    judges a layer once, at birth. This proposes judging it for its whole
    life, with the stack's own primitives, and (§9) not only for the
    stack's layers but for any entity James sets out to build. His answers
    to the first four questions are in §2; the decisions still open are §8.

Status:   agreed (James 2026-11-22: "yes to all"); the plan for 0.2.0, not built
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)

---

## 1. Birth, life, death

| When | Question | Today |
|---|---|---|
| **Birth** | Should we build it? | 0.1.0: a checklist run before code, kept in `runs/` |
| **Life** | Is it used? Does it still conform? Is its reason still true? | Nothing asks. James's memory. |
| **Death** | Should it go? | The checklist's kill signal (RETIREMENT, with a check-by date). Only a person remembers to look. |

0.2.0 adds **life**, and makes **death** something the stack raises
rather than something someone remembers.

## 2. James's answers (2026-11-21)

1. **"Used"** means the **import graph, plus "reached on a real path"**,
   not call counts.
2. **The unit judged** is the **claim**, not the layer as a whole.
3. **Decay is per kind:** a primitive's reason ages slowly, a consumer's
   fast.
4. **Where the question is asked:** **both** the daily Saboteur report and
   the Legacy's Field.

## 3. Claims: what a layer says about itself

A layer's validation run already makes claims. Each becomes a claim with
an id `<repo>/<KEY>`:

| Claim | From the run | Example (this layer) |
|---|---|---|
| Why it exists | PURPOSE, and the real need from the 5 Whys | "the stack had no layer whose job is to judge proposals" |
| Its success test | SUCCESS (a number and a date) | "3 new layers each have a recorded run with a verdict by 2027-02-28" |
| What it was chosen over | DECISION (Chosen, Rejected) | "a Python port, over an ADR template" |
| When it should stop | RETIREMENT (kill signal, check by) | "3 runs with no decision changed, by 2027-02-28" |
| That it conforms | the stack's rules | naming, headers, archive, tests, no private material |

**Layers built before 0.1.0 have no run.** For each one, a first claim,
"why it exists", is drafted from its SPEC's Function paragraph and
marked as **Assumption** until James confirms it. That fits the
checklist's own rule: an assumption is not a fact until it has a source.

## 4. Evidence: what the stack already produces

Each piece of evidence is a Leighton observation `{timestamp, value,
confidence}`:

- a value **above 1.0** supports the claim;
- a value **below 1.0** counts against it;
- the confidence says how much this kind of evidence counts.

| Evidence | Source, already running | Bears on |
|---|---|---|
| **Reached on a real path** | The import graph from the real entry points (the Legacy's boot, the consumer runtime, the VPS check), across the sibling repos. Tests are not a real path. | why it exists, is it used |
| **Its tests pass on the VPS** | check_v3, every 6 hours | it conforms |
| **The Saboteur's attacks on it** | the rotation results, per layer, daily | it conforms; it holds |
| **The agents' checks** | naming, headers, archive (`~/.forge/agents/<repo>/turns.jsonl`) | it conforms |
| **Its success test held or failed** | the checklist retro, after the date | its success test |
| **Its kill signal fired** | the check-by date has passed, and the signal is true | when it should stop |
| **Someone outside James checked it** | external evidence in a run (F9) | any. Counts more than any self-evidence. |

**Silence is not evidence.** A claim with no new evidence decays. That
is Leighton's job, not a penalty.

## 5. λ, per claim: P10, P11 and P14, unchanged

- λ is computed by **P14 Leighton V2's `compute_lambda_for_domain`**. Its
  weighted fusion (P11 V2) fades each observation by e^(−kΔt). With no
  fresh evidence, λ returns to **1.0, "unknown"**: **not distrusted,
  just unknown.**
- **Per kind**, through Leighton's domain registry: one `k` for
  `primitive` (slow) and one for `consumer` (fast), and perhaps a third
  for `tool` (the Saboteur, the agents).
- **λ is never stored**, as P10 requires. It is recomputed from the
  evidence. The same evidence gives the same λ.

What λ means for a claim:

| λ | Reading | What happens |
|---|---|---|
| well above 1.0 | the claim holds, with recent evidence | nothing |
| near 1.0 for longer than its kind's half-life | **unknown**: nobody has used or proven it lately | the question is asked: "Why is this here?" |
| below 1.0 | **doubted**: evidence counts against it (failing tests, a broken rule, a missed success test) | the question is asked, as a doubt |
| kill signal fired | its own stop condition is true | the question is asked: "Your kill signal fired. Stop?" |

**A quiet primitive is not deleted.** canon-verify might be called once
a month and still be essential: it is the auditor. If it drifts to
unknown, the stack asks why it is here. James answers once, with a
reason, and that answer is new evidence.

## 6. The question, and the answer

**The question goes to both places (§2.4):**

- **The daily Saboteur report** (saboteur_report_v1_1, on the VPS)
  gains a **Relevance** section. It holds every claim now unknown,
  doubted or past its kill signal, with its λ and the evidence behind
  it.
- **The Field:** the validation layer writes a read-only
  `relevance.json`, and a later Field view shows each layer's claims
  with their λ. The Field's signed claims are not touched.

**The answer is James's, and signed.** A HAL seal (P15), made on his
laptop where his key is:

- **keep**, with a reason;
- **consolidate**;
- **retire to the archive**;
- or **revise the claim**.

The seal is the strongest evidence a claim can get: a named human
signed it. **Nothing is ever removed automatically** (0.1.0's advise
first).

## 7. Cautions

- **This is still the stack checking itself.** F9 applies: "it is used
  and its tests pass" proves less than one outside check. External
  evidence gets the highest confidence.
- **Usage can be gamed.** That's why "used" means reached from a real
  entry point, not a call count.
- **The weights are judgements.** The value and confidence for each kind
  of evidence, and each kind's k, are guesses until real outcomes
  calibrate them. That is the checklist's own rule for viability.

## 8. Decisions for James

1. **The evidence table:** the values and confidences of §4 as a draft:

   | Evidence | Value | Confidence |
   |---|---|---|
   | reached on a real path | 1.2 | 0.5 |
   | tests pass | 1.1 | 0.3 |
   | tests fail | 0.6 | 0.8 |
   | Saboteur: no new problem | 1.1 | 0.3 |
   | Saboteur: a new problem | 0.6 | 0.8 |
   | agent check fails | 0.7 | 0.6 |
   | success test held | 1.5 | 1.0 |
   | success test failed | 0.5 | 1.0 |
   | kill signal fired | 0.3 | 1.0 |
   | outside check | 1.5 | 1.0 |
   | HAL keep seal | 1.8 | 1.0 |

   Recommended: accept them as **draft weights**, recalibrated after 90
   days of outcomes.
2. **The half-lives:** primitive **365 days**, consumer **60 days**, tool
   **120 days**. Recommended, as a draft.
3. **The first claims for the existing layers:** drafted from their
   SPECs as Assumptions, for James to confirm one by one. Recommended:
   yes, starting with the 5 he cares most about.
4. **The first slice:**
   - the import graph and "reached on a real path";
   - claims from runs and SPECs;
   - λ through Leighton V2;
   - the Relevance section in the daily report.

   Recommended. **Not in the first slice:** the Field view, HAL seals
   for answers, or evidence from agent logs.
5. **Before building:** a checklist run on this proposal (run 0002), as
   0.1.0 did. Recommended. It is drafted alongside, and James gives the
   verdict. Run 0002 was drafted before §9, so it is redrafted once §9's
   decisions are made.
6. **Any entity (§9):**
   - The subject is any entity to build, with the kinds and half-lives
     of §9.3 as drafts.
   - Runs on anything other than the stack's layers stay private.

   Recommended. In the first slice the stack's layers come first; other
   entities follow once the claims and λ work on the layers.

## 9. Any entity to build, not only the stack's layers

James, 2026-11-22: "this should also be in as a way to validate a
entity to build."

The stack's layers are one kind of thing James builds. The substrate (P9)
already holds the rest:
- an **entity** is a name and a free `kind`;
- the Field draws "James Gilbert **is building** SCPBot" as a project orb
  around him (scp-substrate SPEC_V8).

So the subject of validation becomes **any entity to build**:

1. **At birth:** before "James is building X" is claimed, X gets a
   checklist run, in the mode that fits:
   - Full for a project or a layer;
   - Business for a business idea;
   - Career for a personal or career decision.

   The verdict says whether the "is building" claim should be made
   at all:
   - BUILD: make it;
   - PARK: make a "parked" claim, with its revisit trigger;
   - KILL: don't.
2. **For its life:** the run's claims (why X exists, its success test,
   what it was chosen over, its kill signal) attach to entity X, and
   their λ is kept current as in §5.
3. **The kinds of entity, and their decay:**

   | Kind | Half-life (draft) |
   |---|---|
   | primitive | slow (365 days) |
   | tool | 120 days |
   | consumer | 60 days |
   | project | 60 days |
   | product | 60 days |
   | business | 30 days |
   | career decision | 90 days |

   Each kind is a domain in Leighton V2's registry.
4. **The evidence** for an entity that isn't code comes from outside the
   import graph:
   - its success test met or missed (by its date);
   - its kill signal;
   - outside checks (a buyer, a reviewer, someone who hires);
   - James's own signed answers.

   An entity with only self-evidence stays capped (F9), as in the
   checklist.
5. **Where the run lives:**

   | Entity | Where |
   |---|---|
   | the stack's own layers | `runs/` in this public repo |
   | any other entity | private, in `~/.forge/validation/runs/`, beside the profile |

   Business ideas, career decisions and anything near work never come
   here (R9), and never into a claim that leaves the laptop.

**The Field would show more.** Each project orb could carry its λ:
- **bright:** it holds;
- **fading to grey:** unknown, nobody has touched it;
- **marked:** doubted, or its kill signal fired.

So "what am I building, and is it still worth it" becomes something
James can see, not something he has to remember.

---

## Document control

- 2026-11-21: drafted, by the VS Code AI, from James's "it feels more
  powerful than this" and his four answers (§2).
- 2026-11-22: §9 (any entity to build) added, on "this should also be in
  as a way to validate a entity to build". Run 0002 redrafted to cover it.
- 2026-11-22: **agreed**. James: "yes to all" to §8.1–6, with the
  recommendations as written. The weights and half-lives are drafts,
  recalibrated after 90 days.
  - **Still open for the build:** which 5 existing layers get their first
    claims (§8.3).
  - **Also James's:** run 0002's outside check, red team and verdict
    (§8.5), before 0.2.0 is built.

