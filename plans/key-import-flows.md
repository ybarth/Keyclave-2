# Key import flows (single + bulk) + masking + dedup + provenance + clipboard (MVP)

This spec defines how users import API keys into KeyClave safely and efficiently.

Related:

- Scope: [`plans/product-scope.md`](plans/product-scope.md:1)
- Security boundaries: [`plans/security-crypto-2fa.md`](plans/security-crypto-2fa.md:1)
- Providers: [`plans/provider-plugins-and-github.md`](plans/provider-plugins-and-github.md:1)
- Data model: [`plans/data-model.md`](plans/data-model.md:1)

## 1) Goals

- Support **single key** entry and **bulk import**.
- Prevent accidental leakage (masking, limited reveal, clipboard hygiene).
- Deduplicate intelligently.
- Capture provenance (where a key came from) without storing sensitive content.

## 2) Import sources (MVP)

### 2.1 Single entry

User provides:

- Provider (e.g., GitHub)
- Key name (usually an env var name)
- Secret value (paste/typed)
- Optional notes/tags

### 2.2 Bulk import (text)

Accept pasted text in one of these forms:

1) dotenv lines

```
GITHUB_TOKEN=...
STRIPE_API_KEY=...
```

2) shell export lines

```
export GITHUB_TOKEN=...
```

3) JSON object (best-effort)

```
{ "GITHUB_TOKEN": "...", "STRIPE_API_KEY": "..." }
```

MVP should treat invalid formats as “unparsed lines” and show them back to the user.

### 2.3 Bulk import (file)

User selects a file to import:

- `.env` / `.env.*` files
- plaintext `.txt` containing dotenv-style lines

Rules:

- Never silently scan the whole disk for secrets.
- Always show a preview list before importing.

## 3) Parsing and normalization

### 3.1 Normalization

- Trim whitespace around keys.
- Strip optional `export ` prefix.
- Support quoted values:
  - `KEY="value"`
  - `KEY='value'`

### 3.2 Key-name validation

- Accept keys matching `\b[A-Z][A-Z0-9_]{2,}\b`.
- Reject keys that contain spaces or `=`.

### 3.3 Value handling

- Treat values as opaque strings.
- Do not expand `${VAR}`.
- Do not attempt to detect secrets inside longer strings.

## 4) Provider mapping

When a key name matches a provider alias, auto-suggest provider.

Example:

- `GITHUB_TOKEN` → provider `github`
- `GH_TOKEN` → provider `github`

If unknown:

- Allow importing as provider `generic` (or “Unassigned”) for MVP, OR require provider selection.

Recommended MVP default:

- Require user to pick a provider or leave as Unassigned; do not guess beyond known aliases.

## 5) Deduplication rules

Uniqueness is per `(profile_id, provider_id, key_name)` (see [`plans/data-model.md`](plans/data-model.md:1)).

When importing a key that already exists:

- Show a per-item decision:
  - Keep existing
  - Replace with imported
  - Skip import

Bulk import should allow:

- Apply-to-all for same conflict type.

## 6) Masking and reveal rules

- Secret value fields are masked by default.
- Reveal is explicit and time-limited.
- In bulk preview, values are never shown by default; only show:
  - key name
  - provider
  - “value present” indicator

## 7) Clipboard policy

### 7.1 Reading

- Never read clipboard continuously.
- Only read clipboard when user clicks “Paste” in a focused input.

### 7.2 Writing (copying secrets)

- When user clicks “Copy secret”, warn and copy.
- Attempt to clear clipboard after a configurable timeout.
- Provide a setting to disable auto-clear.

## 8) Provenance

Purpose: help user audit where keys came from without storing sensitive content.

Store (non-secret) provenance metadata per secret:

- `source_type`: manual | paste | file_import | dotenv_patch | export_bundle_import
- `source_label`: e.g., file path (optional, user-controlled)
- `imported_at`

Never store:

- full raw pasted blob
- any token values in provenance

## 9) Validation integration

After import, offer:

- “Validate now” (Online Mode only)
- “Validate later”

Offline Mode:

- Record status `unknown` until validation.

## 10) Acceptance criteria

- Single and bulk import work without leaking values.
- Users always preview bulk imports and resolve conflicts.
- Clipboard is only accessed on explicit user action.
- Provenance is stored without secret values.
- Provider mapping uses registry aliases and remains conservative.
