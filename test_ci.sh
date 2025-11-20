#!/bin/bash
set -e

echo "=== Testing CI workflow locally ==="
echo

echo "Step 1: Clone spqr dependency (if needed)"
if [ ! -d "third_party/libsignal/third_party/spqr" ]; then
    mkdir -p third_party/libsignal/third_party
    git clone --depth 1 --branch v1.2.0 https://github.com/signalapp/SparsePostQuantumRatchet.git third_party/libsignal/third_party/spqr
    echo "✓ Cloned spqr"
else
    echo "✓ spqr already exists"
fi
echo

echo "Step 2: Sync vendored crates"
python3 sync.py
echo "✓ Synced crates"
echo

echo "Step 3: Build workspace"
cargo build --workspace
echo "✓ Build succeeded"
echo

echo "Step 4: Package all crates (dry-run)"
echo "  Packaging spqr-syft..."
cargo package --allow-dirty --manifest-path crates/spqr-syft/Cargo.toml > /dev/null 2>&1
echo "  ✓ spqr-syft"

echo "  Packaging libsignal-core-syft..."
cargo package --allow-dirty --manifest-path crates/libsignal-core-syft/Cargo.toml > /dev/null 2>&1
echo "  ✓ libsignal-core-syft"

echo "  Packaging signal-crypto-syft..."
cargo package --allow-dirty --manifest-path crates/signal-crypto-syft/Cargo.toml > /dev/null 2>&1
echo "  ✓ signal-crypto-syft"

echo "  Packaging libsignal-protocol-syft (will fail until deps published)..."
if cargo package --allow-dirty --manifest-path crates/libsignal-protocol-syft/Cargo.toml > /dev/null 2>&1; then
    echo "  ✓ libsignal-protocol-syft"
else
    echo "  ⚠ libsignal-protocol-syft (expected - needs published deps)"
fi
echo

echo "=== All CI steps completed successfully! ==="
