---
name: poteto-help
description: Explain the mainart-stack router, the bug-fix path, and the skills included on that path. Answer the question. Do not start the work.
---

# Poteto help

The product is mainart-stack. pstack names the upstream playbook source, not this product.

Answer a help question from the files in core. Do not start the work. Read the file you route to before you quote it, and trust that file when it disagrees with this map.

A message that asks for the work itself, such as "fix this save bug", is not a help question. The router skill poteto-mode owns that request.

## Find out what they need

Infer the need from the message. If it is still unclear, ask one question with these options, then answer only the section they pick:

- How an unscoped request is classified
- How bug-fix runs
- Which included skill fits a situation
- How to word the prompt

Word a prompt from [`references/prompting.md`](references/prompting.md). Example prompts are in [`references/recipes.md`](references/recipes.md). Skills that are not in core are not on this slice. Do not invent a route to one.

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
| Design a bespoke run only when the user asks and the what is already settled | skills/figure-it-out/SKILL.md |
| Stop the repo from repeating one agent mistake | skills/correct/SKILL.md |
| Explain this surface | skills/poteto-help/SKILL.md |

The principle-* skills apply during the playbook, not during Matt HITL. principle-never-block-on-the-human must not suppress clarification.

## Bug-fix

Use bug-fix for a reported defect to reproduce, root-cause, and fix with runtime evidence. The playbook keeps cheap failing-test-first and skips that test when it would be impractical or expensive. It does not call the tdd skill. It does not need a tracker packet before it starts, and it does not need a nested worker.

## Reply

Lead with the answer. Give at most one example prompt, adapted from [`references/recipes.md`](references/recipes.md) when one fits, then the core file the answer came from. Keep it short unless the person asked for the whole map.
