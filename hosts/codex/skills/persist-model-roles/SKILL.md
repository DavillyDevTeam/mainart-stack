---
name: persist-model-roles
description: Persist setup-selected host model ids for the opaque roles xhigh, max, and fast in Codex configuration.
---

# persist-model-roles

This shim is Skill-tooled by setup, not a slash front door. Core asks for this host operation by directory name. Native configuration stays in this adapter.

Request: model ids for `xhigh`, `max`, and `fast`. When setup omits ids, use this adapter's defaults.

Write those three roles in Codex's own model configuration. Keep the request shape identical to other hosts.
