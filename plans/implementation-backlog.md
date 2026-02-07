# KeyClave implementation backlog (milestones)

This is the execution-oriented backlog derived from the approved specs.

Inputs:

- Scope: [`plans/product-scope.md`](plans/product-scope.md:1)
- Architecture: [`plans/architecture-module-boundaries.md`](plans/architecture-module-boundaries.md:1)
- Security/crypto/2FA: [`plans/security-crypto-2fa.md`](plans/security-crypto-2fa.md:1)
- Data model: [`plans/data-model.md`](plans/data-model.md:1)
- Provider plugins: [`plans/provider-plugins-and-github.md`](plans/provider-plugins-and-github.md:1)
- Markdown ingestion: [`plans/markdown-ingestion.md`](plans/markdown-ingestion.md:1)
- Dotenv merge: [`plans/dotenv-merge.md`](plans/dotenv-merge.md:1)
- Online assistant: [`plans/online-assistant-ux.md`](plans/online-assistant-ux.md:1)
- Export bundles: [`plans/export-import-bundles.md`](plans/export-import-bundles.md:1)
- Key import flows: [`plans/key-import-flows.md`](plans/key-import-flows.md:1)
- Key validation: [`plans/key-validation.md`](plans/key-validation.md:1)
- Telemetry/logging: [`plans/telemetry-logging.md`](plans/telemetry-logging.md:1)
- Local LLM inference: [`plans/local-llm-inference.md`](plans/local-llm-inference.md:1)
- UX/brand/sonic: [`plans/ux-brand-sonic.md`](plans/ux-brand-sonic.md:1)
- Testing strategy: [`plans/testing-strategy.md`](plans/testing-strategy.md:1)
- Error taxonomy: [`plans/error-taxonomy.md`](plans/error-taxonomy.md:1)
- UI stack ADR: [`plans/adr-0001-ui-stack-pyside6-qtwebengine.md`](plans/adr-0001-ui-stack-pyside6-qtwebengine.md:1)

## Milestone 0: Repo scaffolding + third-party reference setup

- Create project skeleton for a PySide6 app (packages, naming, linting).
- Set up per-OS data directory convention (see [`plans/data-model.md`](plans/data-model.md:28)).
- Add [`third_party/`](third_party/) structure and manifest for pinned upstream references.
- Clone approved reference repos (Infisical + dotenv-vault) and record commit SHAs.
- Add `LICENSES/` or attribution notes as needed.
- Set up pytest test infrastructure per [`plans/testing-strategy.md`](plans/testing-strategy.md:1).
- Implement the structured error taxonomy base classes per [`plans/error-taxonomy.md`](plans/error-taxonomy.md:1).

Acceptance:

- Repo builds a minimal Qt window.
- `third_party/manifest.yml` lists upstream URLs + SHAs.
- `pytest` runs with empty test suite.
- Error base classes are importable.

## Milestone 1: Vault + profiles (local-only MVP core)

- Implement profile manager:
  - create profile (writes to `index.db`)
  - switch profile
  - lock/unlock
  - inactivity auto-lock (default 5 minutes, configurable via `profile_settings`)
- Implement passphrase-only vault:
  - Argon2id KDF defaults (128 MiB, time 4, parallelism 1; with fallback to 64 MiB on memory error)
  - PVK wrap/unwrap
  - per-record AES-256-GCM encryption with random 96-bit nonces
  - PVK rotation with transactional re-encryption
- Implement initial SQLite schema + migrations per [`plans/data-model.md`](plans/data-model.md:1):
  - `index.db`: `app_profiles`, `profile_vault_meta`
  - per-profile `vault.db`: `profile_settings`, `providers`, `secrets`, `projects`, `project_docs`, `project_requirements`, `dotenv_targets`, `validations`, `audit_events`
  - Seed `generic` provider row
- Implement secrets CRUD:
  - add (with provenance fields: `source_type`, `source_label`, `imported_at`)
  - edit metadata
  - delete
  - list with masking
- Implement optional per-profile TOTP enrollment and enforcement for export:
  - 8 one-time recovery codes
  - recovery code storage encrypted with PVK

Acceptance:

- Secrets are never stored in plaintext.
- Unlock required to reveal/export.
- Multi-profile separation works.
- Auto-lock triggers after configured timeout.
- Unit tests pass for vault crypto, profiles, and secrets CRUD.

## Milestone 2: Import + Export bundles

- Implement single-key entry UI + flows.
- Implement bulk import:
  - paste parsing
  - file import
  - preview + conflict resolution
  - provenance metadata
  - `generic` provider for unrecognized keys
- Implement encrypted export bundles:
  - `.kcbundle` format with binary header
  - password KDF + AES-256-GCM AEAD
  - JSON-UTF8 payload serialization
  - optional expiry
- Implement bundle import:
  - preview header
  - decrypt
  - per-key conflict prompts
  - expiry enforcement

Acceptance:

- Import never reads clipboard without explicit user action.
- Export/import is confidential and tamper-evident.
- Expired bundles are rejected.
- Unit and integration tests pass.

## Milestone 3: Project scanning + Markdown requirement inference

