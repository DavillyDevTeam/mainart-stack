---
name: persist-model-roles
description: Persist setup-selected host model ids for the opaque roles xhigh, max, and fast in Grok configuration.
---

# persist-model-roles

This shim is Skill-tooled by setup, not a slash front door. Core asks for the host operation by directory name. Native configuration stays in this adapter.

Request: model ids for `xhigh`, `max`, and `fast`. When setup omits ids, use this adapter's defaults (`grok-4.7` for each role).

The write implementation is `hosts/grok/persist_model_roles.py`. It updates `[subagents.roles.<role>].model` in the Grok user config (`~/.grok/config.toml` by default; tests may pass another path), keeps unrelated tables and comments, and validates the result as TOML. Do not copy those paths or model ids into core.
