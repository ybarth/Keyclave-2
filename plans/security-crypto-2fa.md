# KeyClave security, cryptography, and 2FA specification

This document specifies the security model for KeyClave and the cryptographic and authentication mechanisms required to implement it.

Related:

- Scope: [`plans/product-scope.md`](plans/product-scope.md)
- Reuse rules: [`plans/reuse-strategy.md`](plans/reuse-strategy.md)
- UI stack: [`plans/adr-0001-ui-stack-pyside6-qtwebengine.md`](plans/adr-0001-ui-stack-pyside6-qtwebengine.md)
- Architecture boundaries: [`plans/architecture-module-boundaries.md`](plans/architecture-module-boundaries.md)

## 1) Threat model (baseline)

### Assets
- API keys and tokens (primary)
- Encrypted export bundles
- Vault metadata (providers used, project folder paths, key names)
- Online assistant browsing context (URLs, page text) when enabled
- TOTP shared secrets (for Google Authenticator)

### Adversaries
- Local malware / attacker with user-level access
- Attacker with filesystem read access (stolen laptop, backups)
- Shoulder-surfing / screen capture
- Supply-chain attacker (malicious update)
- Network attacker (MITM) during Online Mode validation

### Security goals
- Secrets are encrypted at rest and never logged.
- Passphrase compromise should be required to decrypt vault when using passphrase-only default.
- Online Mode must never exfiltrate secrets to cloud services.
- Export bundles remain confidential and tamper-evident.
- UX prevents accidental leakage (masking, clipboard rules, short reveal timers).

### Non-goals
- Defending against a fully compromised OS with kernel/root access.
- Perfect secure deletion guarantees on modern filesystems/SSDs.

## 2) Data classification and redaction

### Sensitive
- Secret values (API keys, tokens)
- TOTP secrets
- Export bundle contents
- Any payment tokens if ever used (tokenized only)

### Potentially sensitive
- Provider list per profile
- Project paths
- Error details returned from providers

### Redaction requirements
- Audit log: store event types and timestamps; never store secret values.
- Error dialogs: redact tokens in messages.
- Crash reports: opt-in only; must strip secrets.

## 3) Vault cryptography (at rest)

### Overview
Each profile has its own encrypted vault.

Terminology:

- `ProfileVaultKey` (PVK): symmetric key used to encrypt the vault database.
- `Passphrase`: user-entered secret.
- `KDFSalt`: random per-profile salt.

### Default: passphrase-only vault

#### KDF
- Use a memory-hard KDF suitable for desktop environments.
- Preferred: Argon2id.
- Store KDF parameters per profile (so parameters can be upgraded over time).

Default Argon2id parameters (desktop strong baseline):

- memory: 128 MiB
- time: 4
- parallelism: 1

Derived key:

- `KEK = KDF(Passphrase, KDFSalt, params)`

Key wrapping:

- Generate random `PVK` on profile creation.
- Wrap PVK with KEK using an AEAD scheme:
  - `WrappedPVK = AEAD_Encrypt(KEK, PVK, aad=profile_id)`
- Store `WrappedPVK` + `KDFSalt` + KDF params in profile metadata.

#### Vault storage encryption
- Encrypt vault contents with `PVK`.
- Use AEAD.
- Default AEAD for record encryption: AES-256-GCM.
- Nonce strategy: generate a random 96-bit (12-byte) nonce per encryption operation using a CSPRNG. At the expected scale (hundreds to low thousands of records per profile), random nonce collision probability is negligible. Store the nonce alongside each ciphertext.
- Each record encryption must use a unique nonce; never reuse a nonce with the same key.

#### Unlock flow
1) User provides passphrase.
2) Derive KEK via KDF.
3) Decrypt `WrappedPVK` to recover PVK.
4) Keep PVK in memory only; wipe buffers on lock.

### Optional: OS credential store backed
If enabled by user:

- Store a wrapped PVK (or a key-encryption secret) in OS keychain/credential manager.
- Optionally still require passphrase gate.

Rules:

- OS store is an option, not default.
- Must work across macOS Keychain, Windows Credential Manager, and Linux Secret Service where available.

### Key rotation
- Support PVK rotation by re-encrypting vault records with a new PVK.
- Support KDF parameter upgrades (e.g., stronger settings) by re-wrapping PVK.

#### Key rotation mechanics

1) User initiates rotation from profile settings (requires current passphrase + TOTP if enabled).
2) Generate a new PVK.
3) Re-encrypt all vault records in a transaction:
   - Begin SQLite transaction.
   - For each encrypted record: decrypt with old PVK, re-encrypt with new PVK.
   - Update `profile_vault_meta.wrapped_pvk` and increment `rotation_version`.
   - Commit transaction.
