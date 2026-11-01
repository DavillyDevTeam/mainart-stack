---
name: no-comments
description: Review comments in the caller's diff, delete the ones that do not earn their place, and offer a structural encoding for a constraint the code cannot show.
---

# No comments

Request spawn-worker with role comment-sicko. Act on accepted findings.

Defer to that agent's fresh pass. Do not restate its rules in the prompt. This skill runs during a playbook. It does not replace Matt HITL, and principle-never-block-on-the-human must not suppress a clarification the review uncovers.

## Scope

Use the caller's files or diff. Otherwise use the current diff against the base branch, default main, including the working tree.

## Steps

1. Request spawn-worker with role comment-sicko and isolation same-tree. Pass the scope.
2. Inspect its report and diff. Reject application-code edits, scope escapes, exception-protected deletions, misstated MUST KILL reasons, and flags that treat kept intentional code as guilty. Reshape flags on our-code surprises stay actionable. Do not restore those comments. A keep survives only with proof it is about something we cannot change. Audit missed scoped lint and type suppressions. Correctness or safety suppressions stay actionable MUST KILLs. Restore deletions only with exact exceptions and scoped proof. Before accepting a thin IMPORTANT or "do not remove" kill or keep, read the symbol in the surrounding code. If a kill is ambiguous, do not restore. If a keep is refuted or still ambiguous, delete it. Revert and rerun one rejected report with the failure named. Reject a second, report it open, and stop this skill as failed.
3. Fix trivial accepted flags directly by deleting a dead path, dropping a parameter, or using the real API. If a fix needs a new module shape, stop and report that shape as open work. Do not widen the fence to invent the shape here.
4. Implement the smallest root-cause fix in scope. Remove every named workaround. If the root cause is out of scope, land the smallest in-scope fix and report the rest open. principle-fix-root-causes and principle-redesign-from-first-principles guide intent only. Neither authorizes widening the fence nor fixing instances outside it. Never bolt on symptom guards.
5. Constraint comments say "do not remove", "do not change wording", or "talk to someone before changing". Leave keeps about things we cannot change. Offer the cheapest in-scope type, runtime, test, or CI lint. Wait for interactive approval. An unattended run needs the caller's pre-approval. If approved, encode then delete. Otherwise delete, report the constraint open, and sketch the out-of-scope work.
6. Report the deletion count, restored comments, reruns, fixes, encoding offers, encodings, unenforced constraints, and other open work.
