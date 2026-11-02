"""Compare vendor/pstack and core skill dirs with Git tree IDs recorded in provenance."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git_output(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def git_tree(path: str) -> str:
    return git_output("rev-parse", f"HEAD:{path}")


def git_files(path: str) -> set[str]:
    listing = git_output("ls-tree", "-r", "--name-only", f"HEAD:{path}")
    return {line for line in listing.splitlines() if line}


def main() -> int:
    try:
        provenance = json.loads((ROOT / "vendor/pstack-provenance.json").read_text())
        expected = provenance["tree"]
        actual = git_tree("vendor/pstack")
        if actual != expected:
            print(f"Vendor mismatch: expected {expected}, got {actual}", file=sys.stderr)
            return 1
        print(f"Pristine pstack {provenance['version']}: {actual}")
        return 0
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f"Vendor check failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
