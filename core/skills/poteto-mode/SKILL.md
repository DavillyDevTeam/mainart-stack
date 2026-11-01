---
name: poteto-mode
description: The mode skill that classifies an unscoped request as Matt HITL or a pstack playbook. Explicit skills and named playbooks skip it. Canonical invocation is `mstack`; `poteto-mode` is an alias.
---

# Router

The internal skill directory is poteto-mode. Adapters expose the canonical token mstack and the only alias poteto-mode. Both tokens run this skill and classify the same way. There is no mainart alias and no router alias. Adapters own punctuation and plugin qualification.

Read `router-policy.json` in this directory and apply it. Do not invent a second classification table.

## Unscoped requests

A settled what already includes a data shape, a repro, a metric, or an acceptance sufficient to build. This path does not create a tracker packet.

- A settled reported defect, while bug-fix is an included playbook, selects bug-fix. Execute that playbook.
- Any other unscoped request enters Matt HITL at grill-with-docs. Wait for clarification. Do not start engineering.

## Explicit invocation

An explicit HITL skill, or an explicit named playbook that this core includes, is already a classification. Keep it. Do this even when validation.judge disagrees, and even when the prompt looks settled or unsettled.

## validation.judge

Advice from validation.judge is optional. Ask the capability-registry gateway when it is present. If the gateway is missing, the judge is unbound, or the call fails, skip the advice and continue. Advice must not override an explicit invocation, replace the settled-what gate, impose a confidence floor, or block this path.

## Execution

playbook-runner is the worker prompt. poteto-agent is the in-step code-writing delegate. The host places playbook-runner. A depth-one host adopts it in this coordinator session instead of spawning it. Do not assume every host rejects a nested worker. Bug-fix can start without one.

Request spawn-worker only for an in-step delegate such as poteto-agent. A worker must not call spawn-worker.

## Principles and testing

Apply the principle skills during the playbook only. Do not apply them while Matt HITL is clarifying a request. principle-never-block-on-the-human must not suppress that clarification.

Bug-fix keeps its own testing contract in `playbooks/bug-fix.policy.json`: cheap failing-test-first, with an exception when the test would be impractical or expensive. Do not call the tdd skill from the playbook, and do not ask for testing seams to be confirmed again.

## Included on this path

Playbook: bug-fix. Supporting skills: no-comments, figure-it-out, poteto-help, and correct. Agents: playbook-runner and poteto-agent. comment-sicko is the review delegate for no-comments. All twenty-four principle skills are included, and they stay in the playbook phase.
