# KeyClave UX visual system + brand assets + sonic design (MVP)

This spec defines the **visual**, **brand**, and **sound** direction for KeyClave so implementation can build consistent UI components in Qt.

Related:

- Scope: [`plans/product-scope.md`](plans/product-scope.md)
- Online assistant UX constraints: [`plans/online-assistant-ux.md`](plans/online-assistant-ux.md)

## 1) Brand narrative

KeyClave should feel like a **conclave of keys**:

- A secure meeting place for secrets.
- A sense of ceremony when unlocking, exporting, and validating.
- Visual motifs: keys, wards, keyrings, vault doors, inlays.
- Industrial polish: silver edge accents like beveled metal trim.

## 2) Color system (tokens)

Primary direction required:

- Bright Coca-cola red + gold primary
- Azure purple accent
- Silver edge accents

### 2.1 Core palette (recommended defaults)

All values are hex.

**KeyClave Red**

- `kc.red.600` = `#E41D2D` (primary)
- `kc.red.700` = `#B81422` (pressed / deeper)
- `kc.red.050` = `#FFF1F3` (tint backgrounds)

**KeyClave Gold**

- `kc.gold.500` = `#D4AF37` (primary gold)
- `kc.gold.600` = `#B8922E` (pressed)
- `kc.gold.050` = `#FFF7DD` (tint)

**Azure Purple (accent)**

- `kc.purple.500` = `#6A4CFF` (accent)
- `kc.purple.600` = `#553AE6` (pressed)
- `kc.purple.050` = `#F1EEFF` (tint)

**Silver (edges, separators, chrome)**

- `kc.silver.300` = `#CBD5E1` (divider)
- `kc.silver.500` = `#94A3B8` (border)
- `kc.silver.700` = `#475569` (dark border)

**Neutrals**

- `kc.neutral.950` = `#0B1020` (near-black)
- `kc.neutral.900` = `#111827`
- `kc.neutral.100` = `#F3F4F6`
- `kc.neutral.000` = `#FFFFFF`

### 2.2 Semantic tokens

- `color.bg.app` = `kc.neutral.950`
- `color.bg.panel` = `#0F172A`
- `color.fg.primary` = `kc.neutral.000`
- `color.fg.muted` = `#B6C2D1`
- `color.brand.primary` = `kc.red.600`
- `color.brand.secondary` = `kc.gold.500`
- `color.brand.accent` = `kc.purple.500`
- `color.border.default` = `kc.silver.500`

**Status**

- `color.status.success` = `#22C55E`
- `color.status.warning` = `#F59E0B`
- `color.status.danger` = `#EF4444`
- `color.status.info` = `kc.purple.500`

### 2.3 Accessibility requirements

- Minimum contrast ratio target: 4.5:1 for body text.
- Red/gold combinations must not be used for small text without a neutral background.
- Provide non-color cues for status (icons + labels), not color alone.

## 3) Typography

### Recommended direction

- Use a modern, highly legible sans for UI.
- Prefer system fonts per OS to reduce packaging risk.

Suggested mapping:

- macOS: SF Pro
- Windows: Segoe UI
- Linux: Noto Sans / DejaVu Sans (fallback)

Type scale (approx):

- `type.h1` 24/32
- `type.h2` 20/28
- `type.h3` 16/24
- `type.body` 14/20
- `type.caption` 12/16

## 4) Layout, spacing, and surfaces

### 4.1 Spacing scale

- `space.1` = 4
- `space.2` = 8
- `space.3` = 12
- `space.4` = 16
- `space.5` = 24
- `space.6` = 32

### 4.2 Radii

- `radius.sm` = 6
- `radius.md` = 10
- `radius.lg` = 14

### 4.3 Panels and edges

KeyClave should include subtle “silver edging”:

- Use `kc.silver.500` borders with 1px width
- Add gentle inner highlight:
  - top-left highlight `#FFFFFF12`
  - bottom-right shadow `#00000066`

Avoid heavy drop shadows; prefer inlay-like depth.

## 5) Component styling guidance (Qt)

### Buttons

- Primary button: red background, white text.
- Secondary button: neutral panel background with silver border.
- Accent button (rare): purple.

States:

- Hover: slight brightness increase
- Pressed: use `.700` shades
- Disabled: neutral + reduced contrast (still readable)

### Sensitive fields

Secret input:

- Masked by default.
- Reveal control is explicit.
- Auto-hide after timeout.

### Mode banners

- Offline Mode: neutral banner.
- Online Mode: purple-accent banner with clear text.
- Local LLM assist (if enabled): secondary indicator with disclosure link (local-only).

## 6) Iconography and brand assets

### 6.1 KeyClave logo (primary)

User requirement:

- Logo is **four keys** blending ancient/renaissance gate keys and USB sticks.
- Keys form a letter **K** in **gold** over a **red** background.

Specification (MVP):

