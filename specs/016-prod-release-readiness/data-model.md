# Data Model: Production Release Readiness

## CanonicalAnswer

Represents the only supported Copier answer surface.

- `api_module`: enabled or disabled.
- `api_languages`: ordered list of selected API languages.
- `docs_module`: enabled or disabled.
- `docs_framework`: selected docs implementation when docs are enabled.
- `mcp_module`: enabled or disabled.
- `mcp_languages`: ordered list of selected MCP languages.
- `saas_infra_module`: enabled or disabled.

Removed keys are invalid input, not aliases.

## RenderEvidence

Records proof from template rendering and sample smoke checks.

- `variant`: sample or temp-render name.
- `answers_path`: checked answer file or temp answer file.
- `metadata_path`: produced metadata artifact.
- `commands`: exact commands run.
- `result`: passed, failed, or blocked.
- `notes`: concise explanation of any blocker.

## ReleaseGate

Describes a release-readiness command and whether it blocks handoff.

- `id`: stable gate identifier.
- `command`: exact shell command.
- `owner`: responsible workstream.
- `blocking`: true for release-critical gates.
- `evidence`: expected output or artifact.

## SkillMirror

Represents a maintainer skill mirrored across agent runtimes.

- `source`: `.agents/skills/riso-release-readiness`.
- `mirror`: `.claude/skills/riso-release-readiness`.
- `required_files`: `SKILL.md`, references, scripts.
- `invariant`: every mirrored file is byte-identical.

## ReleaseTodoEntry

Tracks the final handoff ledger in `tmp/riso-prod-ready-release-todo.md`.

- `timestamp`: local run timestamp.
- `gate`: release gate identifier.
- `command`: exact command run.
- `status`: pass, fail, skipped, or blocked.
- `evidence`: exact summary output.
- `next_action`: owner and remediation when not passed.

