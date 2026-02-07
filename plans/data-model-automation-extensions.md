# Data Model Extensions for Automation Subsystem

This document defines the additional database tables and schema changes required by the automation subsystem.

**Status:** Post-MVP extension. Extends the base data model from [`plans/data-model.md`](plans/data-model.md:1).

Related:

- Base data model: [`plans/data-model.md`](plans/data-model.md:1)
- Automation architecture: [`plans/automation-subsystem-architecture.md`](plans/automation-subsystem-architecture.md:1)
- API dashboard and discovery: [`plans/api-dashboard-and-discovery.md`](plans/api-dashboard-and-discovery.md:1)
- AI script generation: [`plans/ai-script-generation.md`](plans/ai-script-generation.md:1)

## 1) Storage location

All new tables are added to the per-profile `vault.db` (post-unlock), consistent with the existing data model. Automation data is profile-scoped and encrypted at rest via the existing PVK mechanism.

Exception: the reference library is stored outside the vault at `<root_data_dir>/reference_library/` since it contains no secrets.

## 2) Schema changes to existing tables

### 2.1 profile_settings additions

Add columns to `profile_settings` in `vault.db`:

- `autonomous_mode_enabled` (bool, default false) — enables autonomous read-only operations
- `discovery_network_enabled` (bool, default false) — independent network toggle for discovery engine
- `discovery_schedule_hour` (int, default 3) — hour of day for daily discovery search (0-23, local time)
- `dashboard_refresh_interval_seconds` (int, default 3600) — interval between automatic dashboard refreshes
- `dashboard_quiet_hours_start` (int, nullable) — hour to stop background refresh (0-23)
- `dashboard_quiet_hours_end` (int, nullable) — hour to resume background refresh (0-23)
- `automation_max_retries` (int, default 3) — max retry attempts for failed automation actions
- `discovery_retention_days` (int, default 90) — days to keep discovery findings

### 2.2 providers additions

Add columns to `providers` table:

- `dashboard_url` (text, nullable) — URL for the provider's usage dashboard
- `api_base_url` (text, nullable) — base URL for provider's REST API
- `dashboard_supported` (bool, default false) — whether dashboard data collection is available
- `discovery_enabled` (bool, default true) — whether discovery engine monitors this provider

## 3) New tables

### 3.1 dashboard_snapshots

Stores collected dashboard data for each API key.

- `id` (PK text UUID)
- `profile_id` (FK)
- `secret_id` (FK → `secrets.id`)
- `provider_id` (FK → `providers.id`)
- `collected_at` (text, UTC ISO 8601)
- `collection_method` (text enum: `api`, `scrape`, `cached`)
- `collection_status` (text enum: `success`, `partial`, `failed`)
- `usage_stats_json` (text, nullable) — JSON blob of usage statistics
- `config_attributes_json` (text, nullable) — JSON blob of configuration
- `restrictions_json` (text, nullable) — JSON blob of restrictions
- `health_status` (text enum: `valid`, `invalid`, `degraded`, `outage`, `unknown`)
- `service_status` (text enum: `operational`, `degraded`, `outage`, `unknown`)
- `warnings_json` (text, nullable) — JSON array of warning strings
- `error_message_redacted` (text, nullable)

Indexes:

- `(secret_id, collected_at DESC)` — for retrieving latest snapshot per key
- `(profile_id, collected_at DESC)` — for dashboard overview queries

Retention:

- Keep last 24 snapshots per secret (hourly for one day)
- Older snapshots aggregated to `dashboard_daily_summaries`

### 3.2 dashboard_daily_summaries

Aggregated daily dashboard data for historical trends.

- `id` (PK text UUID)
- `profile_id` (FK)
- `secret_id` (FK → `secrets.id`)
- `provider_id` (FK → `providers.id`)
- `summary_date` (text, date only: `YYYY-MM-DD`)
- `avg_usage_percent` (real, nullable)
- `max_usage_percent` (real, nullable)
- `total_cost` (real, nullable)
- `cost_currency` (text, nullable)
- `health_summary` (text) — most common health status for the day
- `collection_success_count` (int)
- `collection_failure_count` (int)

Index:

- `UNIQUE(secret_id, summary_date)`

### 3.3 discovery_findings

Stores API discovery engine results.

