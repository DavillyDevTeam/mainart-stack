# Inventory: Matt Pocock packet-chain skills for `core/`

**Ticket:** [Inventory Matt packet-chain skills](https://github.com/DavillyDevTeam/mainart-stack/issues/3)
**Question:** Which of Matt Pocock's packet-chain skills get vendored into mainart-stack `core/`, and under what license and host-coupling constraints?

## Answer

Vendor the **packet chain** from [`mattpocock/skills`](https://github.com/mattpocock/skills) (MIT, Copyright (c) 2026 Matt Pocock, v1.3.1) as host-agnostic `SKILL.md` bodies into `core/`. The chain is not the eight names in the ticket alone.

**In the chain (vendor with companions):**

| Skill | Role in the chain | Invocation |
|---|---|---|
| `grill-with-docs` | In-repo grilling (the default start) | user |
| `grill-me` | Stateless grilling (no working directory) | user |
| `grilling` | Interview primitive both wrappers call | model |
| `domain-modeling` | Glossary/ADR discipline; paired with grilling | model |
| `prototype` | Throwaway artifact that answers a design question | model |
| `to-spec` | Collapse a grilled thread into a tracker spec | user |
| `to-tickets` | Tracer-bullet packets with blocking edges | user |
| `wayfinder` | Multi-session decision map (on-ramp onto `to-spec`) | user |
| `triage` | Inbox on-ramp onto `implement` | user |
| `implement` | Per-packet TDD + review | user |
| `implement-spec` | Whole-spec task-graph orchestration | user |
| `tdd` | Red-green loop at agreed seams | model |
| `code-review` | Two-axis Standards + Spec review | model |
| `research` | AFK fact-finding; wayfinder research tickets | model |
| `setup-matt-pocock-skills` | Precondition: tracker / labels / domain-doc layout | user |

**Copies do not need pstack-scale stripping.** Matt already refuses Cursor/Claude `AskUserQuestion` / `AskQuestion`. Remaining host coupling is smaller and localized: the phrase **"Call the Skill tool"** (Claude Code's `Skill` tool; Grok claims Claude compatibility), `disable-model-invocation` frontmatter, Codex `agents/openai.yaml`, and `/clear` `/compact` in the router. pstack playbooks still name Cursor `Task`, `subagent_type: "poteto-agent"`, `AskQuestion`, `control-ui`, and Cursor model ids — that is a different job.

MIT requires the copyright and permission notices in every substantial copy. Do not drop `grilling`, `domain-modeling`, `prototype`, or `research` if you vendor the wrappers that call them.

## Sources and snapshot

Primary sources used (every claim below traces to one of these):

- Installed copies on this machine: `/home/luizdmm/.agents/skills/<name>/` (from `mattpocock/skills`, plugin `mattpocock-skills`, last lock update 2026-10-07). Catalog: `/home/luizdmm/.agents/.skill-lock.json`.
- Upstream repo: <https://github.com/mattpocock/skills> — [`LICENSE`](https://github.com/mattpocock/skills/blob/main/LICENSE), [`package.json`](https://github.com/mattpocock/skills/blob/main/package.json) `version: 1.3.1`, [`.claude-plugin/plugin.json`](https://github.com/mattpocock/skills/blob/main/.claude-plugin/plugin.json), [`README.md`](https://github.com/mattpocock/skills/blob/main/README.md), [`.agents/invocation.md`](https://github.com/mattpocock/skills/blob/main/.agents/invocation.md), [`.out-of-scope/native-question-tool.md`](https://github.com/mattpocock/skills/blob/main/.out-of-scope/native-question-tool.md), [`.out-of-scope/harness-name-collisions.md`](https://github.com/mattpocock/skills/blob/main/.out-of-scope/harness-name-collisions.md), [`SCOPE.md`](https://github.com/mattpocock/skills/blob/main/SCOPE.md).
- Host tool names: [Claude Code tools reference](https://code.claude.com/docs/en/tools-reference) (`Skill`, `AskUserQuestion`, `Agent`); [Claude Code skills](https://code.claude.com/docs/en/skills) (`disable-model-invocation`); [Cursor Agent Skills](https://cursor.com/docs/skills); [Grok skills/plugins](https://docs.x.ai/build/features/skills-plugins-marketplaces.md); [Grok modes/commands](https://docs.x.ai/build/modes-and-commands).
- pstack comparison only: [`cursor/plugins` `pstack/skills/poteto-mode/SKILL.md`](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/SKILL.md) (not a full pstack inventory; that is [Inventory upstream pstack](https://github.com/DavillyDevTeam/mainart-stack/issues/2)).
- Product intent already on this map: [Spec mainart-stack](https://github.com/DavillyDevTeam/mainart-stack/issues/1) Notes; this repo [`GLOSSARY.md`](../../GLOSSARY.md).

Local copies lag upstream HEAD (upstream README/plugin still 1.3.1 as of 2026-10-12; last local update 2026-10-07). Bodies cited here are the **local** files unless a GitHub URL is named.

## License

Upstream `package.json` and `.claude-plugin/plugin.json` both set `"license": "MIT"`. The repo `LICENSE` is the MIT text:

```
MIT License

Copyright (c) 2026 Matt Pocock
```

Permission is granted to use, copy, modify, merge, publish, distribute, sublicense, and sell, **provided** "The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software."

Vendoring into `core/` is a copy of a substantial portion. Keep a `NOTICE` or `LICENSE` next to the vendored skills with that copyright line and the MIT permission notice. Individual skill folders on disk have **no** per-skill `LICENSE` file; the grant is repo-level.

Compatible in kind with pstack's MIT (Copyright (c) 2026 Lauren Tan). This inventory does not decide how the two notices sit together in `core/`.

## What the packet chain is

Matt's own router, `ask-matt`, names one **main flow** and two **on-ramps**. That is the packet chain. Paraphrased from `/home/luizdmm/.agents/skills/ask-matt/SKILL.md` (and the same list in the upstream README "Reference"):

```
vague idea
  → /grill-with-docs   (in a working directory)
     or /grill-me      (no working directory)
  → optional /prototype detour (via /handoff)
  → /to-spec           destination document on the tracker
  → /to-tickets        tracer-bullet slices, blocking edges
  → /implement         per ticket, driving /tdd then /code-review
     or /implement-spec  whole spec, implementers drive /tdd, one /code-review
```

On-ramps that merge onto that flow:

- **`/triage`** — incoming bugs/requests (not tickets `/to-tickets` already made). Produces agent-ready issues that `/implement` picks up.
- **`/wayfinder`** — effort bigger than one grilling session. Charts **decision tickets**, not build tickets. When the map clears, hand off at **`/to-spec`**, then `/to-tickets` and `/implement`. "Looping the map straight into `/implement` skips that collapse."

`ask-matt` also states the invocation invariant used everywhere else: **user-invoked skills may call model-invoked skills, never another user-invoked skill.** Wrappers (`grill-me`, `grill-with-docs`, `wayfinder`, `triage`, `implement`, `implement-spec`) therefore call primitives by the Skill tool (`grilling`, `domain-modeling`, `prototype`, `research`, `tdd`, `code-review`). Dropping a primitive while keeping its wrapper breaks the chain.

This repo's glossary already names the product of that chain: a **packet** is "A Matt tracker ticket: a spec or an implementable slice with acceptance criteria." Map Notes already prefer vendoring "Matt's packet-chain skills into `core/`."

## Scoped skills, one by one

Ticket scope: `grill-me`, `to-spec`, `to-tickets`, `wayfinder`, `triage`, `implement-spec`, `tdd`, `code-review`, plus `domain-modeling` / `prototype` if they are part of the chain. They are.

### `grill-me` — in the chain, but not the in-repo default

`/home/luizdmm/.agents/skills/grill-me/SKILL.md` is seven lines: `disable-model-invocation: true`, then `Call the Skill tool with "grilling".`

`ask-matt` Standalone: use `/grill-me` when **not** in a working directory. In a repo, `/grill-with-docs` is "strictly the better one" because it leaves `GLOSSARY.md` and ADRs. mainart-stack is a working directory, so the HITL start is **`grill-with-docs`**, which is the same one-liner calling **two** primitives: `grilling` and `domain-modeling`.

Vendor `grill-me` if you want the stateless entry; vendor `grill-with-docs` for the product path. Both are empty without `grilling`.

### `grilling` — required primitive (not in the ticket list)

`/home/luizdmm/.agents/skills/grilling/SKILL.md`: model-invoked. Rounds of numbered questions with a recommended answer; frontier = questions whose prerequisites are settled; facts are the agent's job, decisions the user's; done when the frontier is empty. Questions are **plain chat**, not a host question tool (see Host coupling).

Called by `grill-me`, `grill-with-docs`, `wayfinder`, `triage`, and `improve-codebase-architecture`.

### `domain-modeling` — part of the chain

`/home/luizdmm/.agents/skills/domain-modeling/SKILL.md`: model-invoked. Active glossary/ADR work (challenge terms, edge-case scenarios, write `GLOSSARY.md` / ADRs inline). `ask-matt` Vocabulary: this is what `/grill-with-docs` drives. `wayfinder` and `triage` both say "call the Skill tool twice, for `grilling` and `domain-modeling`." Companion files: `GLOSSARY-FORMAT.md`, `ADR-FORMAT.md`.

### `prototype` — part of the chain

`/home/luizdmm/.agents/skills/prototype/SKILL.md`: model-invoked. Throwaway code that answers one question: `LOGIC.md` (shareable HTML state demo) or `UI.md` (variant UI on one route). `ask-matt` main-flow step 2 is a prototype detour. `wayfinder` ticket type **Prototype** "calling the Skill tool with `prototype`."

### `to-spec` — in the chain

`/home/luizdmm/.agents/skills/to-spec/SKILL.md`: user-invoked. No interview; synthesizes the current conversation into a spec (Problem, Solution, User Stories, Implementation Decisions, Testing Decisions, Out of Scope) and publishes it to the configured tracker with `ready-for-agent`. Defers tracker mechanics to `docs/agents/issue-tracker.md`; if missing, tell the human to run `/setup-matt-pocock-skills`.

### `to-tickets` — in the chain

`/home/luizdmm/.agents/skills/to-tickets/SKILL.md`: user-invoked. Tracer-bullet **vertical** slices, each with blocking edges, sized to one context window. Publishes local files under `.scratch/<feature>/issues/` or real tracker issues with native blocking. Same setup-skill precondition as `to-spec`.

### `wayfinder` — in the chain (on-ramp)

`/home/luizdmm/.agents/skills/wayfinder/SKILL.md`: user-invoked. Map issue labelled `wayfinder:map`; child tickets labelled `wayfinder:<type>` (`research` / `prototype` / `grilling` / `task`). Planning by default: decisions, not deliverables. Internally calls `grilling` + `domain-modeling`, `prototype`, and `research`. Tracker ops (map, sub-issues, blocking, claim, resolve) are **not** inlined as `gh`/`glab`; they live in the repo's tracker doc.

### `triage` — in the chain (on-ramp)

`/home/luizdmm/.agents/skills/triage/SKILL.md`: user-invoked. State machine `needs-triage` → `needs-info` / `ready-for-agent` / `ready-for-human` / `wontfix`, plus category `bug`/`enhancement`. Grills via `grilling` + `domain-modeling` when needed. Companion files: `AGENT-BRIEF.md`, `OUT-OF-SCOPE.md`. `ask-matt`: do **not** triage tickets `/to-tickets` already produced.

### `implement-spec` — in the chain (whole-spec path)

`/home/luizdmm/.agents/skills/implement-spec/SKILL.md`: user-invoked. Reads tickets as a task graph; implementer subagents each call `tdd`; one `code-review` on the integration branch. Speaks "subagents" and "worktree" in prose; does **not** name Cursor `Task`, Grok `spawn_subagent`, or Claude `Agent`.

The per-ticket twin **`implement`** is also in the chain (`ask-matt` step 3). Same Skill-tool calls to `tdd` and `code-review`. Ticket list omitted it; dropping it leaves no single-ticket path.

### `tdd` — in the chain

`/home/luizdmm/.agents/skills/tdd/SKILL.md`: model-invoked. Red → green at pre-agreed seams; anti-patterns; companions `tests.md`, `mocking.md`. Optionally `Call the Skill tool with "codebase-design"` for module-shape vocabulary. That is a **soft** dependency: only when the seam itself is in question. `codebase-design` is not otherwise on the packet chain.

### `code-review` — in the chain

`/home/luizdmm/.agents/skills/code-review/SKILL.md`: model-invoked. Two parallel sub-agents (Standards vs Spec). Bare name `code-review` collides with Claude Code's bundled `/code-review`. Matt's out-of-scope rule: **do not rename**; Claude plugin users type `/mattpocock-skills:code-review`; a skills.sh (or vendored) copy may rename the folder and `name:` field. Map fog already lists "Skill namespacing vs a user's existing Matt install" — this collision is why that ticket exists.

### `research` — required by wayfinder (not in the ticket list)

`/home/luizdmm/.agents/skills/research/SKILL.md`: model-invoked. Background agent, primary sources, one cited Markdown file. `wayfinder` research tickets "spin up a subagent that calls the Skill tool with `research`." This file is that skill running.

## Chain companions the ticket did not name

Still needed if the wrappers above are vendored:

- **`grill-with-docs`** — in-repo HITL start. Same shape as `grill-me`.
- **`grilling`** — see above.
- **`implement`** — per-packet path.
- **`research`** — wayfinder AFK tickets.
- **`setup-matt-pocock-skills`** — `to-spec`, `to-tickets`, `triage`, `wayfinder`, `code-review`, `implement-spec` all tell the user to run it when `docs/agents/*` is missing. Templates (`issue-tracker-github.md`, `issue-tracker-gitlab.md`, `issue-tracker-local.md`, `triage-labels.md`, `domain.md`) are how tracker CLI names (`gh`, `glab`) enter a **consumer repo**, not how they enter `core/` skill bodies.

Not required for the packet chain (leave out of `core/` unless a later ticket says otherwise): `ask-matt` (this product has its own **router**), `handoff`, `pr`, `retro`, `diagnosing-bugs`, `improve-codebase-architecture`, `codebase-design` (optional tdd consult), `wizard`, `wait-what`, `teach`, `to-questionnaire`, `writing-for-agents`, and everything under `in-progress/` / `misc/`.

## Host coupling

### What Matt already stripped

[`.out-of-scope/native-question-tool.md`](https://github.com/mattpocock/skills/blob/main/.out-of-scope/native-question-tool.md): grilling asks questions as **plain chat**. Routing through Claude Code `AskUserQuestion`, a host "question tool", or a structured questionnaire is out of scope, because "Naming one harness's tool in the skill means either a harness-specific branch in every grilling skill, or a skill that only works properly in one place." Cursor's `AskQuestion` is the same class of tool (pstack names it; Matt does not).

None of the packet-chain `SKILL.md` files mention `AskUserQuestion`, `AskQuestion`, `Task`, `subagent_type`, `spawn_subagent`, `control-ui`, or Cursor model ids.

### What is still host-named

**1. `Call the Skill tool with "<name>"`**

Matt's own rule ([`.agents/invocation.md`](https://github.com/mattpocock/skills/blob/main/.agents/invocation.md)): dependencies are an instruction to **call the Skill tool**, not a `/skill` slash and not a cross-folder markdown link. "Naming the tool is what gets it fired: most harnesses expose skill invocation as a tool the model calls." Dropping the leading `/` is their idea of harness-neutrality.

That tool's **actual name** is host-specific:

| Host | Skill invocation | Question UI | Subagent spawn |
|---|---|---|---|
| Claude Code | tool `Skill` ("Executes a skill within the main conversation") | `AskUserQuestion` | `Agent` |
| Grok Build | skills are slash commands `/<skill-name>`; Grok "is fully compatible with Claude Code" and reads `disable-model-invocation`; this research subagent was **not** given a `Skill` tool | (none in the grilling skills) | subagents / "the task tool" (`GROK_SUBAGENTS`); types `general-purpose`, `explore`, `plan` |
| Cursor | human `/skill-name` or `@`; agent is "presented with available skills" from `SKILL.md`. Cursor CLI hook rewrite table maps `Bash`→`Shell`, keeps `Task`; **`Skill` is not a documented Cursor CLI `tool_name`** | docs template: "ask questions tool"; pstack uses `AskQuestion` | `Task` + `subagent_type` |
| Codex | `$skill-name` (CLI/IDE), `@` in ChatGPT; `agents/openai.yaml` `policy.allow_implicit_invocation` | (not named in these skills) | Codex child-agent API (not in these skill bodies) |

So "Call the Skill tool" is a Claude-shaped (and, where Grok mirrors Claude, Grok-shaped) instruction. It is the one host tool name Matt **does** put in chain bodies. Occurrences in the packet chain:

- `grill-me` → `"grilling"`
- `grill-with-docs` → `"grilling"` and `"domain-modeling"`
- `wayfinder` → `"grilling"` + `"domain-modeling"`, `"prototype"`, `"research"`
- `triage` → `"grilling"` + `"domain-modeling"`
- `implement` / `implement-spec` → `"tdd"`, `"code-review"`
- `tdd` → `"codebase-design"` (optional)

**2. `disable-model-invocation: true`**

Claude Code extension of Agent Skills (Claude docs: Claude cannot invoke on its own; you type `/name`). Cursor reads the same field ("only included when explicitly invoked via `/skill-name`"). Grok reads it ("Slash command only; no automatic invoke"). Codex does **not**: it uses `agents/openai.yaml` `policy.allow_implicit_invocation: false` instead ([`.agents/invocation.md`](https://github.com/mattpocock/skills/blob/main/.agents/invocation.md)).

On the packet chain, the flag is set on every **user-invoked** skill (`grill-me`, `grill-with-docs`, `to-spec`, `to-tickets`, `wayfinder`, `triage`, `implement`, `implement-spec`, `setup-matt-pocock-skills`) and omitted on every **model-invoked** primitive (`grilling`, `domain-modeling`, `prototype`, `research`, `tdd`, `code-review`). That split is load-bearing: wrappers cannot Skill-tool-call other wrappers.

Map fog already lists "`disable-model-invocation` on HITL skills" as not yet specified. This inventory only records that the upstream chain uses it, and that three of the three target hosts (Grok, Claude, Cursor) honor the same key; Codex needs the yaml twin.

**3. `agents/openai.yaml`**

Every local packet-chain skill folder has `agents/openai.yaml`: Codex picker `interface.display_name` / `short_description`, and `policy.allow_implicit_invocation: false` on user-invoked skills. That file is **Codex host metadata**, not skill procedure. A host-agnostic `core/` would keep it out of skill bodies (Codex adapter copies or generates it). Matt ships it next to every `SKILL.md`.

**4. `/clear` and `/compact`**

Only in `ask-matt` (`SKILL.md` + `PHASE-BOUNDARIES.md`), which is the Matt router, not a packet-chain primitive. Claude Code has `/compact` as a built-in command; Grok has `/compact` and `/new` (alias `/clear`). If `ask-matt` is not vendored, this coupling does not enter `core/`. `implement` still says "`/clear`ing context between each [ticket]" via `ask-matt`, not in `implement/SKILL.md` itself.

**5. Human-facing `/setup-matt-pocock-skills`**

Tracker-consuming skills tell the **human** to run `/setup-matt-pocock-skills`. That slash is how user-invoked skills are typed on Claude, Cursor, and Grok. Codex would write `$setup-matt-pocock-skills`. Matt's invocation.md keeps `/name` in human-facing prose on purpose.

**6. Name collisions**

Matt will not rename skills when a harness ships a built-in of the same name ([`harness-name-collisions.md`](https://github.com/mattpocock/skills/blob/main/.out-of-scope/harness-name-collisions.md)). Live collisions called out there: `/code-review`, `/research`, `/prototype`. Claude plugin path is namespaced (`/mattpocock-skills:code-review`). A vendored copy in `core/` is a skills.sh-style copy: the files are yours, so a later namespacing ticket may rename. Grok docs: colliding slash commands use a qualified form such as `/local:commit`.

## Must copies be stripped like pstack playbooks?

**Same policy, much smaller edit.**

This product's standing preference (map Notes; glossary **core** = "host-agnostic skills, playbooks, and agent prompts") is: do not put Cursor/Grok/Claude tool names in `core/`. pstack's `poteto-mode` skill is the contrast case. Its body names, in one file:

- Cursor `AskQuestion`
- `subagent_type: "poteto-agent"` on every playbook spawn
- **Defaults for every `Task` call** (`run_in_background: true`, `model:` per role)
- Cursor model ids `grok-4.7-xhigh-fast`, `claude-opus-5-5-xhigh`
- `control-ui` / `control-cli` from `cursor-team-kit`
- Cursor `/loop`, `/deslop`, Custom Mode frontmatter (`mode: true`, `icon`, `color`, `reminder`)

Matt's packet-chain bodies contain **none** of those. Grilling is already the stripped form of "ask the user." Subagent spawn is prose ("spin up a subagent", "implementer subagents", "parallel sub-agents"), which each host adapter can bind to `Agent` / `Task` / Grok subagents.

What a `core/` copy still has to decide (and possibly rewrite) is the **Skill-tool sentence**, the **invocation frontmatter pair** (`disable-model-invocation` vs `openai.yaml`), and **whether `code-review` / `research` / `prototype` keep their upstream names**. That is not the pstack playbook strip. It is a handful of mechanical substitutions plus LICENSE/NOTICE.

Do **not** strip the grilling question format into `AskUserQuestion` / `AskQuestion` to "fit" a host. That would reverse Matt's out-of-scope decision and break HITL (a structured picker "push[es] the model towards multiple-choice questions with pre-baked answers, which is the opposite of what grilling is for").

## Suggested `core/` contents (inventory, not a layout ADR)

Minimum set that actually runs the chain:

```
core/skills/
  grill-me/
  grill-with-docs/
  grilling/
  domain-modeling/     (+ GLOSSARY-FORMAT.md, ADR-FORMAT.md)
  prototype/           (+ LOGIC.md, UI.md)
  to-spec/
  to-tickets/
  wayfinder/
  triage/              (+ AGENT-BRIEF.md, OUT-OF-SCOPE.md)
  implement/
  implement-spec/
  tdd/                 (+ tests.md, mocking.md)
  code-review/
  research/
  setup-matt-pocock-skills/  (+ tracker/label/domain templates)
LICENSE or NOTICE      # MIT, Copyright (c) 2026 Matt Pocock
```

Keep `agents/openai.yaml` out of that tree (Codex adapter). Keep marketplace manifests, plugin.json, and spawn-API mapping in `hosts/`. Tracker CLI recipes stay as **templates** the setup skill writes into a consumer repo, not as Grok/Claude/Cursor tool calls inside the skill bodies.

## Not decided here

These are already on the map as fog or other tickets; this research only supplies facts:

- Skill namespacing vs a user's existing Matt install (`code-review` / `research` / `prototype` collisions).
- Whether HITL skills keep `disable-model-invocation: true`.
- Whether `/implement-spec` workers are `poteto-agent`.
- How "Call the Skill tool" is phrased in host-agnostic core (adapter-local rewrite vs leave Matt's sentence).
- Whether `ask-matt` is replaced entirely by this product's **router**.
