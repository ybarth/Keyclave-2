# External Infrastructure Setup Instructions

This document enumerates every **external dependency** implied by the approved plan set and provides **complete, step-by-step setup instructions** for each.

KeyClave is designed to be **local-first**: the vault, database, and audit logs are stored locally; most functionality works with **no external infrastructure**.

In the revised plan:

- There is **no cloud-hosted LLM** and **no third-party inference API** usage. All LLM inference (if enabled) runs locally per [`plans/local-llm-inference.md`](plans/local-llm-inference.md:1).
- There is **no off-device crash/error reporting in MVP** (see [`plans/telemetry-logging.md`](plans/telemetry-logging.md:1)).

External systems are only needed for **Online Mode** features (e.g., provider validation and guided browsing) and optional **release/update distribution**.

## 0) Quick inventory (what is actually required)

### Required for MVP plan

1) **None for Offline Mode**
   - The MVP must be usable end-to-end offline for vault/import/export/dotenv workflows.

### Required to exercise Online Mode validation in MVP

2) **GitHub account + API token**
   - Purpose: validate a GitHub token in Online Mode and support the reference provider onboarding playbook.
   - References:
     - [`plans/provider-plugins-and-github.md`](plans/provider-plugins-and-github.md:1)
     - [`plans/key-validation.md`](plans/key-validation.md:1)
     - [`plans/product-scope.md`](plans/product-scope.md:29)

### Optional (explicitly opt-in in the plan)

3) **Local model distribution (optional)**
   - Purpose: install a local GGUF model for optional local LLM assistance.
   - Notes:
     - This is not an account or hosted service.
     - If the environment is air-gapped, models must be sideloaded.
   - Reference: [`plans/local-llm-inference.md`](plans/local-llm-inference.md:1).

4) **Release hosting + code signing identities** (only if packaging/updates are implemented)
   - Purpose: distribute signed installers and (optionally) an update feed.
   - References:
     - [`plans/adr-0001-ui-stack-pyside6-qtwebengine.md`](plans/adr-0001-ui-stack-pyside6-qtwebengine.md:97) (packaging + signed updates requirement)
     - [`plans/security-crypto-2fa.md`](plans/security-crypto-2fa.md:222) (secure update/build baseline)
     - [`plans/implementation-backlog.md`](plans/implementation-backlog.md:145) (packaging/updates milestone)

## 1) Conventions and assumptions

If a provider-specific detail is not specified in the plans, this document either:

- **States a provider-agnostic requirement** (preferred), or
- Makes a clearly labeled **assumption** that engineering can later swap.

### Naming assumptions (you may adjust)

- App name: KeyClave.
- Environments: `dev`, `prod`.
- Local runtime configuration is loaded from a local `.env` file during development (implementation detail; consistent with dotenv workflows in [`plans/dotenv-merge.md`](plans/dotenv-merge.md:1)).

### Security baseline for all external integrations

- Never send stored secrets (API keys, vault contents) to any external service (see [`plans/security-crypto-2fa.md`](plans/security-crypto-2fa.md:155)).
- Treat any external credentials (API keys for LLM, crash reporter DSNs, etc.) as **secrets**.
- Prefer per-environment credentials (`DEV` vs `PROD`) and rotate on compromise.

## 2) External dependency: GitHub (required for Online Mode validation)

### 2.1 Purpose

- Provide a first-class provider plugin for GitHub (reference provider).
- Support:
  - Offline onboarding playbook (links + steps)
  - Online validation: one safe authenticated call in Online Mode only

References:

- Env var naming and aliases: [`plans/provider-plugins-and-github.md`](plans/provider-plugins-and-github.md:1)
- Online-only validation rule: [`plans/key-validation.md`](plans/key-validation.md:49)

### 2.2 Prerequisites

1) A GitHub account for each human who needs to generate a token.
2) Permission to create tokens in that GitHub account.

### 2.3 Resources to create

GitHub-side resources:

1) A GitHub account (if not already present).
2) At least one token suitable for API auth.

No other GitHub resources are required by the MVP plans.

### 2.4 Configuration values to obtain

