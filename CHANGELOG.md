# Changelog

## [1.1.1] - 2026-09-14

- Remove administrator Agent authentication, token exchange, device identity and context/audit clients from the public SDK. Their inclusion in 1.1.0 was a product-boundary error.
- Keep user API-key authentication, capability discovery, schema enhancements, task categories and preview metadata.
- Add regression checks rejecting administrator credentials in the public client.

## [1.1.0] - 2026-09-14

- Add device-bound AgentAuth with Ed25519 proof, token exchange/refresh, and context/audit operations; ordinary sk- keys remain supported.
- Add API capability discovery and title/category support, including category=all for website tasks.
- Preserve preview metadata and URL fields; encode identifiers and surface API errors.
- Add an enhanced schema example and cross-language API/device-proof contract checks.

New capability/category features require the corresponding website API update. Registry publication is a separate step from the Git release tag.