- `id` (PK text UUID)
- `profile_id` (FK)
- `provider_id` (FK → `providers.id`)
- `discovered_at` (text, UTC ISO 8601)
- `source_url` (text)
- `source_title` (text)
- `source_snippet` (text)
- `category` (text enum: `capability_change`, `pricing_update`, `deprecation`, `security_advisory`, `new_alternative`, `service_modification`)
- `impact_summary` (text) — AI-generated
- `action_recommendation` (text) — AI-generated
- `urgency` (text enum: `informational`, `advisory`, `action_needed`, `critical`)
- `relevance_score` (real) — 0.0-1.0
- `user_status` (text enum: `new`, `reviewed`, `dismissed`, `actioned`)
- `reviewed_at` (text, nullable, UTC ISO 8601)
- `user_notes` (text, nullable)
- `created_at` (text, UTC ISO 8601)

Indexes:

- `(profile_id, provider_id, discovered_at DESC)`
- `(profile_id, user_status, urgency)`

### 3.4 discovery_search_log

Tracks discovery search executions for rate limiting and audit.

- `id` (PK text UUID)
- `profile_id` (FK)
- `provider_id` (FK → `providers.id`)
- `searched_at` (text, UTC ISO 8601)
- `trigger_type` (text enum: `scheduled`, `on_demand`, `launch_catchup`)
- `queries_executed` (int)
- `results_found` (int)
- `findings_generated` (int)
- `status` (text enum: `success`, `partial`, `failed`)
- `error_message_redacted` (text, nullable)

Index:

- `(profile_id, provider_id, searched_at DESC)`

### 3.5 automation_scripts

Stores AI-generated and user-approved automation scripts.

- `id` (PK text UUID)
- `profile_id` (FK)
- `provider_id` (FK → `providers.id`)
- `task_type` (text enum: `account_creation`, `payment_config`, `billing_restriction`, `api_key_management`, `dashboard_scrape`, `custom`)
- `title` (text)
- `description` (text)
- `script_content` (text) — the Python/Playwright script source
- `model_used` (text) — LLM model that generated the script
- `research_data_json` (text, nullable) — serialized research results
- `plan_data_json` (text, nullable) — serialized execution plan
- `approval_status` (text enum: `pending`, `approved`, `rejected`)
- `approved_at` (text, nullable, UTC ISO 8601)
- `version` (int, default 1)
- `execution_count` (int, default 0)
- `last_executed_at` (text, nullable, UTC ISO 8601)
- `last_execution_status` (text enum: `success`, `failure`, `aborted`, nullable)
- `auto_approve_repeat` (bool, default false) — skip review on repeat execution
- `created_at` (text, UTC ISO 8601)
- `updated_at` (text, UTC ISO 8601)

Indexes:

- `(profile_id, provider_id, task_type)`
- `(profile_id, approval_status)`

### 3.6 automation_executions

Logs each execution of an automation script.

- `id` (PK text UUID)
- `profile_id` (FK)
- `script_id` (FK → `automation_scripts.id`)
- `started_at` (text, UTC ISO 8601)
- `completed_at` (text, nullable, UTC ISO 8601)
- `status` (text enum: `running`, `success`, `failure`, `aborted`, `paused_at_checkpoint`)
- `checkpoints_reached` (int, default 0)
- `checkpoints_approved` (int, default 0)
- `checkpoints_rejected` (int, default 0)
- `error_message_redacted` (text, nullable)
- `debug_screenshot_paths_json` (text, nullable) — local paths to debug screenshots
- `result_summary_json` (text, nullable) — structured execution results

Index:

- `(script_id, started_at DESC)`

### 3.7 hitl_checkpoints

Records human-in-the-loop checkpoint decisions.

- `id` (PK text UUID)
- `profile_id` (FK)
- `execution_id` (FK → `automation_executions.id`)
- `checkpoint_type` (text enum: `financial`, `account`, `irreversible`, `api_key`, `billing`, `script_review`)
- `checkpoint_description` (text)
- `proposed_action` (text)
- `context_json` (text) — non-secret context shown to user
- `decision` (text enum: `approved`, `rejected`, `modified`)
- `user_notes` (text, nullable)
- `decided_at` (text, UTC ISO 8601)

Index:

- `(execution_id, decided_at)`

### 3.8 provider_selectors

