# KeyClave plan review — 2026-02-06

Comprehensive review of all plan documents for inconsistencies, outstanding decisions, areas needing clarification, and potential red flags.

## Documents reviewed

1. [`plans/product-scope.md`](plans/product-scope.md:1)
2. [`plans/architecture-module-boundaries.md`](plans/architecture-module-boundaries.md:1)
3. [`plans/data-model.md`](plans/data-model.md:1)
4. [`plans/implementation-backlog.md`](plans/implementation-backlog.md:1)
5. [`plans/security-crypto-2fa.md`](plans/security-crypto-2fa.md:1)
6. [`plans/adr-0001-ui-stack-pyside6-qtwebengine.md`](plans/adr-0001-ui-stack-pyside6-qtwebengine.md:1)
7. [`plans/reuse-strategy.md`](plans/reuse-strategy.md:1)
8. [`plans/local-llm-inference.md`](plans/local-llm-inference.md:1)
9. [`plans/export-import-bundles.md`](plans/export-import-bundles.md:1)
10. [`plans/dotenv-merge.md`](plans/dotenv-merge.md:1)
11. [`plans/provider-plugins-and-github.md`](plans/provider-plugins-and-github.md:1)
12. [`plans/markdown-ingestion.md`](plans/markdown-ingestion.md:1)
13. [`plans/online-assistant-ux.md`](plans/online-assistant-ux.md:1)
14. [`plans/key-import-flows.md`](plans/key-import-flows.md:1)
15. [`plans/key-validation.md`](plans/key-validation.md:1)
16. [`plans/telemetry-logging.md`](plans/telemetry-logging.md:1)
17. [`plans/ux-brand-sonic.md`](plans/ux-brand-sonic.md:1)
18. [`README.md`](README.md:1)
19. [`third_party/manifest.yml`](third_party/manifest.yml:1)
20. [`External Infrastructure Setup Instructions`](External%20Infrastructure%20Setup%20Instructions:1)

---

## 1. Inconsistencies

### 1.1 Validation status enum mismatch

- [`plans/key-validation.md`](plans/key-validation.md:30) defines **five** statuses: `unknown`, `valid`, `invalid`, `unverifiable`, `error`.
- [`plans/data-model.md`](plans/data-model.md:159) defines only **four** statuses for `validations.status`: `unknown`, `valid`, `invalid`, `error`.
- [`plans/provider-plugins-and-github.md`](plans/provider-plugins-and-github.md:57) uses four: `valid`, `invalid`, `unknown`, `error`.

**Missing:** `unverifiable` is absent from the data model and the provider contract. This is the status for providers that have no safe free/auth endpoint. The data model and provider contract need updating to include it.

### 1.2 Validation storage: last-only vs history table

- [`plans/key-validation.md`](plans/key-validation.md:91) says: *Store only the last result per secret. No full history in MVP.*
- [`plans/data-model.md`](plans/data-model.md:153) defines a `validations` table with its own `id` PK and an index on `(secret_id, checked_at DESC)`, which implies a **history table** with multiple rows per secret.

**Decision needed:** Should the `validations` table store only the latest row per secret, or accumulate history? The index design suggests history, but the validation spec says last-only. These need to be reconciled.

### 1.3 Provenance: data model vs import flows

- [`plans/key-import-flows.md`](plans/key-import-flows.md:143) defines provenance metadata per secret: `source_type`, `source_label`, `imported_at`.
- [`plans/data-model.md`](plans/data-model.md:194) lists *Do we store per-secret provenance as a first-class table?* as an **open question** (item 3).
- The `secrets` table in [`plans/data-model.md`](plans/data-model.md:89) has no provenance fields.

**Gap:** The import flows spec assumes provenance is stored, but the data model has not committed to where. This needs a decision: add columns to `secrets` or create a `secret_provenance` table.

### 1.4 Telemetry logging line reference error

- [`External Infrastructure Setup Instructions`](External%20Infrastructure%20Setup%20Instructions:189) references `plans/telemetry-logging.md:151` for redacted logging rules, but the file only has 147 lines. This is a broken reference.

