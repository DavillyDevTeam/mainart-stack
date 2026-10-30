---
name: spawn-worker
description: Grok host-adapter shim for spawn-worker. Adopts playbook-runner in this session and rejects nested workers.
---

# spawn-worker

Core asks for this host operation by directory name. Native calls stay in this adapter.

Request:

- role: a name from core/agents
- prompt: the worker brief
- isolation: isolated or same-tree. Omitted isolation means same-tree. When this shim runs on Grok, isolated maps to a git worktree.
- model_role: optional xhigh, max, or fast. When this shim runs on Grok, map that opaque role onto the host model id in host configuration. The checked-in coordinator records the requested role and does not write that configuration.

Grok rules for this path:

- Adopt playbook-runner in the coordinator session. The native spawn call is spawn_subagent, and this role is not a spawn_subagent request.
- A delegate requested from the coordinator, such as poteto-agent or comment-sicko, uses spawn_subagent with subagent type mainart-stack:<agent>.
- Reject nested spawn-worker. A worker cannot call this shim.
- Bug-fix does not require a nested worker. Routing and adopting playbook-runner happen in this session.
- Do not copy spawn_subagent, host model ids, or host configuration paths into core.
