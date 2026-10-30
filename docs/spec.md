# mainart-stack implementation specification

## Status and authority

This is the documentation deliverable for [Write the consolidated mainart-stack implementation specification](https://github.com/DavillyDevTeam/mainart-stack/issues/15), under [Spec mainart-stack: core, Grok adapter, and module registry](https://github.com/DavillyDevTeam/mainart-stack/issues/1). It specifies a future implementation; it does not indicate that the product, adapters, imports, or tests exist. The repository currently has domain documentation and research, with no product implementation or test suite.

Use the vocabulary in [GLOSSARY.md](../GLOSSARY.md). The seven ADRs remain authoritative. This specification consolidates them without reversing decisions. Supporting research is a recorded snapshot, not a request to upgrade upstreams or perform live API research.

## Problem and outcome

Developers need one agent operating system that clarifies underspecified product work and executes a settled what across agent hosts. Matt Pocock's packet chain supplies clarification and packets; Lauren Tan's pstack supplies engineering playbooks. mainart-stack joins them at the packet/playbook boundary, keeping host behavior in host adapters and optional advice behind a capability registry.

The first runtime is Grok Build. Claude Code and Codex are specified at interface depth only. An implementer must be able to derive observable acceptance checks from this document without reconstructing tracker history or reopening settled decisions.

## Architecture and ownership

The eventual repository has these sibling trees; this packet does not create them:

| Location | Responsibility |
| --- | --- |
| `core/` | Host-agnostic packet-chain skills, rewritten playbooks and supporting skills, agent prompts, router, setup, capability-registry |
| `hosts/grok/` | First runtime, invocation metadata, manifests, required host-operation shims, native configuration and runtime glue |
| `hosts/claude/`, `hosts/codex/` | Later adapters implementing the same interfaces |
| `modules/<id>/` | Optional capability declarations and private provider assets |
| `vendor/pstack/` | Pristine pstack subtree; upstream provenance and maintenance source, not the shipped plugin |
| `.mainart/pins.yaml` | Committed project capability pins, including optional host overlays |
| `.mainart/host` | Local host selection; ignored by git |

Required host operations are runtime obligations. Optional capabilities cannot replace them. Core refers to skills by directory name and requests host behavior through adapter shims. Native tool names, model identifiers, configuration paths, invocation syntax and host manifests belong to adapters. Provider credentials and vendor API details belong to modules.

## Upstreams and maintenance

### Provenance

Use the agreed snapshots from [Inventory upstream pstack](research/pstack-inventory.md) and [Inventory Matt packet-chain skills](research/matt-packet-chain.md):

- pstack 0.15.20 at `cursor/plugins@1b6d44ff`, MIT, Copyright (c) 2026 Lauren Tan.
- Matt Pocock's skills: the inventory reports v1.3.1 metadata, while its installed packet-chain bodies are pinned to `mattpocock/skills@b645f47de3e17ed3bf60586c9bebb8092e0f79fd`, MIT, Copyright (c) 2026 Matt Pocock. Local verification matched all fifteen selected skill-directory Git tree hashes at this revision to the recorded `skillFolderHash` values in the installation lock updated 2026-10-07. Use this revision to reproduce the inventoried bodies. The v1.3.1 tag differs for `to-tickets`, `implement`, and `setup-matt-pocock-skills`; do not substitute the release tag or a newer installed checkout. Record the revision and selected directory tree hashes with the eventual import.

Preserve both upstream copyright and full MIT permission notices with substantial core copies. Keep `vendor/pstack/LICENSE` intact. mainart-stack is the product name; do not brand the product as pstack.

### Vendor and core-copy policy

Follow [ADR-0001](adr/0001-pristine-vendor-tree-core-copies.md), as amended by [ADR-0005](adr/0005-packet-chain-names-occupy-core.md), and the parent map's subtree decision:

1. Take pstack through a `pstack/` prefix-split of `cursor/plugins`, imported as a git subtree at `vendor/pstack/`. Use squash pulls and record the upstream SHA. Do not use a submodule of the whole monorepo or introduce a separate mirror repository.
2. Leave the vendor tree pristine. Rewrite selected files into core at the same relative locations.
3. Compute pstack core-copy membership from `core/X` with matching `vendor/pstack/X`, excluding packet-chain-occupied paths. Do not maintain a separate allowlist file.
4. On updates, port each core copy with a per-file three-way merge: previous upstream file, updated upstream file, and rewritten core file. Review host stripping and acceptance behavior after the port.
5. New vendor files do not automatically enter core. Upstream deletion does not automatically delete a core copy; retain it pending an explicit maintenance decision.

Packet-chain names occupy core first. The current collision is `skills/tdd`: ship Matt's version, retain pstack's only in the vendor tree, and never merge the two. Apply the same exclusion to later collisions. Unique pstack directory names remain unprefixed.

## Exact first-extract scope

### Matt packet chain

Vendor these fifteen skills and their required companions from the agreed inventory:

| Invocation category | Skills |
| --- | --- |
| Explicit user entry | `grill-with-docs`, `grill-me`, `to-spec`, `to-tickets`, `wayfinder`, `triage`, `implement`, `implement-spec`, `setup-matt-pocock-skills` |
| Model-invoked primitives | `grilling`, `domain-modeling`, `prototype`, `tdd`, `code-review`, `research` |

Carry companion instructions and templates, including `domain-modeling/{GLOSSARY-FORMAT.md,ADR-FORMAT.md}`, `prototype/{LOGIC.md,UI.md}`, `triage/{AGENT-BRIEF.md,OUT-OF-SCOPE.md}`, `tdd/{tests.md,mocking.md}`, and setup's tracker/domain templates (`issue-tracker-github.md`, `issue-tracker-gitlab.md`, `issue-tracker-local.md`, `triage-labels.md`, `domain.md`). Preserve referenced companion dependencies from the snapshot. Host metadata such as `agents/openai.yaml` belongs to the relevant adapter, not shared procedure bodies.

Replace Matt's `ask-matt` router with mainart-stack's router. Other Matt skills are outside this chain unless separately selected. In particular, optional consultation of `codebase-design` does not make it a bundled chain dependency. Matt's excluded `teach` is distinct from the included pstack `teach`.

The packet chain uses `grill-with-docs` as its in-repository HITL start; `grill-me` provides the stateless entry. `wayfinder` supports multi-session decisions, `triage` supports inbox classification, `to-spec` produces specifications, and `to-tickets` produces vertical implementation packets. Tracker mechanics and canonical triage labels come from the consumer repository's `docs/agents/*` rather than host-native assumptions.

### pstack core copies

[ADR-0006](adr/0006-first-extract-pstack-core-copies.md) defines the complete first extract. Preserve upstream relative locations, including the router at `core/skills/poteto-mode/SKILL.md`.

**Included playbooks (19):** `investigation`, `bug-fix`, `perf-issue`, `hillclimb`, `runtime-forensics`, `trace-forensics`, `feature`, `refactoring`, `prototype`, `visual-parity`, `pause-safely`, `multi-phase-plan`, `opening-a-pr`, `shipping`, `autonomous-run`, `babysit`, `autopilot-full`, `autopilot-stack`, `worktree-cleanup`.

**Included supporting skills (18):** `how`, `why`, `architect`, `blast-radius`, `arena`, `swarm`, `interrogate`, `no-comments`, `unslop`, `technical-writing`, `typescript-best-practices`, `benchmark-checklist`, `teach`, `bro`, `ketchup`, `figure-it-out`, `poteto-help`, `correct`.

Also include all 24 upstream `principle-*` skills and `agents/poteto-agent.md` plus `agents/comment-sicko.md`. Add core-owned `skills/setup`, `agents/playbook-runner.md`, and the `capability-registry` gateway; these are not pstack overlay pairs.

**Vendor-only exclusions:**

- `skills/setup-pstack`; skills `recall`, `reflect`, `automate-me`, `show-me-your-work`, `create-verification-skill`, `maintain-verification-skill`.
- Playbooks `orchestrate`, `session-pickup`, `eval`, `authoring-a-skill`.
- `skills/poteto-mode/scripts/` and `skills/poteto-mode/references/bugbot-triage.md`.
- Upstream `plugin.json`, `README.md`, `assets/`, and `scripts/`.
- ADR-0001 exclusions: `.cursor-plugin/`, `automations/benny/`, `skills/make-bot-ui/`, `docs/guide/`, and scripts hardcoding host paths.
- Packet-chain collisions, currently pstack `skills/tdd`.

### Rewrite requirements

Rewrite Cursor-specific worker, question, overnight, and UI behavior through host-agnostic interaction or the four host operations. Preserve Matt grilling as numbered questions and recommendations in plain chat; adapters must not replace it with structured question tools or fixed-choice pickers. Strip TypeScript guidance's `paths` auto-attach behavior. Do not move host-specific tools or paths into core.

Swarm and arena request workers from the coordinator session. Visual parity requests `ui-proof`. Overnight playbooks request the appropriate `overnight` mode. Worktree cleanup discovers this repository's registered git worktrees through git, without naming a host worktree directory.

Opening-a-PR invokes `unslop` before committing. Forge operations require `gh`; use `gt` when appropriate/present, including Graphite stacks, and Bugbot when present. Missing Bugbot skips that integration. Never use Origin. This does not introduce another capability.

All 24 principles apply to the playbook phase. Their nonblocking behavior must not suppress Matt HITL clarification. Playbooks retain inline cheap failing-test-first cadence, including bug-fix's exception when a test is impractical or expensive; they do not invoke Matt `tdd` to reconfirm seams. `implement` still invokes Matt `tdd`; `implement-spec` retains its per-packet TDD and integration review discipline. Reuse testing seams already confirmed for the packet; do not ask for the same confirmation again unless changed scope invalidates those seams. Playbook execution supplies the engineering workflow within that discipline, rather than a second implementation path.

## Router and packet execution

Follow [ADR-0002](adr/0002-hybrid-router-classification.md) and [ADR-0007](adr/0007-router-slash-name.md).

The canonical user token is `mstack`; `poteto-mode` is the only alias. Both classify identically. No `mainart` or `router` alias is added. The internal directory and skill-call name remain `poteto-mode`. Adapters expose `/mstack` on Grok and Claude and `$mstack` on Codex, own qualification such as `/mainart-stack:name`, and display the glossary's router description. Plugin identity is `mainart-stack`.

| Input or event | Required behavior |
| --- | --- |
| Explicit HITL skill or named playbook | Honor the user's classification; bypass unscoped router selection |
| Unscoped `ready-for-agent` packet | Treat as a settled what and select an eligible included playbook |
| Unscoped prompt with a data shape, repro, metric, or acceptance sufficient to build | Select an eligible included playbook even without a packet |
| Remaining unscoped request | Enter Matt HITL, normally `grill-with-docs`, with the appropriate chain on-ramp |
| `implement` or `implement-spec` pickup with unsettled outcome | Return to Matt HITL before execution |
| Product fork discovered during execution | Stop the affected playbook execution and clarify with Matt HITL |
| Empirical product question remains after grilling | Use Matt's `prototype` primitive |
| Empirical engineering choice within a settled what | Use pstack's Prototype playbook |
| Factual how/why-built question | Eligible for Investigation |
| “Should we” or product-meaning question | Matt HITL rather than Investigation |
| Product fork resolved | Reclassify using the updated outcome; do not blindly resume the prior todo list |

Use pstack's inherited matching rules only among the included playbooks; the factual-only Investigation rule is the deliberate match-rule patch. The optional `validation.judge` may advise whether the what is settled, whether a choice is a product fork, or which playbook fits. It cannot override explicit invocation, impose a confidence floor, or become a required gate.

`implement` and `implement-spec` wrap playbook selection and execution rather than supplying a parallel engineering workflow. `implement-spec` handles the packet task graph; `playbook-runner` is the matched-playbook worker prompt, while `poteto-agent` is the in-step code-writing delegate. On Grok the current coordinator session adopts `playbook-runner` in-process; fan-out uses the adapter's overnight/workflow binding rather than nested workers.

## Host adapter contract

[ADR-0004](adr/0004-host-adapter-interface.md) requires every adapter to supply shims under `hosts/<id>/skills/` named `spawn-worker`, `persist-model-roles`, `overnight`, and `ui-proof`. Core requests those names; adapter bodies own native APIs. The following are semantic interfaces, not a new executable API or chosen implementation framework.

| Operation | Request and behavior |
| --- | --- |
| `spawn-worker` | `{ role, prompt, isolation: isolated | same-tree, model_role? }`; omitted isolation means `same-tree`. Role set derives from `core/agents`; optional model role is `xhigh`, `max`, or `fast`. Honor requested isolation. |
| `persist-model-roles` | Persist the setup-selected host model ids for opaque roles `xhigh`, `max`, `fast` in the host's own configuration. Core does not freeze model names or configuration syntax. |
| `overnight` | Either `{ mode: "until", done }` with a completion condition, or `{ mode: "every", interval, prompt }` for recurring execution. Keep the modes distinct. |
| `ui-proof` | Return `{ ok, evidence_paths, error? }`. A required-proof step cannot complete when proof fails or evidence cannot be produced; other call sites skip on failure. |

### Grok binding

The existing [Grok adapter research](research/grok-host-adapter-surface.md) supplies the runtime surface; later ADR decisions take precedence over earlier alternatives.

- Grok uses a depth-one worker model. Adopt `playbook-runner` in-session; worker requests from that session may start `poteto-agent` and other core agents. Reject nested `spawn-worker`; do not rely on changing a depth setting.
- Native worker types use `mainart-stack:<agent>`. Map isolated execution to git worktrees. Map `model_role` to `[subagents.roles.<slug>].model` in Grok configuration. The shim owns native spawn APIs and configuration locations.
- `until` binds to the goal driver (`/goal`), respecting its eight-continuation cap and spanning turns as needed. It must not imply an unlimited continuation budget. `every` binds to the durable scheduler (`/loop`). Grok workflows, including `.rhai` packaging for fan-out, are adapter internals rather than a third core mode.
- The specified drivers do not resume after process death. A durable schedule is not a process-recovery guarantee.
- UI proof binds MCP and hooks. Do not assume a first-party browser tool. Required proof fails closed when that integration cannot produce evidence.
- Grok manifest and marketplace packaging belong under `hosts/grok/`; this packet creates no packaging files.

### Claude Code and Codex

Both must bind the same four operations, invocation policy, setup/model-role persistence, and project pin behavior. They may support nested workers, but core must not assume nesting. Their manifests, skill invocation syntax, native worker APIs, configuration files, overnight drivers, and UI proof integrations are adapter responsibilities. The [Claude Code and Codex research](research/claude-codex-adapter-interfaces.md) records the interface surfaces; full runtime internals and manifests remain outside this packet.

### Setup and invocation policy

Core `setup` selects `grok`, `claude`, or `codex`, persists `.mainart/host`, delegates model-role persistence, and initializes `.mainart/pins.yaml` from `hosts/<id>/pins.yaml` only when the project file is missing. Preserve existing project pins. Host selection is local and ignored by git; project pins are committed. On Grok ask for the three model ids using adapter defaults rather than freezing model names in core.

Setup provides a human checklist to disable/uninstall the separate Matt plugin and remove same-named packet-chain copies from user/project skill directories when bare names are desired. It does not inspect the host plugin list. A deliberate dual install may use host qualification.

HITL entry skills and the router require explicit user invocation, with implicit invocation disabled. Model-invoked chain primitives remain available internally. Setup may auto-invoke for first run. Shims and playbook-step skills are internal calls, not slash front doors. Adapters own invocation metadata; the final serialization policy for unresolved copied frontmatter keys remains deferred.

## Capability registry and Jev exemplar

Follow [ADR-0003](adr/0003-capability-registry.md). Scan `modules/*/module.yaml`; module `id` must match its directory. Invalid or id-mismatched packs are ignored. A declaration identifies capability and private entrypoint, for example:

```yaml
id: jev
provides:
  validation.judge:
    entrypoint: skills/validation-judge.md
```

The slot contract lives here rather than being duplicated in each declaration. Provider entrypoints are private files, not user-facing skills.

### Binding and invocation

Read top-level capability-to-module pins from `.mainart/pins.yaml`, then overlay `hosts.<current-host>` using `.mainart/host`. For example, a top-level `validation.judge: jev` may be replaced by `hosts.codex.validation.judge`. This is configuration, not a host-operation shim. The registry does not read native host configuration files.

An effective pin selects an installed, valid module declaring the capability. A dangling or otherwise invalid selection is unbound, even if another provider exists. Without an effective pin, exactly one declarer auto-binds; zero or competing declarers are unbound. Empty or missing pin configuration therefore supports unique auto-binding. At most one provider is live per capability per host/session.

Call sites request only capability and payload:

```text
capability-registry({ capability: "validation.judge", input: { state, questions } })
  → { unbound: true }
  | { answers, usage?, provider_model? }
  | { error: { code: "auth" | "unavailable" | "invalid" } }
```

Bind before calling. Missing or invalid credentials produce `auth` for a bound provider, not unbound. Network failure, timeout, or temporary service/rate-limit failures produce `unavailable`; bad payloads produce `invalid`. Every call site continues through its no-advice behavior for unbound or unhandled typed errors. Calls must not hang; timeout and retry policy belong to the provider implementation, with no global numeric timeout chosen here.

### `validation.judge` contract

Input is `state` (text, object, or array of text) and a named `questions` map. Each question has `kind: yes_no | choice | score` and string `instructions`. The `criteria` field defines the outcomes as follows; no separate options field is used:

| Kind | Request criteria |
| --- | --- |
| `yes_no` | Optional map with string keys `true` and `false` and string descriptions of yes and no |
| `choice` | Required nonempty map of choice name → string description; its keys are the allowed outcomes |
| `score` | Required nonempty ordered list of string level descriptions; list positions define consecutive integer levels starting at zero |

Answers correspond to question ids:

| Kind | Answer |
| --- | --- |
| `yes_no` | `{ kind: "yes_no", p_yes }`, probability in 0..1 |
| `choice` | `{ kind: "choice", winner, probabilities, confidence }`, distribution over supplied choices |
| `score` | `{ kind: "score", value, legend, probabilities, confidence }`, distribution over defined levels and a probability-weighted value |

Validate provider answers before returning success: answer ids must match request question ids, kinds must match, and all required answer fields must have the declared types. Probabilities and confidence must be finite numbers in 0..1. Choice winners must be declared outcomes; choice probability maps must cover exactly the declared choices. Score legends must map the stringified zero-based level indices to the requested descriptions, and score probability maps must cover exactly those indices. Score values must be finite and equal the probability-weighted level value. Choice/score probabilities sum to one, allowing ordinary floating-point rounding. Missing fields, mismatched outcomes, or malformed provider answers return typed `invalid`; call sites skip that advice. Invalid request shapes also return `invalid` for a bound provider. Confidence describes distribution concentration, not permission to proceed. Optional `usage` reports input/output token counts when available. Optional `provider_model` is opaque logging information; playbooks must not branch on it. The capability returns typed judgments, not a free-text rationale.

`modules/jev/` is the first exemplar, not a hardcoded branch. Carry forward [the recorded Jev contract](research/jev-validation-judge.md): its module maps generic `yes_no` to provider-native `noul`, translates the returned value to `p_yes`, and translates provider `choice` to `winner`. It owns the hosted `POST https://api.typesafe.ai/v1/systemone` integration, Bearer credentials from `TYPESAFE_API_KEY`, base URL, model selection, retries, and deadlines. Core call sites never name those vendor details. This is a frozen research contract for this packet; no paid calls or new live API research are required.

## Future implementation acceptance requirements

The user confirmed one primary end-to-end acceptance seam: the router / packet-to-playbook boundary with controlled host-operation shims and capability providers. Adapter contract checks and static policy checks support that seam. There is no existing test prior art. Do not infer a framework, production test API, or executable test suite from these requirements.

Observe the selected workflow, honored explicit invocation, stopping for clarification, provider fallback, adapter requests, and proof outcomes. Do not assert internal prompt wording, helper structure, private reasoning, or an exact reasoning transcript. Use deterministic providers and controlled adapters rather than paid APIs. A live Grok evaluation is not a completion requirement for this documentation packet.

### Primary acceptance scenarios

| ID | Controlled scenario | Observable acceptance |
| --- | --- | --- |
| R1 | Unscoped request without a settled outcome | Matt HITL selected; engineering execution waits for clarification |
| R2 | Settled prompt with acceptance/repro but no packet | Eligible included playbook selected without requiring tracker creation |
| R3 | Pickup of a `ready-for-agent` packet through router or implement wrapper | Settled outcome reaches an eligible playbook |
| R4 | Pickup whose outcome remains unsettled | Matt HITL selected before execution |
| R5 | Explicit HITL invocation with a settled prompt; explicit named playbook invocation | Each explicit entry preserved, including when judge advice disagrees |
| R6 | Factual how/why-built request versus a should-we question | Investigation eligible for the factual case; product question enters HITL |
| R7 | Playbook encounters a product fork | Affected execution stops for clarification; empirical product remainder uses Matt prototype |
| R8 | Empirical engineering question within settled scope | pstack Prototype playbook used without inventing product meaning |
| R9 | Clarification changes the intended outcome | Fresh classification follows updated outcome rather than resuming stale steps |
| R10 | Identical requests through `mstack` and `poteto-mode` | Same classification and workflow |
| R11 | Grok implement-spec execution/fan-out | In-session playbook-runner and overnight/workflow requests, without nested worker requests |

### Registry scenarios through the primary seam

| ID | Provider/configuration fixture | Observable acceptance |
| --- | --- | --- |
| C1 | No declarer, or invalid/id-mismatched packs only | Unbound advice skipped; workflow remains available |
| C2 | One valid declarer, missing/empty pins | Unique provider invoked through capability name |
| C3 | Multiple declarers without a pin | Unbound; no arbitrary provider selected; workflow continues |
| C4 | Competing declarers with a valid project pin | Only selected provider invoked |
| C5 | Project pin overridden for current host | Host-specific selection wins; another host uses its own effective selection |
| C6 | Pin names missing pack or pack not declaring the capability | Unbound; no silent fallback to another provider |
| C7 | Bound provider lacks or rejects credentials | Typed `auth`; remains a bound failed call; optional advice skipped |
| C8 | Provider returns unavailable/timeout or invalid payload error | Corresponding typed error; unhandled advice skipped; call terminates |
| C9 | Deterministic yes_no, choice, and score answers | Typed answers/probabilities preserved; opaque model identity does not change routing |
| C10 | Missing, failing, or disagreeing judge with explicit invocation | Explicit selection preserved; judge never becomes a required gate |
| C11 | Requests using optional yes/no descriptions, named choice criteria, and ordered score criteria | Providers receive the agreed shapes; answers retain the same ids, outcomes, and score levels |
| C12 | Malformed requests or provider answers, including missing fields, mismatched ids/kinds, undeclared outcomes, or invalid probabilities | Typed `invalid` for a bound provider; malformed advice is skipped and workflow continues |

### Adapter contract checks

- Omitted spawn isolation means `same-tree`; explicit `isolated` requests obtain isolation. Roles come from core agents, and model-role requests preserve `xhigh`, `max`, or `fast` without embedding host model ids in core.
- Setup persists local host selection and delegates all three model mappings. Missing project pins initialize from host defaults; existing pins survive setup.
- `until` carries its completion condition to the appropriate driver; `every` carries interval and prompt to the recurring driver. Grok bindings respect the continuation cap and expose no process-death recovery guarantee.
- UI proof success returns usable evidence paths. Error, unsuccessful result, or inability to produce required evidence prevents required-proof completion; optional call sites skip.
- Grok adopts playbook-runner in-session, permits coordinator worker requests, maps isolated work to worktrees, and rejects nested spawn. Fan-out uses the specified overnight/workflow mechanism.
- Claude Code and Codex implementations will satisfy the shared contracts without requiring Grok-native tools or paths.

### Static policy checks

Future checks must verify pristine vendor content against recorded provenance; same-relative-path core copies; computed membership and collision exclusion; exact first-extract inclusions with vendor-only exclusions absent from core; both MIT notices and recorded versions/revisions; canonical naming with only the agreed alias; and invocation policy, including preservation of plain-chat grilling and the distinction between packet-level Matt TDD and inline playbook testing.

Inspect core procedure bodies for native host APIs, configuration locations, model ids, invocation metadata, provider names/credentials at call sites, and Cursor auto-attach leakage. Check that worktree cleanup uses registered git worktrees, forge steps follow the agreed integrations, and playbook-phase principles cannot suppress HITL. These are policy checks on shipped content, not assertions that this specification cannot discuss adapter details.

## Deferred work and scope limits

This packet delivers documentation only: no upstream import, port script, host manifest, installable plugin, module implementation, product runtime, or executable tests. It does not close the parent map or mark the future product implemented.

Keep these follow-ups visible without deciding them here:

- Marketplace and installation packaging under `hosts/`.
- Grok comparative bug-fix evaluation with the same prompt and proof.
- Later Orchestrate extract, subject to a host-agnostic rewrite without Cursor Projects/cloud/control APIs.
- Transcript-shaped skills and playbooks pending a transcript host operation.
- Host-agnostic skill-authoring rewrite before extracting authoring-a-skill and related verification authoring flows.
- Final serialization/policy for copied frontmatter keys, including `disable-model-invocation`; required invocation behavior is settled, representation is not.
- Modules beyond the Jev exemplar and capabilities beyond `validation.judge`.
- Full Claude Code and Codex adapter internals.

Passing upstream pstack through unchanged, merging grilling and shipping into one mega-skill, letting nonblocking playbook principles suppress product clarification, and unsupported process-recovery guarantees are outside the agreed design.

## Decision traceability and documentation validation

| Settled source | Specification coverage |
| --- | --- |
| [Parent map](https://github.com/DavillyDevTeam/mainart-stack/issues/1) and [consolidated packet](https://github.com/DavillyDevTeam/mainart-stack/issues/15) | Destination, upstream snapshots, all scope limits, confirmed seams, deferred work |
| [ADR-0001](adr/0001-pristine-vendor-tree-core-copies.md) | Pristine vendor tree, relative paths, computed copy set, licenses and exclusions |
| [ADR-0002](adr/0002-hybrid-router-classification.md) | Hybrid gate, explicit invocation, product forks, Investigation, packet execution |
| [ADR-0003](adr/0003-capability-registry.md) | Declarations, binding, typed gateway, advisory judge, Jev exemplar |
| [ADR-0004](adr/0004-host-adapter-interface.md) | Four shims, setup, pins, Grok flat execution, overnight, invocation ownership |
| [ADR-0005](adr/0005-packet-chain-names-occupy-core.md) | Collision precedence, inline playbook testing, separate Matt install checklist |
| [ADR-0006](adr/0006-first-extract-pstack-core-copies.md) | Exact included/deferred inventory and rewrite rules |
| [ADR-0007](adr/0007-router-slash-name.md) | mstack canonical token, sole poteto-mode alias, preserved internal directory |

Validate this documentation against the glossary, all seven ADRs, the packet, and parent map. Confirm inventories and exclusions are complete, relative links resolve, settled decisions are traceable without contradiction, and unknowns remain explicitly deferred. No glossary or ADR change is needed unless consolidation reveals an actual inconsistency.
