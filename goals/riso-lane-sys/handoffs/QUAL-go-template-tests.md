# QUAL handoff: maintainer `tests/unit/test_go_templates.py` is outside SYS write root

**From:** SYS lane  
**To:** QUAL / maintainer  
**Priority:** P3  

## Context

SYS exclusive write roots are `template/files/go/**` and `template/files/rust/**`.  
`tests/unit/test_go_templates.py` remains the maintainer gate for Go templates and **passed** after SYS changes (42 tests).

## Notable template changes tests should keep covering

1. Shared packages: `template/files/go/internal/config`, `template/files/go/internal/logger`
2. API imports use `{{ project_slug }}/internal/config` (not `cli/internal`)
3. MCP `go.mod` uses `go {{ go_version | default('1.22') }}` (test currently expects default `1.22` when unset)
4. Framework matrix gin/fiber/echo/chi still rendered in `server.go.jinja`

## Optional QUAL follow-ups

- Add explicit assertion that API-only render has no `cli/internal` import
- Add existence checks for `go/internal/config` and `go/internal/logger`
- When raising MCP default to `1.24`, update `test_mcp_go_mod_renders_when_enabled`

SYS did not edit the test file; keep running `uv run pytest tests/unit/test_go_templates.py -q` in CI.
