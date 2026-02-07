# KeyClave testing strategy (MVP)

This document defines the testing approach, frameworks, and coverage expectations for KeyClave.

Related:

- Architecture: [`plans/architecture-module-boundaries.md`](plans/architecture-module-boundaries.md:1)
- Security: [`plans/security-crypto-2fa.md`](plans/security-crypto-2fa.md:1)
- Implementation backlog: [`plans/implementation-backlog.md`](plans/implementation-backlog.md:1)

## 1) Testing principles

- **Test early**: unit tests are written alongside implementation, not deferred to a hardening milestone.
- **Security tests are mandatory**: any code handling secrets, encryption, or redaction must have dedicated tests.
- **No secrets in test fixtures**: use deterministic test keys and values that are clearly fake.
- **Offline-first testing**: all core tests must pass without network access.

## 2) Test framework and tooling

### 2.1 Unit and integration tests

- Framework: **pytest** (standard Python test runner).
- Assertions: pytest built-in assertions + `pytest-mock` for mocking.
- Coverage: **pytest-cov** with a target of ≥80% line coverage for core modules.

### 2.2 UI tests

- Framework: **pytest-qt** for PySide6 widget testing.
- Scope: test view models, signal/slot connections, and critical UI flows (unlock, import, export).
- Do not test pixel-level rendering; focus on behavior.

### 2.3 End-to-end tests

- Use pytest with temporary directories and in-memory SQLite where possible.
- E2E tests exercise full workflows: create profile → import key → scan project → generate dotenv → export bundle.
- Network-dependent tests (validation) are isolated behind a marker (`@pytest.mark.online`) and skipped by default.

### 2.4 Fuzz testing

- Use **Hypothesis** (property-based testing) for:
  - dotenv parser (arbitrary input strings)
  - Markdown ingestion (arbitrary Markdown content)
  - Bundle format parsing (arbitrary byte sequences)
- Fuzz tests run in CI but with a time budget (e.g., 60 seconds per test).

### 2.5 Security-specific tests

- **Redaction tests**: assert that no test output, log capture, or error message contains known test secret values.
- **Encryption round-trip tests**: encrypt → decrypt → verify equality for all AEAD operations.
- **KDF parameter tests**: verify that stored KDF params produce the expected derived key.
- **TOTP tests**: verify code generation and validation against known test vectors (RFC 6238 test vectors).
- **Policy tests**: verify that LLM prompts reject secret-containing inputs.

## 3) Test directory structure

```
tests/
  conftest.py                    # shared fixtures (temp dirs, test profiles, fake secrets)
  unit/
    test_vault_crypto.py         # KDF, AEAD, PVK wrap/unwrap
    test_vault_storage.py        # SQLite CRUD, schema migrations
    test_profiles.py             # profile creation, switching, lock state
    test_secrets.py              # secret CRUD, masking, provenance
    test_providers.py            # provider registry, env var mapping
    test_github_provider.py      # GitHub-specific detection, validation mock
    test_dotenv_parser.py        # parse, format preservation, edge cases
    test_dotenv_merge.py         # merge policy, conflict handling, backups
    test_markdown_ingestion.py   # extraction rules, confidence scoring, citations
    test_export_bundle.py        # bundle create, encrypt, decrypt, integrity
    test_import_flows.py         # single/bulk import, dedup, provenance
    test_validation.py           # status model, rate limiting, offline behavior
    test_audit_log.py            # event recording, redaction, retention
    test_redaction.py            # global redaction rules
    test_totp.py                 # enrollment, verification, recovery codes
    test_llm_policy.py           # prompt policy, secret rejection
  integration/
    test_profile_lifecycle.py    # create → unlock → use → lock → switch
    test_import_export_cycle.py  # import keys → export bundle → import bundle
    test_scan_and_generate.py    # scan project → infer requirements → generate dotenv
    test_online_mode.py          # mode toggle, validation flow (mocked network)
  e2e/
    test_full_workflow.py        # complete user journey
  fuzz/
    test_dotenv_fuzz.py          # Hypothesis-based dotenv parsing
    test_markdown_fuzz.py        # Hypothesis-based Markdown ingestion
    test_bundle_fuzz.py          # Hypothesis-based bundle parsing
```

## 4) CI pipeline expectations

- Run `pytest tests/unit/ tests/integration/` on every commit.
- Run `pytest tests/fuzz/` on nightly or weekly schedule.
- Run `pytest tests/e2e/` on merge to main.
- Fail the build if coverage drops below threshold.
- Fail the build if any redaction test fails.

## 5) Test data and fixtures

### 5.1 Fake secrets

All test secrets must use clearly fake values:

- `GITHUB_TOKEN=ghp_FAKE_TEST_TOKEN_000000000000`
- `STRIPE_API_KEY=sk_test_FAKE_000000000000`

### 5.2 Test profiles

- Create temporary profile directories using `tmp_path` fixture.
- Use deterministic passphrases (e.g., `test-passphrase-do-not-use`).

### 5.3 Test Markdown documents

- Include sample Markdown files in `tests/fixtures/` with known provider references.
- Include edge cases: no providers, multiple providers, ambiguous references.

## 6) Accessibility testing

- Use **pytest-qt** to verify keyboard navigation for critical flows.
- Verify that all interactive elements have accessible names.
- Manual testing with screen readers (VoiceOver on macOS, NVDA on Windows) before each release.
- Verify contrast ratios meet WCAG 2.1 AA (4.5:1 for body text) using automated tooling during UI review.

## 7) Acceptance

- All milestones must pass their associated test suites before being marked complete.
- Security tests must pass with zero failures.
- No known test that asserts secret redaction may be skipped or marked xfail.