You must obtain a token value from GitHub.

KeyClave will store this token in its **local encrypted vault** (not in GitHub).

### 2.5 Environment variables / secrets

KeyClave's canonical dotenv name for the GitHub token is:

- `GITHUB_TOKEN` (canonical)

It must also recognize the alias:

- `GH_TOKEN` (alias)

Reference: [`plans/provider-plugins-and-github.md`](plans/provider-plugins-and-github.md:1)

#### Recommended local development setup

1) Create or update your local development `.env` file (if your dev setup uses dotenv).
2) Add exactly one of the following (prefer canonical):

```
GITHUB_TOKEN=<your_github_token>
```

If you already have existing projects using the alias, you may instead set:

```
GH_TOKEN=<your_github_token>
```

KeyClave's dotenv patcher must handle the alias conflict rules (see [`plans/dotenv-merge.md`](plans/dotenv-merge.md:110)).

### 2.6 Network and allowlist settings

KeyClave must enforce an allowlist for provider validation domains.

Provider-agnostic requirement:

1) Allowlist the base domains required to call GitHub's safe validation endpoint.
2) Reject validation calls to any other domains.

References:

- Domain allowlist requirement: [`plans/security-crypto-2fa.md`](plans/security-crypto-2fa.md:171)
- Validation allowlist requirement: [`plans/key-validation.md`](plans/key-validation.md:49)

Concrete allowlist (MVP):

- `github.com` (onboarding flows)
- `api.github.com` (validation endpoint)

### 2.7 Auth method and token management

Auth method:

- GitHub token used as an API credential (exact header scheme depends on GitHub docs).

Token generation:

1) Sign in to GitHub.
2) Navigate to token creation.
3) Create a new token.
4) Copy the token once and store it in KeyClave via manual paste.

Reference: onboarding playbook skeleton in [`plans/provider-plugins-and-github.md`](plans/provider-plugins-and-github.md:1).

Rotation:

1) In GitHub, revoke the old token.
2) Create a new token.
3) In KeyClave, update the stored secret value.
4) Run validation.

### 2.8 Sandbox vs production

The plan does not specify a GitHub sandbox environment.

Assumption:

- Use the same GitHub account type as required by GitHub; treat tokens as "production-like" credentials.

### 2.9 Verification steps

1) In KeyClave, ensure Online Mode is explicitly enabled (Online Mode is opt-in; see [`plans/online-assistant-ux.md`](plans/online-assistant-ux.md:26)).
2) Trigger validation via an explicit user action (see [`plans/key-validation.md`](plans/key-validation.md:38)).
3) Confirm KeyClave reports:
   - `valid` for a working token
   - `invalid` for a revoked/incorrect token
   - `unknown` in Offline Mode

### 2.10 Operational notes

- Apply per-provider rate limiting to avoid lockouts (see [`plans/key-validation.md`](plans/key-validation.md:64)).
- Do not log request/response bodies; log only redacted summaries (see [`plans/telemetry-logging.md`](plans/telemetry-logging.md:110)).

### 2.11 Teardown / cleanup

To fully remove GitHub access:

1) Revoke the GitHub token(s) in GitHub.
2) Delete the GitHub secret from KeyClave.
3) Remove any GitHub token from local development `.env` files.

## 3) Local model distribution (optional)

### 3.1 Purpose

KeyClave may optionally install a local GGUF model to enable local LLM assistance.

Reference: [`plans/local-llm-inference.md`](plans/local-llm-inference.md:1).

### 3.2 Prerequisites

1) Sufficient local disk space for the chosen GGUF model.
2) Hardware that meets the chosen quantization tier.

### 3.3 Resources to create

None (no accounts, no credentials).

### 3.4 Configuration values to obtain

MVP uses a curated model catalog with checksums.

If sideloading, obtain:

1) The GGUF file.
2) The expected SHA-256 checksum.

### 3.5 Environment variables / secrets

None (no cloud credentials).

### 3.6 Network settings and policy controls

If the model is downloaded from the internet:

1) Downloads must be explicit user action.
2) Verify checksums before enabling the model.

