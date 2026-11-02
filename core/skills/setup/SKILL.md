---
name: setup
description: Configure the local mainart-stack host, model roles, and project pins on first run or when the user asks to set up Grok, Claude, or Codex.
---

# Setup

Configure this repository's local host, opaque model roles, and optional capability pins. First-run sessions may start here. Later adapters share the same host ids and pin files.

## Steps

### 1. Select the host

Ask which host this machine uses. The ids are `grok`, `claude`, and `codex`.

Completion: `.mainart/host` contains exactly one of those ids, and `.gitignore` lists `.mainart/host`. Project pins stay eligible to commit.

### 2. Persist model roles

Ask for host model ids for the opaque roles `xhigh`, `max`, and `fast`. Offer the selected adapter's defaults. Skill-tool `persist-model-roles` with those three mappings. Core keeps role names only.

Completion: the adapter has stored all three mappings in its own configuration.

### 3. Initialize project pins

If `.mainart/pins.yaml` is missing, copy `hosts/<id>/pins.yaml` from the selected host. If the project file already exists, including an empty file, leave it unchanged.

Completion: the project either gained host defaults or kept its existing pins.

### 4. Present the Matt dual-install checklist

Tell the human, as a checklist they run:

1. Disable or uninstall a separate Matt plugin when this plugin should replace it.
2. Remove same-named packet-chain copies from user and project skill directories when they want bare `/tdd` and `/wayfinder`.
3. Keep a deliberate dual install through host qualification such as `/mainart-stack:tdd`.

Leave the host plugin list unread. Dual install stays an escape hatch.

Completion: the human has the checklist. Setup does not inspect plugins.
