# Inventory of upstream pstack

Snapshot of Lauren Tan's **pstack** as it exists in `cursor/plugins` at the commit this note pins. mainart-stack will take this tree via git subtree or submodule, then strip Cursor-specific APIs so they do not leak into host-agnostic **core**.

This is a read of the published sources. It does not decide subtree vs submodule, and it does not implement product code.

## Snapshot

| Field | Value | Source |
|---|---|---|
| Host repo | [`cursor/plugins`](https://github.com/cursor/plugins) (`main`) | [repo README](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/README.md) |
| Path in repo | `pstack/` (one plugin directory among many) | [plugins table](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/README.md) |
| Homepage | https://github.com/cursor/plugins/tree/main/pstack | [`plugin.json`](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/pstack/plugin.json) |
| Author | Lauren Tan | both manifests; [LICENSE](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/pstack/LICENSE) |
| Version | **0.15.20** | [`plugin.json`](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/pstack/plugin.json), [`.cursor-plugin/plugin.json`](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/pstack/.cursor-plugin/plugin.json) |
| Pinned commit | `1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def` | [commit](https://github.com/cursor/plugins/commit/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def) |
| Commit subject | `chore(pstack): bump to 0.15.20 (#581)` | same |
| Commit time | 2026-10-12T08:10:51Z | same |
| Commit author | lauren `<poteto@users.noreply.github.com>` | same |
| `pstack/` tree SHA | `1dbec20ada6e40cb12774b8893960a558319fd6b` | GitHub contents API for `pstack` at that commit; `git rev-parse HEAD:pstack` |
| Files in `pstack/` | 167 (160 non-image) | tree listing at that commit |
| Default branch HEAD | same SHA as the pin (fetched 2026-10-12) | `git ls-remote origin HEAD` |

The bump commit itself only edits the two version fields in the manifests. The rest of the tree is whatever `main` already had at that SHA.

There is **no standalone pstack git repository**. pstack is a subdirectory of the Cursor plugins monorepo. The parent README says each plugin is "a standalone directory at the repository root with its own `.cursor-plugin/plugin.json` manifest."

## License

**Confirmed MIT**, copyright Lauren Tan 2026.

The file [`pstack/LICENSE`](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/pstack/LICENSE) is the standard MIT text:

> MIT License
>
> Copyright (c) 2026 Lauren Tan

The grant is unrestricted use, copy, modify, merge, publish, distribute, sublicense, and sell, provided the copyright notice and permission notice are included in all copies or substantial portions.

Both manifests declare `"license": "MIT"`:

- [`pstack/plugin.json`](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/pstack/plugin.json) (agent-plugins.org schema)
- [`pstack/.cursor-plugin/plugin.json`](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/pstack/.cursor-plugin/plugin.json) (Cursor marketplace). Cursor's [`plugin.schema.json`](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/schemas/plugin.schema.json) defines `license` as an SPDX identifier.

The [pstack README](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/pstack/README.md) ends with `MIT`.

The **parent repo has no LICENSE file** and GitHub reports `"license": null` on `cursor/plugins`. Taking files from *other* plugin directories in that monorepo is a separate license question. Taking `pstack/` is covered by `pstack/LICENSE`.

MIT does not block a host-agnostic extract. It does require keeping the copyright notice with any copy of the Software that lands in mainart-stack.

## Dual manifests

pstack ships two plugin manifests.

| File | Schema | What it declares |
|---|---|---|
| [`pstack/plugin.json`](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/pstack/plugin.json) | `$schema`: `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json` | `name`, `version`, `description`, `author`, `homepage`, `repository`, `license`, `keywords`. No `skills` or `agents` paths. |
| [`pstack/.cursor-plugin/plugin.json`](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/pstack/.cursor-plugin/plugin.json) | Cursor marketplace (see repo `schemas/plugin.schema.json`) | Same identity fields plus `displayName`, `logo`, `category`, `tags`, `"skills": "./skills/"`, `"agents": "./agents/"`. |

`.cursor-plugin/` is Cursor marketplace glue. `plugin.json` is the portable Agent Plugins identity. core should not keep the Cursor marketplace manifest.

## Layout of `pstack/`

```
pstack/
  LICENSE
  README.md
  plugin.json                          # agent-plugins.org
  .cursor-plugin/plugin.json           # Cursor marketplace
  .gitignore                           # node_modules, .DS_Store, *.log
  agents/
    poteto-agent.md
    comment-sicko.md
  assets/logo.png
  automations/benny/                   # dormant Cursor automations, not slash skills
  docs/guide/                          # 10-page user guide + images
  skills/                              # 52 skill directories, each with SKILL.md
    poteto-mode/
      SKILL.md                         # router; mode: true
      playbooks/                       # 23 playbooks
      references/bugbot-triage.md
      scripts/                         # bun CLIs: orch, watch-pr, check-plan, worktree-audit
```

Install, per README: `/add-plugin pstack`. First-run: `/setup-pstack`, then `/poteto-mode`.

## Skills (52)

Every registered skill lives at `skills/<dir>/SKILL.md`. 24 of them are `principle-*`. 28 are workflow / style / setup.

All but one set `disable-model-invocation: true` in YAML frontmatter. The exception is [`setup-pstack`](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/pstack/skills/setup-pstack/SKILL.md), which has no such key. [`poteto-help`](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/pstack/skills/poteto-help/SKILL.md) states the consequence: "Only `/setup-pstack` loads from the user's words."

[`poteto-mode`](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/pstack/skills/poteto-mode/SKILL.md) is the only skill with Cursor Custom Mode frontmatter: `mode: true`, `icon: crown`, `color: yellow`, plus a `reminder` string.

[`typescript-best-practices`](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/pstack/skills/typescript-best-practices/SKILL.md) is the only skill with a `paths` glob: `["**/*.ts", "**/*.tsx"]`.

Benny's three `SKILL.md` files also set `disable-model-invocation: true`, but they are **not** registered slash skills (see Automations).

### Router, setup, help

| Directory | Frontmatter `name` | Role |
|---|---|---|
| `poteto-mode` | `Poteto Mode` | Default entry. Matches a playbook, copies its steps into a todo list, routes other skills. Cursor Custom Mode. |
| `poteto-help` | `poteto-help` | Onboarding / which-skill map. Runs only when typed. |
| `setup-pstack` | `setup-pstack` | Detects Task-tool model slugs, writes `~/.cursor/rules/pstack-models.mdc`. Auto-invocable. |
| `figure-it-out` | `figure-it-out` | Designs a bespoke playbook when no bundled one fits. |

### Workflow skills (the steps playbooks invoke)

| Directory | Frontmatter `name` | Role (from description / README table) |
|---|---|---|
| `how` | `how` | Walkthrough of how a subsystem works. Spawns `generalPurpose` Task subagents, `readonly: true`. |
| `why` | `why` | Design rationale. Discovers Cursor MCPs, fans investigators. `generalPurpose`, `readonly: false` because "readonly strips MCP". |
| `recall` | `recall` | Rebuild recent context from `~/.cursor/projects/<slug>/agent-transcripts/`. |
| `ketchup` | `ketchup` | Catch the user up on this chat since their last message. |
| `blast-radius` | `blast-radius` | What else a small change could break, proven by running code. |
| `architect` | `architect` | Types / signatures / module shape before code that crosses a function boundary. |
| `arena` | `arena` | N parallel candidates, pick a base, graft. |
| `swarm` | `swarm` | N parallel workers (`environment: "cloud"`), one report. |
| `interrogate` | `interrogate` | Multi-model adversarial review. `subagent_type: generalPurpose`, `readonly: true`. |
| `tdd` | `tdd` | Failing test first when the path is cheap. |
| `no-comments` | `no-comments` | Spawn `comment-sicko`, act on accepted findings. |
| `unslop` | `unslop` | Strip AI tells from prose. |
| `technical-writing` | `technical-writing` | Diátaxis + Google developer style + STE + Global English. |
| `typescript-best-practices` | `typescript-best-practices` | Type-system-discipline in TS syntax. Auto-attaches on `*.ts` / `*.tsx`. |
| `benchmark-checklist` | `benchmark-checklist` | Vet a measured number before reporting it. |
| `create-verification-skill` | `create-verification-skill` | Generate `.cursor/skills/verify-<app>/`. |
| `maintain-verification-skill` | `maintain-verification-skill` | Bring that verify skill's feature map back in line. |
| `show-me-your-work` | `show-me-your-work` | TSV decision trail. Audits against `agent-transcripts/`. |
| `reflect` | `reflect` | Mine the active transcript into skill edits. |
| `correct` | `correct` | Make repeated agent mistakes impossible (architecture → types → lint → tests → docs last). |
| `teach` | `teach` | Runs how + why, explains plainly. |
| `automate-me` | `automate-me` | Draft a personal `-mode` skill from transcripts via Cursor `create-skill`. |
| `bro` | `bro` | Restate the last message in plain language. |
| `make-bot-ui` | `Make Bot UI` | Page whose buttons wake a Grok Bot webhook. Cursor Routines / Tailscale. |

### Principles (24)

Indexed inline in `poteto-mode` and shipped as leaf skills so other skills can reference a principle by name. Groups and one-line rules are from the [README principles table](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/pstack/README.md) and the [inline index](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/pstack/skills/poteto-mode/SKILL.md).

**Core:** `principle-laziness-protocol`, `principle-foundational-thinking`, `principle-redesign-from-first-principles`, `principle-attack-the-premise`, `principle-subtract-before-you-add`, `principle-minimize-reader-load`, `principle-outcome-oriented-execution`, `principle-experience-first`, `principle-exhaust-the-design-space`, `principle-build-the-lever`.

**Architecture:** `principle-model-the-domain`, `principle-boundary-discipline`, `principle-type-system-discipline`, `principle-make-operations-idempotent`, `principle-migrate-callers-then-delete-legacy-apis`, `principle-separate-before-serializing-shared-state`.

**Verification:** `principle-prove-it-works`, `principle-fix-root-causes`, `principle-sequence-verifiable-units`, `principle-test-behavior-not-implementation`, `principle-explain-the-number`.

**Delegation:** `principle-guard-the-context-window`, `principle-never-block-on-the-human`.

**Meta:** `principle-encode-lessons-in-structure`.

`principle-never-block-on-the-human` is the rule the map already refuses to average with Matt's grill-until-empty. It is a first-class pstack skill, not a side note.

## Playbooks (23)

Playbooks are **not** slash skills. They are markdown step lists under [`skills/poteto-mode/playbooks/`](https://github.com/cursor/plugins/tree/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/pstack/skills/poteto-mode/playbooks). `/poteto-mode` matches one, copies its steps verbatim into a todo list, and invokes Opening a PR at the end of every other playbook.

The README calls this "twenty-three playbooks." The files:

| File | Title | For |
|---|---|---|
| `investigation.md` | Investigation | Read-only question. |
| `bug-fix.md` | Bug fix | Reproduce, root-cause, fix with runtime evidence. |
| `perf-issue.md` | Perf issue | Measured slowness against a baseline. |
| `hillclimb.md` | Hillclimb | Sustained metric improvement, one commit per accepted win. |
| `runtime-forensics.md` | Runtime forensics | Live symptom diagnosis (not a fix). |
| `trace-forensics.md` | Trace forensics | Diagnosis from a captured profile artifact. |
| `feature.md` | Feature | New or changed behavior from a named data shape. |
| `refactoring.md` | Refactoring | Behavior-preserving structure change. |
| `prototype.md` | Prototype | Throwaway sketch to settle a fork by observing it. |
| `visual-parity.md` | Visual parity | Pixel-exact UI equivalence. |
| `authoring-a-skill.md` | Authoring or modifying a skill | Writing a `SKILL.md` via Cursor's built-in `create-skill`. |
| `eval.md` | Eval | Blind test of a skill/prompt change against transcripts. |
| `babysit.md` | Babysit | Drive a PR/stack to merge-ready. Supersedes Cursor's built-in `/babysit`. |
| `shipping.md` | Shipping | Independent per-PR verdict, then land the contiguous verified run. |
| `autonomous-run.md` | Autonomous run | Drive a long task to a predicate; uses Cursor `/loop`. |
| `orchestrate.md` | Orchestrate | Multi-day coordinator chat, fleets of cloud subagents, `scripts/orch`. |
| `autopilot-full.md` | Autopilot-full | Independent PRs to merged, one owner per PR. |
| `autopilot-stack.md` | Autopilot-stack | Linear base-branch stack the operator lands. |
| `session-pickup.md` | Session pickup | Resume from transcript, cloud-agent URL, or branch. |
| `pause-safely.md` | Pause safely | Clean stop for resume (explicit pause, Cursor restart, compaction). |
| `multi-phase-plan.md` | Multi-phase or multi-PR plan | Plan is the deliverable. Does not implement. |
| `worktree-cleanup.md` | Worktree and simulator cleanup | Prune git worktrees (including `.cursor/worktrees/…`) and simulators. |
| `opening-a-pr.md` | Opening a PR | Invoked at the end of every other playbook. Runs `/deslop` from cursor-team-kit. |

Large or cross-cutting work routes to the **figure-it-out** skill even when Feature would fit. Standing multi-day programs route to Orchestrate, not Autonomous run.

## Agent prompts

Registered via `.cursor-plugin/plugin.json` `"agents": "./agents/"`.

### `poteto-agent`

Source: [`agents/poteto-agent.md`](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/pstack/agents/poteto-agent.md).

Frontmatter:

```yaml
name: poteto-agent
description: Delegate subagent for code-writing and helper tasks spawned during a `/poteto-mode` run. …
is_background: true
```

Body (entire prompt after the heading): the delegate must read `poteto-mode`'s `SKILL.md` in full, including the inline Principles index, before any work, and navigate to a leaf `principle-*` skill when applying a principle. Substituting `generalPurpose` skips that read and drifts.

[`poteto-mode` Subagents](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/pstack/skills/poteto-mode/SKILL.md) requires `subagent_type: "poteto-agent"` for playbook-step delegates, and forbids spawning `poteto-agent` to run the playbook itself. Routed skills (`how`, `why`, `interrogate`, `reflect`, `swarm`) set their own `subagent_type` (usually `generalPurpose`) and must not be overridden to `poteto-agent`.

### `comment-sicko`

Source: [`agents/comment-sicko.md`](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/pstack/agents/comment-sicko.md).

Frontmatter: `name: comment-sicko`. No `is_background`.

Read-only comment reviewer. First output must be exactly `Yes... Ha ha ha... Yes!`. Invoked through `/no-comments` as `subagent_type: "comment-sicko"`, which then inspects the report and applies accepted deletions. Keep-list is license headers, foreign-gotcha comments, `// prettier-ignore`, public-API doc comments, and issue/RFC links. Everything else is deleted. It does not write application code.

## Scripts under `poteto-mode`

[`skills/poteto-mode/scripts/package.json`](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/pstack/skills/poteto-mode/scripts/package.json) names the package `@cursor-skill/poteto-mode-tools`. Private. ESM. Tests via **bun**. Runtime dep: `commander@14.0.0`.

| Script | Role |
|---|---|
| `bootstrap.ts` | Idempotent `bun install --frozen-lockfile` keyed off `package.json` + `bun.lock`. Uses `Bun.spawnSync`. |
| `orch/orch.ts` + `store.ts` | Orchestrate bookkeeping CLI. Playbook: agents spawn only through the Task tool; state goes through this CLI. |
| `watch-pr/` | GitHub PR watcher used by Babysit. GitHub-specific; playbook says do not pretend it covers Origin. |
| `check-plan.mjs` | Plan checker (used with `/loop` in tests). |
| `worktree-audit.sh` | Read-only classifier of git worktrees. Transcript dir hardcoded to `~/.cursor/projects/<slug>/agent-transcripts`. |

These are host-runtime tools, not playbook prose. They assume bun and, in the audit script, Cursor transcript layout.

## Docs

[`docs/guide/`](https://github.com/cursor/plugins/tree/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/pstack/docs/guide) is a 10-page user guide (setup through recipes). It is Cursor-user documentation: `/add-plugin`, Custom Modes, `/loop`, cloud subagents, Cursor Projects. Useful as intent, not as core.

## Not shipped in pstack (hard references)

The README section "not shipped here" and `poteto-mode` Non-negotiables name dependencies that live outside this tree:

| Name | Where it lives | What pstack does with it |
|---|---|---|
| `/deslop` (`deslop` skill) | `cursor-team-kit` plugin | Required before commit / Opening a PR / Autopilot slop-strip. |
| `control-cli` | `cursor-team-kit` | CLIs and TUIs. Shipping, Orchestrate, multi-phase plan. |
| `control-ui` | `cursor-team-kit` | Browser / Electron / web. Same playbooks. |
| `/create-skill` | Cursor built-in | Authoring-a-skill playbook; automate-me; reflect. |
| `/babysit` (built-in) | Cursor built-in | Explicitly superseded by the babysit playbook. |
| `/loop` | Cursor built-in | Autonomous run, overnight, babysit `drive`. |
| Plan Mode | Cursor built-in | README: pstack has no planning skill; Cursor's plan mode "works great with pstack." |

`cursor-team-kit` is a sibling directory in the same monorepo, not a file pstack vendors.

## Automations (benny)

[`automations/benny/`](https://github.com/cursor/plugins/tree/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/pstack/automations/benny) is a dormant pack. README: "its files are not registered as slash skills."

Setup copies the pack to `<target>/.cursor/automations/benny/`, enables pstack in `.cursor/settings.json`:

```json
{ "plugins": { "pstack": { "enabled": true } } }
```

and keeps user config outside the pack (e.g. `.cursor/benny/`). Entry is "point Cursor at `FOR_AGENTS.md`." Live prompts are Cursor automations, drafted through `/automate`. This whole subtree is Cursor automation runtime. It is not core material.

## Cursor-specific APIs and tool names (must not leak into core)

These strings are the host contract. core may keep the *procedure* (playbook steps, principle rules, comment-sicko keep-list). It must not keep the *tool names, paths, frontmatter keys, or slash commands* below. Those belong in a Cursor host adapter, or they get rewritten to host-agnostic capabilities.

### Task tool (Cursor subagent spawn)

Named as **`Task`** / **`Task tool`**. Parameters actually used in this tree:

| Parameter | Values used | Where |
|---|---|---|
| `subagent_type` | `"poteto-agent"`, `"comment-sicko"`, `generalPurpose` | poteto-mode, no-comments, how, why, interrogate, reflect, swarm, multi-phase-plan |
| `model` | Cursor slugs, or omitted for `auto` / `inherit-parent` | setup-pstack role table; every fan-out skill |
| `readonly` | `true` (how, interrogate) / `false` (why, reflect; "readonly strips MCP") | how, why, interrogate, reflect |
| `run_in_background` | `true` (default for every Task call in poteto-mode) | poteto-mode Subagents; arena; swarm |
| `environment` | `"cloud"` or `"local"` | swarm; orchestrate |
| `cloud_base_branch` | non-default pushed branch for a cloud worker | swarm |

Defaults from poteto-mode: `run_in_background: true`, agent mode, file pointers not inlined context, `grok-4.7-xhigh-fast` for code, `claude-opus-5-5-xhigh` for prose and judgment. Those slugs are Cursor model ids.

`generalPurpose` is Cursor's built-in subagent type. pstack treats using it in place of `poteto-agent` as drift.

### Other Cursor tools named in skills

| Tool / protocol | Used as | Where |
|---|---|---|
| `AskQuestion` | Structured multi-choice. `allow_multiple: true` on automate-me. Prefer over free text on setup-pstack. poteto-mode classifies before asking. Autonomous run forbids it. | setup-pstack, automate-me, poteto-mode, autonomous-run |
| `SendToUser` / `type: secret-request` | Secret card for webhook sender key. The agent never sees the value. | make-bot-ui |
| `update_state` | `target: routine`, `action: create`, webhook trigger. Confirm card. | make-bot-ui |
| `Read`, `Grep`, `Glob`, `Shell` | Named as the tools subagent prompts should use. | how explainer prompt; interrogate rubric; reflect reviewers |
| Todo list | "Open a todolist whose first items are the matched playbook's steps." | poteto-mode Playbooks; swarm; arena |

### Cursor slash commands and product features

| Name | Kind | Notes |
|---|---|---|
| `/add-plugin pstack` | Install | README, guide, poteto-help. |
| `/loop` | Built-in wake loop | Autonomous run, overnight, babysit. "not a pstack skill." |
| `/create-skill` | Built-in skill author | authoring-a-skill, automate-me, reflect. |
| `/in-cloud` | Cloud subagent | [guide 02](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/pstack/docs/guide/02-poteto-mode.md). |
| `/automate` | Cursor automations | Benny setup. |
| Custom Mode | `mode: true` + Option+Enter / Alt+Enter | https://cursor.com/docs/skills. Keeps `/poteto-mode` on across turns. |
| Plan Mode | Cursor built-in | README: pstack has none. |
| Cursor Projects | Persistent coordinator thread | [guide 07](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/pstack/docs/guide/07-overnight.md), Orchestrate. |
| Cloud subagents | VM-isolated workers | `environment: "cloud"`; https://cursor.com/docs/subagents#cloud-subagents |
| Bugbot | Cursor agentic security review | poteto-mode trigger; `references/bugbot-triage.md`; babysit / autopilot. |
| Origin CLI | `command -v origin` then `origin pr …` | babysit, shipping, autopilot. Cursor Origin. Never require Graphite (`gt`) in babysit; Orchestrate still treats `gt` as authoritative for stack tracking. |
| Grok Bot / Routines | `https://api2.cursor.sh/automations/webhook/<id>` | make-bot-ui. UI: Cmd+Shift+I, Routines list. |

### Cursor filesystem / config layout

| Path | Written or read by |
|---|---|
| `~/.cursor/rules/pstack-models.mdc` | setup-pstack (`alwaysApply: true`). Read by how, why, arena, swarm, architect, interrogate, reflect, poteto-help. |
| `~/.cursor/projects/<slug>/agent-transcripts/` | recall, reflect, automate-me, show-me-your-work, eval, session-pickup, worktree-audit.sh. Skills forbid globbing `~/.cursor/projects/*/`. |
| `.cursor/skills/` and `~/.cursor/skills/` | automate-me output; create-verification-skill writes `.cursor/skills/verify-<app>/`; reflect reviewers treat a Read of `SKILL.md` under these (or `~/.cursor/plugins/`) as "skill was used." |
| `.cursor/settings.json` `plugins.pstack.enabled` | Benny. |
| `.cursor/automations/benny/` | Benny install target. |
| `.cursor/worktrees/<repo>/x` | worktree-cleanup (Cursor's default worktree location). |
| `mcps/` | why skill: "inspect the `mcps/` directory Cursor exposes for enabled MCP servers." |
| `~/Library/Application Support/Cursor` | worktree-cleanup reclaim list (`state.vscdb.backup`, `snapshots/roots/<root>`). |

### Cursor skill / agent frontmatter keys

These are Cursor (or Cursor-extended Agent Skills) keys, not portable procedure:

- `disable-model-invocation`
- `mode`, `icon`, `color`, `reminder` (Custom Mode)
- `paths` (auto-attach glob)
- `is_background` (agent)

### Sibling-plugin names that are not pstack

Do not copy these names into core as if they were capabilities of this tree: `cursor-team-kit`, `deslop`, `control-cli`, `control-ui`. The map already wants optional modules behind a capability registry (`validation.judge`, never a hardcoded if-Jev). The same pattern applies here: a host adapter or a module may provide a `deslop` / UI-drive capability; core playbooks should call the capability, not `cursor-team-kit`.

## What would block a host-agnostic extract

None of these are license blocks. They are coupling. Leaving them in core would make core a Cursor plugin.

1. **pstack is a subdirectory of a monorepo, not a repo.** `git submodule add https://github.com/cursor/plugins.git` would pull cursor-team-kit, third_party SaaS plugins, ralph-loop, orchestrate, etc. There is no `pstack.git`. A history-preserving take is `git subtree split` of `pstack/` at `1b6d44ff…` (or an equivalent filter-repo), then subtree/submodule *that*. A copy of the directory plus `LICENSE` is also MIT-legal.

2. **The Task tool is the process model.** poteto-mode, how, why, arena, swarm, interrogate, reflect, no-comments, and Orchestrate are written as `Task` calls with Cursor `subagent_type` / `model` / `environment`. Grok Build, Claude Code, and Codex do not share that API. core needs a host-agnostic spawn contract; the Cursor parameter names stay in a host adapter.

3. **Named Cursor subagent types** (`poteto-agent`, `comment-sicko`, `generalPurpose`) are Cursor agent-registry ids. The *prompts* can live in core; the `subagent_type:` wiring cannot.

4. **Model config is a Cursor rule file.** `pstack-models.mdc` + `alwaysApply: true` + Cursor slug ladder (`xhigh`, `max`, `fast`) is `/setup-pstack`. Map already flags "setup skill and where model roles are written" as unspecified. That skill cannot land in core as-is.

5. **Transcript mining is Cursor-path-shaped.** recall, reflect, automate-me, eval, session-pickup, show-me-your-work, worktree-audit.sh all key off `agent-transcripts/` under `~/.cursor/projects/`. Other hosts will not have that layout.

6. **Overnight / autonomy is `/loop` + cloud VMs + Cursor Projects.** Autonomous run, Orchestrate, Autopilot, babysit `drive` are not portable loops. Map already has "Grok overnight / autonomous loop (workflow vs ralph-loop vs scheduler)" in fog.

7. **Hard dependency on cursor-team-kit** for `/deslop`, `control-cli`, `control-ui`. Opening a PR, Shipping, Orchestrate, Autopilot call these by name. core playbooks that say `/deslop` are Cursor-only. Replace with a capability slot or a core-owned equivalent.

8. **`make-bot-ui` is a Cursor Routines client** (`update_state`, `SendToUser` secret-request, `api2.cursor.sh`). Do not put this skill in core.

9. **Benny is Cursor automations** (`.cursor/automations/`, `.cursor/settings.json`, `/automate`). Do not put this pack in core.

10. **Custom Mode frontmatter and `/add-plugin`** are Cursor UX. core skills should not carry `mode: true` / `icon` / `color` / `reminder`. Marketplace manifests belong under `hosts/`, not core.

11. **MCP discovery via Cursor `mcps/` and "readonly strips MCPs"** is a Cursor runtime quirk encoded into why/reflect. The *evidence categories* (git, tracker, docs, chat, observability, errors, warehouse) are host-agnostic; the discovery mechanism is not.

12. **Bugbot, Origin, Graphite, Cursor dashboard, Cmd+Shift+I, Tailscale-on-the-agent-machine** are product-specific. Babysit/Shipping/Orchestrate need a forge adapter (`gh` is already the default and is portable). Origin/`gt`/Bugbot stay out of core.

13. **Scripts assume bun** (`Bun.spawnSync`, `bun.lock`). Fine as optional tooling if a host can run them; not a skill-prose problem, but they also hardcode Cursor transcript paths.

14. **`principle-never-block-on-the-human` vs Matt HITL.** The principle is in the tree. The map already says do not average it with grill-until-empty. An extract that dumps poteto-mode into core unchanged would import that autonomy rule onto HITL work.

15. **poteto-help says the quiet part out loud:** "pstack is built for Cursor. Its skills use the Agent Skills format, so other tools can read them. But most workflow skills, including `/poteto-mode`, `/how`, `/why`, and `/teach`, spawn Cursor subagents with per-role models, and Custom Modes and `/loop` are Cursor features, so those parts may not work there."

What *can* move into core with light rewriting: playbook step lists (minus Cursor tool names), the 24 principle bodies, unslop / technical-writing / tdd / typescript-best-practices / comment-sicko rules, the poteto-agent "read the mode skill first" contract, and the agent-plugins.org identity (`name`, MIT, version pin). Everything that names `Task`, `AskQuestion`, `.cursor/`, `/loop`, `cursor-team-kit`, Bugbot, or Routines is adapter or out of scope.

## Git take: subtree vs submodule (constraints only)

- **Pin** `cursor/plugins@1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def` (pstack 0.15.20). Record the `pstack/` tree SHA `1dbec20ada6e40cb12774b8893960a558319fd6b`.
- **Keep** `pstack/LICENSE` (Copyright (c) 2026 Lauren Tan) next to any vendored copy.
- **Do not** submodule the whole `cursor/plugins` repo. That is the official plugins marketplace, not pstack.
- **Do** split or copy only `pstack/`. `git subtree split --prefix=pstack` (or `git filter-repo`) preserves history if that matters for later upstream merges. A plain copy is enough for MIT compliance and is easier to patch.
- **Patches on top** will be large: dual manifests, Cursor frontmatter, Task/AskQuestion strings, `~/.cursor/**` paths, cursor-team-kit calls, make-bot-ui, benny. Map fog already names "How patches stay mergeable with upstream while stripping Cursor-specific APIs." Expect ongoing conflict cost if the take keeps Cursor strings in the same files upstream edits.

This inventory does not pick subtree vs submodule. It says a whole-repo submodule is the wrong object, and that the extract is a strip-and-adapt job, not a drop-in.

## Source pin

All file citations above are to

https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/pstack/…

fetched from `https://github.com/cursor/plugins.git` at that commit (also then-current `origin/main`). No secondary write-ups were used.
