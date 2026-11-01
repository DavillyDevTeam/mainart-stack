# Packet-chain import

Issue #23 vendors the fifteen Matt packet-chain skills into `core/skills/`
from `mattpocock/skills@b645f47de3e17ed3bf60586c9bebb8092e0f79fd`.
The machine-readable record is [matt-packet-chain-provenance.json](../vendor/matt-packet-chain-provenance.json).
Each `tree` value is the skill-directory Git tree ID and matches the
`skillFolderHash` inventory from the 2026-10-07 installation lock.
Do not substitute the `v1.3.1` tag; that tag differs for `to-tickets`,
`implement`, and `setup-matt-pocock-skills`.

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

The checker reconstructs each skill-directory Git tree from copied blobs plus
recorded omitted adapter blobs, and compares that tree ID with the
skillFolderHash inventory. It also rejects extra files, adapter metadata, and
unselected skills in core, and checks that Grok HITL entries require explicit
`/mainart-stack:<name>` invocation with `disable-model-invocation` while
primitives stay internally available. Grilling remains numbered questions and
recommendations in plain chat.
