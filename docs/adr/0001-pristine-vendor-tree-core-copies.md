# Pristine vendor tree, rewritten copies in core

mainart-stack takes pstack as a git subtree and must strip Cursor APIs from anything that ships in core, without making upstream pulls impossible. Keep a pristine **vendor tree** at `vendor/pstack/` and put rewritten copies in **core** at the same relative path. Pulls squash into the vendor tree, then three-way-merge each pstack core copy: `core/X` where `vendor/pstack/X` exists and `X` is not a Matt packet-chain path (ADR-0005).

## Considered Options

- **In-place commits** on the subtree: squash-pull merges our rewrites with upstream on every playbook. A conflict farm, and the prefix cannot be `core/` because Matt is vendored there.
- **Quilt** (`patches/*.diff`): wrong granularity for replacing `Task` / `AskQuestion` / `~/.cursor/**` across 23 playbooks and 52 skills.
- **Shadow overlay** (union-mount): new upstream files with Cursor APIs appear in the product until someone overlays them.
- **Pristine vendor tree + allowlisted core copies** (chosen).

## Consequences

- Subtree prefix is `vendor/pstack/`, not `core/` and not a root `pstack/`.
- The allowlist is computed: a pstack core copy is `core/X` where `vendor/pstack/X` exists **and** `X` is not a Matt packet-chain path. No `ALLOWLIST` file. Today the occupancy exclusion is `skills/tdd`. See ADR-0005.
- Do not copy a pstack file onto a path Matt already occupies. Drop that pstack copy (ADR-0005); do not 3-way-merge it into the Matt file.
- Never copy `.cursor-plugin/`, `automations/benny/`, `skills/make-bot-ui/`, `docs/guide/`, or scripts that hardcode `~/.cursor/`.
- `vendor/pstack/LICENSE` stays with the subtree; core ships the Lauren Tan MIT notice with the copies.
- This map names the recipe. It does not run the subtree or write a port script.
