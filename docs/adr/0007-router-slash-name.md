# Router slash name is mstack; poteto-mode is an alias

The **router** lives at `skills/poteto-mode/` (ADR-0006) and core Skill-tools that directory name (ADR-0004). The user-facing token is `mstack` (`/mstack` on Grok and Claude, `$mstack` on Codex). `poteto-mode` is the only alias. Adapters expose both; they classify the same.

## Considered Options

- **Canonical token: `mstack` vs `mainart` vs `poteto-mode` (chosen: `mstack`).** Canonical `poteto-mode` would brand the front door with the upstream name. `mainart` is longer. `mstack` sits next to the product name **mainart-stack** and leaves `/mainart-stack:` for plugin qualification (ADR-0005).
- **Alias: keep `poteto-mode` vs canonical-only (chosen: alias).** pstack muscle memory still works. Disk path stays `poteto-mode`.
- **Further aliases (`mainart`, `router`) (chosen: none).** One extra name is enough.

## Consequences

- Slash menus list `mstack` and `poteto-mode`. The skill description is the glossary **router** one-liner.
- Core path and Skill-tool name stay `poteto-mode`. Adapters own `/` vs `$` vs `@` (ADR-0004).
- Plugin qualification remains `/mainart-stack:name`.
