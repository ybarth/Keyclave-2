# Provider plugins + GitHub reference spec (MVP)

This document defines the provider plugin contract and specifies **GitHub** as the reference implementation.

Related:

- Scope: [`plans/product-scope.md`](plans/product-scope.md)
- Architecture: [`plans/architecture-module-boundaries.md`](plans/architecture-module-boundaries.md)
- Security: [`plans/security-crypto-2fa.md`](plans/security-crypto-2fa.md)
- Data model: [`plans/data-model.md`](plans/data-model.md)

## 1) Provider plugin goals

Each provider plugin must:

- Define required environment variables and recommended names.
- Provide onboarding guidance that works offline (static playbook) and can be enhanced in Online Mode.
- Provide safe key validation (no paid calls; free/auth endpoints only).
- Provide metadata for Markdown inference (aliases and detection rules).

MVP constraints:

- Built-in providers only.
- GitHub is the first provider.

## 2) Provider plugin contract (conceptual)

Represent each provider with a stable `provider_id`.

### 2.1 Metadata
- `provider_id: str` (e.g., `replicate`)
- `provider_id: str` (e.g., `github`)
- `display_name: str`
- `homepage_url: str`
- `docs_url: str`
- `env_vars: list[EnvVarSpec]`

`EnvVarSpec`:

- `canonical_name: str` (the name KeyClave writes by default)
- `aliases: list[str]` (names KeyClave will recognize/import)
- `value_hint: str` (masked UI hint)
- `required: bool`

### 2.2 Requirements inference hooks
- `detect_in_markdown(text: str) -> DetectionResult`
  - Returns whether provider is mentioned, with confidence and citations.
- `extract_env_vars(text: str) -> list[str]`
  - Extract explicit env var names from docs (e.g., `REPLICATE_API_TOKEN`).

### 2.3 Validation
- `validate(secret_value: str, mode: ValidationMode) -> ValidationResult`
  - Must use only safe, non-billed endpoints.
  - Must support Offline Mode by returning `unknown` without network.

`ValidationResult`:

- `status: valid | invalid | unknown | error`
- `checked_at`
- `error_code` (optional)
- `error_message_redacted` (optional)

### 2.4 Onboarding playbook
- `onboarding_steps() -> list[OnboardingStep]`

`OnboardingStep`:

- `id: str`
- `title: str`
- `instructions_markdown: str`
- `links: list[str]`
- `can_use_embedded_browser: bool`
- `requires_user_confirmation: bool` (always true for actions)

## 3) Replicate provider spec
## 3) GitHub provider spec

### 3.1 Provider identity
- `provider_id`: `github`
- `display_name`: `GitHub`
- `homepage_url`: `https://github.com`
- `docs_url`: `https://docs.github.com`

### 3.2 Environment variables

Decision (MVP): support common GitHub token env var names, write a canonical name by default.

- Canonical env var to write: `GITHUB_TOKEN`
- Aliases to recognize/import:
  - `GITHUB_TOKEN`
  - `GH_TOKEN`

Rules:

- When importing from existing `.env`, accept either name.
- When generating/patching `.env`, write `GITHUB_TOKEN` unless user overrides.
- When both exist in a target `.env`, warn user and require a choice for which to keep active.

### 3.3 Validation (safe endpoints only)

Decision (approved): validation must avoid side effects and usage charges.

Validation procedure:

1) If Offline Mode: return `unknown`.
2) In Online Mode:
   - Perform a single authenticated request to a GitHub endpoint that:
     - verifies token validity
     - is documented as a standard auth introspection call
     - has minimal side effects
   - Recommended endpoint: `GET https://api.github.com/user`
   - Interpret responses:
     - 200 -> `valid`
     - 401/403 -> `invalid`
     - 429 -> `error` with `rate_limited`
     - other 5xx -> `error` with `provider_unavailable`

Notes:

- Store only redacted errors.

### 3.4 Restrictions probing (MVP)

Decision (approved): MVP only tracks:

- `valid/invalid/unknown/error`
- `last_verified_at`

No quota/limit extraction in MVP.

### 3.5 Onboarding playbook (full onboarding)

Decision (approved): guide full onboarding (account + personal access token).

Offline playbook steps (example skeleton):

1) Ensure you have a GitHub account
   - Link: `https://github.com`
2) Navigate to token creation
   - Link: `https://github.com/settings/tokens`
3) Create a new token (PAT or fine-grained PAT)
4) Copy token into KeyClave
   - Use paste/import field
   - No background clipboard reading
5) Validate token

Online assistant behavior:

- Default uses embedded browser.
- Steps are presented as proposals; user confirms completion.
- KeyClave must not auto-enter passwords or the token into web forms.

## 4) Implementation notes

### Built-in provider registry

- Maintain a registry mapping `provider_id -> plugin`.
- Ensure provider ids are stable for DB references.

### Provider expansion

- Future providers add:
  - env var specs
  - markdown detection aliases
  - safe validators
  - onboarding playbooks

## 5) Acceptance criteria (provider layer)

- Provider id stable and stored in DB.
- GitHub `.env` generation uses `GITHUB_TOKEN` by default.
- Validation never uses paid endpoints.
- Offline Mode never calls network.
- Onboarding is human-in-the-loop with explicit confirmations.