- Implement project selection UI.
- Implement filesystem scanning with exclusions.
- Implement Markdown ingestion rules:
  - env-var detection
  - code-block heuristics
  - provider names/domains
  - citations (path + line range + excerpt)
  - additive confidence scoring with dampeners
- Implement requirements report UI:
  - grouped by provider
  - missing keys vs present
  - user accept/reject

Acceptance:

- Output always includes citations.
- Offline Mode supported.
- Confidence scores are explainable.
- Unit and fuzz tests pass.

## Milestone 4: Dotenv generation + safe patching

- Implement dotenv AST-preserving parser:
  - safe fallback for unparseable lines (preserve as opaque blocks)
- Implement diff preview (masked values).
- Implement backup + atomic write:
  - max 10 backups per target file (configurable)
- Implement merge prompting per key.
- Implement provider alias conflict handling (e.g., GitHub `GITHUB_TOKEN` vs `GH_TOKEN`).

Acceptance:

- Never deletes unknown keys.
- Never corrupts multi-line values it cannot parse.
- Always backup + preview.
- Unit and fuzz tests pass.

## Milestone 5: Provider system + GitHub first-class support

- Implement provider registry + plugin interface.
- Implement GitHub plugin:
  - env var aliases (`GITHUB_TOKEN`, `GH_TOKEN`)
  - offline playbook
  - validator placeholder
  - `unverifiable` status support for providers without safe endpoints
- Seed `generic` provider in registry.

Acceptance:

- GitHub env var defaults are correct.
- Plugin system can add providers later.
- `unverifiable` status works correctly.

## Milestone 6: Local LLM stack (optional assist, fully offline)

- Implement local model catalog and model manager:
  - download or sideload GGUF
  - checksum verification
  - storage location per OS (under `<root_data_dir>/models/`)
  - rollback to previous model
- Implement local inference adapter:
  - bundled `llama.cpp` runtime path (default)
  - optional Ollama integration via localhost if installed
- Implement policy guardrails:
  - no secrets in prompts
  - no prompt persistence by default
  - local-only execution (no network)
- Add local inference smoke test and benchmark capture.

Acceptance:

- App is fully usable without any model installed.
- When installed, inference runs locally and continues to work with network disabled.
- Policy tests pass (secrets rejected from prompts).

## Milestone 7: Online Mode + validation + embedded browsing

- Implement Online Mode toggle (explicit enable).
- Implement key validation framework:
  - explicit user click
  - per-provider rate limiting
  - statuses incl `unverifiable`
  - last-result-only storage (upsert on `validations` table)
- Implement embedded browser panel (QtWebEngine) with:
  - session-only cookies default
  - mode banner
  - external browser fallback
  - feature restrictions per [`plans/online-assistant-ux.md`](plans/online-assistant-ux.md:168)
- Implement Online Assistant session UX:
  - step proposals
  - confirmations
  - provider playbook integration

Note: cloud-hosted LLM assistance is out of scope; optional assistance is local-only per [`plans/local-llm-inference.md`](plans/local-llm-inference.md:1).

Acceptance:

- No secrets are sent to cloud.
- Online Mode clearly visible.
- WebEngine features restricted per spec.
- Validation results stored correctly.

## Milestone 8: Packaging, updates, and polish

- Package for Windows/macOS/Linux using **PyInstaller** (see [`plans/adr-0001-ui-stack-pyside6-qtwebengine.md`](plans/adr-0001-ui-stack-pyside6-qtwebengine.md:108)).
- Add code signing pipeline placeholders.
- Implement custom update feed with signed manifests.
- Apply theme tokens and component styling per [`plans/ux-brand-sonic.md`](plans/ux-brand-sonic.md:1).
- Implement `SoundManager` and integrate sonic cues (user-configurable, accessibility aware).
- Source and bundle sound assets per [`plans/ux-brand-sonic.md`](plans/ux-brand-sonic.md:253).
- Implement accessibility requirements per [`plans/ux-brand-sonic.md`](plans/ux-brand-sonic.md:275).

Acceptance:

- Installers run on target OSes.
- Visual identity is consistent.
- Sound cues work and are configurable.
- Accessibility testing passes (keyboard navigation, screen reader, contrast).

## Milestone 9: Security hardening + QA

- Add fuzz/edge tests for dotenv parsing.
- Add security tests:
  - ensure logs contain no secrets
  - redaction tests for all error codes
- Add local LLM tests:
  - policy tests ensuring secrets are rejected from prompts
  - offline regression tests for model install/inference
- Add dependency pinning + SBOM generation.
- Threat-model review against implemented behavior.
- Run accessibility audit per [`plans/ux-brand-sonic.md`](plans/ux-brand-sonic.md:289).
- Document bundled Chromium version and QtWebEngine security update policy.

Acceptance:

- No sensitive data in logs.
- Vault encryption verified.
- All error codes have redaction tests.
- Accessibility audit complete.

## Provider expansion (post-MVP track)

- Add providers beyond GitHub.
- Expand restriction probing where safe.
- Add user-defined provider templates (optional future).
