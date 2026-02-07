# Local LLM inference + model management (local-first, no cloud)

This spec defines how KeyClave can use a **fully local** large language model to improve guidance and extraction while remaining executable end-to-end offline.

Key constraints (locked):

- **No cloud-hosted LLMs**.
- **No third-party inference APIs**.
- All model execution occurs **on-device / on-prem** inside the KeyClave application boundary.

Related:

- Architecture boundaries: [`plans/architecture-module-boundaries.md`](plans/architecture-module-boundaries.md:1)
- Product scope: [`plans/product-scope.md`](plans/product-scope.md:1)
- Online assistant policy: [`plans/online-assistant-ux.md`](plans/online-assistant-ux.md:1)
- Markdown ingestion (rule-based MVP): [`plans/markdown-ingestion.md`](plans/markdown-ingestion.md:1)
- Security boundaries: [`plans/security-crypto-2fa.md`](plans/security-crypto-2fa.md:1)

## 1) Goals

- Provide optional local LLM assistance for:
  - better next-step suggestions in Guided Setup Sessions
  - improved mapping of doc text to provider requirements
  - summarizing playbooks and explaining inferred requirements
- Keep the system fully functional without any model present (rule-based fallback).
- Ensure the model never becomes a requirement for core vault/import/dotenv workflows.

## 2) Non-goals

- No remote inference.
- No model fine-tuning in MVP.
- No training data collection.

## 3) Runtime approach (supports both)

KeyClave supports two local inference backends:

### 3.1 Bundled runtime (default)

- Bundle a local runtime based on `llama.cpp` (or an equivalent embedded GGUF runtime).
- Execute the model in-process or as a child process started by KeyClave.
- Models are stored locally as `.gguf` files.

### 3.2 Optional Ollama integration (if installed)

- If Ollama is present, KeyClave may use it via the local HTTP API (`localhost`).
- KeyClave may ask Ollama to pull models, list models, and run inference.
- If Ollama is absent, KeyClave continues to operate via the bundled runtime.

Policy: Ollama integration must not require any Ollama cloud account. All traffic must remain local.

## 4) Default model family and variants

Decision (recommended default): use a current, state-of-the-art **open-source** instruct model with strong tool-following and small-footprint options.

### 4.1 Default model (recommended)

- Family: **Qwen2.5 Instruct**
- Default size: **7B Instruct** for broad CPU compatibility

Rationale:

- Strong instruction-following and extraction capabilities.
- Widely available as GGUF via community conversions.
- Practical latency on modern laptops under quantization.

### 4.2 Optional bigger model (post-MVP option)

- Qwen2.5 14B Instruct for higher quality on stronger hardware.

## 5) Quantization strategy (GGUF tiers)

KeyClave must support multiple quantization tiers for the same model family:

- **Q4_K_M**: default for CPU-first deployments (best balance)
- **Q5_K_M**: quality bump; higher RAM
- **Q6_K**: higher quality; stronger CPU/RAM required
- **Q8_0**: near-fp16 quality; large RAM footprint

Selection policy:

- MVP: pick a safe default based on detected RAM and whether a GPU backend is available.
- Allow user override per profile.

## 6) Hardware requirements (planning assumptions)

These are planning targets for user-facing expectations. Actual performance depends on CPU/GPU, backend, and model choice.

### 6.1 CPU-only (bundled runtime)

- Minimum: modern 4-core CPU, **16 GB RAM**
- Recommended: 8+ performance cores, **32 GB RAM**

### 6.2 GPU acceleration (optional)

- If supported by the chosen backend, GPU acceleration may be enabled automatically.
- Minimum VRAM for 7B at common quantizations: ~6–8 GB VRAM (varies by backend and offload strategy).

## 7) Performance expectations (planning targets)

KeyClave should document approximate expectations for user trust:

- 7B Q4 on CPU: interactive but not instant (single-digit to low double-digit tokens/sec typical on modern laptops)
- 7B Q4 with GPU offload: low latency, higher throughput when VRAM is sufficient

MVP must include a built-in benchmark/smoke test:

- measure prompt latency and tokens/sec on first-run after model install
- store results locally for troubleshooting

## 8) Model management

### 8.1 Model catalog

KeyClave maintains a small curated catalog:

- model id
- family/size
- quantization
- SHA-256 checksum
- download URL(s)
- license metadata

### 8.2 Storage locations

- Store models under an app-controlled directory (per-OS standard app data location).
- Never store models inside the encrypted vault (models are not secrets).

### 8.3 Download and verification

- Downloads must be explicit user action.
- Verify checksums before making the model available.
- Support resumable downloads.

### 8.4 Updates

- Model updates are optional and user-controlled.
- If the catalog updates a model, keep the previous version available for rollback.

## 9) Data boundaries and retention

- Prompts and completions must be treated as potentially sensitive.
- Default: do not persist raw prompts/completions.
- If the user enables history, store it locally and apply redaction rules consistent with [`plans/telemetry-logging.md`](plans/telemetry-logging.md:1).
- Never include secret values in prompts.

## 10) Integration points in the app

### 10.1 `LLMService`

Conceptual interface:

- `llm.health_check() -> status`
- `llm.list_models() -> list[ModelInfo]`
- `llm.install_model(model_id, quant) -> progress`
- `llm.generate(prompt, policy) -> completion`

### 10.2 Policy wrapper

Every call must pass a policy object that enforces:

- max tokens
- allowed inputs (no secrets)
- local-only execution (no network)
- logging redaction (no raw content)

## 11) Acceptance criteria

- KeyClave has no dependency on cloud LLM services.
- Inference runs locally via bundled runtime and/or local Ollama.
- Model downloads are user-initiated and checksum-verified.
- The app remains fully usable without installing any model.

