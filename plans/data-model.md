# KeyClave data model (MVP)

Decisions locked for MVP:

- Storage engine: SQLite per profile.
- Secret uniqueness: unique per `(profile_id, provider_id, key_name)`.
- Project records: optional scan index across disk with explicit opt-in, storing last-scan timestamps.
- Audit retention: user-configurable (stored in `profile_settings`).
- Providers: built-in only for MVP (start with GitHub); includes a built-in `generic` provider for unrecognized keys.
- Provider env var templates: kept in code only (not stored in DB); the `providers` table stores identity metadata only.
- Provenance: stored as columns on the `secrets` table (not a separate table) for MVP simplicity.
- Validation storage: last result only per secret (single row, upserted on each validation).

Related:

- Architecture: [`plans/architecture-module-boundaries.md`](plans/architecture-module-boundaries.md)
- Security: [`plans/security-crypto-2fa.md`](plans/security-crypto-2fa.md)
- Key import flows: [`plans/key-import-flows.md`](plans/key-import-flows.md)
- Key validation: [`plans/key-validation.md`](plans/key-validation.md)

## 1) Storage layout

### Root data directory (per OS)

KeyClave stores all application data under a platform-standard directory:

- **macOS**: `~/Library/Application Support/KeyClave/`
- **Windows**: `%LOCALAPPDATA%\KeyClave\`
- **Linux**: `~/.local/share/keyclave/`

Within this root:

- `index.db` — top-level profile index (see section 3.0)
- `profiles/<profile_id>/vault.db` — per-profile encrypted vault database
- `models/` — local LLM model storage (not encrypted; models are not secrets)
- `logs/` — operational log files
- `backups/` — diagnostics package exports

### Per-profile database
Each profile has its own SQLite database file (and associated encrypted blobs if used).

Path: `<root_data_dir>/profiles/<profile_id>/vault.db`

Encryption note:

- SQLite is treated as an application-level storage engine.
- Sensitive fields are encrypted at the application layer using the per-profile `PVK` described in [`plans/security-crypto-2fa.md`](plans/security-crypto-2fa.md:1).

## 2) Entity overview

### Entities
- `app_profiles` (in `index.db`, accessible before unlock)
- `profile_vault_meta` (in `index.db`, stores KDF/wrapped-key metadata)
- `profile_settings` (in per-profile `vault.db`)
- `providers`
- `secrets`
- `projects`
- `project_docs`
- `project_requirements`
- `dotenv_targets`
- `validations`
- `audit_events`

### Common fields
All tables that store timestamps should use UTC ISO 8601 text strings consistently (e.g., `2026-02-06T14:25:00Z`).

## 3) Tables

### 3.0 app_profiles (in index.db — top-level, pre-unlock)

The profile index lives in a top-level `index.db` at the root data directory. This database is **not encrypted** because it must be readable before any profile is unlocked.

Fields:

- `id` (PK, text UUID)
- `display_name` (text)
- `created_at` (text, UTC ISO 8601)
- `updated_at` (text, UTC ISO 8601)
- `vault_storage_mode` (text enum: `passphrase_only`, `os_keychain_optional`)
- `totp_enabled` (bool)
- `online_mode_enabled_default` (bool)
- `local_llm_assist_enabled_default` (bool, default false)

Notes:

- `local_llm_assist_enabled_default` must default to false (approved).
- This table does **not** contain any encrypted secrets or TOTP shared secrets.
- `totp_secret_enc` is stored in the per-profile `vault.db` (encrypted with PVK), not here.

### 3.1 profile_vault_meta (in index.db — pre-unlock)

Stores KDF and wrapped-key metadata. Must be accessible before unlock to derive the vault key.

- `profile_id` (PK/FK → `app_profiles.id`)
- `kdf_alg` (text; e.g., `argon2id`)
- `kdf_params_json` (text)
- `kdf_salt` (blob)
- `wrapped_pvk` (blob)
- `rotation_version` (int)

### 3.2 profile_settings (in per-profile vault.db — post-unlock)

Per-profile configuration that is only accessible after vault unlock.

- `profile_id` (PK)
- `totp_secret_enc` (blob, encrypted with PVK)
- `auto_lock_timeout_seconds` (int, default 300 = 5 minutes)
- `audit_retention_max_count` (int, nullable; default 10000)
- `audit_retention_max_days` (int, nullable; default 365)
- `clipboard_auto_clear_seconds` (int, default 30)
- `updated_at` (text, UTC ISO 8601)

### 3.3 providers

Built-in providers known to the app.

- `id` (PK; e.g., `github`, `generic`)
- `display_name`
- `homepage_url` (nullable for `generic`)
- `docs_url` (nullable for `generic`)
- `created_at`
- `updated_at`

Notes:

- A built-in `generic` provider (id: `generic`, display_name: "Unassigned") is always present for keys that do not match any known provider.
- Provider env var templates (canonical names, aliases, value hints) are defined in Python code within the provider plugin system, not stored in this table. This keeps the DB schema simple and avoids sync issues between code and DB.

### 3.4 secrets

One stored secret value.

- `id` (PK text UUID)
- `profile_id` (FK)
- `provider_id` (FK → `providers.id`; never null; use `generic` for unrecognized keys)
- `key_name` (text)
  Example: `GITHUB_TOKEN`
- `secret_value_enc` (blob/text encrypted)
- `notes` (text, optional)
- `tags_json` (text, optional)
- `source_type` (text; enum: `manual`, `paste`, `file_import`, `dotenv_patch`, `export_bundle_import`)
- `source_label` (text, optional; e.g., file path, user-controlled)
- `imported_at` (text, UTC ISO 8601, nullable; set on import, null for manual entry)
- `created_at`
- `updated_at`

Uniqueness:

- `UNIQUE(profile_id, provider_id, key_name)`

Notes:

- `provider_id` is never null. Keys with no recognized provider use `generic`.
- Provenance fields (`source_type`, `source_label`, `imported_at`) are stored directly on the secrets table for MVP simplicity. A separate provenance table may be introduced post-MVP if richer audit trails are needed.

### 3.5 projects

Represents a project folder the user has scanned or pinned.

- `id` (PK text UUID)
- `profile_id` (FK)
- `root_path` (text)
- `display_name` (text)
- `scan_index_opt_in` (bool)
- `last_scanned_at` (timestamp, nullable)
- `created_at`
- `updated_at`

Notes:

- Full-disk scan indexing must be opt-in; `scan_index_opt_in` captures that.
- Project paths are considered potentially sensitive metadata. In Online Mode, project paths must not be transmitted or logged to external services. Locally, paths are stored in the per-profile vault.db which is encrypted at rest.

### 3.6 project_docs

Markdown (and possibly other) documents used during scans.

- `id` (PK)
- `project_id` (FK)
- `path` (text)
- `sha256` (blob/text)
  Used to detect changes without re-parsing everything.
- `last_parsed_at`

### 3.7 project_requirements

Outputs of Markdown ingestion.

- `id` (PK)
- `project_id` (FK)
- `provider_id` (FK)
- `required_env_vars_json` (text)
- `confidence` (real)
- `citations_json` (text)
- `created_at`

### 3.8 dotenv_targets

Represents a dotenv file target within a project.

- `id` (PK)
- `project_id` (FK)
- `path` (text)
  e.g., `.env`, `.env.local`
- `last_written_at`
- `last_diff_summary_json` (text, optional)

### 3.9 validations

Stores the **last validation result only** per secret. On each validation, the existing row for that secret is upserted (replaced).

- `secret_id` (PK, FK → `secrets.id`; one row per secret)
- `provider_id` (FK)
- `status` (text enum: `unknown`, `valid`, `invalid`, `unverifiable`, `error`)
- `checked_at` (text, UTC ISO 8601)
- `error_code` (text, optional)
- `error_message_redacted` (text, optional)
- `restriction_info_json` (text, optional)

Notes:

- Changed from previous design: `secret_id` is now the PK (not a separate `id`), enforcing exactly one row per secret.
- Added `unverifiable` status for providers that have no safe free/auth validation endpoint in MVP (see [`plans/key-validation.md`](plans/key-validation.md:35)).
- No validation history is stored in MVP. If history is needed post-MVP, a `validation_history` table can be added.

### 3.10 audit_events

Local-only redacted audit events.

- `id` (PK)
- `profile_id` (FK)
- `event_type` (text)
- `created_at`
- `metadata_json_redacted` (text)

Retention:

- Governed by `profile_settings.audit_retention_max_count` and `profile_settings.audit_retention_max_days`.
- Cleanup runs on profile unlock and periodically during active sessions.

## 4) Indexing

Recommended indexes:

- `secrets(profile_id, provider_id)`
- `projects(profile_id, root_path)`
- `audit_events(profile_id, created_at DESC)`

Note: the `validations` table no longer needs a `(secret_id, checked_at DESC)` index since `secret_id` is the PK and there is only one row per secret.

## 5) Migration strategy

- Use schema migrations (e.g., Alembic if SQLAlchemy is used, or a lightweight custom migration runner).
- Version the schema.
- Initial migration must create all tables including `profile_vault_meta`, `profile_settings`, and the `generic` provider seed row.

## 6) Resolved questions

The following questions from the original spec have been resolved:

1. **Provider env var templates in DB or code only?** → **Code only.** The `providers` table stores identity metadata; env var specs (canonical names, aliases, value hints) live in the Python provider plugin code. This avoids DB/code sync issues and keeps the schema simple.

2. **Project path privacy in Online Mode?** → **Paths stay local.** Project paths are stored in the per-profile `vault.db` (encrypted at rest). They must never be transmitted to external services, logged to off-device systems, or exposed in the embedded browser context. The Online Mode network adapter must not include project paths in any request.

3. **Per-secret provenance as a first-class table?** → **Columns on `secrets` for MVP.** Provenance fields (`source_type`, `source_label`, `imported_at`) are added directly to the `secrets` table. A separate table may be introduced post-MVP for richer audit trails.
