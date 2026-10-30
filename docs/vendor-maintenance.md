# Pristine pstack vendor tree

Issue #22 imports pstack 0.15.20, including its full LICENSE, without rewrites.
The machine-readable record is [pstack-provenance.json](../vendor/pstack-provenance.json).
The vendor tree is a maintenance source; shipped core copies are separate (ADR-0001).
Do not run upstream skills or scripts as part of the provenance check.

## Reproduce the snapshot

Requires Git with `git subtree` installed. The original import used Git 2.56.0
and its official `contrib/subtree/git-subtree.sh` script.
Use a temporary checkout of the original upstream, not a separate mirror repository:

```sh
git clone --no-checkout https://github.com/cursor/plugins.git /tmp/pstack-upstream
git -C /tmp/pstack-upstream subtree split --prefix=pstack 1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def
# Split commit: 24329adf5b1f1a1fe6cadac75553b9cb8809d991
git -C /tmp/pstack-upstream rev-parse 1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def:pstack
git -C /tmp/pstack-upstream rev-parse 24329adf5b1f1a1fe6cadac75553b9cb8809d991^{tree}
# Both trees: 1dbec20ada6e40cb12774b8893960a558319fd6b
```

On the pre-import mainart-stack commit (`4e545adb8b6671e25889e4bf92436c3e14d6340e`),
the import command is:

```sh
git subtree add --prefix=vendor/pstack /tmp/pstack-upstream 24329adf5b1f1a1fe6cadac75553b9cb8809d991 --squash
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

Do not update to a newer upstream for this ticket. For an authorized update,
repeat the prefix split at the approved full upstream revision, then use
`git subtree pull --prefix=vendor/pstack /tmp/pstack-upstream <new-split> --squash`.
Record the new original revision, split, tree, and version outside `vendor/pstack/`.
Keep that tree pristine. Port rewritten core copies separately using the previous
upstream file, new upstream file, and rewritten file; apply the computed membership
and packet-chain collision exclusions from ADR-0001 and ADR-0005.
