#!/usr/bin/env python3
"""
Sync selected crates from third_party/libsignal into the vendored workspace.

Copies the upstream libsignal crates we depend on, rewrites their Cargo manifests
to use a new package name/version, and replaces `workspace = true` dependencies
with concrete versions so they can be published independently.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

VERSION = "0.85.3-beta.2"

CRATES = [
    {
        "source": "third_party/spqr",
        "dest": "spqr-syft",
        "description": "Vendored spqr crate for syft",
        "locals": [],
    },
    {
        "source": "rust/core",
        "dest": "libsignal-core-syft",
        "description": "Vendored libsignal core crate for syft",
        "locals": [],
    },
    {
        "source": "rust/crypto",
        "dest": "signal-crypto-syft",
        "description": "Vendored libsignal crypto crate for syft",
        "locals": [("libsignal-core", "libsignal-core-syft")],
    },
    {
        "source": "rust/protocol",
        "dest": "libsignal-protocol-syft",
        "description": "Vendored libsignal protocol crate for syft",
        "locals": [
            ("libsignal-core", "libsignal-core-syft"),
            ("signal-crypto", "signal-crypto-syft"),
            ("spqr", "spqr-syft"),
        ],
    },
]  # order matters (spqr -> core -> crypto -> protocol)


def parse_workspace_dependencies(path: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    lines = path.read_text().splitlines()
    inside = False
    buffer = ""
    current_key: str | None = None
    brace_balance = 0

    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[workspace.dependencies]"):
            inside = True
            continue
        if inside and line.startswith("["):
            break
        if not inside:
            continue

        if current_key is None:
            if "=" not in line:
                continue
            key, rest = line.split("=", 1)
            current_key = key.strip()
            buffer = rest.strip()
        else:
            buffer += " " + line

        brace_balance += buffer.count("{") - buffer.count("}")
        if brace_balance > 0:
            continue

        value = buffer.strip()
        if value.startswith("{"):
            snippet = value[1:-1].strip()
        else:
            snippet = f'version = {value}'

        mapping[current_key] = snippet
        current_key = None
        buffer = ""

    return mapping


def copy_crate(src: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def replace_first(pattern: str, repl: str, text: str) -> str:
    return re.sub(pattern, repl, text, count=1, flags=re.MULTILINE)


def patch_manifest(
    manifest: Path,
    crate_name: str,
    description: str,
    workspace_deps: dict[str, str],
    local_deps: list[tuple[str, str]],
) -> None:
    text = manifest.read_text()
    text = replace_first(r'^name\s*=\s*".*"$', f'name = "{crate_name}"', text)
    text = replace_first(r'^version\s*=\s*".*"$', f'version = "{VERSION}"', text)
    if 'description = "' in text:
        text = replace_first(
            r'^description\s*=\s*".*"$', f'description = "{description}"', text
        )
    else:
        text = text.replace(
            '[package]',
            f'[package]\ndescription = "{description}"',
            1,
        )

    # Add repository and homepage if not present
    if 'repository.workspace = true' not in text and 'repository = ' not in text:
        text = replace_first(
            r'^edition\s*=',
            'repository.workspace = true\nhomepage.workspace = true\nedition =',
            text
        )

    for dep, alias in local_deps:
        pattern = rf'{dep}\s*=\s*\{{[^}}]*\}}'
        replacement = (
            f'{dep} = {{ version = "{VERSION}", package = "{alias}", path = "../{alias}" }}'
        )
        text, count = re.subn(pattern, replacement, text)
        if count == 0:
            raise RuntimeError(f"failed to rewrite local dependency {dep} in {manifest}")

    local_names = {name for name, _ in local_deps}
    for dep, snippet in workspace_deps.items():
        if dep in local_names:
            continue

        pattern = rf'({dep}\s*=\s*\{{[^}}]*?)workspace\s*=\s*true([^}}]*\}})'

        def repl(match: re.Match[str], insert=snippet) -> str:
            return f"{match.group(1)}{insert}{match.group(2)}"

        text = re.sub(pattern, repl, text)

    manifest.write_text(text)


def main() -> None:
    repo_root = Path(__file__).resolve().parent
    upstream_root = repo_root / "third_party" / "libsignal"
    workspace_deps = parse_workspace_dependencies(upstream_root / "Cargo.toml")
    crates_root = repo_root / "crates"
    crates_root.mkdir(parents=True, exist_ok=True)

    for spec in CRATES:
        src = upstream_root / spec["source"]
        dest = crates_root / spec["dest"]
        copy_crate(src, dest)
        patch_manifest(
            dest / "Cargo.toml",
            spec["dest"],
            spec["description"],
            workspace_deps,
            spec["locals"],
        )

    print("Synced libsignal crates:")
    for spec in CRATES:
        print(f"  - {spec['dest']}")


if __name__ == "__main__":
    main()