4) If rotation fails mid-way, the transaction rolls back and the old PVK remains valid.
5) Show a progress indicator during rotation (may take seconds for large vaults).
6) On success, wipe old PVK from memory.

#### Argon2id parameter fallback for constrained environments

The default Argon2id parameters (128 MiB memory, time 4, parallelism 1) are strong but may cause issues on machines with limited RAM.

Fallback policy:

- If KDF derivation fails due to memory allocation, retry with reduced parameters: memory 64 MiB, time 6, parallelism 1.
- If that also fails, present an error with guidance (minimum 4 GB system RAM recommended).
- Reduced parameters are stored per-profile so the profile remains unlockable on the same machine.
- When the user moves to a more capable machine, offer to upgrade KDF parameters.

## 4) In-memory handling and UX leakage controls

- Mask secrets by default.
- Reveal action requires explicit click and auto-hides after a short timeout.
- Clipboard copy should:
  - warn user
  - auto-clear clipboard after configurable delay where feasible
- Prevent secrets from being included in screenshots where possible (best-effort; cannot guarantee).

## 5) 2FA (Google Authenticator TOTP)

### Scope
TOTP is optional per profile.

Recommended enforcement points:

- Export encrypted bundle (default enforcement when TOTP is enabled)
- Reveal secret value (optional setting)
- Enable local LLM assistance (optional setting)

### Enrollment
- Generate random TOTP secret per profile.
- Display as QR code + backup codes (optional) or allow manual entry.
- Confirm enrollment with first valid code.

### Verification
- Use standard TOTP (RFC 6238), 30s step, 6 digits.
- Allow small clock skew window.

### Recovery/lockout
- If user loses authenticator, provide recovery path:
  - recovery codes (if enabled)
  - or profile reset that destroys access to secrets unless vault can be unlocked without TOTP.

Important: do not weaken security by offering "email reset" unless a secure identity system exists (out of scope for local app).

#### Recovery code specification

- Generate **8 recovery codes** during TOTP enrollment.
- Each code: 8 alphanumeric characters, grouped as `XXXX-XXXX` for readability.
- Codes are **one-time use**: each code is consumed on successful use and cannot be reused.
- Store recovery codes encrypted with PVK in `profile_settings` (as an encrypted JSON array).
- Display codes once during enrollment; offer a "Download as text file" option.
- Warn user that losing both authenticator and recovery codes means TOTP-gated actions (e.g., export) will be blocked. The passphrase alone can still unlock the vault, but TOTP enforcement cannot be bypassed without a recovery code or profile TOTP reset (which requires current passphrase).

## 6) Online Mode security boundaries

### Online Mode gating
- Online Mode is disabled by default.
- Requires explicit user enable per profile or per session.

### Local LLM assistance toggle
If the user enables local LLM assistance:

- All inference must run locally per [`plans/local-llm-inference.md`](plans/local-llm-inference.md:1).
- Disallowed inputs include:
  - API keys
  - email addresses, payment info
  - clipboard contents
  - passwords

### Domain allowlisting
- Provider validators should use an allowlist of base domains.
- Reject validation calls to unknown domains.

### Rate limiting
- Apply per-provider rate limits to avoid lockouts and unintended charges.

## 7) Embedded browser (QtWebEngine) guardrails

- Use a separate browser profile/container for Online Mode.
- Cookie persistence default: off or session-only (configurable).
- No programmatic form autofill with stored secrets.
- Provide clear “You are in Online Mode” banner.

## 8) Encrypted export bundles

### Goals
- Confidentiality: bundle reveals nothing without credentials.
- Integrity: detect tampering.
- Usability: bundle can be shared offline.

### Modes

#### A) Password-encrypted bundle (required)
- Derive bundle key from user-provided password using a memory-hard KDF.
- Encrypt payload using AEAD.
- Include manifest metadata and versioning.

#### B) Recipient public-key encryption (optional)
- Encrypt a random bundle key to recipient public key.
- Use AEAD to encrypt payload.

### Bundle contents
- Selected secrets + necessary metadata (provider id, env var name, notes optional).
- Optional expiry.
- Never include vault passphrase or PVK.

### Import
- Validate integrity before decrypt.
- Prompt user to map env var names if needed.

## 9) Audit logging

- Local-only.
- Redacted.
- Events:
  - unlock success/failure
  - Online Mode toggles
  - export/import
  - dotenv write operations

## 10) Secure update and build pipeline (baseline requirements)

- Updates must be signed.
- Update mechanism must not read vault contents.
- Dependency pinning and SBOM generation recommended.

## 11) Open questions to resolve before implementation

Locked defaults (approved):

1) KDF: Argon2id with memory 128 MiB, time 4, parallelism 1 (stored per-profile; upgradable).
2) Record AEAD: AES-256-GCM with versioned record format.
3) TOTP: when enabled, require for export by default.
4) Local LLM assistance: default OFF for all new profiles.
