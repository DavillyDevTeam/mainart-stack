# Claude Code and Codex host-adapter interfaces

**Ticket:** [Document Claude Code and Codex adapter interfaces](https://github.com/DavillyDevTeam/mainart-stack/issues/6)

**Question:** What must the host adapter *interface* include so Claude Code and Codex can be added later without rewriting `core/`?

This note lists the **ports** a host adapter must own. It does not specify plugin internals, skill bodies, or a product implementation. `core/` is the host-agnostic skills, playbooks, and agent prompts ([`GLOSSARY.md`](../../GLOSSARY.md)). Each host adapter is the runtime glue for one agent host.

Fetched 2026-10-12 from first-party docs and first-party example plugins.

## Answer

`core/` must not call Claude Code or Codex surfaces by name. Five ports cover the ticket:

| Port | What `core/` names | Claude Code adapter owns | Codex adapter owns |
| --- | --- | --- | --- |
| **Manifest / skill layout** | “install this pack” | `.claude-plugin/plugin.json`, `skills/<name>/SKILL.md`, `agents/*.md`, `hooks/hooks.json`, marketplace `.claude-plugin/marketplace.json` | Root `plugin.json` (Agent Plugins schema) and/or `.codex-plugin/plugin.json`; `skills/<name>/SKILL.md`; skill `agents/openai.yaml`; marketplace `.agents/plugins/marketplace.json` |
| **Invocation** | “run this skill” | `/<plugin>:<directory>` or `/skill-name`; `disable-model-invocation` / `user-invocable` | `$skill` / `/skills` / `$` in CLI/IDE; `@` in ChatGPT; `policy.allow_implicit_invocation` |
| **Subagent spawn** | “delegate this worker” | Agent tool + `subagent_type`; `@agent-<name>` / `@agent-<plugin>:<name>`; plugin `agents/*.md` | Spawn request or skill instruction; custom agents as `~/.codex/agents/*.toml` or `.codex/agents/*.toml`; plugin-level `agents/` |
| **Model-role / setup file** | “write durable host instructions and model” | `CLAUDE.md` (or `AGENTS.md`); `/init`; settings `model` | `AGENTS.md`; `/init`; `config.toml` `model`; plugin `extensions.com.openai.onboardingSkill` |
| **Overnight / long-run** | “keep working until done” | `/goal` (prompt-based Stop hook); `/loop`; Stop hook `ok:false` / `impossible:true`; cloud/desktop scheduled tasks | `/goal` (`features.goals`); Stop hook `decision: "block"`; automations; plugin lifecycle hooks (desktop, not public directory) |

Those five strings are the only host-specific names later Claude Code and Codex adapters may bind. Everything else in this note is evidence for those bindings.

## 1. Manifest / skill / marketplace layout

### Claude Code

A plugin is a directory of components, usually with a manifest. The manifest is `.claude-plugin/plugin.json`. It gives the plugin its name and optional metadata. Components include skills (`SKILL.md` Claude loads when relevant and that the user can run as a command), agents (subagent definitions), hooks, and MCP servers. ([Plugins overview](https://code.claude.com/docs/en/plugins/overview))

The manifest is optional. Without it, Claude Code loads the standard layout. The plugin name then comes from the marketplace entry, or from the directory name with `--plugin-dir`. When a manifest exists, `name` is the only required key: kebab-case, no spaces, `@`, `:`, or path separators. Claude Code namespaces every component under it, so an agent `reviewer` in plugin `deploy-tools` appears as `deploy-tools:reviewer`. Put every other plugin file at the plugin root, not inside `.claude-plugin/`. That includes `skills/`, `commands/`, and `hooks/`. ([Plugin manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference))

Default component layout and what the user sees ([Add components to a plugin](https://code.claude.com/docs/en/plugins/components)):

- Skills: `skills/<name>/SKILL.md`. Command name is `/<plugin>:<directory>` (example: `skills/review/SKILL.md` in `my-plugin` is `/my-plugin:review`). Frontmatter `name` replaces the last segment; the plugin prefix stays.
- Commands: older format at `commands/<file>.md` → `/<plugin>:<file>`. Skills supersede commands for new work.
- Agents: each Markdown file under `agents/` defines one subagent. Name form is `<plugin>:<name>`. The `agents` manifest key replaces the `agents/` scan.
- Hooks: `hooks/hooks.json` at the plugin root, under a top-level `"hooks"` key, same shape as `settings.json`. Plugin hooks register when the session loads the plugin; they do not wait for a plugin skill to run.
- MCP: `.mcp.json` at the plugin root.

A marketplace is a repository or directory with `.claude-plugin/marketplace.json` that lists plugins and where to fetch each one. Users install by name such as `commit-commands@claude-plugins-official`. ([Plugins overview](https://code.claude.com/docs/en/plugins/overview)) Top-level required fields are `name`, `owner`, and `plugins`. Each plugin entry requires `name` and `source`. ([Marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference))

First-party catalog shape: Anthropic’s official marketplace file at [`anthropics/claude-plugins-official/.claude-plugin/marketplace.json`](https://github.com/anthropics/claude-plugins-official/blob/main/.claude-plugin/marketplace.json) sets `"name": "claude-plugins-official"`, an `owner` object, and a `plugins` array of `{name, source, ...}` entries.

**Adapter port:** emit `.claude-plugin/plugin.json` + `skills/<name>/SKILL.md` (+ optional `agents/`, `hooks/hooks.json`, `.mcp.json`) and, for distribution, `.claude-plugin/marketplace.json`. Do not put those paths in `core/`.

### Codex

OpenAI’s packaging docs describe two layouts on the same plugin folder ([Package your plugin](https://developers.openai.com/plugins/build/plugins)):

1. **Portable Agent Plugins package:** `plugin.json` at the plugin root with `"$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"`. Skills live under `skills/`. Portable packages discover skills from that directory, so the manifest does not need a `skills` field. Plugin hosts use kebab-case `name` as the plugin identifier and component namespace.
2. **Codex compatibility overlay:** existing `.codex-plugin/plugin.json` files remain supported as a fallback. `@plugin-creator` still scaffolds that overlay. Only `plugin.json` belongs in `.codex-plugin/`; `skills/`, `mcp.json` / `.mcp.json`, `hooks/`, and `assets/` stay at the plugin root.

When `extensions.com.openai` is an object on the root manifest, it **replaces** the entire `.codex-plugin/plugin.json` overlay as the source of OpenAI-specific settings; the two are not merged. Put presentation, registered MCP mappings, hooks, and `onboardingSkill` under `extensions.com.openai`. ([Package your plugin](https://developers.openai.com/plugins/build/plugins))

First-party example repo [`openai/plugins`](https://github.com/openai/plugins) still documents the compatibility layout as required: each plugin lives under `plugins/<name>/` with a required `.codex-plugin/plugin.json` and optional `skills/`, `.app.json`, `.mcp.json`, plugin-level `agents/`, `commands/`, `hooks.json`, and `assets/`. The default marketplace is `.agents/plugins/marketplace.json`. Zoom’s first-party overlay ([`plugins/zoom/.codex-plugin/plugin.json`](https://github.com/openai/plugins/blob/main/plugins/zoom/.codex-plugin/plugin.json)) has `name`, `version`, `description`, `skills: "./skills/"`, `apps`, and `interface`. Figma’s overlay ([`plugins/figma/.codex-plugin/plugin.json`](https://github.com/openai/plugins/blob/main/plugins/figma/.codex-plugin/plugin.json)) is the same shape.

A Codex / ChatGPT marketplace is a JSON catalog. Repo-scoped list: `$REPO_ROOT/.agents/plugins/marketplace.json`. Personal list: `~/.agents/plugins/marketplace.json`. Entries live under `plugins[]`; `source.path` is a `./`-prefixed path relative to the marketplace root. Enable a local-marketplace plugin in `.codex/config.toml` as `[plugins."plugin-name@marketplace-name"] enabled = true`. CLI: `codex plugin marketplace add`. ([Package your plugin](https://developers.openai.com/plugins/build/plugins))

Skill-level OpenAI metadata lives at `agents/openai.yaml` beside `SKILL.md`. Official skill docs list it as optional appearance, invocation policy, and tool dependencies. ([Build skills](https://developers.openai.com/codex/skills), [Build skills (plugins)](https://developers.openai.com/plugins/build/skills)) First-party Zoom skill overlay:

```yaml
interface:
  display_name: "/setup-zoom-oauth"
  short_description: Use when setting up OAuth.
policy:
  allow_implicit_invocation: false
```

([`plugins/zoom/skills/setup-zoom-oauth/agents/openai.yaml`](https://github.com/openai/plugins/blob/main/plugins/zoom/skills/setup-zoom-oauth/agents/openai.yaml)) Plugin-level `agents/openai.yaml` is used for surface copy (Figma: `interface.display_name`, `short_description`, icons, `default_prompt`). ([`plugins/figma/agents/openai.yaml`](https://github.com/openai/plugins/blob/main/plugins/figma/agents/openai.yaml)) MCP tool dependencies are declared in `agents/openai.yaml` as `dependencies.tools[]` with `type: "mcp"`. ([Build skills (plugins)](https://developers.openai.com/plugins/build/skills))

**Adapter port:** emit either root `plugin.json` (schema `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`) plus optional `extensions.com.openai`, or the ticket’s `.codex-plugin/plugin.json` overlay; always `skills/<name>/SKILL.md`; per-skill `agents/openai.yaml` when invocation policy or MCP deps are host-specific; marketplace `.agents/plugins/marketplace.json`.

## 2. Invocation (slash vs `$skill`)

### Claude Code

Users invoke a skill with `/skill-name`. Plugin skills are namespaced as `/plugin-name:skill-name`. ([Extend Claude with skills](https://code.claude.com/docs/en/skills); [Add components](https://code.claude.com/docs/en/plugins/components); [Plugins in the SDK](https://code.claude.com/docs/en/agent-sdk/plugins))

Two frontmatter fields restrict who may invoke ([Extend Claude with skills](https://code.claude.com/docs/en/skills)):

| Frontmatter | User can invoke | Claude can invoke | Context |
| --- | --- | --- | --- |
| default | yes | yes | description always in context; full skill loads when invoked |
| `disable-model-invocation: true` | yes (`/name`) | not on its own | description not in context; full skill loads when invoked |
| `user-invocable: false` | no | yes | description always in context; full skill loads when invoked |

`disable-model-invocation: true` also prevents the skill from being preloaded into subagents and from running when a scheduled task fires with the skill as its prompt. Plugin skills and a skill at any other location both load, because plugin skills are namespaced as `/plugin-name:skill-name`.

**Adapter port:** map `core/` “run skill X” to `/<plugin>:<skill>` (and `/skill` for non-plugin skills). HITL-only skills set `disable-model-invocation: true`. Model-only skills set `user-invocable: false`.

### Codex

Codex and ChatGPT activate skills two ways ([Build skills](https://developers.openai.com/codex/skills)):

1. **Explicit:** include the skill in the prompt. ChatGPT: type `@` to select a skill (and `@plugin-creator` for the creator). Codex CLI / IDE: run `/skills` or type `$` to mention a skill (example: `$skill-creator`).
2. **Implicit:** the host chooses a skill when the task matches `description`.

Zoom’s first-party README states the same explicit form: invoke a bundled skill with `$skill-name`, for example `$start` or `$setup-zoom-oauth`. Developer skills in that package set `policy.allow_implicit_invocation: false` in `agents/openai.yaml` so they are available when invoked directly and are not selected from ordinary task wording. ([openai/plugins Zoom README](https://github.com/openai/plugins/tree/main/plugins/zoom))

**Adapter port:** map `core/` “run skill X” to `$<skill>` (CLI/IDE) and `@<skill>` (ChatGPT). HITL-only skills set `policy.allow_implicit_invocation: false` in `agents/openai.yaml`. Do not emit `/plugin:skill` from a Codex adapter.

## 3. Subagent spawn

### Claude Code

Claude invokes subagents through the **Agent tool**. An Agent tool call that omits `subagent_type` fails with `subagent_type is required` when the session has no `general-purpose` fallback. Denying the Agent tool prevents all delegation. ([Create custom subagents](https://code.claude.com/docs/en/sub-agents); [Subagents in the SDK](https://code.claude.com/docs/en/agent-sdk/subagents))

Plugin agents live in the plugin’s `agents/` directory. They have the lowest scope priority (managed settings → `--agents` CLI → `.claude/agents/` → `~/.claude/agents/` → plugin `agents/`). The user invokes a plugin agent explicitly as `@agent-my-plugin:security-reviewer` (or `@agent-<name>` for local agents). `claude --agent <name>` runs the whole session as that subagent; for a plugin agent the short name is enough. ([Create custom subagents](https://code.claude.com/docs/en/sub-agents); [Add components](https://code.claude.com/docs/en/plugins/components))

Plugin subagent frontmatter supports `name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, `omitClaudeMd`, `isolation` (`"worktree"` only), `color`, and experimental `cacheTtl`. For security, plugin subagents **ignore** `hooks`, `mcpServers`, `permissionMode`, and `initialPrompt`. Ship hooks in the plugin’s `hooks/hooks.json` and MCP servers in `.mcp.json` instead; those apply whenever the plugin is enabled, not only inside the subagent. ([Add components](https://code.claude.com/docs/en/plugins/components); [Create custom subagents](https://code.claude.com/docs/en/sub-agents))

**Adapter port:** spawn = Agent tool with `subagent_type` (`<plugin>:<name>` for plugin agents). User pin = `@agent-<plugin>:<name>`. Session-as-agent = `--agent`. Worker definitions are Markdown under `agents/`. Do not rely on per-agent `hooks` / `mcpServers` / `permissionMode` in a plugin agent file.

### Codex

ChatGPT Work and Codex spawn specialized agents in parallel and collect results. Current local Codex releases delegate when the user asks directly (“spawn two agents”, “delegate this work in parallel”) or when `AGENTS.md` or skill instructions request it. Codex handles orchestration: spawning, routing follow-ups, waiting, closing threads. ([Subagents](https://developers.openai.com/codex/subagents))

Built-in agents: `default`, `worker`, `explorer`. Custom agents are standalone TOML files: `~/.codex/agents/` (personal) or `.codex/agents/` (project). Required fields: `name`, `description`, `developer_instructions`. Optional: `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`, `skills.config`. Global knobs live under `[agents]` in `config.toml` (`enabled`, `max_concurrent_threads_per_session`, `default_subagent_model`, `default_subagent_reasoning_effort`). A custom agent whose `name` matches a built-in (for example `explorer`) takes precedence. ([Subagents](https://developers.openai.com/codex/subagents))

Plugin-level `agents/` is a first-party companion surface in [`openai/plugins`](https://github.com/openai/plugins) (Zoom bundles reviewer agents `zoom-oauth-scope-auditor` and `zoom-integration-reviewer` under `agents/`). That is a plugin packaging convention, distinct from the TOML custom-agent files Codex loads from `~/.codex/agents/` and `.codex/agents/`.

**Adapter port:** spawn = host “spawn/delegate” instruction (or skill/`AGENTS.md` text that requests it), optionally naming a custom agent `name` from `.codex/agents/<name>.toml`. Do not emit Claude’s Agent tool or `@agent-` mentions from a Codex adapter.

## 4. Model-role / setup file

### Claude Code

Each session starts empty. Durable project instructions are **CLAUDE.md** files. Claude can also read a repository’s **AGENTS.md** in place of CLAUDE.md. Load order (broadest → most specific): managed policy CLAUDE.md → `~/.claude/CLAUDE.md` → `./CLAUDE.md` or `./.claude/CLAUDE.md` (and `./AGENTS.md` when that is the project file) → `./CLAUDE.local.md`. ([How Claude remembers your project](https://code.claude.com/docs/en/memory))

`/init` generates a starting CLAUDE.md from the codebase. If CLAUDE.md already exists, `/init` suggests improvements rather than overwriting it. With `CLAUDE_CODE_NEW_INIT=1`, `/init` can also set up skills and hooks. Claude Code does **not** load a `CLAUDE.md` at a **plugin** root (`claude plugin validate` warns `CLAUDE.md at the plugin root is not loaded as project context`). Plugin instructions belong in a skill. ([How Claude remembers your project](https://code.claude.com/docs/en/memory); [Add components](https://code.claude.com/docs/en/plugins/components))

Model selection, in priority order: `/model` during the session → `claude --model` at startup → `ANTHROPIC_MODEL` → settings file field `model` → `ANTHROPIC_DEFAULT_MODEL`. `/model` writes the `model` field in user settings as the default for new sessions. Aliases include `sonnet`, `opus`, `haiku`, `fable`, `best`, `opusplan`. Subagents may set their own `model` in frontmatter (`sonnet`, `opus`, `haiku`, `fable`, `inherit`, or a full id). ([Model configuration](https://code.claude.com/docs/en/model-config); [Create custom subagents](https://code.claude.com/docs/en/sub-agents))

**Adapter port:** write project instructions to `CLAUDE.md` (Claude-native) or `AGENTS.md` (shared filename Claude also reads). Scaffold with `/init`. Persist default model in settings `model`. Put plugin setup in a skill, not a plugin-root CLAUDE.md.

### Codex

Codex reads **AGENTS.md** before doing any work. Discovery: global `~/.codex/AGENTS.override.md` else `~/.codex/AGENTS.md`; then from project root down to cwd, at most one of `AGENTS.override.md` / `AGENTS.md` / `project_doc_fallback_filenames` per directory; concatenate root → cwd so closer files override. Default combined cap: `project_doc_max_bytes` (32 KiB). ([Custom instructions with AGENTS.md](https://developers.openai.com/codex/guides/agents-md))

`/init` in the CLI scaffolds a starter `AGENTS.md` in the current directory. ([Best practices](https://developers.openai.com/codex/learn/best-practices))

Default model is `model` in `config.toml` (example value in the config reference: `gpt-6.1-sol`). Custom agents may override `model` and `model_reasoning_effort`. ([Configuration Reference](https://developers.openai.com/codex/config-reference); [Subagents](https://developers.openai.com/codex/subagents))

Plugin setup after install is `extensions.com.openai.onboardingSkill`, a path relative to the plugin root pointing at a packaged skill (docs example: `./skills/setup/SKILL.md`). For the compatibility format, put the same field in `.codex-plugin/plugin.json`; the path still resolves from the plugin root. ([Package your plugin](https://developers.openai.com/plugins/build/plugins))

**Adapter port:** write durable instructions to `AGENTS.md`. Scaffold with `/init`. Persist default model in `config.toml` `model`. Plugin first-run setup is `onboardingSkill`, not a plugin-root CLAUDE.md.

`AGENTS.md` is the overlapping setup filename. Claude Code also reads it. A later shared `core/` instruction file can be `AGENTS.md` if the Claude adapter does not also require Claude-only fields that belong in CLAUDE.md.

## 5. Overnight / long-run hook

### Claude Code

Three in-session ways to keep working, plus out-of-session schedules ([Keep Claude working toward a goal](https://code.claude.com/docs/en/goal); [Run prompts on a schedule](https://code.claude.com/docs/en/scheduled-tasks)):

| Approach | Next turn starts when | Stops when |
| --- | --- | --- |
| `/goal` | previous turn finishes (or idle check-in / retry) | evaluator says the condition is met or impossible, or an unrecoverable error, or `/goal clear` |
| `/loop` | a time interval elapses | user stops it, or Claude decides the work is done |
| Stop hook | previous turn finishes | the hook’s script or prompt decides |

`/goal` is a session-scoped wrapper around a **prompt-based Stop hook**. After each turn, the small fast model returns one of: not yet met (keep working), met (clear goal), impossible (clear goal as failed). Condition length cap: 4,000 characters. One goal per session. `/goal` works in `-p` non-interactive mode. A goal does not change permission mode; unattended runs need auto mode. ([Keep Claude working toward a goal](https://code.claude.com/docs/en/goal))

Prompt-based Stop hooks: `"ok": true` allows stop; `"ok": false` feeds `reason` back so Claude keeps working, unless `"impossible": true` also, which allows the stop. Agent-based Stop hooks use the same `"ok"` / `"reason"` shape, with no `impossible` field. ([Automate actions with hooks](https://code.claude.com/docs/en/hooks-guide))

`/loop` is a bundled skill: `/loop 5m <prompt>` on a cron interval; `/loop <prompt>` with a model-chosen delay; `/loop` with a built-in maintenance prompt. A scheduled fire only runs skills Claude is allowed to invoke on its own; `disable-model-invocation: true` skills arrive as plain text. Cloud routines and desktop scheduled tasks outlive the session. ([Run prompts on a schedule](https://code.claude.com/docs/en/scheduled-tasks))

Plugin hooks, including Stop, live in `hooks/hooks.json` and fire for the whole session once the plugin is enabled. ([Add components](https://code.claude.com/docs/en/plugins/components))

**Adapter port:** long-run = `/goal <condition>` (Stop-hook wrapper) or a Stop hook that returns `ok: false` until done. Interval polling = `/loop`. Do not put `/goal` strings in `core/`.

### Codex

`/goal` gives Codex a durable objective across turns. Codex can work independently for multiple hours. Commands: `/goal <objective>`, `/goal` (status), `/goal pause`, `/goal resume`, `/goal clear`. If `/goal` is missing from the slash list, enable it:

```toml
[features]
goals = true
```

or `codex features enable goals`. ([Follow a goal](https://developers.openai.com/codex/use-cases/follow-goals); [Prompting](https://developers.openai.com/codex/prompting))

Stop hooks continue a turn by returning:

```json
{ "decision": "block", "reason": "Run one more pass over the failing tests." }
```

For Stop, `decision: "block"` does not reject the turn. It creates a new continuation prompt from `reason`. Exit code `2` with a reason on stderr is equivalent. `continue: false` from any matching Stop hook wins over continuation. Input includes `stop_hook_active` (whether this turn was already continued) and `last_assistant_message`. SubagentStop uses the same `decision: "block"` continuation shape. ([Hooks](https://developers.openai.com/codex/hooks))

Plugin lifecycle hooks are supported for plugins installed manually in Codex desktop. Plugins that contain lifecycle hooks are not eligible for the public plugin directory. Codex discovers `hooks/hooks.json` by default when the OpenAI extension or compatibility manifest does not define `hooks`. Plugin-bundled hooks are non-managed: Codex skips them until the user reviews and trusts the current hook definition. ([Package your plugin](https://developers.openai.com/plugins/build/plugins))

Out-of-session: ChatGPT/Codex scheduled tasks / automations (`/docs/automations` on the Learn site linked from Codex docs).

**Adapter port:** long-run = `/goal` (feature-flagged) or a Stop hook that returns `decision: "block"` plus `reason`. Plugin overnight hooks are a desktop-only packaging choice, not a public-directory one.

## Ports `core/` must not call

`core/` names host-agnostic operations. Each host adapter binds them. These identifiers stay out of `core/`:

1. **Manifest paths and marketplace files**
   - Claude: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `/<plugin>:` namespacing.
   - Codex: root `plugin.json` (`$schema` `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`), `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `extensions.com.openai`, `onboardingSkill`.
2. **Skill invocation syntax and invocation-policy keys**
   - Claude: `/skill-name`, `/plugin:skill`, `disable-model-invocation`, `user-invocable`.
   - Codex: `$skill`, `/skills`, `$`, ChatGPT `@`, `policy.allow_implicit_invocation` in `agents/openai.yaml`.
3. **Subagent spawn APIs**
   - Claude: Agent tool, `subagent_type`, `@agent-<name>`, `@agent-<plugin>:<name>`, `--agent`, plugin `agents/*.md` (and the ignored `hooks` / `mcpServers` / `permissionMode` fields).
   - Codex: spawn/delegate prompts, `[agents]` in `config.toml`, `~/.codex/agents/*.toml` / `.codex/agents/*.toml` (`name`, `description`, `developer_instructions`).
4. **Setup file and model-role writes**
   - Claude: `CLAUDE.md`, `/init` (CLAUDE.md + optional skills/hooks), settings `model`, `/model`.
   - Codex: `AGENTS.md`, `/init` (AGENTS.md), `config.toml` `model`, `onboardingSkill`.
5. **Overnight continuation**
   - Claude: `/goal`, `/loop`, prompt Stop `{ok:false, reason, impossible?}`, cloud/desktop scheduled tasks.
   - Codex: `/goal` + `features.goals`, Stop `{decision:"block", reason}`, automations, desktop-only plugin lifecycle hooks.

Shared on-disk shapes that `core/` *may* own, with adapters wrapping them:

- `skills/<name>/SKILL.md` with `name` and `description` (both hosts; Agent Skills standard).
- `AGENTS.md` as a project instruction file (Codex primary; Claude reads it in place of CLAUDE.md).
- Markdown worker prompts (Claude: `agents/*.md`; Codex custom agents need a TOML wrapper the adapter writes).

## Out of scope (this ticket)

Plugin internals (skill bodies, MCP server implementations, hook scripts, marketplace hosting, evals). Product code under `core/` or `hosts/`. Grok adapter surface (separate ticket).

## Sources

Claude Code (docs.claude / code.claude.com):

- [Plugins overview](https://code.claude.com/docs/en/plugins/overview)
- [Plugin manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference)
- [Add components to a plugin](https://code.claude.com/docs/en/plugins/components)
- [Marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference)
- [Plugins in the SDK](https://code.claude.com/docs/en/agent-sdk/plugins)
- [Extend Claude with skills](https://code.claude.com/docs/en/skills)
- [Create custom subagents](https://code.claude.com/docs/en/sub-agents)
- [Subagents in the SDK](https://code.claude.com/docs/en/agent-sdk/subagents)
- [How Claude remembers your project](https://code.claude.com/docs/en/memory)
- [Model configuration](https://code.claude.com/docs/en/model-config)
- [Keep Claude working toward a goal](https://code.claude.com/docs/en/goal)
- [Automate actions with hooks](https://code.claude.com/docs/en/hooks-guide)
- [Hooks reference](https://code.claude.com/docs/en/hooks)
- [Run prompts on a schedule](https://code.claude.com/docs/en/scheduled-tasks)
- First-party marketplace: [anthropics/claude-plugins-official `.claude-plugin/marketplace.json`](https://github.com/anthropics/claude-plugins-official/blob/main/.claude-plugin/marketplace.json)

Codex / OpenAI plugins (developers.openai.com and learn.chatgpt.com first-party pages):

- [Package your plugin](https://developers.openai.com/plugins/build/plugins)
- [Build skills (plugin packaging)](https://developers.openai.com/plugins/build/skills)
- [Build skills (Codex)](https://developers.openai.com/codex/skills)
- [Plugins (Codex product)](https://developers.openai.com/codex/plugins)
- [Subagents](https://developers.openai.com/codex/subagents)
- [Custom instructions with AGENTS.md](https://developers.openai.com/codex/guides/agents-md)
- [Best practices](https://developers.openai.com/codex/learn/best-practices) (`/init`)
- [Configuration Reference](https://developers.openai.com/codex/config-reference) (`model`)
- [Follow a goal](https://developers.openai.com/codex/use-cases/follow-goals)
- [Prompting](https://developers.openai.com/codex/prompting) (Goal mode)
- [Hooks](https://developers.openai.com/codex/hooks)
- First-party examples: [openai/plugins README](https://github.com/openai/plugins), [Zoom `.codex-plugin/plugin.json`](https://github.com/openai/plugins/blob/main/plugins/zoom/.codex-plugin/plugin.json), [Zoom `agents/openai.yaml`](https://github.com/openai/plugins/blob/main/plugins/zoom/skills/setup-zoom-oauth/agents/openai.yaml), [Figma overlay](https://github.com/openai/plugins/blob/main/plugins/figma/.codex-plugin/plugin.json)