### 1.5 Crash reporting section numbering

- [`External Infrastructure Setup Instructions`](External%20Infrastructure%20Setup%20Instructions:270) section 4 starts with subsection `4.2` — there is no `4.1`. This appears to be a numbering error (likely `4.1 Purpose` was removed or merged into the intro paragraph but the numbering was not updated).

### 1.6 LLM API keys mentioned in infrastructure doc

- [`External Infrastructure Setup Instructions`](External%20Infrastructure%20Setup%20Instructions:470) lists *LLM API keys* as something engineering will need to manage. However, the entire plan set explicitly prohibits cloud-hosted LLMs and third-party inference APIs. There should be no LLM API keys. This bullet is misleading and should be removed or clarified to say *none required per current plan*.

---

## 2. Outstanding decision questions

### 2.1 Open questions explicitly listed in data-model.md

[`plans/data-model.md`](plans/data-model.md:192) lists three open questions:

1. **Provider env var templates in DB or code only?** — Affects whether the `providers` table needs an `env_vars_json` column or if env var specs live purely in Python code.
2. **Project path privacy in Online Mode?** — When embedded browsing is enabled, should project paths be visible/accessible? No spec addresses this.
3. **Per-secret provenance as a first-class table?** — See inconsistency 1.3 above.

### 2.2 Packaging toolchain not specified

- [`plans/adr-0001-ui-stack-pyside6-qtwebengine.md`](plans/adr-0001-ui-stack-pyside6-qtwebengine.md:117) lists *Confirm packaging tooling and update mechanism compatibility* as a follow-up.
- [`plans/implementation-backlog.md`](plans/implementation-backlog.md:168) mentions packaging but does not name a tool (PyInstaller? Briefcase? Nuitka? cx_Freeze?).

**Decision needed:** Which packaging tool will be used? This affects binary size, QtWebEngine bundling, and auto-update feasibility.

### 2.3 Auto-update mechanism not designed

- [`plans/implementation-backlog.md`](plans/implementation-backlog.md:172) says *Add auto-update mechanism design + stub*.
- [`External Infrastructure Setup Instructions`](External%20Infrastructure%20Setup%20Instructions:399) notes *the exact auto-update mechanism is not specified in the plans*.

**Decision needed:** Will auto-update use Sparkle (macOS), WinSparkle (Windows), a custom feed, or something else? This is a significant engineering decision that affects Milestone 8.

### 2.4 Payload serialization format for export bundles

- [`plans/export-import-bundles.md`](plans/export-import-bundles.md:92) says the payload is *a versioned structure (e.g., CBOR/MessagePack/JSON within ciphertext)* but does not commit to one.

**Decision needed:** Pick one format. JSON is simplest; CBOR/MessagePack are more compact. This affects implementation and interoperability.

### 2.5 Generic/Unassigned provider handling

- [`plans/key-import-flows.md`](plans/key-import-flows.md:99) mentions importing as provider `generic` or *Unassigned* for unknown keys.
- The `providers` table in [`plans/data-model.md`](plans/data-model.md:78) and the provider plugin contract in [`plans/provider-plugins-and-github.md`](plans/provider-plugins-and-github.md:26) do not define a `generic` or `unassigned` provider.

**Decision needed:** Should there be a built-in `generic` provider record, or should `provider_id` be nullable on `secrets`? The current `UNIQUE(profile_id, provider_id, key_name)` constraint would need adjustment if nullable.

### 2.6 Audit retention configuration location

- [`plans/data-model.md`](plans/data-model.md:176) says retention is *user-configurable* and suggests storing config in `profiles` settings or a separate table.
- [`plans/telemetry-logging.md`](plans/telemetry-logging.md:64) says *user-configurable retention policy (count-based and/or time-based)*.

**Decision needed:** Where is retention config stored? A `profile_settings` table or columns on `profiles`?

### 2.7 Inactivity auto-lock timeout value

