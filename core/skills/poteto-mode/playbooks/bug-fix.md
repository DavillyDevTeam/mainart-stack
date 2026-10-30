### Bug fix

You own this defect. Plan, review, and verify. The coordinator session is playbook-runner. Delegate the code change to poteto-agent when a step needs a separate pass. Do not spawn another playbook-runner.

Every shipped line traces to runtime evidence. A change that only might help is a hypothesis. When evidence refutes a hypothesis, revert what it motivated. Ship the smallest change the evidence justifies.

Follow `bug-fix.policy.json` for the testing contract. If the work turns into a product fork, stop this playbook and return to Matt HITL. principle-never-block-on-the-human does not apply to that stop.

1. Reproduce the defect on the surface where it happens. Ask the user only after no available surface can reach the target, and state the specific reason. If it will not reproduce directly, synthesize the trigger, tighten the conditions, or add instrumentation until it fires.
2. Binary-search the cause. Form candidate hypotheses and rule them out until one survives. Each pass, take the split that cuts the most remaining problem space and get runtime evidence. When program state is unclear, add instrumentation and read it as the code runs. A long hunt requests the overnight host operation with mode until and a done condition that the surviving mechanism is confirmed. Do not name a host driver. Confirm the surviving mechanism with runtime evidence before the failing test.
3. When the bug has a cheap local test path, write that failing test before any fix. Follow `bug-fix.policy.json`: cheap failing-test-first, then the fix on top. Skip the test when building it would be impractical or expensive, including a heavy integration test or a check whose assertion is unclear. Do not call the tdd skill, and do not ask the user to confirm testing seams again. principle-sequence-verifiable-units is the principle for this order.
4. Plan the fix inside the reproduced mechanism, then request spawn-worker with role poteto-agent to make it. Use model_role xhigh for a hard change and fast for a mechanical edit. Use max when neither applies. Pass a specific scope. On a depth-one host this request comes from the coordinator session, not from another worker.
5. Verify on the same surface. The original repro now passes, and the cheap test passes if step 3 wrote one. Inconclusive, or a pass on a different surface, is not a pass. Flag it. The cheap test shows the branch. It does not by itself show the bug is gone.
6. Stop when the original repro passes on the same surface. The failing test commit lands before the fix commit when step 3 wrote a test. Report what was broken, the root cause, the fix, and how you verified it. Include the failing-then-passing repro output. This playbook does not open a pull request.
