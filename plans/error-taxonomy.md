# KeyClave error taxonomy and recovery strategy (MVP)

This document defines the unified error classification system and recovery strategies across all KeyClave modules.

Related:

- Architecture: [`plans/architecture-module-boundaries.md`](plans/architecture-module-boundaries.md:1)
- Security: [`plans/security-crypto-2fa.md`](plans/security-crypto-2fa.md:1)
- Key validation errors: [`plans/key-validation.md`](plans/key-validation.md:75)

## 1) Design principles

- Every error must have a **category**, a **user-facing message**, and a **recovery suggestion**.
- Error messages must **never contain secret values** (enforced by the redaction layer).
- Errors are structured objects, not raw strings.
- All errors are logged to the local audit/operational log with redaction applied.

## 2) Error categories

### 2.1 Vault errors

| Code | Description | Recovery |
|------|-------------|----------|
| `vault.locked` | Vault is locked; operation requires unlock | Prompt user to unlock |
| `vault.wrong_passphrase` | Passphrase incorrect | Retry; after 5 failures, add delay |
| `vault.totp_required` | TOTP code required for this action | Prompt for TOTP code |
| `vault.totp_invalid` | TOTP code invalid or expired | Retry with new code |
| `vault.kdf_memory_error` | KDF memory allocation failed | Retry with reduced params; see fallback policy |
| `vault.corruption` | Vault database integrity check failed | Offer restore from backup; log for diagnostics |
| `vault.rotation_failed` | PVK rotation failed mid-transaction | Transaction rolled back; old PVK still valid |

### 2.2 Profile errors

| Code | Description | Recovery |
|------|-------------|----------|
| `profile.not_found` | Profile ID does not exist | Show profile list |
| `profile.already_exists` | Display name collision | Suggest alternative name |
| `profile.index_corrupt` | Profile index DB corrupted | Attempt repair; offer manual recovery |

### 2.3 Import/export errors

| Code | Description | Recovery |
|------|-------------|----------|
| `import.parse_error` | Could not parse input format | Show unparsed lines; allow manual entry |
| `import.conflict` | Key already exists in vault | Prompt per-key resolution |
| `export.bundle_write_failed` | Could not write bundle file | Check disk space and permissions |
| `import.bundle_integrity` | Bundle AEAD tag verification failed | File may be corrupted or tampered |
| `import.bundle_expired` | Bundle expiry timestamp is in the past | Inform user; block import |
| `import.bundle_wrong_password` | Bundle password incorrect | Retry |
| `import.bundle_version_unsupported` | Bundle format version not recognized | Update KeyClave |

### 2.4 Dotenv errors

| Code | Description | Recovery |
|------|-------------|----------|
| `dotenv.parse_warning` | Some lines could not be parsed | Preserve as opaque; warn user |
| `dotenv.write_failed` | Atomic write failed | Check permissions; retry |
| `dotenv.backup_failed` | Could not create backup | Abort write; inform user |
| `dotenv.alias_conflict` | Multiple aliases for same provider in file | Prompt user to choose canonical key |

### 2.5 Validation errors

| Code | Description | Recovery |
|------|-------------|----------|
| `validation.offline` | Cannot validate in Offline Mode | Enable Online Mode or skip |
| `validation.rate_limited` | Provider rate limit hit | Wait and retry |
| `validation.network_error` | Network failure during validation | Check connection; retry |
| `validation.provider_error` | Provider returned unexpected error | Retry later |
| `validation.unverifiable` | No safe validation endpoint for provider | Inform user; no action needed |

### 2.6 Project scanning errors

| Code | Description | Recovery |
|------|-------------|----------|
| `scan.permission_denied` | Cannot read project directory | Check permissions |
| `scan.too_large` | File exceeds size limit for parsing | Skip file; inform user |
| `scan.no_markdown` | No Markdown files found in project | Verify project root |

### 2.7 LLM errors

| Code | Description | Recovery |
|------|-------------|----------|
| `llm.not_installed` | No model installed | Offer model download |
| `llm.inference_failed` | Model inference returned error | Fall back to rule-based; log for diagnostics |
| `llm.checksum_mismatch` | Downloaded model checksum does not match | Re-download or sideload |
| `llm.insufficient_resources` | Not enough RAM/VRAM for model | Suggest smaller quantization tier |

### 2.8 System errors

| Code | Description | Recovery |
|------|-------------|----------|
| `system.disk_full` | Insufficient disk space | Free space and retry |
| `system.permission_denied` | OS permission error | Check file/directory permissions |
| `system.keychain_unavailable` | OS credential store not available | Fall back to passphrase-only |

## 3) Error structure

All errors should follow a consistent structure:

```python
class KeyClaveError:
    code: str           # e.g., "vault.wrong_passphrase"
    category: str       # e.g., "vault"
    message: str        # user-facing, redacted
    detail: str | None  # developer detail, redacted
    recoverable: bool   # whether the user can retry/fix
    suggestion: str     # what the user should do
```

## 4) Redaction enforcement

- The error construction layer must pass all string fields through the global redaction filter before storage or display.
- Test: for every error code, there must be a test that constructs the error with a fake secret embedded and asserts the output does not contain the secret.

## 5) Error display UX

- Recoverable errors: show inline with a retry/fix action button.
- Non-recoverable errors: show a dialog with the suggestion and a "Copy diagnostics" button.
- Never show raw stack traces to users; stack traces go to operational logs only.

## 6) Acceptance criteria

- Every module uses the structured error taxonomy.
- No error message contains secret values.
- Every error code has a corresponding test.
- Users always see a recovery suggestion.
