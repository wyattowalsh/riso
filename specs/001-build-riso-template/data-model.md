# Data Model: Riso Template Foundation

## Entity: Template Module Definition
- **Description**: Represents an optional capability that the template can scaffold on demand.
- **Fields**:
  - `name` (string, required): Human-readable module identifier (e.g., `cli`, `api_python`).
  - `prompt_key` (string, required): Copier prompt name controlling inclusion.
  - `default_state` (enum: `enabled`, `disabled`, required): Indicates baseline behavior.
  - `dependencies` (list[string], optional): Tooling or other modules required (e.g., `uv`, `pnpm`, `shared_logic`).
  - `docs_path` (string, optional): Documentation fragment generated when the module is selected.
  - `ci_jobs` (list[string], optional): CI jobs that must pass when the module is enabled.
  - `validation_commands` (list[string], required): Commands executed post-render to validate module health.
- **Relationships**:
  - References `Sample Project Artifact` instances that demonstrate the module in action.

## Entity: Sample Project Artifact
- **Description**: Concrete render of the template captured for CI verification and documentation snapshots.
- **Fields**:
  - `variant_name` (string, required): Identifier such as `default`, `cli-docs`, `api-monorepo`, `full-stack`.
  - `prompt_answers` (map[string, any], required): Prompt selections used to generate the sample.
  - `ci_pipeline` (string, required): Workflow file that validates the sample.
  - `doc_links` (list[string], optional): Generated documentation URLs/screenshots tied to the variant.
  - `last_regenerated` (date, required): Timestamp of the most recent successful regeneration.
- **Relationships**:
  - Includes one or more `Template Module Definition` entries to show combined configurations.

## Entity: Governance Checkpoint
- **Description**: Recorded assertion that automation enforces constitutional principles for a given template revision.
- **Fields**:
  - `principle` (enum: `template_sovereignty`, `deterministic_generation`, `minimal_baseline`, `documented_scaffolds`, `automation_governed`, required)
  - `evidence` (string, required): Link or reference to CI artifacts/logs proving compliance.
  - `status` (enum: `pass`, `fail`, `needs_review`, required): Current compliance state.
  - `recorded_at` (datetime, required): When the checkpoint was captured.
  - `owner` (string, required): Maintainer accountable for the evidence trail.
- **Relationships**:
  - Tied to specific `Sample Project Artifact` instances when evidence is render-specific.
