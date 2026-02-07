# Telemetry, logging, and diagnostics policy (MVP)

This spec defines what KeyClave logs locally, what (if anything) may be sent off-device, and the required redaction and consent rules.

Policy choices locked:

- Default: **no off-device reporting**.
- MVP includes **local-only** audit logs and operational logs.
- MVP includes a **local diagnostics package export** (user-initiated, stored locally).
- **Off-device crash/error reporting is out of scope for MVP** (no UI, no backend, no telemetry transport, no credentials, no integrations).

Related:

- Security boundaries: [`plans/security-crypto-2fa.md`](plans/security-crypto-2fa.md:1)
- Data model (audit events): [`plans/data-model.md`](plans/data-model.md:1)
- Online assistant policy: [`plans/online-assistant-ux.md`](plans/online-assistant-ux.md:1)

## 1) Principles

1) **Minimize data**
   - Log only what is needed for user trust, debugging, and auditing.
2) **No secrets ever**
   - API keys, tokens, passphrases, TOTP secrets, wrapped keys, decrypted payloads must never appear in logs or crash reports.
3) **No sensitive metadata by default**
   - Avoid file paths, user identifiers, clipboard contents, page text.
4) **User control**
   - Diagnostics features are opt-in and easily revocable.
5) **Local-first**
   - Local audit logs are the primary record.

## 2) Logging types

### 2.1 Local audit log (security-relevant)

Stored locally, per profile.

Purpose:

- Provide accountability for security-sensitive actions.
- Help users understand what happened and when.

 Must record events such as:

- Vault unlock success/failure (without passphrase data)
- Profile switch
- Export bundle created
- Bundle import attempted/completed
 - Dotenv write operations (counts only)
 - Online Mode toggled (enabled/disabled)
 - Guided Setup Session started/ended (provider_id only)

Must never record:

- secret values
- raw URLs visited (allowed: provider_id only, or a coarse domain label)
- file paths

Storage:

- `audit_events` table as in [`plans/data-model.md`](plans/data-model.md:1)

Retention:

- User-configurable retention policy (count-based and/or time-based).

### 2.2 Local operational logs (debugging)

Purpose:

- Help diagnose bugs, performance issues, and integration failures.

Defaults:

- Off or minimal verbosity.
- Provide a “Generate diagnostics package” action that collects logs locally.

Redaction rules apply (see section 4).

### 2.3 Metrics/telemetry (product analytics)

MVP stance:

- No product analytics telemetry.
- No off-device crash/error reporting.

## 3) Off-device crash/error reporting (post-MVP, not in MVP)

MVP constraint (locked): KeyClave must not send crash or error reports off-device.

Post-MVP (optional) may later add opt-in crash reporting, but only if:

- A separate spec is approved.
- Payload redaction and consent UX are implemented and tested.
- The integration is treated as an external dependency (credentials, allowlisting, retention, access controls).

## 4) Global redaction rules

### 4.1 Secret patterns

Always redact:

- Known env var keys from provider registry (e.g., `GITHUB_TOKEN`) if a value appears in same line.
- Anything coming from secret input widgets.

### 4.2 Path handling

- Local logs may store paths only when user explicitly enables “include file paths in diagnostics”.
- Because MVP has no off-device crash reporting, there is no off-device path handling requirement in MVP.

### 4.3 Network payloads

- Never log full headers or bodies.
- Log only:
  - provider_id
  - endpoint label (not full URL)
  - status code
  - duration

## 5) Online assistant data boundaries

- Never log page text.
- Never log DOM excerpts.
- For Guided Setup Sessions, log only:
  - provider_id
  - step id
  - mode (Offline/Online)

## 6) Diagnostics package (local export)

Provide a “Create diagnostics package” action that:

- Collects local operational logs
- Collects app configuration (redacted)
- Collects audit log summary (counts)
- Produces a zip/tar archive stored locally

Rules:

- Must show a preview list of included files.
- Must default to excluding file paths.
- Must never include secret DB content.

## 7) Acceptance criteria

- No secrets appear in logs.
- No off-device crash/error reporting exists in MVP.
- Audit log is local-only, redacted, and user-retained.
