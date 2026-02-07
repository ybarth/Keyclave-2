# Encrypted export/import bundles (MVP)

This spec defines the format and UX for exporting encrypted key bundles to another user and importing them safely.

Decisions confirmed:

- Container: single binary file with header + version + encrypted payload.
- Password bundles: required in MVP.
- KDF: Argon2id with the same defaults as the vault (memory 128 MiB, time 4, parallelism 1) with its own per-bundle salt.
- Public-key recipient encryption: defer to v2.
- Bundle contents: minimal (secrets + provider_id + key_name only).
- Expiry: optional expiry timestamp in metadata; enforced by importer.
- Import conflicts: prompt per key.
- File extension: `.kcbundle`.

Related:

- Security/crypto: [`plans/security-crypto-2fa.md`](plans/security-crypto-2fa.md:1)
- Data model: [`plans/data-model.md`](plans/data-model.md:1)
- Import flows: [`plans/key-import-flows.md`](plans/key-import-flows.md:1)

## 1) Goals

- Allow sharing selected secrets offline.
- Provide strong confidentiality and tamper detection.
- Avoid metadata over-sharing.
- Provide safe import with user review and conflict resolution.

## 2) Non-goals (MVP)

- Recipient public-key encryption (planned v2).
- Multi-device sync.
- Automatic revocation.

## 3) Bundle container format

### 3.1 File extension

- Use `.kcbundle`.

### 3.2 High-level structure

Binary file structure:

- `Magic` bytes: `KCB1` (example)
- `Version`: uint16
- `HeaderLength`: uint32
- `Header` (TLV or compact JSON-UTF8) containing non-secret metadata
- `CiphertextLength`: uint32/uint64
- `Ciphertext`

Header must not contain secrets.

### 3.3 Header fields (non-secret)

- `bundle_id` (UUID)
- `created_at`
- `expires_at` (optional)
- `kdf_alg` = `argon2id`
- `kdf_params` (memory/time/parallelism)
- `kdf_salt` (bytes)
- `aead_alg` (for payload) (default AES-256-GCM)
- `nonce` (bytes)
- `payload_type` (e.g., `secrets_v1`)

## 4) Cryptography

### 4.1 Password-encrypted bundles (required)

Inputs:

- `bundle_password` (user-provided)
- `kdf_salt` (random per bundle)
- `kdf_params` (Argon2id defaults)

Derivation:

- `BundleKey = Argon2id(bundle_password, kdf_salt, params)`

Encryption:

- Use AEAD (default AES-256-GCM) to encrypt payload.
- Use header as AEAD AAD so tampering is detected.

### 4.2 Integrity

- Integrity is provided by AEAD authentication tag.
- Importer must verify before any decrypt output is acted upon.

## 5) Payload contents (minimal)

Payload serialization format (decided): **JSON-UTF8** within ciphertext.

Rationale: JSON is the simplest to implement, debug, and validate. The payload is small (selected secrets only) so compactness is not critical. The entire payload is encrypted, so JSON readability is only relevant during development/testing.

Payload is a versioned JSON structure:

- `secrets: list[SecretItem]`

`SecretItem`:

- `provider_id`
- `key_name`
- `secret_value` (plaintext inside payload; encrypted by bundle AEAD)

Explicitly excluded in MVP:

- notes
- tags
- project paths

Rationale:

- Reduce accidental metadata leakage.

## 6) Export UX

### 6.1 Selection

- User selects secrets to export.
- UI shows only provider + key_name; values remain masked.

### 6.2 Password requirements

- Require user to enter and confirm bundle password.
- Encourage strong password; optionally show strength indicator.

### 6.3 Expiry

- Optional expiry timestamp.
- UI makes it clear expiry is enforced by importer, not by remote revocation.

### 6.4 Output

- Save file dialog with default name:
  - `keyclave-export-YYYYMMDD.kcbundle`

## 7) Import UX

### 7.1 Open bundle

- User selects `.kcbundle` file.
- App reads header and shows:
  - created_at
  - expires_at (if any)
  - number of secrets

### 7.2 Expiry enforcement

- If `expires_at` is present and in the past:
  - block import
  - explain why

### 7.3 Decrypt

- Prompt for password.
- Decrypt and parse payload.

### 7.4 Review + conflicts

- Show list of secrets to be imported (provider + key_name).
- For each conflict where `(provider_id, key_name)` already exists:
  - prompt per key: keep existing / replace / skip

### 7.5 Post-import

- Mark validation status as `unknown` initially.
- Offer user-initiated validation (Online Mode only).

## 8) Logging and privacy

- Never log secret values.
- Audit event should record export/import occurred (counts only).

## 9) Acceptance criteria

- Bundles are confidential and tamper-evident.
- Import refuses expired bundles.
- Import conflict resolution is per key.
- No additional metadata is leaked in header or payload beyond provider_id and key_name.