- [`plans/architecture-module-boundaries.md`](plans/architecture-module-boundaries.md:94) mentions *Timed lock: auto-lock after inactivity*.
- No document specifies a default timeout value.

**Decision needed:** What is the default auto-lock timeout? (e.g., 5 minutes, 15 minutes, configurable?)

---

## 3. Areas needing clarification or elaboration

### 3.1 Profile storage location and discovery

- [`plans/data-model.md`](plans/data-model.md:22) says *profiles/profile_id/vault.db* conceptually.
- No document specifies the **root data directory** per OS (e.g., `~/.keyclave/`, `%APPDATA%/KeyClave/`, `~/.local/share/keyclave/`).

**Clarification needed:** Define the per-OS data directory convention. This affects profile discovery, model storage, backup paths, and diagnostics export.

### 3.2 Profile metadata storage: where does the profile list live?

- Each profile has its own SQLite DB, but the **list of profiles** (display names, IDs) must be stored somewhere accessible before any profile is unlocked.
- No document specifies a top-level index DB or config file.

**Clarification needed:** Is there a `profiles.json` or `index.db` at the root data directory?

### 3.3 Nonce management for AES-256-GCM

- [`plans/security-crypto-2fa.md`](plans/security-crypto-2fa.md:97) says *Ensure each record encryption uses a unique nonce*.
- No guidance on nonce generation strategy (random 96-bit? counter-based?).

**Clarification needed:** For per-record encryption, random 96-bit nonces are standard but require care to avoid collisions at scale. Given the expected record count (hundreds to low thousands per profile), random nonces are safe, but this should be stated explicitly.

### 3.4 Key rotation mechanics

- [`plans/security-crypto-2fa.md`](plans/security-crypto-2fa.md:116) says *Support PVK rotation by re-encrypting vault records with a new PVK*.
- No document describes the UX or the migration process (batch re-encrypt, progress indicator, failure recovery).

**Clarification needed:** Is key rotation a background task? What happens if it fails mid-way? Is there a rollback mechanism?

### 3.5 Embedded browser: which QtWebEngine APIs are restricted?

- [`plans/adr-0001-ui-stack-pyside6-qtwebengine.md`](plans/adr-0001-ui-stack-pyside6-qtwebengine.md:92) says *restricted APIs* but does not enumerate them.
- [`plans/online-assistant-ux.md`](plans/online-assistant-ux.md:157) says *dedicated browser profile/container* but does not specify which WebEngine features to disable.

**Clarification needed:** Should JavaScript be enabled? WebRTC? Geolocation? Notifications? File downloads? A concrete allowlist/blocklist of WebEngine features would help implementation.

### 3.6 Backup file cleanup policy

- [`plans/dotenv-merge.md`](plans/dotenv-merge.md:130) specifies timestamped backups but does not define a cleanup/retention policy.

**Clarification needed:** Will old backups accumulate indefinitely? Should there be a max count or age-based cleanup?

### 3.7 Multi-line dotenv values

- [`plans/dotenv-merge.md`](plans/dotenv-merge.md:41) explicitly lists *Complex multi-line values* as a non-goal for MVP.
- Some real-world dotenv files (e.g., RSA private keys) use multi-line values.

**Clarification needed:** Should the parser at least preserve multi-line values it cannot parse, rather than corrupting them? A safe fallback strategy should be documented.

### 3.8 Confidence scoring: how are multiple evidence items for the same provider combined?

- [`plans/markdown-ingestion.md`](plans/markdown-ingestion.md:142) defines per-evidence weights but does not specify whether they are summed, max-ed, or use some other aggregation.

**Clarification needed:** If a document mentions `GITHUB_TOKEN` (+0.7) and `github.com` (+0.2), is the combined confidence 0.9 or max(0.7, 0.2) = 0.7?

### 3.9 TOTP recovery codes

- [`plans/security-crypto-2fa.md`](plans/security-crypto-2fa.md:149) mentions recovery codes as optional.
- No document specifies how many codes, their format, or storage.