If the environment is air-gapped:

1) Sideload the GGUF file into the KeyClave model directory.
2) Verify checksum locally.

### 3.7 Model updates (no key rotation)

1) Download a newer GGUF version from the catalog.
2) Verify checksum.
3) Keep the older model for rollback.

### 3.8 Dev vs prod

Recommended:

- Use the same model family across dev/prod to reduce behavior drift.
- Allow dev to use smaller quantization for faster iteration.

### 3.9 Verification steps

1) Install a model via the catalog (or sideload).
2) Run the built-in local inference smoke test.
3) Confirm that inference works with network disabled.

### 3.10 Operational notes

- Treat model files as third-party artifacts; pin checksums.
- Log only high-level events (local_llm_assist enabled, provider id, step id) per [`plans/telemetry-logging.md`](plans/telemetry-logging.md:1).

### 3.11 Teardown / cleanup

1) Disable local LLM assistance in KeyClave.
2) Delete the local model files.

## 4) Off-device crash/error reporting (post-MVP, not in MVP)

MVP constraint (locked): KeyClave has no off-device crash/error reporting.

Reference: [`plans/telemetry-logging.md`](plans/telemetry-logging.md:86).

### 4.1 Prerequisites

1) An account with a crash reporting provider.
2) Ability to create a project/application and obtain an ingestion credential (DSN, API key, or equivalent).
3) Security review approval confirming the payload redaction rules are implemented.

### 4.2 Resources to create

Provider-agnostic:

1) Create a crash reporting project named `keyclave`.
2) Create separate projects for `dev` and `prod` (recommended) or use environment tags.
3) Obtain the ingestion credential (e.g., DSN).

### 4.3 Configuration values to obtain

1) Ingestion credential (DSN or API key).
2) Environment name mapping (`dev`, `prod`).
3) Release/version identifier support (so crash reports group by build).

### 4.4 Environment variables / secrets

The plans do not specify env var names.

Assumption (recommended defaults):

- `KEYCLAVE_CRASH_REPORTING_ENABLED_DEFAULT=false`
- `KEYCLAVE_CRASH_REPORTING_DSN` (or provider-equivalent)
- `KEYCLAVE_ENV` (example values: `dev`, `prod`)

### 4.5 Network settings

1) Ensure outbound HTTPS is permitted to the crash reporting ingestion endpoint.
2) If you implement egress allowlisting, allowlist only the provider ingestion domains.

### 4.6 Privacy, redaction, and consent controls

Must satisfy all of the following before enabling in production:

1) Default OFF.
2) Explicit opt-in toggle.
3) Scrub secrets, file paths, URLs/page text, request bodies.

References:

- Default OFF and allowed fields: [`plans/telemetry-logging.md`](plans/telemetry-logging.md:7)
- Must never send secrets or file paths: [`plans/telemetry-logging.md`](plans/telemetry-logging.md:107)
- Redaction rules: [`plans/telemetry-logging.md`](plans/telemetry-logging.md:116)

### 4.7 Sandbox vs production

Recommended:

1) Use a separate `dev` project/DSN.
2) In `dev`, enable crash reporting for engineers by default only in local builds (not user builds).
3) In `prod`, keep default OFF and require user opt-in.

### 4.8 Verification steps

1) In a dev build, trigger a controlled crash.
2) Confirm the crash appears in the provider console.
3) Inspect the payload (locally) and confirm it contains:
   - app version/build id
   - OS version
   - redacted stack trace
4) Confirm it does not contain:
   - any env var values
   - any token-like substrings
   - absolute file paths or usernames

Reference: payload requirements in [`plans/telemetry-logging.md`](plans/telemetry-logging.md:96).

### 4.9 Operational notes

- Set retention policies and access controls in the provider console.
- Restrict console access to the minimum set of engineers.

### 4.10 Teardown / cleanup

1) Disable crash reporting in the app configuration.
2) Revoke the ingestion credential.
3) Delete the crash reporting project if no longer needed.

## 5) External dependency: Release hosting, code signing, and update distribution (optional)

### 5.1 Purpose

