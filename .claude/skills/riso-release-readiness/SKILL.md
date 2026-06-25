---
name: riso-release-readiness
description: Use when preparing the Riso repository for a production release, especially to coordinate no-legacy Copier answer cleanup, release gates, render validation, docs hardening, package dry-runs, and final evidence capture.
---

# Riso Release Readiness

Use this skill only in the Riso maintainer repository. Do not copy it into
rendered project payloads.

## Workflow

1. Inspect `git status --short --branch` and preserve unrelated dirty work.
1. Read `specs/016-prod-release-readiness/` before editing release surfaces.
1. Enforce the no-legacy-answer policy in
   `references/no-legacy-answer-policy.md`.
1. Use the validation ladder in `references/release-gates.md`.
1. Use the parallel task graph in `references/task-graph.md` to split work while
   keeping same-file edits serialized.
1. Record final command evidence in `tmp/riso-prod-ready-release-todo.md`.

## Stop Rules

- Stop before branch switches, stashes, resets, rebases, commits, tags, pushes,
  or publishing.
- Stop on secrets or generated artifacts that contain sensitive data.
- Stop if a release-critical gate is made non-blocking instead of fixed.
- Stop if compatibility logic is added for removed answer keys.
- Stop if `samples/*/render` would need manual edits.

## Commands

```bash
uv run python scripts/ci/validate_release_readiness_skill.py
uv run --group docs sphinx-build -W -b html docs /tmp/riso-docs-build-release
uv run python scripts/ci/validate_workflows.py
uv run python scripts/ci/validate_release_configs.py
```

Use `scripts/collect_release_evidence.py` when a compact JSON summary of
evidence files is useful.
