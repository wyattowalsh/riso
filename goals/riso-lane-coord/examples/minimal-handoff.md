# EXAMPLE ONLY — do not apply

# Handoff: `example-docs-flag-doc`

| Field | Value |
|-------|-------|
| **change_id** | `example-docs-flag-doc` |
| **requesting_lane** | `platform` |
| **summary** | Example: document-only illustration of handoff fields (fictional key) |
| **status** | `proposed` |
| **needs_shared_generation_gates** | `no` |

> **Not a real contract change.** Agents must not edit `copier.yml` from this file.

## Prompt keys

| key | type | default | when | help | choices |
|-----|------|---------|------|------|---------|
| `example_coord_doc_flag` | str | `disabled` | `true` | Example flag for docs only | `enabled`, `disabled` |

## Hook validation rules

| condition | error message | preferred surface |
|-----------|---------------|-------------------|
| _(none for example)_ | | |

## Module catalog rows

| name | prompt_key | default_state | selected_state | dependencies | docs_path | ci_jobs | validation_commands |
|------|------------|---------------|----------------|--------------|-----------|---------|---------------------|
| _(none)_ | | | | | | | |

## Macros

| file | change |
|------|--------|
| _(none)_ | |

## Context snippets

| filename | intent |
|----------|--------|
| _(none)_ | |

## CLI / generation_gates handoff

| Item | Detail |
|------|--------|
| Needed? | `no` |
| Files | n/a |
| Summary | n/a |

## Payload follow-ups

| lane | exclusive paths | acceptance note |
|------|-----------------|-----------------|
| _(none)_ | | |

## Samples to re-validate

| path |
|------|
| `samples/default/copier-answers.yml` |

## Non-goals

- Any real template mutation
