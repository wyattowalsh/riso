---
name: riso-scaffold
description: >-
  Scaffold Python/Node/full-stack projects from the Riso Copier template using the
  `riso` CLI. Use when the user wants to generate a Riso project, run copier copy/update,
  validate copier-answers.yml, list template variants, explore module catalog, or
  scaffold from the riso template. Triggers: "scaffold riso", "riso template", "copier copy riso",
  "generate riso project", "riso variants", "validate copier answers".
---

# Riso Scaffold

Use the `riso` CLI with `--json` output. Read `template/` files directly for file content.

## Workflow

1. `uv run riso doctor --json` — verify copier, template path, uv
1. `uv run riso variants list --json` — discover sample configurations
1. `uv run riso prompts --json` — inspect copier.yml questions
1. Build or load `copier-answers.yml`
1. `uv run riso validate --answers-file copier-answers.yml --json`
1. `uv run riso copy ./dest --answers-file copier-answers.yml --json`
1. Optional dry-run: add `--dry-run` to copy/update/recopy

## Stop rules

- Never use removed answer keys (see `references/removed-keys.md`)
- Never write to `samples/*/render/` — use temp directories
- Always use `uv run riso`, never `riso-mcp`
- Clone repo or pass `--template-path` when template is not in checkout

## References

- `references/workflows.md` — copy/update/recopy command sequences
- `references/removed-keys.md` — legacy keys that fail validation
- `references/cli-contract.md` — JSON envelope and exit codes

## Commands

See `references/workflows.md` for full command tables.
