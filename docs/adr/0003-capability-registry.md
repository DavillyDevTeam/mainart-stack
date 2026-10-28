# Capability registry gateway

Optional **modules** live at `modules/` beside **core** and **host adapter** trees. Each pack declares **capabilities** in `module.yaml`. A scan plus unique-declarer auto-bind (else a per-host **pin**) selects at most one **provider**. Router and playbooks call the core `capability-registry` skill with a capability name and payload. Unbound is a skip; a failed provider call is a typed error. `validation.judge` is typed decision plus probability (`yes_no` | `choice` | `score`); Jev is the first provider and is never named at the call site.

## Considered Options

- **Tree location: `modules/` vs `core/modules/` vs `hosts/<host>/modules/` (chosen: `modules/`).** Optional packs stay out of always-on core. Jev is host-agnostic.
- **One provider vs many with a pin (chosen: many, pin in host-adapter config, unique auto-bind).** A single declarer is live with no pin. Pins may differ per host. Serialization of the pin map is a host-adapter port.
- **Committed catalog vs host skill presence vs computed scan (chosen: scan `modules/*/module.yaml`).** Same computed-set idea as the vendor-tree allowlist.
- **`modules/registry.yaml` vs host config for the pin (chosen: host config).** Bind is per session/host. The map is capability name → module id.
- **Lookup-only vs per-capability core facade vs gateway (chosen: gateway).** One core skill binds and invokes. Provider entrypoints are private implementation files.
- **Fail closed / HITL install vs degrade (chosen: degrade at every call site).** Matches ADR-0002: `validation.judge` is never required. A dangling or ambiguous pin is unbound.
- **Free-text vs thin verdict vs three typed kinds (chosen: `yes_no` | `choice` | `score` plus probabilities).** The Jev module maps `yes_no` → noul. Playbooks never write noul, `jev-*`, or `TYPESAFE_API_KEY`.

## Consequences

- The host-adapter ticket includes a pin-map port. File and key format live there.
- A missing or invalid API key is `error.auth` (provider bound, call failed), not unbound.
- Unhandled typed error (`auth` | `unavailable` | `invalid`) is skip, same as unbound. The gateway must not hang.
- First pack: `modules/jev/` provides `validation.judge`.