**Clarification needed:** If recovery codes are offered, how many? Are they one-time use? Where are they stored (encrypted in vault meta)?

### 3.10 Replicate provider plugin

- A tab `plans/provider-plugins-and-replicate.md` is open in the editor but the file does not exist on disk.

**Clarification needed:** Was a Replicate provider plugin planned and removed, or is this a future placeholder? If planned, it should be created or removed from consideration.

---

## 4. Potential red flags

### 4.1 QtWebEngine binary size and security surface

- QtWebEngine bundles Chromium, adding ~100-200 MB to the installer.
- Chromium requires frequent security patches. If the PySide6 release cadence lags upstream Chromium, the embedded browser could ship with known CVEs.

**Risk:** Users may be running an outdated Chromium in Online Mode. Mitigation: document a policy for tracking PySide6/QtWebEngine security updates and consider the external browser fallback as the recommended path for security-sensitive providers.

### 4.2 Argon2id with 128 MiB memory on low-end machines

- [`plans/security-crypto-2fa.md`](plans/security-crypto-2fa.md:77) sets Argon2id memory to 128 MiB.
- This is a strong default but may cause noticeable delays or even failures on machines with limited RAM (e.g., 4 GB Linux VMs, older laptops).

**Risk:** Poor UX on low-end hardware. Mitigation: the spec says params are stored per-profile and upgradable, but there is no documented fallback or minimum-viable parameter set for constrained environments.

### 4.3 Local LLM 7B model on 16 GB RAM minimum

- [`plans/local-llm-inference.md`](plans/local-llm-inference.md:91) sets minimum RAM at 16 GB for CPU-only inference.
- Many developer laptops (especially older ones) have 8 GB RAM.

**Risk:** The local LLM feature may be unusable for a significant portion of the target audience. This is mitigated by the feature being optional, but the minimum should be clearly communicated in the UI before download.

### 4.4 No schema for profile_vault_meta in data model migrations

- [`plans/data-model.md`](plans/data-model.md:68) defines `profile_vault_meta` as a separate table.
- [`plans/implementation-backlog.md`](plans/implementation-backlog.md:43) mentions *initial SQLite schema + migrations* but does not explicitly list `profile_vault_meta`.

**Risk:** This table could be missed during implementation. It should be explicitly listed in the migration plan.

### 4.5 No test strategy document

- [`plans/implementation-backlog.md`](plans/implementation-backlog.md:181) mentions security tests and fuzz tests in Milestone 9, but there is no dedicated testing strategy document.
- No mention of unit test frameworks, integration test approach, or CI pipeline design.

**Risk:** Testing may be ad-hoc without a clear strategy. A testing plan should be created before or during Milestone 0.

### 4.6 No error handling / recovery strategy document

- Multiple specs mention error states (validation errors, import failures, KDF failures, bundle integrity failures) but there is no unified error handling strategy.
- No document defines the error taxonomy beyond validation errors.

**Risk:** Inconsistent error handling across modules. Consider a brief error taxonomy and recovery strategy document.

### 4.7 Clipboard auto-clear is platform-dependent

- [`plans/security-crypto-2fa.md`](plans/security-crypto-2fa.md:125) and [`plans/key-import-flows.md`](plans/key-import-flows.md:139) mention auto-clearing clipboard after a timeout.
- On some platforms (especially Linux with multiple clipboard managers), clearing the clipboard is unreliable.

**Risk:** Users may have a false sense of security. The spec says *where feasible* which is appropriate, but the UI should clearly communicate when auto-clear cannot be guaranteed.

### 4.8 Bundle expiry is client-enforced only

- [`plans/export-import-bundles.md`](plans/export-import-bundles.md:127) notes *expiry is enforced by importer, not by remote revocation*.
- A modified client could ignore expiry.

**Risk:** This is inherent to offline-first design and is documented, but users should understand that expiry is advisory. The UI explanation is specified, which is good.

### 4.9 No accessibility testing plan

- [`plans/ux-brand-sonic.md`](plans/ux-brand-sonic.md:82) mentions contrast ratios and non-color cues.
- No document specifies accessibility testing tools, screen reader compatibility, or keyboard navigation requirements.

