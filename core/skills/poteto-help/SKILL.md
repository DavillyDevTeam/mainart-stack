---
name: poteto-help
description: Explain the mainart-stack router, the bug-fix path, and the skills included on that path. Answer the question. Do not start the work.
---

# Poteto help

The product is mainart-stack. pstack names the upstream playbook source, not this product.

Answer a help question from the files in core. Do not start the work. Read the file you route to before you quote it.

A message that asks for the work itself, such as "fix this save bug", is not a help question. The router skill poteto-mode owns that request.

## Tokens

The canonical token is mstack. The only alias is poteto-mode. Both classify the same way. There is no mainart token and no router token. The internal skill directory remains poteto-mode. The host adapter owns punctuation and plugin qualification.

## What an unscoped request does

- No settled what. Matt HITL, normally grill-with-docs. Engineering waits.
- A settled reported defect, with a repro, metric, data shape, or acceptance, and no packet. The bug-fix playbook. The router does not create a tracker packet first.
- An explicit HITL skill, or the named bug-fix playbook, stays as the user invoked it.

validation.judge is optional. A missing or disagreeing judge does not block either path and does not override an explicit invocation.

## Skills on this path

| Need | Where to look |
| --- | --- |
| Classify an unscoped request | skills/poteto-mode/SKILL.md, through mstack or the poteto-mode alias |
| Reproduce and fix a reported defect | skills/poteto-mode/playbooks/bug-fix.md |
| Run that playbook | agents/playbook-runner.md, adopted in the coordinator session |
| Write the code change | agents/poteto-agent.md |
| Remove comments that do not earn their place | skills/no-comments/SKILL.md |
| Design a playbook when bug-fix does not fit | skills/figure-it-out/SKILL.md |
| Stop the repo from repeating one agent mistake | skills/correct/SKILL.md |
| Explain this surface | skills/poteto-help/SKILL.md |

The principle-* skills apply during the playbook, not during Matt HITL. principle-never-block-on-the-human must not suppress clarification.

## Bug-fix

Use bug-fix for a reported defect to reproduce, root-cause, and fix with runtime evidence. The playbook keeps cheap failing-test-first and skips that test when it would be impractical or expensive. It does not call the tdd skill. It does not need a tracker packet before it starts, and it does not need a nested worker.

## Reply

Lead with the answer. Name the core file the answer came from. Keep it short unless the person asked for the whole map.
