# KeyClave (planning index)

This repository currently contains the **approved planning/spec set** for building KeyClave: a cross-platform desktop API key manager with intelligent project scanning, dotenv generation/patching, and an optional human-in-the-loop online assistant.

## Specs and decisions (start here)

### Product
- Scope + non-goals: [`plans/product-scope.md`](plans/product-scope.md:1)

### Architecture
- UI stack ADR (PySide6 + QtWebEngine + packaging + auto-update): [`plans/adr-0001-ui-stack-pyside6-qtwebengine.md`](plans/adr-0001-ui-stack-pyside6-qtwebengine.md:1)
- Module boundaries: [`plans/architecture-module-boundaries.md`](plans/architecture-module-boundaries.md:1)
- Data model (SQLite per profile): [`plans/data-model.md`](plans/data-model.md:1)
- Error taxonomy and recovery: [`plans/error-taxonomy.md`](plans/error-taxonomy.md:1)

### Security
- Reuse policy (third-party reference + selective snippet rules): [`plans/reuse-strategy.md`](plans/reuse-strategy.md:1)
- Security/crypto/2FA spec: [`plans/security-crypto-2fa.md`](plans/security-crypto-2fa.md:1)
- Telemetry/logging policy (local-only in MVP): [`plans/telemetry-logging.md`](plans/telemetry-logging.md:1)

### Providers and automation
- Provider plugins + GitHub reference: [`plans/provider-plugins-and-github.md`](plans/provider-plugins-and-github.md:1)
- Key validation framework: [`plans/key-validation.md`](plans/key-validation.md:1)
- Online assistant UX + embedded browser policy: [`plans/online-assistant-ux.md`](plans/online-assistant-ux.md:1)
- Local LLM inference + model management: [`plans/local-llm-inference.md`](plans/local-llm-inference.md:1)

### Project integration
- Markdown ingestion rules + citation format: [`plans/markdown-ingestion.md`](plans/markdown-ingestion.md:1)
- Dotenv generation/merge/patch rules: [`plans/dotenv-merge.md`](plans/dotenv-merge.md:1)

### User workflows
- Key import flows (single + bulk): [`plans/key-import-flows.md`](plans/key-import-flows.md:1)
- Encrypted export/import bundles: [`plans/export-import-bundles.md`](plans/export-import-bundles.md:1)

### UX / brand
- Visual system + logo guidance + sonic design + accessibility: [`plans/ux-brand-sonic.md`](plans/ux-brand-sonic.md:1)

### Quality
- Testing strategy: [`plans/testing-strategy.md`](plans/testing-strategy.md:1)

### Operations
- External infrastructure setup: [`plans/external-infrastructure-setup.md`](plans/external-infrastructure-setup.md:1)

## Implementation roadmap

- Milestone backlog: [`plans/implementation-backlog.md`](plans/implementation-backlog.md:1)

## Review
- Plan review (2026-02-06): [`plans/plan-review-2026-02-06.md`](plans/plan-review-2026-02-06.md:1)
