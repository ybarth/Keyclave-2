# KeyClave reuse strategy (third-party reference + selective reuse)

## Purpose
Establish safe, license-compliant reuse rules for building KeyClave as a **local desktop API key vault** (multi-profile, offline-first, optional online assistant).

This project will:

- Use a small number of upstream repositories as **reference implementations** for UX flows, env-var workflows, and operational patterns.
- Prefer **small, well-scoped libraries** (Python packages) over copying application code.
- Allow **small MIT-only snippet reuse** from select upstreams, with strict boundaries (no crypto/business logic copying).

## Approved upstreams (reference repos)

### Infisical
- Upstream: https://github.com/Infisical/infisical
- License: MIT-style with explicit carve-outs noted in the repository LICENSE.
- Allowed use in KeyClave:
  - Primary: **reference only** (architecture ideas, CLI UX, env handling patterns, audit/log concepts).
  - Secondary: **small MIT-only snippets** may be reused if ALL conditions hold:
    - The snippet comes from a clearly MIT-licensed portion of the repo.
    - It is not cryptography, key derivation, token handling, auth, or security-critical enforcement logic.
    - It is reviewed and documented with a source link + commit SHA.

License note (recorded): Infisical is MIT-style with explicit carve-outs in its LICENSE (e.g., restrictions for any enterprise/"ee" portions if present). KeyClave should treat Infisical as reference-first; any snippet reuse must be from clearly MIT-licensed portions only.

### dotenv-vault
- Upstream: https://github.com/dotenv-org/dotenv-vault
- License: MIT.
- Allowed use in KeyClave:
  - Reference for encrypted env-bundle workflows and ergonomics.
  - Inspiration for **KeyClave encrypted export bundles**.
  - We will not adopt dotenv-vault format verbatim unless it clearly matches KeyClave’s threat model.

License note (recorded): dotenv-vault is MIT.

## Explicit non-goals for reuse

- Do not embed a full server-based secrets platform inside KeyClave.
- Do not import upstream crypto designs wholesale.
- Do not vendor-copy large codebases to avoid hidden license/security debt.

## Third-party code policy

### 1) Prefer libraries over copying
Implement core functionality using maintained Python libraries where possible:

- `.env` parsing/writing: prefer `python-dotenv` or equivalent.
- Crypto primitives: `cryptography`.
- OS keychain integration (optional): `keyring` or platform-specific bindings.
- TOTP (Google Authenticator): `pyotp`.

### 2) If we copy any snippet
We must:

- Record it in a reuse log (file path, upstream URL, commit SHA, license, rationale).
- Add a short comment in code pointing to the upstream source.
- Ensure the copied snippet does not process secrets in plaintext outside intended boundaries.

### 3) No “crypto/business logic” copying
Disallowed from any upstream (even permissive):

- Key derivation, encryption formats, vault storage, auth/session enforcement.
- Key validation logic that could change security behavior.
- Anything handling credentials/tokens in a way that could silently weaken protections.

## Optional interoperability: SOPS

KeyClave may offer an **advanced, opt-in** integration path for users who already use SOPS.

Constraints:

- Not required for the core product.
- KeyClave must not assume SOPS exists or that it can access SOPS keys.
- Interop should be implemented as a separate adapter layer with clear user prompts.

## How this affects the implementation plan

1) Create `third_party/` directory and clone approved upstreams for reference.
2) Maintain a `third_party/manifest.yml` listing:
   - upstream URL
   - commit SHA pinned
   - license summary
   - allowed use category: reference-only or limited-snippet
3) Maintain a `third_party/reuse-log.md` if any snippets are actually reused.

## Acceptance checks

- No raw credit-card data is ever stored.
- No upstream crypto is copied.
- Any reused snippets are traced, licensed, and reviewed.
- Offline Mode works fully without network.
