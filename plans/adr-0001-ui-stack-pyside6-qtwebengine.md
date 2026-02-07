# ADR-0001: UI stack selection (PySide6 + QtWebEngine)

## Status
Accepted.

## Context
KeyClave is a cross-platform desktop application with:

- Multi-profile local encrypted vault
- Local project scanning + Markdown ingestion
- Dotenv file generation and safe patch/merge flows
- Optional Online Mode with **human-in-the-loop** guided browsing
- Strong emphasis on security boundaries (no raw card storage; no secret exfil)

We need a UI stack that:

- Works well on Windows, macOS, Linux
- Supports an embedded browser for Online Mode guidance (default) with external browser fallback
- Is maintainable with Python-first implementation
- Supports rich UI theming (red/gold primary, purple accents, silver edge accents)
- Has a packaging story for standalone installers and auto-update

## Decision
Use **Python + Qt via PySide6** as the desktop UI framework, and use **QtWebEngine** for embedded browsing.

## Options considered

### Option A: PySide6 (Qt) + QtWebEngine (chosen)
Pros:

- Mature cross-platform UI toolkit with strong widget set.
- Good Python bindings, documentation, and community.
- QtWebEngine provides an embedded Chromium-based browser for human-in-the-loop flows.
- Theming is achievable via Qt stylesheets and custom painting.

Cons / risks:

- QtWebEngine increases binary size.
- Sandboxing policies and embedded browser security require careful configuration.
- Licensing: Qt is LGPL/commercial; PySide6 is LGPL. We must respect dynamic linking requirements.

### Option B: PySide6 (Qt) without embedded browser (external browser only)
Pros:

- Smaller app size; simpler security surface.
- Fewer embedded-browser patch risks.

Cons:

- Breaks a key requirement: embedded browser default for guided onboarding.
- Less cohesive user experience.

### Option C: Tauri shell + local Python service
Pros:

- Modern web UI with small footprint; strong OS integration.
- Webview-based embedded UI.

Cons:

- Split architecture (Rust + Python) increases complexity.
- Embedded browsing for agentic flows still tricky; webview limitations vary by OS.
- More moving parts for secure secret boundaries.

### Option D: Electron + Python backend
Pros:

- Mature ecosystem; easy rich UI.

Cons:

- Larger footprint and higher resource usage.
- More complex security posture (Node/Electron attack surface).
- Packaging + auto-update heavier.

### Option E: Tkinter
Pros:

- In stdlib; simplest dependency story.

Cons:

- UI polish and theming limitations.
- Embedded browser support is weak.

## Key constraints and guardrails

### Embedded browser security
- Online Mode must be explicit and clearly indicated.
- Never auto-fill stored secrets into web forms.
- Use a dedicated “browser session” container with:
  - restricted APIs
  - clear user confirmation gates
  - minimal persistent storage (or explicit opt-in for cookies)
- Provide external browser fallback for providers where embedded login is brittle.

### Packaging and updates
- Target standalone installers (Windows/macOS/Linux).
- Use a packaging toolchain compatible with PySide6/QtWebEngine.
- Auto-update must be signed and should not expose secrets during update.

### Licensing compliance
- Ensure compliance with LGPL requirements for Qt/PySide6.
- Keep third-party reuse policy aligned with [`plans/reuse-strategy.md`](plans/reuse-strategy.md:1).

## Consequences

### Positive
- Single-language implementation (Python) with mature GUI.
- Embedded browsing supports the Online Assistant requirement.
- Good path to a cohesive UX.

### Negative
- Larger build artifacts and potentially more frequent security updates related to embedded Chromium.
- More engineering effort needed for safe webview boundaries.

## Packaging toolchain (decided)

**Decision:** Use **PyInstaller** as the primary packaging tool for MVP.

Rationale:

- Mature and widely used for PySide6/Qt applications.
- Supports Windows, macOS, and Linux.
- Handles QtWebEngine bundling (with known configuration steps).
- Good community documentation for Qt-specific packaging issues.

Alternatives considered:

- **Briefcase** (BeeWare): promising but less mature for QtWebEngine bundling.
- **Nuitka**: good performance but more complex build configuration.
- **cx_Freeze**: viable but smaller community for Qt apps.

Notes:

- PyInstaller spec files should be version-controlled.
- QtWebEngine requires specific data files and locales to be included; test packaging on all three OSes early.

## Auto-update mechanism (decided)

**Decision:** Use a **custom update feed** with signed manifests for MVP.

Design:

- Publish a JSON manifest at a stable HTTPS URL containing:
  - latest version number
  - per-platform download URLs
  - SHA-256 checksums
  - minimum required version (for forced updates if critical security fix)
- App checks the manifest on startup (if Online Mode is enabled) or on explicit user action.
- App downloads the installer and verifies checksum before prompting user to install.
- The update mechanism must not read vault contents or transmit any user data.

Platform-specific:

- macOS: use Sparkle (if feasible with PySide6) or manual download + DMG.
- Windows: download installer + prompt user to run.
- Linux: manual download; consider AppImage for self-contained updates.

Post-MVP: evaluate integrating Sparkle/WinSparkle for a more native experience.

## QtWebEngine security update policy

- Track PySide6 releases and their bundled Chromium version.
- When a Chromium CVE is published that affects QtWebEngine, evaluate severity:
  - Critical/High: prioritize PySide6 update or recommend external browser fallback.
  - Medium/Low: include in next scheduled release.
- Document the bundled Chromium version in release notes.
- Recommend external browser fallback as the default for security-sensitive provider logins.

## Follow-ups (resolved)
- ~~Define the embedded browsing interaction model and security policy.~~ → See [`plans/online-assistant-ux.md`](plans/online-assistant-ux.md:157).
- ~~Confirm packaging tooling and update mechanism compatibility.~~ → Decided above.
- Document external browser fallback flows per provider (per-provider implementation detail).
