# Grok host adapter surface

Research for [Document the Grok host adapter surface](https://github.com/DavillyDevTeam/mainart-stack/issues/4).

**Question:** What Grok Build plugin/runtime APIs must a host adapter implement, and which of those belong in `hosts/grok` rather than `core/`?

**Terms:** **mainart-stack** is this product (shared core, host adapters, optional modules). **core** is host-agnostic skills, playbooks, and agent prompts. A **host adapter** is the runtime glue for one agent host. See `GLOSSARY.md`.

**Primary sources** (this machine, 2026-10-12):

- `/home/luizdmm/.grok/docs/user-guide/09-plugins.md` (identical to `/home/luizdmm/.grok_personal/docs/user-guide/09-plugins.md`)
- `/home/luizdmm/.grok_personal/docs/user-guide/` — plugins, configuration, config reference, skills, project rules, subagents, hooks, background tasks, slash commands, agent mode (ACP), sandbox, clone
- Installed plugins under `/home/luizdmm/.grok/installed-plugins/`
- Bundled agents/roles/workflows under `/home/luizdmm/.grok/bundled/`
- Installed Claude-layout ralph-loop under `/home/luizdmm/.grok_personal/marketplace-cache/783232b622f8182e/plugins/ralph-loop/`
- Live `~/.grok/config.toml` keys (values that are secrets are not quoted)

---

## Short answer

A Grok host adapter is a **plugin** plus the Grok-only runtime it sits on. Grok discovers a plugin from a directory of `skills/`, `commands/`, `agents/`, `hooks/hooks.json`, `.mcp.json`, and `.lsp.json`, with an optional `plugin.json`. Users get it by adding a marketplace and installing; plugins stay off until listed in `[plugins].enabled` and stay inert until trusted.

The adapter must speak these Grok APIs:

| Surface | Grok API | Put it in |
| --- | --- | --- |
| Plugin package | `.grok-plugin/marketplace.json` (+ `.claude-plugin/` equivalent), optional `plugin.json`, standard component dirs | `hosts/grok` |
| Install | `grok plugin marketplace add`, `grok plugin install --trust`, `[plugins].enabled` / `.paths` | `hosts/grok` |
| Skills / playbooks | `skills/*/SKILL.md` (and optional `commands/`) | **bodies in `core/`**; Grok frontmatter, qualified names, and packaging in `hosts/grok` |
| Plugin agents | `agents/*.md`, spawned as `plugin-name:agent-name` | `hosts/grok` (prompt bodies that are host-agnostic can live in `core/`) |
| Subagents | `spawn_subagent` (`isolation`, `cwd`, `resume_from`, optional `subagent_type` / `model`) | `hosts/grok` |
| Worktrees | `isolation: worktree` + ACP `x.ai/git/worktree/*` (`create`, `remove`, `apply`, `list`, `gc`) | `hosts/grok` |
| Model / role | `~/.grok/config.toml` (`[models]`, `[agent]`, `[subagents.models]`, `[subagents.roles]`, `[subagents.personas]`) and `.grok/roles/*.toml` | `hosts/grok` |
| Project rules | `AGENTS.md` / `.grok/rules/*.md` | **content in `core/` or repo root**; Grok load order is host behavior |
| Overnight | Grok **workflows** (`.rhai` + `workflow` tool + `/goal`) first; **scheduler** `/loop` for timed wakeups; **ralph-loop** only as a Stop-hook pattern, with Grok’s 8-continuation cap | `hosts/grok` |
| UI proof | No first-party browser tool. Proof is MCP (plugin `.mcp.json`), `PostToolUse` hooks, and shell. `image_gen` / `image_edit` generate, they do not capture a UI. | `hosts/grok` (MCP/hook wiring); proof *procedure* in `core/` |

Everything else — playbook steps, packet language, capability names such as `validation.judge` — stays in `core/` and must not name Grok tools, `spawn_subagent`, or `~/.grok`.

---

## 1. Plugin manifest layout

A plugin is a directory. Grok auto-discovers components from fixed paths; `plugin.json` is optional and “can override paths or add metadata.” Without it, the standard directories are enough.

**What a plugin may contain** (`09-plugins.md` “What a plugin contains”):

- `skills/` — `SKILL.md` files
- `commands/` — slash commands
- `agents/` — agent definitions
- `hooks/hooks.json` — lifecycle hooks
- `.mcp.json` — MCP servers
- `.lsp.json` — LSP servers
- optional `plugin.json`

A skill or command may ship a helper script next to `SKILL.md`. Plugins copy files; they do not install runtimes or native binaries.

**Marketplace repo layout** (required index at `.grok-plugin/marketplace.json`; Grok also accepts `.grok-plugin/plugin.json` and the `.claude-plugin/` equivalents):

```
my-org-plugins/
  .grok-plugin/
    marketplace.json      # required index
    plugin-index.json     # optional catalog for the Marketplace tab
  plugins/
    gdrive/
      plugin.json         # optional
      skills/gdrive/SKILL.md
      .mcp.json
```

`marketplace.json` names the marketplace and lists plugins. Each plugin `source` is either in-repo (`{ "type": "local", "path": "./plugins/gdrive" }` or the string `"./plugins/gdrive"`) or a separate git repo (`{ "source": "url", "url": "…", "sha": "<full commit sha>" }`). Optional per-plugin fields: `version`, `author`, `homepage`, `tags`, `keywords`.

`plugin-index.json` is display-only (`version: 1`, per-plugin `components.skills[]` etc.). Installs work without it. Pinning (`[marketplace] require_sha = true` or `GROK_MARKETPLACE_REQUIRE_SHA=1`) requires `sha` values in that catalog.

**Gap:** Grok documents that `plugin.json` “can override paths” but does not list the override keys. Installed manifests on this machine only carry metadata (`name`, `version`, `description`, `author`, `license`, `keywords`, sometimes `repository`). Do not invent Claude `commands`/`agents` path keys as Grok contract.

### Evidence from installed plugins

**python-fastapi-development-bundle** (`/home/luizdmm/.grok/installed-plugins/python-fastapi-development-bundle-b42dd014/`):

- Layout: `.claude-plugin/plugin.json` + `skills/<name>/SKILL.md` only. No `agents/`, `hooks/`, or `.mcp.json`.
- Manifest:

```json
{
  "name": "python-fastapi-development-bundle",
  "version": "1.0.0",
  "description": "Curated Python/FastAPI development workflow …",
  "author": { "name": "local-curated" },
  "license": "MIT",
  "keywords": ["fastapi", "python", "workflow"]
}
```

- Registry (`installed-plugins/registry.json`): installed from a local path `~/.grok/plugins/python-fastapi-development-bundle`, kind `Local`, plugin version `1.0.0`.
- Skills use YAML frontmatter (`name`, `description`, plus extra keys Grok does not document as required: `category`, `risk`, `source`, `date_added`). Bodies are host-agnostic procedures.

**github** (`installed-plugins/github-f4ae7665/`): `.claude-plugin/plugin.json` + `.mcp.json` only. MCP is HTTP:

```json
{
  "github": {
    "type": "http",
    "url": "https://api.githubcopilot.com/mcp/",
    "headers": { "Authorization": "Bearer ${GITHUB_PERSONAL_ACCESS_TOKEN}" }
  }
}
```

**sentry** (`installed-plugins/sentry-for-claude-b356088e/`): multi-host source tree. Grok slice is `plugin-src/grok/` with `plugin.json`, `marketplace.json`, `build.sh`, `validate.sh`. README install line: `grok plugin install getsentry/plugin-grok --trust`. Sentry’s own `AGENTS.md` says Grok auto-discovers `.mcp.json` (Codex’s validator requires the dotted name; Claude inlines `mcpServers` in `plugin.json` instead). Live MCP file:

```json
{ "mcpServers": { "sentry": { "type": "http", "url": "https://mcp.sentry.dev/mcp?utm_source=plugin" } } }
```

Sentry also ships `commands/seer.md` (slash command) and a large `skills/` tree. That is the fullest “skills + commands + MCP” shape on this machine.

**Implication for mainart-stack:** `hosts/grok` owns the marketplace index, `plugin.json` metadata, Grok `.mcp.json` / `hooks/hooks.json` / `agents/`, and any `.claude-plugin/` dual-layout if the same tree is also a Claude plugin. `core/` owns skill *bodies*.

---

## 2. Marketplace install

Two steps, like an app store: add a marketplace (browse only), then install one plugin at a time. Install turns the plugin on; hooks and MCP stay inactive until the plugin is trusted.

**Add a source**

```bash
grok plugin marketplace add my-org/team-plugins
grok plugin marketplace add https://gitlab.com/acme/plugins.git
grok plugin marketplace add ./my-marketplace
```

Also `list` / `update [<name>]` / `remove <url>`.

Or always-on sources in `~/.grok/config.toml`:

```toml
[[marketplace.sources]]
name = "My Team Plugins"
git = "https://github.com/my-org/plugins.git"

[[marketplace.sources]]
name = "Local Dev"
path = "~/dev/my-plugins"
```

Claude-compat `extraKnownMarketplaces` in `~/.grok/settings.json` or `~/.claude/settings.json` is also accepted (`git`+`url`, `github`+`repo`, `local`+`path`).

**Install**

```bash
grok plugin install deploy-tools --trust
```

Sources: `owner/repo`, `owner/repo@v1.0`, `owner/repo@<commit-sha>`, `owner/repo#subdir`, full git/SSH URL, local path. Without `--trust`, Grok prints the source, warns that install activates hooks/MCP/skills, and stops.

**Enable** — plugins are off by default:

```toml
[plugins]
paths = ["~/my-plugins/custom-tools"]
disabled = ["user/a1b2c3d4/noisy-plugin"]
enabled = ["project/9f8e7d6c/team-tools"]   # name from `grok plugin list`, or `<scope>/<hash>/<name>`
```

This machine’s user config lists `enabled = ["sentry", "github", "firecrawl", "gitlab", "python-fastapi-development-bundle"]`.

**Discovery order** (higher wins on name collision; `.claude/plugins/` equivalents work):

| Location | Scope | Trust |
| --- | --- | --- |
| `_meta.pluginDirs` on `session/new` (and `session/load` on the shell route) | That session only | Auto |
| `--plugin-dir` on `grok agent … stdio` | That process; ignored in leader mode | Auto |
| `.grok/plugins/` | Project | Requires trust |
| `~/.grok/plugins/` | User | Auto |
| `[plugins].paths` | Custom | Depends on location |

On the daemon route, `_meta.pluginDirs` loads only if the daemon reports `grok_session_plugin_dir_hooks.v1`, and then **only hooks** bind.

**Trust:** `~/.grok/plugins/` is auto-trusted. Project `.grok/plugins/` needs `--trust`. Trusted plugin `.mcp.json` attaches to the session; child agents inherit those servers. Plugin hook env: `GROK_PLUGIN_ROOT` (install dir), `GROK_PLUGIN_DATA` (writable data); `CLAUDE_PLUGIN_ROOT` / `CLAUDE_PLUGIN_DATA` aliases are set too.

**Org policy** (native `managed_config.toml` / `requirements.toml`, Claude `managed-settings.json` advisory): `strict_known_marketplaces`, `extra_known_marketplaces`, MCP allow/deny, `plugin_auto_update = false` (tighten-only), `[marketplace] require_sha = true`. `grok inspect` shows what loaded.

**CLI / TUI:** `grok plugin list [--json] [--available]`, `uninstall`/`enable`/`disable`/`details`/`update`. Modal: `Ctrl+L` or `/plugins` (six tabs: Hooks, Plugins, Marketplace, Skills, Workflows, MCP Servers). Hide the UI with `disable_plugins = true` in `~/.grok/pager.toml`.

**Adapter duty:** `hosts/grok` ships the marketplace repo and the install docs (`marketplace add` + `install --trust` + `[plugins].enabled`). Do not put marketplace JSON in `core/`.

---

## 3. Plugin agents

Plugin agents live in the plugin’s `agents/` directory. The Plugins tab lists them. They are spawned as `plugin-name:agent-name`.

`spawn_subagent` grows an optional `subagent_type` enum when plugin, project, or user agents exist; values are those agents (example `my-plugin:reviewer`). Built-in names and xAI-bundled agents are **not** listed. An unknown type fails with the list of valid types. If the parent’s `tools` list restricts spawning with `Agent(...)`, the enum is only the allowed types.

**Safety (plugin agent frontmatter cannot):**

- declare `mcpServers` (ignored with a warning)
- declare hooks
- set `permissionMode: bypassPermissions`

They inherit the parent session’s already-connected MCP servers by default (`mcpInheritance`: `all` / `none` / `named: […]` / `except: […]`). Plugin `.mcp.json` attaches to the **parent/session** after trust, not as a child-only declaration.

**Built-in host types** (model cannot pick them by name; omitted `subagent_type` is `general-purpose`):

| Type | Role |
| --- | --- |
| `general-purpose` | Full capability (`all`) |
| `explore` | Read/search/shell; no file edits |
| `plan` | Plan; no file edits |

Bundled definitions (`~/.grok/bundled/agents/`):

- `general-purpose.md` — frontmatter `name`, `description`, `prompt_mode: full`, `model: inherit`, `permission_mode: default`, `agents_md: true`
- `explore.md` — `permission_mode: plan`; body says read-only
- `plan.md` — `model: inherit`, `permission_mode: plan`

A Claude-layout example of a plugin agent (marketplace cache, not a Grok-native plugin) is `math-proof-worker.md`: `name`, `description`, `tools: Read, Write, Edit`, `model: inherit`, `effort: low`, `maxTurns: 80`. Treat Claude tool names as **not** Grok contract; Grok’s own bundled agents use `prompt_mode` / `permission_mode` / `agents_md` and `${{ tools.by_kind.* }}`.

User/project agents: `~/.grok/agents/` and `.grok/agents/` (markdown + YAML frontmatter). Default interactive agent is `[agent] name` / `definition` in `config.toml`.

**Adapter duty:** `hosts/grok` adds any Grok-specific agent `.md` files (reviewer, implementer, …) and maps playbook roles onto `subagent_type`. Prompt prose that does not name Grok tools can be shared from `core/`.

---

## 4. `spawn_subagent`, worktrees, isolation

The parent calls `spawn_subagent`. Parameters (`16-subagents.md`):

| Parameter | Meaning |
| --- | --- |
| `prompt` | Full task prompt |
| `description` | 3–5 word label |
| `run_in_background` | Default `true`; result via `get_command_or_subagent_output` |
| `isolation` | `none` (shared workspace, default) or `worktree` (isolated git worktree) |
| `resume_from` | Continue a **completed** sibling’s conversation (same session, same agent type) |
| `cwd` | Working directory; **mutually exclusive** with `isolation: worktree`; ignored on resume |
| `model` | Optional; hidden when `[features] subagent_model_inheritance = true` and every picker model is xAI |

Capability mode is **not** a spawn argument. It comes from agent type and role/definition defaults:

| Mode | Read | Write | Execute |
| --- | --- | --- | --- |
| `read-only` | yes | no | no |
| `read-write` | yes | yes | no |
| `execute` | yes | no | yes |
| `all` | yes | yes | yes |

`general-purpose` is `all`. Built-in `explore` / `plan` cannot edit files.

**Worktree isolation:** `isolation: worktree` gives the child its own copy of the working tree. The result includes the worktree path. Grok manages worktrees through ACP extension methods `x.ai/git/worktree/*`, including an **apply** that merges back into the main working directory (`15-agent-mode.md`: `create`, `remove`, `apply`, `list`, `gc`; notification `x.ai/git/worktree/status`). Config: `[hints] new_session_worktree_mode` / `fork_worktree_mode` (`ask`/`always`/`never`); `[cli] grove_worktree` / `GROK_WORKTREE_TYPE` for Grove vs copy; `[worktree] auto_gc`. `grok clone` is a separate Grove gate (`27-grok-clone.md`) and does not by itself enable session/`-w` worktrees.

**Depth:** prose says only the top-level session spawns children (max nesting one); a child `spawn_subagent` fails with a depth-limit error. Config still exposes `subagents.max_depth` (clamped ≥1) and `subagents.max_concurrent` / `limit_behavior`. Master switch: `subagents.enabled`, `GROK_SUBAGENTS=0`, `--no-subagents`.

**Follow-ups:** `send_subagent_message` is off by default (`GROK_ACTIVE_AGENT_MESSAGES` / `[features] active_agent_messages`).

**Sandbox vs worktree:** sandbox (`18-sandbox.md`) is OS kernel isolation (Landlock/Seatbelt) of the agent process — `off` / `workspace` / `devbox` / `read-only` / `strict`. It is not the same as git worktree isolation. A host adapter that wants “don’t collide with the parent’s tree” uses `isolation: worktree`. A host adapter that wants “don’t write secrets / the net” uses `GROK_SANDBOX` / `--sandbox`.

**Workflows** expose a parallel knob: `agent(prompt, #{ isolation_worktree: true, … })` — “gives the agent a private worktree but does not merge its edits back into the parent workspace”; the script must add an explicit select-and-apply step (`create-workflow` skill).

**Adapter duty:** `hosts/grok` is the only place that may call `spawn_subagent`, choose `isolation: worktree`, and apply via `x.ai/git/worktree/apply`. `core/` playbooks say “run this worker in isolation,” not the Grok parameter names.

---

## 5. Model-role config (`~/.grok/config.toml`) vs rules

These are different layers. Mixing them is how a host adapter would accidentally put Grok config into `core/`.

### Rules (project instructions)

Grok loads Markdown instruction files into context (`12-project-rules.md`). Filenames, in order: `Agents.md`, `Claude.md`, `CLAUDE.md`, `CLAUDE.local.md`, `AGENT.md`, `AGENTS.md`. Also `*.md` in `<dir>/.grok/rules/` (always), plus `.claude/rules/` / `.cursor/rules/` when compat cells are on, plus `$GROK_HOME/rules/` and `[paths] extra_rule_dirs`.

Load order: home rules first, then repo root → cwd (deeper wins on conflict). Startup loading of project files requires folder trust (`--trust` or interactive grant). No character cap; each file is loaded in full. Session-only: `--rules` / `--append-system-prompt` wraps text in `<human_rules>`; `--system-prompt-override` replaces the default prompt.

**Rules are not where you pin models.** They are conventions, build/test commands, architecture notes.

ACP equivalent: `session/new` `_meta.rules` and `_meta.systemPromptOverride` (`15-agent-mode.md`).

### Config (models, default agent, subagent routing)

User file: `~/.grok/config.toml`. Project `.grok/config.toml` only contributes `[mcp_servers]`, `[plugins]`, `[permission]`, and `[mcp] max_output_bytes`.

**Models** (`05-configuration.md`, `26-config-reference.md`):

```toml
[models]
default = "grok-4.5"
web_search = "grok-4.5"
allowed_models = ["grok-4.5", "grok-4*"]   # picker allowlist; empty = unrestricted
default_reasoning_effort = "high"

[agent]
name = "grok-build"            # default interactive agent
# definition = "/path/to/agent.md"  # path wins over name
```

This machine sets `[models] default = "grok-4.7"` and `default_reasoning_effort = "xhigh"`.

**Subagent model pins and type toggles:**

```toml
[subagents]
enabled = true

[subagents.toggle]
explore = true
plan = false

[subagents.models]
explore = "grok-4.6"
```

Without a pin, a subagent inherits the parent’s model. `[features] subagent_model_inheritance = true` hides the spawn `model` argument when every picker model is xAI.

**Roles** (capability + model defaults) — documented in `16-subagents.md`, not as first-class rows in `26-config-reference.md`:

```toml
[subagents.roles.researcher]
description = "Deep research agent"
default_capability_mode = "read-only"
model = "grok-4.6"
prompt_file = ".grok/prompts/researcher.md"
```

Also discovered from `.grok/roles/*.toml`. Inline `config.toml` wins over files. Bundled example (`~/.grok/bundled/roles/implementer.toml`): `description`, `default_capability_mode = "all"`, `reasoning_effort = "high"`, `default_fork_context = true`.

**Personas** (behavioral overlay on a subagent; **not** a `spawn_subagent` parameter — applied during resolution):

```toml
[subagents.personas.researcher]
instructions = "You are a thorough researcher. Always cite specific file paths."
description = "Deep investigator."
```

File discovery: `.grok/personas/*.toml` (project) → `~/.grok/personas/*.toml` (user) → bundled. Fields: `instructions` / `instructions_file`, `description`, `inputs`/`outputs`, `model`, `reasoning_effort`, `default_isolation` (`none` or `worktree`). Resolution for model/effort: spawn override → role default → persona default → parent session. Isolation uses the first three steps and defaults to `none` rather than inheriting the parent.

**Harness compat** (`[compat.claude]` / `[compat.cursor]`) scans foreign `skills`/`rules`/`agents`/`mcps`/`hooks`. Defaults on. This is how a Grok session sees Claude `CLAUDE.md` and Cursor rules; it is not a reason to put Grok adapter files in those trees.

**Adapter duty:** model IDs, `[subagents.roles]`, `[subagents.models]`, and the default `[agent]` belong in `hosts/grok` (docs + optional example `config.toml` snippets, never required user secrets). `AGENTS.md` in the product repo can stay host-agnostic (`core/` / repo root) and must not assign `grok-4.x` to roles.

---

## 6. Overnight: workflows vs ralph-loop vs scheduler

Issue 1 still lists “Grok overnight / autonomous loop (workflow vs ralph-loop vs scheduler)” as unspecified. The Grok APIs, compared:

### A. Workflows (host-owned engine) — best Grok-native overnight *inside one process*

On by default (`[workflows] enabled`, `GROK_WORKFLOWS`; default on). Disable → `/goal` falls back to legacy `update_goal`.

- Scripts: project `<repo-root>/.grok/workflows/*.rhai`, user `~/.grok/workflows/*.rhai`, plus bundled (`~/.grok/bundled/workflows/deep-research.rhai`, `learn-traces.rhai`).
- Discovery key is `meta.name`. Built-in > project > user on name collision.
- Launch: `/workflow <name>`, the `workflow` tool, `/deep-research`, `/goal` (when workflows are on, the **host** evaluates rounds and runs adversarial verification).
- Host API (`create-workflow` skill): `agent()`, `parallel()`, `phase()`, `complete()`, `pause()` / `await_user()`, `budget()`, scratch files, `isolation_worktree`, `resume_from`, `capability_mode`.
- `agent_budget` default 128 (1–1,024). Concurrent children capped at 32 per run (queue, still a barrier).
- **Process restart:** a run interrupted by process exit is terminal `Interrupted` and is **not** resumed — “external effects have no stable cross-process identity.” Same-process pause/resume replays the journal under the original immutable script and cap.
- Conversion: `[features] workflow_conversion` on the daemon route can rewrite legacy `.rhai` to a JS module.

This is the Grok-native multi-agent pipeline. It is **not** a cron daemon. Overnight only works if the Grok process (TUI, `grok agent stdio`, or `grok agent serve`) stays up.

### B. Scheduler / `/loop` — timed wakeups, optional durable

`/loop [interval] <prompt>` wraps `scheduler_create`. Intervals: `Ns` (min 60s), `Nm`, `Nh`, `Nd`. Behavior:

- Fires immediately, then on the interval
- Each fire is a **detached background subagent**; it cannot see the conversation; the prompt must stand alone
- Recurring tasks **auto-expire after 7 days**
- Max **50** scheduled tasks
- `scheduler_create`: `interval`, `prompt`, `fire_immediately` (default false), `recurring` (default true), **`durable` persist across sessions (default false)**
- Grok schedules are **intervals, not cron expressions** (`sessionCrons[].schedule` is e.g. `every 5 minutes`)
- Auto-wake turns (scheduler fires, task/subagent completions) run `UserPromptSubmit` observe-only

`monitor` is the streaming counterpart (line-based events; `persistent: true` lasts the session; 10-hour default timeout in the bundled long-running-tasks skill).

**Overnight use:** `scheduler_create` with `durable: true` and an interval ≥ 60s, plus a process that can accept the fire (a live session, or a durable task that Grok will resume). Still expires at 7 days. This is polling, not a self-referential coding loop.

### C. Ralph-loop — Stop-hook in-session loop, not a Grok built-in

Ralph-loop is an **installed Claude marketplace plugin**, not a Grok user-guide feature. Layout on this machine:

```
ralph-loop/
  .claude-plugin/plugin.json
  commands/{ralph-loop,cancel-ralph,help}.md
  hooks/hooks.json          # Stop → bash "${CLAUDE_PLUGIN_ROOT}/hooks/stop-hook.sh"
  scripts/setup-ralph-loop.sh
```

Mechanism: `/ralph-loop "<prompt>" --max-iterations N --completion-promise TEXT` writes `.claude/ralph-loop.local.md`; a **Stop** hook blocks exit and feeds the same prompt back until a `<promise>…</promise>` match or max iterations.

Grok **can** run this class of plugin because:

- Stop hooks are Claude-compatible (`decision: "block"` + `reason` continues the turn; exit 2 + stderr also blocks when stdout has no readable reply)
- Plugin hooks get `GROK_PLUGIN_ROOT` and the `CLAUDE_PLUGIN_ROOT` alias
- `[compat.claude] hooks` is on by default

Grok **does not** match Claude 1:1 (`10-hooks.md` “Porting Claude Code stop hooks”):

- **8 continuations per turn**, then the gate is overridden and the turn ends. A long goal must span **turns** (next user prompt / scheduler fire), not one infinite Stop loop.
- stdin is camelCase (`stopHookActive`, `backgroundTasks`, `sessionCrons`) vs Claude snake_case
- Extra observe-only Stop at session end (`reason: "channel_closed"` / `"shutdown"`); filter `reason == "end_turn"`
- Session-end Stop ignores decision output
- `StopCancelled` is Grok-specific
- Plugin agent frontmatter still cannot declare hooks — the loop hook must be plugin `hooks/hooks.json`, not an agent header

**Adapter recommendation (from these APIs, not a product decision):**

| Need | Grok API |
| --- | --- |
| Multi-agent pipeline with verification, one process | Workflows + `/goal` |
| Wake every N minutes while a session/durable scheduler exists | `/loop` / `scheduler_create` (`durable` for cross-session) |
| Iterate the same prompt until tests pass, in one sitting | Stop-hook loop **ported** to Grok (state file under `.grok/`, honor 8-cap by chaining turns or `/goal`) |
| Survive `grok` process death | **None of the three.** Workflows do not resume across process restart. Scheduler durable still needs something to fire into. |

`hosts/grok` implements whichever overnight driver the spec picks. `core/` states the loop’s success criteria, not the hook JSON.

---

## 7. Browser / UI proof hooks

Grok’s user-guide **does not** document a first-party browser-automation or screenshot-capture tool. What exists:

**MCP.** Any proof browser (Playwright, Chrome DevTools, …) is an MCP server: `[mcp_servers.<name>]` in config, or a trusted plugin’s `.mcp.json`. The model then `search_tool` / `use_tool`s those tools. Org allow/deny lists still apply. This is the documented extension point for “drive a UI.”

**Hooks.** `PostToolUse` can read a tool result (including image/PDF reads) and replace the **model-facing** copy; the transcript keeps the original. Images are dropped if the replacement is a string. `PreToolUse` can deny. `Stop` can refuse to end a turn until a proof command succeeded (exit 2 / `decision: "block"`). Matcher on tool events tests the real tool name; MCP calls appear as `server__tool` (and Claude’s `mcp__server__tool`).

There is no hook event named “browser” or “screenshot.” A proof gate is a Stop/PostToolUse script the adapter ships in `hosts/grok/**/hooks/hooks.json`.

**Image tools** (`features.image_gen` / `image_edit`, `/imagine`): generate or edit images. They are not a capture path for the user’s app.

**TUI paste:** users can paste clipboard screenshots into the prompt (`03-keyboard-shortcuts.md`). That is human-provided evidence, not an agent proof hook.

**`web_fetch` / `web_search`:** HTTP fetch and search, not a rendered page. `web_fetch` defaults off (`features.web_fetch`); loopback is fail-closed (`allow_local`).

**ACP:** no browser methods under `x.ai/*`. Filesystem, git, worktree, search, terminal, session, auth, telemetry only.

**computer-use** on this machine is an **Orca** skill (`~/.agents/skills/computer-use/SKILL.md`), not a Grok runtime API. Do not treat it as part of the Grok host adapter surface.

**Adapter duty:** `hosts/grok` may vendor a Playwright (or similar) `.mcp.json`, plus a Stop hook that blocks completion unless a named proof command ran. The *procedure* (“open the ticket URL, screenshot the broken control, attach the image”) lives in `core/` and must call a capability, not `playwright__*`.

---

## 8. What must be implemented, split by tree

### `hosts/grok` — Grok runtime glue

1. **Marketplace package**
   - `.grok-plugin/marketplace.json` listing the Grok plugin
   - optional `.grok-plugin/plugin-index.json` if the Marketplace tab should show components pre-install
   - optional `.claude-plugin/` copies if dual-host layout is desired (Grok accepts both)
2. **Plugin directory**
   - `plugin.json` metadata (`name`, `version`, `description`, `author`, …)
   - `skills/` pointing at or wrapping `core/` skill files
   - `commands/` for Grok slash commands (`/mstack` or whatever the spec names — still open on issue 1)
   - `agents/` for Grok agent `.md` files
   - `hooks/hooks.json` (Stop / PostToolUse proof gates, overnight loop if Stop-based)
   - `.mcp.json` for any Grok-attached MCP (issue tracker, browser proof)
3. **Install surface**
   - documented `grok plugin marketplace add` + `grok plugin install <name> --trust`
   - `[plugins].enabled` snippet; optional `[plugins].paths` for a vendored dir under `~/.grok/plugins/` (auto-trust)
4. **Subagent wiring**
   - `spawn_subagent` mapping from playbook workers → `plugin-name:agent-name`
   - `isolation: worktree` + apply path (`x.ai/git/worktree/apply` or an explicit merge step for workflow `isolation_worktree`)
   - `mcpInheritance` on plugin agents if MCP must be narrowed
5. **Model/role**
   - documented `[subagents.roles]` / `[subagents.models]` / `[models].default` (Grok IDs)
   - optional `.grok/roles/*.toml` and `.grok/personas/*.toml` shipped or generated by a Grok setup command
6. **Overnight driver** (once issue 1 decides)
   - workflows: `.grok/workflows/*.rhai` + `/goal` settings
   - and/or durable `scheduler_create` / `/loop`
   - and/or a Grok-ported Stop-hook loop (not the Claude `.claude/ralph-loop.local.md` paths as-is)
7. **Proof**
   - plugin MCP + hooks; not a new Grok tool

ACP is how IDEs talk to Grok (`grok agent stdio` / `serve`). A host adapter that is a **plugin** does not reimplement ACP; a host adapter that is an **ACP client** wrapping Grok would. mainart-stack’s Grok adapter as specified on the map is the plugin path.

### `core/` — host-agnostic

- Skill and playbook bodies (steps, acceptance, packet language)
- Capability names (`validation.judge`, …) — call the slot, never the module or the Grok tool
- Agent prompt prose that does not mention `spawn_subagent`, `GROK_*`, or `~/.grok`
- Rules content suitable for `AGENTS.md` on any host

### Do not put in `core/`

- `marketplace.json` / `plugin.json` / `.mcp.json` / `hooks.json`
- `[plugins]` / `[subagents]` / `[models]` TOML
- `isolation: worktree` or `x.ai/git/worktree/*`
- `.rhai` workflow scripts (Grok dialect + host API)
- Ralph-loop Stop hook scripts and `.claude/` state files
- Playwright MCP server blocks

---

## 9. Gaps (primary sources do not settle)

- **`plugin.json` path-override schema.** Grok says the file can override paths; no field list in the user-guide. Installed plugins only use metadata.
- **Plugin agent frontmatter schema for Grok.** Bundled agents document `prompt_mode`, `permission_mode`, `agents_md`, `model`. Claude cache agents use `tools`, `effort`, `maxTurns`. The intersection Grok will honor for *plugin* agents is not fully tabulated.
- **Overnight pick.** APIs exist; issue 1 still has the product choice open. Constraint: workflows die with the process; Stop hooks cap at 8 continuations/turn; scheduler expires at 7 days.
- **First-party UI proof.** None. Proof is MCP + hooks + shell.
- **`subagents.roles` in the config-reference table.** Documented in `16-subagents.md` and present as bundled `roles/*.toml`; absent from the `26-config-reference.md` `subagents` key list.
- **Depth limit.** Prose: children cannot spawn. Config: `max_depth` exists. Adapter should assume depth 1 unless inspect shows otherwise.

---

## Sources

| Claim area | Source |
| --- | --- |
| Plugin contents, marketplace JSON, install, trust, discovery, `plugin.json` optional | `/home/luizdmm/.grok/docs/user-guide/09-plugins.md` |
| Skills frontmatter, qualified `/plugin:name`, locations | `/home/luizdmm/.grok_personal/docs/user-guide/08-skills.md` |
| `spawn_subagent`, isolation, worktrees, plugin agent restrictions, roles/personas | `/home/luizdmm/.grok_personal/docs/user-guide/16-subagents.md` |
| ACP `x.ai/git/worktree/*`, `session/new` `_meta` | `/home/luizdmm/.grok_personal/docs/user-guide/15-agent-mode.md` |
| `config.toml` layers, `[plugins]`, `[workflows]`, `[agent]`, `[models]`, `[subagents]` | `/home/luizdmm/.grok_personal/docs/user-guide/05-configuration.md`, `26-config-reference.md` |
| AGENTS.md / rules dirs vs config | `/home/luizdmm/.grok_personal/docs/user-guide/12-project-rules.md` |
| Stop / PostToolUse / 8-continuation cap / camelCase vs Claude | `/home/luizdmm/.grok_personal/docs/user-guide/10-hooks.md` |
| `/loop`, scheduler `durable`, 7-day expiry, monitor | `/home/luizdmm/.grok_personal/docs/user-guide/20-background-tasks.md`, `04-slash-commands.md` |
| Workflow host API, `isolation_worktree`, no cross-process resume | `/home/luizdmm/.grok/bundled/skills/create-workflow/SKILL.md` |
| Sandbox ≠ worktree | `/home/luizdmm/.grok_personal/docs/user-guide/18-sandbox.md` |
| Grove clone vs session worktrees | `/home/luizdmm/.grok_personal/docs/user-guide/27-grok-clone.md` |
| Installed plugin shapes | `/home/luizdmm/.grok/installed-plugins/{python-fastapi-development-bundle-b42dd014,github-f4ae7665,sentry-for-claude-b356088e,registry.json}` |
| Ralph-loop as Stop-hook plugin | `/home/luizdmm/.grok_personal/marketplace-cache/783232b622f8182e/plugins/ralph-loop/` |
| Bundled agents/roles | `/home/luizdmm/.grok/bundled/agents/`, `/home/luizdmm/.grok/bundled/roles/` |
| MCP config | `/home/luizdmm/.grok_personal/docs/user-guide/07-mcp-servers.md` |
| Product terms | `GLOSSARY.md` in this repo |
