# Online Assistant UX + embedded browser policy (MVP)

This spec defines the UX and security policy for KeyClave’s human-in-the-loop online assistant, including embedded browsing via QtWebEngine, confirmation gates, credential entry rules, and optional **local** LLM assistance.

Related:

- Scope and non-goals: [`plans/product-scope.md`](plans/product-scope.md:1)
- Security boundaries: [`plans/security-crypto-2fa.md`](plans/security-crypto-2fa.md:1)
- UI stack: [`plans/adr-0001-ui-stack-pyside6-qtwebengine.md`](plans/adr-0001-ui-stack-pyside6-qtwebengine.md:1)
- Provider playbooks: [`plans/provider-plugins-and-github.md`](plans/provider-plugins-and-github.md:1)

## 1) Goals

- Help users obtain missing API access and tokens safely.
- Keep all actions **human-confirmed**.
- Provide a strong Offline Mode experience (static playbooks + checklists).
- In Online Mode, provide embedded browsing (default) with external browser fallback.

## 2) Modes and default settings

### Offline Mode
- No network calls.
- Show provider onboarding playbooks (steps + links).
- Allow marking steps complete.

### Online Mode (explicit enable)

Online Mode must be disabled by default and explicitly enabled per profile/session.

Online Mode is about embedded browsing and provider validation. KeyClave must not use cloud-hosted LLMs.

Optional local LLM assistance:

- If a local model is installed and the user enables it, the assistant may use it to suggest the next step.
- Local LLM execution must follow [`plans/local-llm-inference.md`](plans/local-llm-inference.md:1).

## 3) UX: the “Guided Setup Session”

### Session model

 The assistant runs setup in a bounded session:

 - `provider_id`
 - `project_id` (optional)
 - `session_mode`: Offline | Online
 - `local_llm_assist`: on/off (only meaningful if a local model is installed)
 - `step_state`: per-step status + notes

### Primary UI components

 1) **Provider Setup Overview**
   - Missing keys list
   - What KeyClave will and will not do
    - Mode indicator (Offline/Online)
    - Local LLM assist toggle (only if a local model is installed)

2) **Step List (Playbook)**
   - numbered steps
   - status: not started / in progress / done / blocked
   - per-step “Open link” and “Mark done” actions

3) **Embedded Browser Panel (Online Mode)**
   - visible URL bar
   - mode banner: Online Mode active
   - optional “Open in system browser” button

4) **Action Proposal Drawer**
   - what the assistant suggests next
   - why it suggests it
   - required user action
   - explicit confirm/cancel

## 4) Confirmation gates (must-have)

Every action that could change state, navigate, or write data must pass through a confirmation gate.

### 4.1 Navigation

- Assistant may suggest navigation targets.
- User must click “Go” (or equivalent) to navigate.
- Allowlist: provider domains only (configured per provider). Warn on external domains.

### 4.2 Copy/paste and secret entry

- KeyClave must not auto-fill tokens into web forms.
- The user manually copies tokens from provider pages and pastes into KeyClave’s import field.
- KeyClave must not read clipboard continuously; only read clipboard on explicit “Paste” user action.

### 4.3 Writing to disk

- Generating or patching dotenv files must require:
  - preview diff
  - explicit user confirmation
  - backup creation

## 5) Credential entry rules

### Passwords and identity

- The assistant must not capture or store provider passwords.
- No “password manager” functionality.
- Login is performed by the user in the embedded browser (or external browser).

### API tokens

- Tokens are treated as secrets.
- Tokens may only enter KeyClave via:
  - paste into KeyClave’s secret input
  - manual typing (discouraged but allowed)

Never:

- auto-detect token strings on a page
- scrape tokens from DOM
- send tokens to cloud LLM

## 6) Screenshot/DOM capture policy

### Default (recommended)

- Do not capture screenshots or full DOM by default.
- Local LLM assistance must not require DOM capture.

### If capture is ever enabled (future)

- Must be explicit per session.
- Must show a preview of what will be sent.
- Must redact obvious secret patterns.

MVP: keep capture disabled by default; rely on playbooks, user confirmations, and optional local inference on user-provided text only.

## 7) Local LLM assistance policy (local-only)

Local LLM assistance is optional and OFF by default.

### Allowed inputs

- Provider playbook step context
- User-authored notes for a step
- User-selected non-secret excerpts (explicitly provided by the user)

### Disallowed inputs

- Any secret values (API keys, tokens)
- Clipboard contents
- Passwords
- Full-page DOM dumps

### Required UX

- Before first use, show a clear disclosure:
  - the model runs locally
  - what data may be used as input
  - what is never used as input
  - how to disable

## 8) Embedded browser isolation (QtWebEngine)

### Browser profile

- Use a dedicated browser profile/container for Online Mode.
- Cookie persistence:
  - default: session-only
  - option: persist cookies per profile (explicit opt-in)

### QtWebEngine feature restrictions

The following WebEngine features must be explicitly configured:

- **JavaScript**: enabled (required for modern provider pages).
- **WebRTC**: disabled (no need for real-time communication; reduces fingerprinting surface).
- **Geolocation**: disabled.
- **Notifications**: disabled.
- **File downloads**: blocked by default (see Downloads section below).
- **Clipboard access from page JS**: disabled (pages must not read clipboard).
- **Local storage / IndexedDB**: session-only by default.
- **Plugins / PDF viewer**: disabled.
- **Autoplay media**: disabled.
- **Fullscreen requests**: disabled.

### Downloads

- Block downloads by default.
- If allowed, require user confirmation and save to user-chosen location.

### External browser fallback

Must support opening the same URL in the system browser and continuing via checklist.

## 9) Provider playbooks and step structure

Each provider plugin supplies:

- Offline step list
- Link targets
- Success checks (manual or automated)

Example step types:

- `open_url`
- `create_account`
- `navigate_to_token_page`
- `create_token`
- `paste_token_into_keyclave`
- `validate_token`

For GitHub, see playbook requirements in [`plans/provider-plugins-and-github.md`](plans/provider-plugins-and-github.md:1).

## 10) Acceptance criteria

- Online Mode is explicit and clearly indicated.
- No auto-entry of passwords or secrets.
- Clipboard reads only on explicit user action.
- No cloud-hosted LLM usage exists.
- Local LLM assist (if present) is local-only and default OFF.
- Embedded browser uses session-only cookies by default.
- External browser fallback is available.
