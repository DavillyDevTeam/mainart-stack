# Host operations bound by adapter shims

`core/` names required **host operations** as skills every **host adapter** ships: `spawn-worker`, `persist-model-roles`, `overnight`, `ui-proof`. Core Skill-tools those names and never writes `spawn_subagent`, `Task`, `/goal`, or `~/.grok`. The **pin** map is a project file, not a shim. Grok spawn is depth-1: the router / implement-spec session loads **playbook-runner** in-process.

## Considered Options

- **Name: port vs host operation vs capability (chosen: host operation).** Glossary already avoids port as a synonym for host adapter. Capabilities are optional module slots; these are required runtime.
- **Call convention: prose vs host gateway vs adapter shims (chosen: shims).** A second gateway like `capability-registry` cannot keep a host-native body in core. Prose leaves the model to guess native tools.
- **Spawn roles: closed list vs host-native types vs computed from `core/agents` (chosen: computed).** Same computed-set idea as the vendor-tree allowlist. `playbook-runner` is a core agent. [Choose which pstack paths enter core](https://github.com/DavillyDevTeam/mainart-stack/issues/13) can add agents.
- **Grok depth: `max_depth=2` vs never spawn playbook-runner vs flat on Grok (chosen: flat on Grok).** User-guide prose forbids child spawn. Do not bet the spec on `subagents.max_depth`. Claude/Codex adapters may nest. implement-spec fan-out on Grok uses overnight / workflows.
- **Pin file: host user config vs `modules/pins.yaml` vs `.mainart/pins.yaml` (chosen).** `capability-registry` stays host-agnostic. Commit `pins.yaml`; gitignore `.mainart/host`.
- **Overnight: interface-only vs pick Grok driver (chosen: hybrid).** `until` → `/goal`; `every` → durable scheduler `/loop`. `.rhai` workflows are Grok-internal packaging.
- **UI proof: new capability vs fog vs required shim (chosen: `ui-proof` shim).** `validation.judge` remains the only capability in view.
- **Model roles: `fast`/`default`/`strong` vs host ids vs pstack slugs (chosen: `xhigh` / `max` / `fast`).** Opaque **model roles**. Grok `persist-model-roles` writes `[subagents.roles.*]`; setup asks for three model ids.
- **Setup: host-only vs `setup-pstack` vs core `setup` (chosen: core skill `setup`).**

## Consequences

- Shim paths: `hosts/<id>/skills/{spawn-worker,persist-model-roles,overnight,ui-proof}/`. Plugin id is `mainart-stack`; Grok `subagent_type` is `mainart-stack:<agent>`.
- `spawn-worker({ role, prompt, isolation: isolated | same-tree, model_role? })`. Default isolation is `same-tree`. Grok maps `isolated` → worktree and `model_role` → `[subagents.roles.<slug>].model`. Nested `spawn-worker` fails on Grok; a `playbook-runner` role is adopted in-session rather than spawned.
- `overnight({ mode: "until", done })` → Grok `/goal` (span turns for the 8-continuation cap). `overnight({ mode: "every", interval, prompt })` → durable scheduler `/loop`. None of the Grok drivers resume after process death.
- `ui-proof` returns `{ ok, evidence_paths, error? }`. A playbook step that requires proof fails closed on error; other call sites skip. Grok binds MCP + hooks.
- Core `setup` writes `.mainart/host`, Skill-tools `persist-model-roles`, and copies `hosts/<id>/pins.yaml` when `.mainart/pins.yaml` is missing. Host ids: `grok` | `claude` | `codex`.
- Pin merge: top-level capability → module id, then `hosts.<id>` overlay for the current `.mainart/host`. Empty/missing file is unique auto-bind. `capability-registry` never opens `~/.grok` or `CLAUDE.md`.
- Invocation: core uses directory names. HITL skills and the router are user-invocable with implicit invoke off. `setup` may auto-invoke. Shims and playbook-step skills are Skill-tooled, not slash front doors. Adapters own `/plugin:name` vs `$skill` vs `@`.
- Manifests (`.grok-plugin/`, `.claude-plugin/`, Codex `plugin.json`) live under `hosts/<id>/`. This map does not write them.
- Amends ADR-0002: a playbook-runner is the worker *prompt*; Grok hosts it in-session.
