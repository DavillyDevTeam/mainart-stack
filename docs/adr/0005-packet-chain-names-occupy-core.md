# Packet-chain names occupy core; this plugin replaces a Matt install

A pstack skill whose path is already a **packet chain** skill in **core** is dropped: core keeps Matt's copy, the vendor tree keeps pstack's, and overlay never treats that path as a pstack core copy. Unique pstack skills keep their upstream directory names. The shipped plugin *is* the packet chain plus playbooks; a separate Matt install is leftover.

## Considered Options

- **Colliding copies: drop vs rename vs merge vs prefix every pstack path (chosen: drop).** Rename would fork a file out of the same-path overlay. Merge mixes HITL seam confirmation with skip-if-impractical. A product prefix on every pstack path would gut ADR-0001.
- **Playbook × `tdd`: inline vs Skill-tool Matt `tdd` vs rewrite `tdd` (chosen: inline).** pstack's `tdd` is user-invoked, so playbooks never Skill-tooled it. Matt's `tdd` asks the human to confirm seams; calling it from a playbook would grill during specified engineering. Bug-fix keeps skip-when-expensive and the cheap failing-test-first cadence in its own step. `implement` still Skill-tools `tdd`.
- **User Matt install: replacement vs dual-install happy path vs companion (chosen: replacement).** Core copies will be rewritten; two live `tdd`s would be different skills with the same name. Companion (do not vendor Matt) reverses the map's vendoring note. Hosts already qualify leftover collisions (`/mainart-stack:tdd`).

## Consequences

- Occupancy is the packet-chain skill directories in `core/skills/`. Today the only overlap with pstack is `skills/tdd`. The same drop applies to any later overlap (for example if `teach` enters the chain).
- Amend ADR-0001: a pstack core copy is `core/X` where `vendor/pstack/X` exists **and** `X` is not a packet-chain path. Overlay must not three-way-merge pstack `tdd` into Matt's file.
- [Choose which pstack paths enter core](https://github.com/DavillyDevTeam/mainart-stack/issues/13) never copies a Matt-occupied path.
- Core `setup` includes a human checklist: disable or uninstall the Matt plugin, and remove same-named packet-chain copies from user/project skill dirs if the user wants bare `/tdd` and `/wayfinder`. `setup` does not inspect the host plugin list. Dual-install remains an escape hatch via host qualification.
- Directory names stay unprefixed. Slash spelling is still adapter-owned (ADR-0004).
