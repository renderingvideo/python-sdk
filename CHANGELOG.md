# Changelog

## [1.1.0] - 2026-09-14

- Add device-bound AgentAuth with Ed25519 proof, token exchange/refresh, and context/audit operations; ordinary sk- keys remain supported.
- Add API capability discovery and title/category support, including category=all for website tasks.
- Preserve preview metadata and URL fields; encode identifiers and surface API errors.
- Add an enhanced schema example and cross-language API/device-proof contract checks.

New capability/category features require the corresponding website API update. Registry publication is a separate step from the Git release tag.