**Risk:** Accessibility may be incomplete without explicit testing criteria.

### 4.10 Sound design dependency

- [`plans/ux-brand-sonic.md`](plans/ux-brand-sonic.md:209) specifies a detailed sonic palette.
- No document addresses how sounds will be created, licensed, or bundled.

**Risk:** Sound assets need to be created or sourced. This is a non-trivial creative dependency that could delay Milestone 8.

---

## 5. Cross-reference gaps

### 5.1 Missing spec: product-scope.md references not in README

- [`plans/product-scope.md`](plans/product-scope.md:37) references [`plans/local-llm-inference.md`](plans/local-llm-inference.md:1) but the README does not list local-llm-inference under any section heading. It is only referenced indirectly via the backlog.

### 5.2 Implementation backlog references product-scope.md

- [`plans/implementation-backlog.md`](plans/implementation-backlog.md:7) references [`plans/product-scope.md`](plans/product-scope.md:1) as an input, which is correct. However, the backlog does not reference [`plans/key-import-flows.md`](plans/key-import-flows.md:1) or [`plans/key-validation.md`](plans/key-validation.md:1) as inputs, even though Milestones 2 and 7 implement those specs.

### 5.3 External Infrastructure doc not in plans/ directory

- [`External Infrastructure Setup Instructions`](External%20Infrastructure%20Setup%20Instructions:1) is at the repo root, not in `plans/`. It is also not listed in the README index.

---

## 6. Summary of recommended actions

| # | Category | Action | Priority |
|---|----------|--------|----------|
| 1 | Inconsistency | Add `unverifiable` to data model validation status enum | High |
| 2 | Inconsistency | Reconcile validation storage: last-only vs history table | High |
| 3 | Inconsistency | Decide on provenance storage and update data model | High |
| 4 | Inconsistency | Fix broken line reference in External Infrastructure doc | Low |
| 5 | Inconsistency | Fix section numbering in External Infrastructure doc section 4 | Low |
| 6 | Inconsistency | Remove or correct LLM API keys mention in External Infrastructure doc | Medium |
| 7 | Decision | Resolve data model open questions 1-3 | High |
| 8 | Decision | Choose packaging toolchain | High |
| 9 | Decision | Design auto-update mechanism | Medium |
| 10 | Decision | Choose bundle payload serialization format | Medium |
| 11 | Decision | Define generic/unassigned provider handling | High |
| 12 | Decision | Define audit retention config location | Low |
| 13 | Decision | Set default auto-lock timeout | Medium |
| 14 | Clarification | Define per-OS data directory convention | High |
| 15 | Clarification | Define profile list/index storage | High |
| 16 | Clarification | Document nonce generation strategy | Medium |
| 17 | Clarification | Document key rotation UX and failure recovery | Medium |
| 18 | Clarification | Enumerate restricted QtWebEngine APIs | Medium |
| 19 | Clarification | Define dotenv backup cleanup policy | Low |
| 20 | Clarification | Define multi-line dotenv safe fallback | Low |
| 21 | Clarification | Clarify confidence score aggregation | Low |
| 22 | Clarification | Specify TOTP recovery code details | Low |
| 23 | Clarification | Resolve phantom replicate provider plugin | Low |
| 24 | Red flag | Document QtWebEngine security update policy | Medium |
| 25 | Red flag | Document Argon2id fallback for low-RAM machines | Low |
| 26 | Red flag | Create a testing strategy document | High |
| 27 | Red flag | Create an error taxonomy/recovery document | Medium |
| 28 | Red flag | Plan sound asset creation/licensing | Low |
| 29 | Red flag | Add accessibility testing criteria | Medium |
| 30 | Housekeeping | Add local-llm-inference.md to README index | Low |
| 31 | Housekeeping | Add key-import-flows.md and key-validation.md as backlog inputs | Low |
| 32 | Housekeeping | Move External Infrastructure doc into plans/ and add to README | Low |
