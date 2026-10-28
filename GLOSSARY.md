# mainart-stack

A host-agnostic agent operating system: Matt Pocock's packet chain for underspecified product work, Lauren Tan's pstack playbooks for specified engineering, glued at the packet/playbook boundary.

## Language

**mainart-stack**:
This product: the shared core, host adapters, and optional modules.
_Avoid_: pstack, pstack-grok, gstack, pstack-hosts, poteto stack (when naming this product)

**pstack**:
Lauren Tan's upstream plugin at `cursor/plugins/pstack`.
_Avoid_: using this name for mainart-stack

**vendor tree**:
The unmodified git-subtree checkout of pstack, kept as the live upstream link. Distinct from core, which holds rewritten copies.
_Avoid_: overlay, patch, using this tree as the shipped plugin

**core**:
The host-agnostic skills, playbooks, and agent prompts.
_Avoid_: plugin, runtime

**host adapter**:
The runtime glue for one agent host (Grok Build, Claude Code, or Codex).
_Avoid_: port, binding

**module**:
An optional capability pack the router and playbooks may use when present.
_Avoid_: plugin, extension, addon, skill (too broad)

**capability**:
A named slot a module may provide, such as `validation.judge`. The router and playbooks call a capability, never a module by name.
_Avoid_: tool, hook, provider (when naming the slot itself)

**router**:
The mode skill that classifies an unscoped request as Matt HITL or a pstack playbook. Explicit skills and named playbooks skip it.
_Avoid_: poteto-mode (upstream name, unless as an alias)

**packet**:
A Matt tracker ticket: a spec or an implementable slice with acceptance criteria.
_Avoid_: issue (generic), task, work item

**playbook**:
A pstack named procedure for a class of specified engineering work.
_Avoid_: skill (skills are steps a playbook invokes)

**settled what**:
A desired outcome already named tightly enough to build: a `ready-for-agent` packet, or a prompt that already includes a data shape, repro, metric, or acceptance.
_Avoid_: specified work, ready (as the name of the concept)

**product fork**:
A choice about what the product should do or mean: user-visible behavior, domain meaning, or scope.
_Avoid_: engineering choice

**engineering choice**:
A choice about how to implement a settled what: structure, APIs, tests, observed timing or layout.
_Avoid_: product fork, implementation detail (as the name of the concept)
