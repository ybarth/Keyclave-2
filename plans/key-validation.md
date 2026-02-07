# API key validation framework (MVP)

This spec defines how KeyClave validates API keys safely, how results are stored, and how errors are classified.

Decisions confirmed:

- Offline Mode: return `unknown` and do not perform network calls.
- Rate limiting: per-provider global rate limit.
- Error taxonomy: simple.
- Storage: keep last result only.
- Providers without safe free/auth endpoint: use distinct `unverifiable` status.
- Validation runs only after explicit user click (Online Mode only).

Related:

- Scope: [`plans/product-scope.md`](plans/product-scope.md:1)
- Security: [`plans/security-crypto-2fa.md`](plans/security-crypto-2fa.md:1)
- Provider contract: [`plans/provider-plugins-and-github.md`](plans/provider-plugins-and-github.md:1)
- Data model: [`plans/data-model.md`](plans/data-model.md:1)

## 1) Goals

- Let users test whether a key is valid.
- Avoid side effects and unexpected costs.
- Provide clear statuses and actionable error messages.
- Enforce Offline/Online Mode boundaries.

## 2) Status model

Each validation result has a status:

- `unknown` (not checked yet or Offline Mode)
- `valid`
- `invalid`
- `unverifiable` (provider has no safe free/auth validation endpoint in MVP)
- `error` (temporary failure; retry may succeed)

## 3) Triggering validation

### Explicit user action only

- Validation must be triggered by an explicit “Validate now” action.
- Bulk “Validate all” is allowed but must still be user-initiated.

### Offline Mode behavior

- “Validate now” is disabled or results in `unknown` with explanation.

## 4) Network and privacy constraints

- Validation calls are permitted only in Online Mode.
- Each provider validator must enforce a domain allowlist (provider base domains only).
- KeyClave must not use cloud-hosted LLMs; never send secrets anywhere.

## 5) Safe test call policy

MVP rule:

- Only call endpoints that are documented as authentication or account introspection and do not incur usage charges.
- If no such endpoint exists, the provider returns `unverifiable`.

Provider plugins must document the chosen endpoint and its safety rationale.

## 6) Rate limiting

Per-provider global limiter:

- One validation request per provider at a time.
- Enforce minimum interval between requests per provider (exact interval is an implementation constant).

Rationale:

- Prevent lockouts and accidental bursts.

## 7) Error taxonomy (simple)

`error_code` values:

- `rate_limited`
- `network_error`
- `provider_error`

Mapping:

- HTTP 429 → `rate_limited`
- Timeouts/DNS/TLS failures → `network_error`
- HTTP 5xx or malformed responses → `provider_error`

`error_message_redacted` must not include secrets.

## 8) Storage of validation results

Store only the last result per secret:

- `status`
- `checked_at`
- `error_code` and redacted message (if error)

No full history in MVP.

## 9) UI expectations

- Show `last verified` time.
- Provide a clear explanation for `unverifiable`.
- For `invalid`, suggest next steps (re-check token, regenerate, etc.).

## 10) Acceptance criteria

- No validation occurs in Offline Mode.
- Validation never uses paid/side-effect endpoints.
- Status is stable and stored per secret.
- Errors are redacted.
