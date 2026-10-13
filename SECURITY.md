# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.4.x   | ✅        |
| 0.3.x   | ✅        |
| < 0.3   | ❌        |

## Reporting a vulnerability

Email `security@ai-virtual-tryon-studio.dev` with:

- Affected version and commit hash
- Reproduction steps (include OS, GPU, driver)
- Impact assessment — what an attacker could do

We acknowledge within 72 hours and aim to ship a patch within 14 days for high-severity issues.

## Threat model

The desktop tool loads user-supplied images and (optionally) community model packs. Relevant classes:

- **Untrusted model files.** ONNX / TorchScript weights from third parties can exploit parser bugs in ONNX Runtime or PyTorch. We sandbox model loading in a subprocess with a memory cap and no network.
- **Malicious image payloads.** PIL / OpenCV decoders have a history of heap bugs. We pin decoder versions and fuzz the ingest path in CI.
- **Plugin directory traversal.** Community plugins under `plugins/` are restricted to a manifest-declared entrypoint; no arbitrary `import` from user-writable paths.
- **Local HTTP API.** The optional REST bridge binds to `127.0.0.1` only and requires a per-session bearer token printed to the console.

## Out of scope

- Attacks that require the user to already have code execution at the same privilege level.
- Model quality / watermarking disputes — see the model card in each pack.