Stores versioned CSS/XPath selectors for dashboard scraping.

- `id` (PK text UUID)
- `provider_id` (FK → `providers.id`)
- `data_type` (text) — e.g., `usage_requests`, `config_region`, `restriction_rate_limit`
- `selector_type` (text enum: `css`, `xpath`, `json_path`)
- `selector_value` (text)
- `verified_at` (text, nullable, UTC ISO 8601)
- `verification_status` (text enum: `verified`, `unverified`, `broken`)
- `version` (int, default 1)
- `created_at` (text, UTC ISO 8601)
- `updated_at` (text, UTC ISO 8601)

Index:

- `UNIQUE(provider_id, data_type, version)`

### 3.9 service_recommendations

Stores AI-generated service recommendations from markdown analysis.

- `id` (PK text UUID)
- `profile_id` (FK)
- `project_id` (FK → `projects.id`, nullable)
- `requirement_text` (text) — original text from markdown
- `capability_needed` (text) — normalized capability description
- `recommended_provider_id` (text, nullable) — FK if existing provider
- `recommended_service_name` (text)
- `rationale` (text) — AI-generated
- `pricing_summary` (text, nullable)
- `free_tier_available` (bool, nullable)
- `documentation_url` (text, nullable)
- `match_score` (real) — 0.0-1.0
- `user_status` (text enum: `new`, `accepted`, `rejected`)
- `created_at` (text, UTC ISO 8601)

Index:

- `(profile_id, project_id, user_status)`

### 3.10 reference_library_manifest

Tracks downloaded reference library content. Stored in `<root_data_dir>/reference_library/manifest.db` (separate SQLite, not in vault).

- `id` (PK text UUID)
- `source_name` (text) — e.g., `playwright-python`, `puppeteer`
- `source_url` (text) — GitHub repository URL
- `commit_sha` (text)
- `downloaded_at` (text, UTC ISO 8601)
- `local_path` (text) — relative path within reference_library/
- `file_count` (int)
- `total_size_bytes` (int)
- `checksum` (text) — SHA-256 of downloaded archive

Index:

- `UNIQUE(source_name)`

## 4) Migration strategy

### 4.1 Migration ordering

These tables are added as a post-MVP migration:

1. Add columns to `profile_settings` (ALTER TABLE)
2. Add columns to `providers` (ALTER TABLE)
3. Create `dashboard_snapshots`
4. Create `dashboard_daily_summaries`
5. Create `discovery_findings`
6. Create `discovery_search_log`
7. Create `automation_scripts`
8. Create `automation_executions`
9. Create `hitl_checkpoints`
10. Create `provider_selectors`
11. Create `service_recommendations`

The `reference_library_manifest` table is in a separate database and created on first use.

### 4.2 Backward compatibility

- All new columns on existing tables have defaults or are nullable
- The automation subsystem is fully optional — the app functions without these tables
- Migration is applied only when the user first enables any automation feature

## 5) Data boundaries

### 5.1 Encryption

- All tables in `vault.db` are protected by the existing PVK encryption at the application layer
- `reference_library_manifest.db` is not encrypted (contains no secrets)
- Debug screenshots are stored unencrypted but auto-deleted after retention period

### 5.2 Redaction

- `error_message_redacted` fields must never contain secrets
- `context_json` in `hitl_checkpoints` must not contain secret values
- `script_content` in `automation_scripts` must use placeholder tokens, not real credentials
- `source_snippet` in `discovery_findings` is public web content and does not require redaction

### 5.3 Retention

| Table | Retention policy |
|---|---|
| `dashboard_snapshots` | 24 rows per secret, then aggregated to daily summaries |
| `dashboard_daily_summaries` | 365 days (configurable) |
| `discovery_findings` | 90 days default (configurable via `discovery_retention_days`) |
| `discovery_search_log` | 30 days |
| `automation_executions` | 90 days |
| `hitl_checkpoints` | 90 days |
| Debug screenshots | 7 days |

## 6) Acceptance criteria

- All new tables follow the existing data model conventions (UTC ISO 8601 timestamps, text UUIDs)
- Migration is backward-compatible and does not affect existing functionality
- Encryption boundaries are maintained
- Redaction rules are enforced for all new fields
- Retention policies are configurable and automatically enforced
