---
name: persist-model-roles
description: Persist setup-selected host model ids for the opaque roles xhigh, max, and fast in Grok configuration.
---

# persist-model-roles

Core asks for this host operation by directory name. Native configuration stays in this adapter.

Request: model ids for `xhigh`, `max`, and `fast`. When setup omits ids, use this adapter's defaults (`grok-4.7` for each role), the same map as `hosts/grok/persist_model_roles.py`.

Write `[subagents.roles.<role>].model` in the Grok user config (`~/.grok/config.toml`). Keep unrelated tables. Do not copy those paths or model ids into core.
