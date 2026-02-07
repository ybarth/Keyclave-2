# Markdown ingestion and requirement inference (MVP)

This spec defines how KeyClave scans projects for Markdown design docs and infers required API providers and environment variables, producing an actionable checklist with citations.

Decisions confirmed:

- Parse `.md` plus `README` files with no extension.
- Extraction priority order: (A) explicit env var tokens → (D) code blocks/config snippets → (B) provider names → (C) URLs/domains.
- Output includes provider id, env var names, confidence, and citations (file path + line range + excerpt).
- Optional local LLM assistance may propose additional requirements, but must require user approval before any write/export actions.
- Default scan exclusions: `.git`, `node_modules`, `dist`, `build`, `.venv`, `__pycache__`.

Related:

- Scope: [`plans/product-scope.md`](plans/product-scope.md:1)
- Provider definitions: [`plans/provider-plugins-and-github.md`](plans/provider-plugins-and-github.md:1)
- Architecture: [`plans/architecture-module-boundaries.md`](plans/architecture-module-boundaries.md:1)
- Security boundaries: [`plans/security-crypto-2fa.md`](plans/security-crypto-2fa.md:1)
- Local LLM inference: [`plans/local-llm-inference.md`](plans/local-llm-inference.md:1)

## 1) Inputs

### 1.1 Project roots
User can:

- Select a project root folder explicitly.
- Opt into broader scanning/indexing (full-disk scan index) as described in [`plans/product-scope.md`](plans/product-scope.md:1).

### 1.2 Included files

- `**/*.md`
- `README` (no extension) within scanned roots

### 1.3 Excluded paths (default)

- `**/.git/**`
- `**/node_modules/**`
- `**/dist/**`
- `**/build/**`
- `**/.venv/**`
- `**/__pycache__/**`

MVP should also ignore obvious binary files and skip extremely large files as a safety valve (implementation detail).

## 2) Output model

### 2.1 Requirement record

Each inferred requirement yields:

- `provider_id` (e.g., `github`)
- `env_vars: list[str]` (e.g., `GITHUB_TOKEN`)
- `confidence: float` (0.0–1.0)
- `citations: list[Citation]`

`Citation`:

- `path` (relative to project root where possible)
- `line_start`, `line_end`
- `excerpt` (short snippet; redact secret values)
- `kind` (enum: `env_var`, `code_block`, `provider_name`, `domain`)

### 2.2 Report structure

- Group by provider.
- Show env var list.
- Show `missing in vault` vs `present in vault` and `present in project dotenv`.
- Allow user to accept/reject inferred requirements.

## 3) Extraction pipeline (rule-based MVP)

### 3.1 Preprocessing

- Normalize line endings.
- Keep line numbers stable.
- Identify fenced code blocks (``` and ~~~) with language tag.
- Extract inline code spans.

### 3.2 Rule priority order

Rules run in order and accumulate evidence. Confidence is computed from weighted evidence.

#### A) Explicit env var tokens (highest priority)

Detect patterns like:

- Inline: ``GITHUB_TOKEN``
- Shell: `export GITHUB_TOKEN=...`
- dotenv: `GITHUB_TOKEN=...`
- YAML: `GITHUB_TOKEN: ...`

Baseline regex:

- `\b[A-Z][A-Z0-9_]{2,}\b`

Mapping:

- Prefer tokens that match known provider env vars or aliases from the provider registry.

Evidence produced:

- Provider match via env var mapping.
- Confidence: high.

#### D) Code blocks/config snippets (second)

Within fenced blocks, look for:

- dotenv-style `KEY=VALUE`
- JSON/YAML keys that look like env vars
- Examples of `.env` files

Heuristics:

- In code blocks, env-var-like tokens get a small confidence boost.
- If a token matches a provider alias, attach provider evidence.

#### B) Provider names (third)

Detect provider mentions using provider registry aliases, for example:

- `GitHub`
- `github`

Evidence produced:

- Provider candidate with medium confidence.
- If provider names appear near env-var tokens, boost confidence.

#### C) URLs/domains (fourth)

Detect domains and URLs:

- `github.com`

Map domains to providers via provider registry.

Evidence produced:

- Provider candidate with low-to-medium confidence.

### 3.3 Confidence scoring (MVP)

Use a simple weighted model with **additive aggregation**:

- Env var alias match: +0.7
- Env var token in code block: +0.1
- Provider name mention: +0.3
- Domain mention: +0.2

Aggregation rule: **sum** all evidence weights for the same provider across all documents, then clamp to 1.0.

Example: if a project mentions `GITHUB_TOKEN` (+0.7) and `github.com` (+0.2), the combined confidence is min(0.9, 1.0) = 0.9.

Then apply dampeners:

- If evidence is only domain mention with no other signals, cap at 0.4.

## 4) Citations

Each evidence item must include a citation:

- file path
- line range
- excerpt (short; redact values after `=`)

Example excerpt redaction:

- Input: `GITHUB_TOKEN=ghp_abc123`
- Stored excerpt: `GITHUB_TOKEN=<redacted>`

## 5) Local LLM augmentation (optional)

When a local model is installed and the user enables local LLM assistance:

- The system may use locally-provided, non-secret text excerpts to propose:
  - additional providers
  - missing env vars
  - better mappings

Hard rules:

- Never include secret values in prompts.
- Never write to project files or vault based solely on LLM output.
- Require explicit user confirmation to accept each proposed requirement.

Reference implementation constraints: [`plans/local-llm-inference.md`](plans/local-llm-inference.md:1).

## 6) Acceptance criteria

- Works in Offline Mode with no network.
- Produces a stable requirement list with confidence and citations.
- Can explain every inferred requirement via citations.
- Does not leak secrets in excerpts or logs.