- Background: `kc.red.600`
- Foreground keys: `kc.gold.500` with subtle highlight `#FFE9A6`
- Optional outline: `kc.silver.300` at low opacity for separation

Composition rules:

- The 4 keys create the vertical and angled strokes of a K.
- Include one “USB-like” rectangular end on each key.
- Avoid thin filigree that disappears at small icon sizes.

Deliverables:

- App icon: 16, 32, 64, 128, 256, 512, 1024 px
- Monochrome variant (for OS areas that require single-color)
- Horizontal lockup: logo + wordmark “KeyClave”

### 6.2 Wordmark

- Text: KeyClave
- Suggested style: slightly condensed sans, strong weight.
- Optional subtle key-tooth notch in the letter K leg (only if it remains legible).

## 7) Motion and interaction

Principles:

- Motion should communicate security state changes: lock/unlock, export, validate.
- Keep animation durations short (150–220ms) and subtle.
- Provide reduced-motion setting.

Suggested micro-interactions:

- Unlock success: brief gold shimmer line along silver border.
- Export ready: “seal” animation (like stamping a wax seal, but modern).

## 8) Sonic design (robust)

KeyClave should have a consistent sound palette that supports focus and reinforces security state.

### 8.1 Sound principles

- Sounds are short, clean, non-intrusive.
- No continuous background music.
- Respect OS mute and accessibility preferences.
- Provide a master toggle and volume slider.

### 8.2 Sonic motifs

- “Key metal” micro-clinks for minor UI interactions.
- “Vault latch” for lock/unlock.
- “Seal stamp” for export/import completion.
- “Crystal ping” (purple accent) for Online Mode enable.

### 8.3 Event sound map (MVP)

- App unlock success: low vault latch + soft gold shimmer
- App lock / auto-lock: short latch close
- Copy secret: subtle click + caution tick
- Export bundle created: seal stamp + short resonance
- Import completed: seal stamp lighter variant
- Validation success: clean confirmation ping
- Validation fail: muted thud + short alert
- Online Mode enabled: purple cue + warning chime

### 8.4 Constraints

- No sound should reveal secret content.
- Sounds must not occur on every keystroke.

### 8.5 Sound asset sourcing plan

Sound assets must be created or sourced before Milestone 8 implementation:

- **Option A (recommended)**: Commission a small set of original sound effects from a sound designer. Budget for ~10 short cues (< 1 second each).
- **Option B**: Source from royalty-free sound libraries with permissive licenses (CC0 or similar). Verify license compatibility before bundling.
- **Option C**: Generate procedurally using a synthesis tool (e.g., sfxr/jsfxr for retro-style cues, or a DAW for polished sounds).

Requirements for all options:

- Deliver as WAV or OGG files (lossless or high-quality lossy).
- Include license documentation in `assets/sounds/LICENSE`.
- Keep total sound asset size under 2 MB.
- Provide a silent/muted fallback for accessibility.

### 8.6 Audio feedback component (implementation)

The audio system should be implemented as a `SoundManager` service in `keyclave/ui/sounds/`:

- Load sound files on app startup.
- Expose a `play(event_id)` method mapped to the event sound map above.
- Respect the master toggle and volume slider from user settings.
- Respect OS mute state via Qt audio APIs.
- Provide a `reduced-motion` / `reduced-audio` mode that disables all sounds.
- Never block the UI thread for sound playback (use Qt multimedia async playback).

## 9) Accessibility

### 9.1 Requirements

- All interactive elements must have accessible names (for screen readers).
- Full keyboard navigation for all critical flows (unlock, import, export, scan, generate dotenv).
- Tab order must follow logical reading order.
- Focus indicators must be visible (use `kc.purple.500` focus ring).
- Status changes must be announced to screen readers (use Qt accessibility roles).

### 9.2 Contrast and color

- Minimum contrast ratio: 4.5:1 for body text (WCAG 2.1 AA).
- 3:1 for large text and UI components.
- Red/gold combinations must not be used for small text without a neutral background.
- Provide non-color cues for all status indicators (icons + labels, not color alone).

### 9.3 Testing criteria

- **Automated**: use `pytest-qt` to verify accessible names on all interactive widgets.
- **Manual (per release)**:
  - macOS: test with VoiceOver enabled.
  - Windows: test with NVDA.
  - Linux: test with Orca (best-effort).
- **Keyboard-only**: complete all primary UX journeys using keyboard only (no mouse).
- **Contrast audit**: verify all color token combinations meet WCAG 2.1 AA using a contrast checker tool.

## 10) Acceptance criteria

- Color tokens are implemented consistently.
- Offline/Online and optional local LLM assist states are visually distinct.
- Secret handling UI is clearly signposted.
- Logo spec is implementable and scales down.
- Sonic cues map to security-relevant actions and are user-configurable.
- Sound assets are sourced, licensed, and bundled.
- Accessibility requirements are met and tested per section 9.
