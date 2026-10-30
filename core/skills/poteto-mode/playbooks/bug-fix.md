### Bug fix

You own this defect. Plan, review, and verify. The coordinator session is playbook-runner. Delegate the code change to poteto-agent when a step needs a separate pass. Do not spawn another playbook-runner.

Every shipped line traces to runtime evidence. A change that only might help is a hypothesis. When evidence refutes a hypothesis, revert what it motivated. Ship the smallest change the evidence justifies.

Follow `bug-fix.policy.json` for the testing contract. If the work turns into a product fork, stop this playbook and return to Matt HITL. principle-never-block-on-the-human does not apply to that stop.

1. Reproduce the defect on the surface where it happens. When it is visible in a UI, request ui-proof and use the returned evidence paths. Ask the user only after that surface cannot reach the target, and state the specific reason. If it will not reproduce directly, synthesize the trigger, tighten the conditions, or add instrumentation until it fires.
2. Binary-search the cause. Form candidate hypotheses and rule them out until one survives. Each pass, take the split that cuts the most remaining problem space and get runtime evidence. When program state is unclear, add instrumentation and read it as the code runs. Confirm the surviving mechanism with runtime evidence before writing the fix.
3. Plan the fix. Keep it inside the reproduced mechanism. Request spawn-worker with role poteto-agent for the code change. Use model_role xhigh for a hard change and fast for a mechanical edit. Use max when neither applies. Pass a specific scope. On a depth-one host this request comes from the coordinator session, not from another worker.
4. Verify on the same surface. The original repro now passes. Inconclusive, or a pass on a different surface, is not a pass. Flag it. Unit tests show branch behavior. They do not by themselves show the bug is gone.
5. Stage the commits so the failing repro lands before the fix. Use the cheap failing-test-first cadence from `bug-fix.policy.json` when the bug has a cheap local test path: the failing test first, then the fix on top. Skip that test when building it would be impractical or expensive, including a heavy integration test or a check whose assertion is unclear. Do not call the tdd skill, and do not ask the user to confirm testing seams again. principle-sequence-verifiable-units is the principle for this order.
6. Stop when the original repro passes on the same surface. Report what was broken, the root cause, the fix, and how you verified it. Include the failing-then-passing repro output. This playbook does not open a pull request.
