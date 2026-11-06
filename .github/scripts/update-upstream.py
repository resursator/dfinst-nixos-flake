#!/usr/bin/env python3
"""Update dfint-installer version and source hash."""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FLAKE = ROOT / "flake.nix"

FAKE_HASH = "sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="

VERSION_RE = re.compile(
    r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?"
)

VERSION_PATTERN = re.compile(
    r'^([ \t]*version = ")[^"]+";[ \t]*$',
    re.MULTILINE,
)

SOURCE_HASH_PATTERN = re.compile(
    r'^([ \t]*hash = ")[^"]*(";\s*)$',
    re.MULTILINE,
)


def replace_one(content, pattern, replacement, description):
    updated, count = pattern.subn(
        replacement,
        content,
        count=1,
    )

    if count != 1:
        raise RuntimeError(
            f"Expected exactly one {description}, found {count}"
        )

    return updated


def write_source_hash(value):
    content = FLAKE.read_text()

    def replacement(match):
        return f"{match.group(1)}{value}{match.group(2)}"

    content, count = SOURCE_HASH_PATTERN.subn(
        replacement,
        content,
        count=1,
    )

    if count != 1:
        raise RuntimeError("Expected exactly one source hash")

    FLAKE.write_text(content)


def run_build(attempt):
    print(f"\n=== Build {attempt}/2 ===", flush=True)

    process = subprocess.run(
        [
            "nix",
            "build",
            ".#packages.x86_64-linux.default",
            "--no-link",
            "--print-build-logs",
        ],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )

    log = process.stdout or ""

    if process.returncode == 0:
        print("Build successful.", flush=True)
        return True, None

    drv_match = re.search(
        r"hash mismatch in fixed-output derivation '([^']+)'",
        log,
    )

    hash_match = re.search(
        r"got:\s*(sha256-[A-Za-z0-9+/=]+)",
        log,
    )

    if drv_match and hash_match:
        drv_path = drv_match.group(1)

        if not Path(drv_path).name.endswith("-source.drv"):
            print(log, end="", flush=True)
            raise RuntimeError(
                f"Unexpected hash mismatch derivation: {drv_path}"
            )

        return False, hash_match.group(1)

    print(log, end="", flush=True)

    raise RuntimeError(
        f"Build failed with exit code {process.returncode}; "
        "could not identify a source hash mismatch."
    )


def main():
    if len(sys.argv) != 2:
        raise SystemExit(
            f"Usage: {sys.argv[0]} VERSION"
        )

    version = sys.argv[1].removeprefix("v")

    if not VERSION_RE.fullmatch(version):
        raise SystemExit(f"Invalid version: {version}")

    print(f"Updating dfint-installer to {version}")

    flake = FLAKE.read_text()

    flake = replace_one(
        flake,
        VERSION_PATTERN,
        rf'\g<1>{version}";',
        "version field",
    )

    flake = replace_one(
        flake,
        SOURCE_HASH_PATTERN,
        lambda match: (
            f"{match.group(1)}{FAKE_HASH}{match.group(2)}"
        ),
        "source hash",
    )

    FLAKE.write_text(flake)

    for attempt in range(1, 3):
        success, new_hash = run_build(attempt)

        if success:
            print(
                f"\nSuccessfully updated dfint-installer to {version}"
            )
            return

        print(f"\nUpdating source hash: {new_hash}")
        write_source_hash(new_hash)

        if attempt == 2:
            raise RuntimeError(
                "Package did not build after two attempts"
            )

    raise RuntimeError("Unexpected updater state")


if __name__ == "__main__":
    main()
