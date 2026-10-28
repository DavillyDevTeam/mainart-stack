# Hybrid router at the packet/playbook boundary

mainart-stack's **router** is the unscoped front door onto Matt HITL or a pstack **playbook**. Classify with a hybrid gate: a `ready-for-agent` **packet** or a **settled what** prompt goes to a playbook (pstack's match among playbooks that exist in core); otherwise Matt (`grill-with-docs`, `wayfinder`, `triage`, `to-spec` / `to-tickets`). Explicit HITL skills and named playbooks are the user's classification. `validation.judge` may advise that gate as an optional prior and must never be required.

## Considered Options

- **Tracker-only vs prompt-only vs hybrid (chosen).** Tracker-only misses a well-specified chat with no packet. Prompt-only misses "do that packet". Hybrid takes both.
- **Reclassify explicit invocations vs honor them (chosen).** The router is the unscoped entry; a typed skill is already a classification.
- **Binding `validation.judge` vs advisory (chosen).** A confidence floor would make a missing module a behavior change.
- **`/implement` unused vs dual path vs packet runner wrapping playbooks (chosen).** Specified execution is playbooks; `/implement` / `/implement-spec` pick up packets and match. Unsettled pickup bounces to Matt HITL.
- **implement-spec workers as poteto-agent vs playbook runners (chosen).** pstack's split stands: the worker runs the playbook; `poteto-agent` is the in-step delegate. Host `subagent_type` binds in the host-adapter ticket.

## Consequences

- A **product fork** leaves the playbook: grill as necessary, then Matt `prototype` when the remainder is empirical. Empirical **engineering choice** uses pstack's Prototype playbook. After bounce, reclassify; do not blindly resume the old todo list.
- Investigation is factual how/why-built. "Should we" is Matt HITL. That is the only match-rule patch; the rest of pstack's table is inherited until which playbooks enter core is decided.
- The router and playbooks call `validation.judge`, never Jev. Closed questions: settled-what vs not, product-fork vs engineering, which playbook.
