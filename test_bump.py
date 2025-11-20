#!/usr/bin/env python3
"""Test version bumping logic locally without modifying files."""

import re
from pathlib import Path

def test_bump(current_version: str, bump_type: str, remove_beta: bool) -> str:
    """Test version bump logic."""
    print(f"Current version: {current_version}")
    print(f"Bump type: {bump_type}")
    print(f"Remove beta: {remove_beta}")

    # Parse version
    if '-beta.' in current_version:
        base, beta_num = current_version.rsplit('-beta.', 1)
        beta_num = int(beta_num)
    else:
        base = current_version
        beta_num = None

    parts = base.split('.')
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

    # Apply bump
    if bump_type == 'beta':
        if remove_beta and beta_num is not None:
            # Remove beta suffix only
            new_version = base
        elif beta_num is None:
            # Add beta.1 to current version
            new_version = f"{base}-beta.1"
        else:
            # Increment beta number
            new_version = f"{base}-beta.{beta_num + 1}"
    elif bump_type == 'patch':
        patch += 1
        new_version = f"{major}.{minor}.{patch}"
        if not remove_beta:
            new_version += "-beta.1"
    elif bump_type == 'minor':
        minor += 1
        patch = 0
        new_version = f"{major}.{minor}.{patch}"
        if not remove_beta:
            new_version += "-beta.1"
    elif bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
        new_version = f"{major}.{minor}.{patch}"
        if not remove_beta:
            new_version += "-beta.1"
    else:
        new_version = current_version

    print(f"New version: {new_version}")
    return new_version


def get_current_version() -> str:
    """Get current version from sync.py."""
    sync_file = Path('sync.py')
    content = sync_file.read_text()
    match = re.search(r'VERSION = "(.+?)"', content)
    return match.group(1)


if __name__ == '__main__':
    current = get_current_version()

    print("=" * 60)
    print("Testing version bump scenarios")
    print("=" * 60)

    test_cases = [
        ("beta", False),
        ("beta", True),
        ("patch", False),
        ("patch", True),
        ("minor", False),
        ("minor", True),
        ("major", False),
        ("major", True),
    ]

    for bump_type, remove_beta in test_cases:
        print()
        result = test_bump(current, bump_type, remove_beta)
        print("-" * 60)
