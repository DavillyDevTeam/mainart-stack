# Pristine pstack vendor tree

The current pin is pstack 0.15.36 at `cursor/plugins@ae5650fe`, including its full LICENSE, without rewrites.
The machine-readable record is [pstack-provenance.json](../vendor/pstack-provenance.json).
The vendor tree is a maintenance source; shipped core copies are separate (ADR-0001).
Do not run upstream skills or scripts as part of the provenance check.

The first import (issue #22) took 0.15.20 at `1b6d44ff`. The 0.15.36 snapshot is a squash subtree pull of a prefix tree that is content-identical to `ae5650fe:pstack`.

## Reproduce the snapshot

Requires Git with `git subtree` installed. The original import used Git 2.56.0
and its official `contrib/subtree/git-subtree.sh` script.
Use a temporary checkout of the original upstream, not a separate mirror repository:

```sh
git clone --filter=blob:none --sparse https://github.com/cursor/plugins.git /tmp/pstack-upstream
git -C /tmp/pstack-upstream sparse-checkout set pstack
git -C /tmp/pstack-upstream checkout ae5650febf4320793844c12c4adaa937f417f8da
TREE=$(git -C /tmp/pstack-upstream rev-parse ae5650febf4320793844c12c4adaa937f417f8da:pstack)
# Tree: 4719e1c4b4c43bac85d4206a8b41dd2899769c1c
SPLIT=$(git -C /tmp/pstack-upstream commit-tree "$TREE" -m "pstack 0.15.36 from ae5650febf4320793844c12c4adaa937f417f8da")
# Split commit recorded here: bd105d05e448baf37841e3978dd8f4c88dd95626
```

A `git subtree split --prefix=pstack` of the same revision yields the same tree ID. The recorded split used `commit-tree` of that prefix tree.

The first import used `git subtree add` of the 0.15.20 split
(`24329adf5b1f1a1fe6cadac75553b9cb8809d991`) onto
`4e545adb8b6671e25889e4bf92436c3e14d6340e`. This pin used:

```sh
git subtree pull --prefix=vendor/pstack /tmp/pstack-upstream bd105d05e448baf37841e3978dd8f4c88dd95626 --squash
```

The generated squash parent records `git-subtree-dir` and `git-subtree-split`.
Only the `pstack/` prefix enters this repository. There is no submodule and no
whole-monorepo import. The full split history need not remain in the local object
database: reproduce it from the pinned upstream revision when needed.

## Verify locally

```sh
python3 scripts/check_vendor.py
```

This offline, standard-library-only check reconstructs the Git tree ID from the
working files, independently of the index and local Git objects. It detects
modified, added (including ignored/untracked), deleted, renamed, or executable-bit
changed files and symlink target changes. Empty directories are also rejected;
Git does not normally preserve them. Non-executable permission bits and timestamps
are not Git content. Run the command from any working directory with Python 3.10+.
The CI workflow runs the same check on pushes and pull requests.

The provenance record is the trust anchor: review any change to it against the
pinned research and upstream before accepting a new snapshot. Changing both the
record and the vendor tree intentionally constitutes a new import, not proof of
the old snapshot.

## Later updates

For an authorized update, take the prefix tree at the approved full upstream
revision (`git rev-parse <rev>:pstack`), record a split commit of that tree,
then `git subtree pull --prefix=vendor/pstack /tmp/pstack-upstream <new-split> --squash`.
Record the new original revision, split, tree, and version outside `vendor/pstack/`.
Keep that tree pristine. Port rewritten core copies separately using the previous
upstream file, new upstream file, and rewritten file; apply the computed membership
and packet-chain collision exclusions from ADR-0001 and ADR-0005. New vendor-only
skills stay out of core until copied and rewritten. Do not merge pstack `tdd`
onto Matt's occupying copy.
