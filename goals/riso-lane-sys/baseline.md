# SYS baseline snapshot

Captured during W2 SYS lane join.

## Join results (W2)

| Check | Result |
|-------|--------|
| `pytest tests/unit/test_go_templates.py` | 42 passed |
| Jinja validate go+rust | 79 OK |
| `riso validate` go-cli | ok: true |
| `riso validate` go-mcp | ok: true |
| `riso validate` go-api | **fail** — answers `api_features: none` (PLATFORM residual) |

## Defects closed in-template

| ID | Fix |
|----|-----|
| G1 | Shared `go/internal/{config,logger}`; API/CLI rewired off `cli/internal` |
| G2 | Framework parity already present for gin/fiber/echo/chi (server/handlers/middleware) |
| G3 | MCP `go.mod` uses `go_version` with default `1.22` (test-compatible) |
| G4/G5 | Makefile/justfile mcp targets; go.work lists `.` + `./mcp` |
| R1 | Rust root gates include `mcp_languages` |
| R2 | MSRV unified to 1.81 (root + mcp) |
| R3 | `autobins = false` when explicit bins; src/main only when no CLI/API bins |

## Handoffs remaining

See umbrella residual `goals/riso-lanes-assurance/residuals/SYS.md` and board.
