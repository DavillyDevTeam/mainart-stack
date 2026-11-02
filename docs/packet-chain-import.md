# Packet-chain import

Issue #23 vendors the fifteen Matt packet-chain skills into `core/skills/`
from `mattpocock/skills@d1478fcb140db0b93c0c8df17bcfd311844749d0` (`v1.3.2`).
The machine-readable record is [matt-packet-chain-provenance.json](../vendor/matt-packet-chain-provenance.json).
Each `tree` value is `git rev-parse HEAD:core/skills/<name>` at this pin.
Codex `agents/openai.yaml` is omitted, so these trees differ from the
upstream skill directories at the same tag. Do not substitute a newer
`main` commit; `v1.3.2` is the latest stable release.

Copied procedure files keep Matt's bodies, including companions and tracker
templates under `setup-matt-pocock-skills/`. Tracker mechanics stay in those
templates for consumer repositories. Codex `agents/openai.yaml` files stay out
of core; Grok invocation metadata lives in [hosts/grok/invocation.json](../hosts/grok/invocation.json).
Copied frontmatter is left as upstream wrote it. This import does not choose a
universal serialization policy for those keys.

Matt `tdd` occupies `core/skills/tdd`. pstack's copy remains only in
`vendor/pstack/skills/tdd`. `ask-matt` and other unselected Matt skills are
not imported. Optional `tdd` consultation of `codebase-design` does not bundle
that skill.

## Verify locally

```sh
python3 scripts/check_packet_chain.py
python3 -m unittest discover -s tests -v
```

The checker compares each skill directory to `git rev-parse HEAD:core/skills/<name>`
and `git ls-tree` of that path. It also rejects extra files, adapter metadata, and
unselected skills in core, and checks that Grok HITL entries require explicit
`/mainart-stack:<name>` invocation with `disable-model-invocation` while
primitives stay internally available. Grilling remains numbered questions and
recommendations in plain chat.
