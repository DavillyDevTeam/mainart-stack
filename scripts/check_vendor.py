"""Compare the complete working vendor tree with its pinned Git tree object ID."""

import hashlib
import json
import os
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def object_id(kind: str, content: bytes) -> bytes:
    header = f"{kind} {len(content)}\0".encode()
    return hashlib.sha1(header + content, usedforsecurity=False).digest()


def tree_id(directory: Path) -> bytes:
    entries: list[tuple[bytes, bytes]] = []
    for path in directory.iterdir():
        mode = path.lstat().st_mode
        name = os.fsencode(path.name)
        if stat.S_ISLNK(mode):
            git_mode = b"120000"
            digest = object_id("blob", os.fsencode(os.readlink(path)))
        elif stat.S_ISDIR(mode):
            git_mode = b"40000"
            digest = tree_id(path)
        elif stat.S_ISREG(mode):
            git_mode = b"100755" if mode & stat.S_IXUSR else b"100644"
            digest = object_id("blob", path.read_bytes())
        else:
            raise ValueError(f"Unsupported vendor entry: {path}")
        sort_name = name + (b"/" if git_mode == b"40000" else b"")
        entries.append((sort_name, git_mode + b" " + name + b"\0" + digest))
    return object_id("tree", b"".join(entry for _, entry in sorted(entries)))


def main() -> int:
    try:
        provenance = json.loads((ROOT / "vendor/pstack-provenance.json").read_text())
        expected = provenance["tree"]
        actual = tree_id(ROOT / "vendor/pstack").hex()
        if actual != expected:
            print(f"Vendor mismatch: expected {expected}, got {actual}", file=sys.stderr)
            return 1
        print(f"Pristine pstack {provenance['version']}: {actual}")
        return 0
    except (OSError, ValueError, KeyError) as error:
        print(f"Vendor check failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
