# PLATFORM/COORD handoff: `api_features` multiselect shape (go-api sample)

**From:** SYS lane  
**To:** PLATFORM (answers) / COORD (schema if needed)  
**Priority:** P2 (was P1; current validate is green)

## Context

Earlier exploration observed:

```text
api_features: expected list for multiselect
```

when validating `samples/go-api/copier-answers.yml` with `api_features: none`.

## Current observation (SYS run)

As of this SYS goal execution, all three validate cleanly:

```bash
uv run riso validate --answers-file samples/go-api/copier-answers.yml --json  # ok: true
uv run riso validate --answers-file samples/go-cli/copier-answers.yml --json  # ok: true
uv run riso validate --answers-file samples/go-mcp/copier-answers.yml --json  # ok: true
```

If regressions reappear, ensure multiselect answers are lists (`[]` or feature ids), not the string `none`.

## SYS scope

No sample answer edits. No template change required for this key.
