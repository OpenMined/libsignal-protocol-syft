#!/bin/bash
set -e

echo "=== Testing Build Commands Locally ==="
echo

echo "Step 1: Clean previous builds"
cargo clean
echo "✓ Cleaned"
echo

echo "Step 2: Build individual crates in dependency order"
echo "  Building spqr-syft..."
cargo build -p spqr-syft
echo "  ✓ spqr-syft built"

echo "  Building libsignal-core-syft..."
cargo build -p libsignal-core-syft
echo "  ✓ libsignal-core-syft built"

echo "  Building signal-crypto-syft..."
cargo build -p signal-crypto-syft
echo "  ✓ signal-crypto-syft built"

echo "  Building libsignal-protocol-syft..."
cargo build -p libsignal-protocol-syft
echo "  ✓ libsignal-protocol-syft built"
echo

echo "Step 3: Build entire workspace"
cargo build --workspace
echo "✓ Workspace built"
echo

echo "Step 4: Check all crates (faster than build)"
cargo check --workspace
echo "✓ All crates checked"
echo

echo "Step 5: Build in release mode"
cargo build --workspace --release
echo "✓ Release build completed"
echo

echo "Step 6: Verify crate metadata"
for crate in spqr-syft libsignal-core-syft signal-crypto-syft libsignal-protocol-syft; do
    echo "  Checking $crate metadata..."
    VERSION=$(grep '^version = ' crates/$crate/Cargo.toml | head -1 | cut -d'"' -f2)
    REPO=$(grep '^repository.workspace' crates/$crate/Cargo.toml | wc -l | tr -d ' ')
    if [ "$REPO" != "1" ]; then
        echo "    ✗ Missing repository metadata"
        exit 1
    fi
    echo "    ✓ $crate v$VERSION has metadata"
done
echo

echo "=== All build tests passed! ==="