To ship a desktop app safely, the plan calls for signed updates and a secure pipeline baseline.

References:

- Packaging and signed updates: [`plans/adr-0001-ui-stack-pyside6-qtwebengine.md`](plans/adr-0001-ui-stack-pyside6-qtwebengine.md:97)
- Secure update/build baseline: [`plans/security-crypto-2fa.md`](plans/security-crypto-2fa.md:222)
- Implementation milestone: [`plans/implementation-backlog.md`](plans/implementation-backlog.md:145)

### 5.2 Prerequisites

Provider-agnostic prerequisites:

1) A repository hosting account for distributing releases (or an internal artifact system).
2) Ability to store signing keys/certificates securely.

Platform prerequisites:

1) macOS: Apple Developer Program membership for signing and notarization.
2) Windows: a code signing certificate (organizational or individual, depending on distribution needs).
3) Linux: distribution-specific signing (optional), depending on packaging format.

### 5.3 Resources to create

#### 5.3.1 Release hosting

Assumption (recommended default): use GitHub Releases (or equivalent) as the public artifact host.

Steps (provider-agnostic):

1) Create a release channel structure:
   - `stable`
   - `beta` (optional)
2) Decide how the app finds updates:
   - static URL to a version manifest, or
   - provider-native update feed mechanism

Note: the exact auto-update mechanism is not specified in the plans; treat this as a packaging-stage design decision.

#### 5.3.2 macOS signing and notarization

Steps:

1) Create an Apple Developer team (if not already).
2) Create signing identities for:
   - Application signing
   - Installer/package signing (if applicable)
3) Configure notarization capability.

#### 5.3.3 Windows signing

Steps:

1) Acquire a code signing certificate.
2) Store the signing private key in a secure location (see section 6).
3) Ensure build tooling can sign the produced installer/binary.

### 5.4 Required configuration values

1) Release hosting base URL (where installers/updates are published).
2) Code signing identity identifiers per platform.
3) (If auto-update is implemented) public keys or signatures required to verify update metadata.

### 5.5 Environment variables / secrets

Assumption (recommended defaults for CI):

- `KEYCLAVE_RELEASE_CHANNEL` (example: `stable`)
- `KEYCLAVE_UPDATE_FEED_URL` (if update feed is implemented)

Signing secrets (store in a secret manager, not in `.env` files):

- macOS signing certificate + private key material
- notarization credentials
- Windows signing certificate + private key material

### 5.6 Network and security settings

1) Enforce TLS for any update feed or release download endpoints.
2) Ensure update metadata is signed and verified by the app.
3) Restrict who can publish releases.

### 5.7 Verification steps

1) Build a signed installer for each OS.
2) Verify the OS reports the signature as valid.
3) If auto-update is implemented:
   - publish a test update
   - confirm the app detects it
   - confirm signature verification passes
   - confirm rollback behavior (if supported)

### 5.8 Operational notes

- Track signing certificate expiration and renew early.
- Keep a clear key rotation plan for signing keys.

### 5.9 Teardown / cleanup

1) Revoke signing certificates if compromised.
2) Remove update feeds and release artifacts if sunsetting the product.

## 6) Secrets management for external credentials (recommended)

The plans include third-party references (Infisical, dotenv-vault) as upstream inspiration only; KeyClave itself is not a hosted secrets platform (see [`plans/reuse-strategy.md`](plans/reuse-strategy.md:12)).

Even so, engineering will need to manage:

- Crash reporting DSNs (optional, post-MVP only)
- Code signing keys/certificates (optional but likely required for shipping)

Note: No LLM API keys are required. All LLM inference runs locally per [`plans/local-llm-inference.md`](plans/local-llm-inference.md:1).

Recommended provider-agnostic approach:

1) Use your organization's existing secret manager for CI/CD and release signing.
2) Limit access by role (build/release engineers only).
3) Audit access and rotate on personnel changes.

Assumption (if no org secret manager exists):

- Use GitHub Actions Secrets (or equivalent) for CI secrets, and store signing keys in a dedicated secure vault/HSM where possible.
