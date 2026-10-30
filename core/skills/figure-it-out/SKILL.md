---
name: figure-it-out
description: Design an auditable playbook when the user asks for a bespoke run and the what is already settled. An unsettled request stays with Matt HITL.
---

# Figure it out

When the user explicitly asks for a bespoke run, and the what is already settled, design a playbook. The deliverable before any code is the workflow itself. Phases scale rigor to the task, run a hypothesis loop, and leave a decision trail a person can audit later.

Do not use this skill as the fallback for an unscoped request. An unscoped request without a settled what enters Matt HITL at grill-with-docs. This skill runs during playbook execution. A product fork or a should-we question also goes back to Matt HITL. principle-never-block-on-the-human must not suppress that clarification.

## Start

Read the principle skills you will apply. Add the phases below as todos.

## Phase A: Frame

State these before the run starts:

- The definition of done as a falsifiable predicate (principle-prove-it-works).
- Scope, quantified. Rough units and effort, plus the blockers the framing surfaced.
- The rigor level, biased high. One-way doors and high blast radius get more gates. Reversible low-stakes steps get fewer. Rigor is gates and artifacts.

Present the framing before a long run. Reversible engineering proceeds. A product question still waits.

## Phase B: Design the workflow

Decompose the work into atomic units. Sequence the riskiest unknown first. Scaffold and verification come before features (principle-foundational-thinking).

- Build the verification harness before the work. Capture the baseline from the pre-change state.
- When a one-way door decides what the product means, stop and return to Matt HITL. A mechanical shape that is already concrete does not need a design bakeoff (principle-laziness-protocol).
- Parallelize only across seams. Request spawn-worker with isolation isolated for each worker so they do not share one working tree (principle-separate-before-serializing-shared-state).
- Write the phase list down. That list is what the person reviews.

Then execute the design. Run each unit under the Phase C loop, and append a Phase D row as each unit lands.

## Phase C: Run the loop

Each unit is an experiment. State the hypothesis, make the smallest change, measure it against the predicate on the real artifact, keep it if it advanced, and revert it if it did not. Apply principle-sequence-verifiable-units. Verify each unit before the next.

- Verify by inspecting the artifact. When something passes too easily, suspect the observation method.
- A verdict is VERIFIED, NOT VERIFIED, or INCONCLUSIVE. Inconclusive is not a pass.

## Phase D: Keep the audit trail

Keep a short decision log beside the work. Record the hypothesis, the evidence, and whether you kept or reverted the change. Commit the log when a reviewer will need it later.

## Phase E: Verify and hand back

Check the whole result against the Phase A predicate on the real product. Encode a recurring correction as a gate, a lint, a check, or a script (principle-encode-lessons-in-structure).

Reply with the playbook you designed, the rigor level and why, where the decision log is, what is verified against the predicate, and what is still open.
