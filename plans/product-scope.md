# KeyClave product scope and non-goals

## One sentence
KeyClave is a cross-platform desktop application that stores and manages API keys safely, can infer required keys from project documentation, can generate or patch dotenv files in project folders, and can optionally guide users through acquiring missing API access via a human-in-the-loop online assistant.

## Target users
- Solo developers and small teams *on a single device* who need a local vault and reliable `.env` workflows.
- Users who want a guided checklist for which APIs a project needs, based on Markdown design docs.

## Platforms
- Windows, macOS, Linux.

## Core product principles
- **Local-first by default**: secrets are stored locally in an encrypted vault.
- **Human-in-the-loop for web actions**: the assistant proposes steps; the user performs/approves them.
- **No raw payment card storage**: the app does not store PAN/CVV or any raw credit-card details.

## Modes

### Offline Mode (default)
Offline Mode performs all operations without network access:

- Store, organize, and retrieve API keys locally.
- Import/export encrypted key bundles.
- Scan local projects and Markdown docs.
- Generate and patch dotenv files.
 - Provide setup guidance as static checklists and provider playbooks.

### Online Mode (explicitly enabled)
Online Mode enables network features for:

- Key validation checks (provider test calls).
- Human-in-the-loop guided browsing for provider onboarding.

Online Mode includes embedded browsing and provider validation.

KeyClave must not use cloud-hosted LLMs in any mode. If LLM assistance is enabled, it must run locally per [`plans/local-llm-inference.md`](plans/local-llm-inference.md:1).

In all cases, KeyClave must never transmit stored secrets (API keys), raw card details, or clipboard contents.

## Functional scope (MVP-level)

### 1) Vault + profiles
- Multiple **local profiles** on the same device.
- Sign in/out between profiles.
- Each profile has its own encrypted vault data.
- Passphrase-only vault is the default; an OS credential-store option may be offered.
- Optional per-profile Google Authenticator TOTP 2FA for sensitive actions (e.g., export).

### 2) API key lifecycle
- Add/edit/delete keys.
- Tag keys by provider, project, environment (dev/stage/prod), and notes.
- Bulk import (clipboard/paste and file-based), with deduplication and masking.

### 3) Project scanning + Markdown understanding
- User selects a project folder (or allows broader scans with explicit opt-in).
- Read Markdown files describing project designs.
- Extract candidate required APIs/providers and map them to provider definitions.
- Output a “required keys” checklist with confidence and citations to doc locations.

### 4) dotenv file generation and patching
- Generate dotenv files (e.g., `.env`) into chosen project folders.
- Safely patch existing dotenv files:
  - deterministic rewrite rules
  - backups
  - preview diff
  - avoid clobbering unknown keys

### 5) Provider plugins (GitHub first)
Provider definitions include:

- Which env vars are expected.
- Setup guide playbooks.
- Key validation checks (safe, rate-limited).
- Restriction probing where feasible (quota/scope/region) via documented APIs.

MVP reference provider: **GitHub** (non-LLM service) for key naming, validation flow, and onboarding guide.

### 6) Human-in-the-loop online assistant (guided onboarding)
When a required provider is missing keys:

- Present a checklist derived from provider playbooks.
- Offer embedded browsing (default) with an external browser fallback.
- The assistant may highlight UI elements and propose steps, but execution requires user confirmation.

 Boundaries:

 - The app must not auto-enter passwords or stored secrets into web forms without explicit user action.
 - The app must not attempt to circumvent provider security controls.

LLM assistance (if enabled) must run locally and must not require network access.

### 7) Encrypted export/import bundles
- Export an encrypted bundle of selected keys for another user.
- Import bundles into a profile.
- Support password-encrypted bundles; optionally support recipient public-key encryption.

### 8) Advanced interoperability (optional)
- Optional integration points for external tools such as SOPS for advanced users.
- Not required for core workflows; must be isolated behind explicit opt-in and clear UX.

## Explicit non-goals (at least for MVP)

### No multi-device sync
- No cloud sync of secrets across devices.
- No shared team vault service.

### No “fully autonomous purchasing”
- KeyClave does not automatically purchase APIs.
- KeyClave does not store raw credit card details.
- If a payment provider is used, it must be tokenized and externalized (PCI-compliant provider) and primarily for *guidance/status*, not for executing purchases.

### No guarantee of universal key validation
- Some providers do not allow safe validation without side effects.
- MVP will validate where a safe test call exists; otherwise it will provide best-effort checks and clear messaging.

### No deep IDE integration in MVP
- No editor plugins required.
- File-based `.env` workflows are the source of truth.

## Data handling boundaries
- Secrets remain in the local encrypted vault.
- Any logs must be redacted and must not contain secrets.
- Online Mode must be opt-in per profile (or per session) and clearly indicated.

## Primary UX journeys (high level)
1) First run → create profile → set passphrase → (optional) enable TOTP.
2) Import keys (single/bulk) → validate supported providers.
3) Select project folder → scan Markdown designs → see required keys list.
4) Generate or patch dotenv files → preview diff → apply.
5) Missing provider keys → open guided onboarding → user completes steps.
6) Export encrypted bundle → recipient imports into their profile.

## Notes / related plan docs
- Reuse policy: [`plans/reuse-strategy.md`](plans/reuse-strategy.md:1)
