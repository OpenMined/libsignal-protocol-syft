# libsignal-protocol-syft (vendored)

This directory contains a vendored copy of the libsignal crates we need for
`syft-crypto-core`. The upstream source lives under `third_party/libsignal`
as a git submodule. We only copy the minimal subset of crates that the
syft protocol depends on (`libsignal-core`, `signal-crypto`, and
`libsignal-protocol`).

To refresh the vendored crates after updating the submodule, run:

```bash
cd vendor/libsignal-protocol-syft
python3 sync.py
```

The sync script:

1. Copies `third_party/libsignal/rust/{core,crypto,protocol}` into `crates/`.
2. Renames the crates to `libsignal-core-syft`, `signal-crypto-syft`,
   and `libsignal-protocol-syft`.
3. Rewrites their manifests so that `workspace = true` dependencies become
   explicit version requirements, and so local dependencies point at the
   vendored siblings.

The generated crates are ready to be published to crates.io and can also
be used in development via a `path` dependency in the outer workspace.
