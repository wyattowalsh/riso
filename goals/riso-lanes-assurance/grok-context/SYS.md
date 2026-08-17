# Lane SYS

## Mission (3 lines)
Finish + heavy planned modernization of Go + Rust payload under `template/files/go/**` and `template/files/rust/**`.
Split GO vs RS sub-parallel when locks disjoint; join validates go-api/cli/mcp + pytest go templates + jinja.
Handoffs to COORD (excludes, go_version) and PLATFORM (rust samples, QUAL tests) — never silent cross-lane.

## Exclusive write roots
- `template/files/go/**`
- `template/files/rust/**` (~79 jinja)
- `goals/riso-lane-sys/**`
- Sub-locks: SYS-GO-* → `go/**` only; SYS-RS-* → `rust/**` only

## Forbidden roots
- `samples/*/render/**`, lockfile hand-edits, secrets, `riso-mcp`
- `tests/unit/test_go_templates.py` (PLATFORM / QUAL — handoff only)
- `samples/*/copier-answers.yml` (PLATFORM)
- COORD contract trees; other payload lanes

## Facts file path
- Umbrella: `goals/riso-lanes-assurance/facts.md`
- Lane: `goals/riso-lane-sys/facts.md` + `plan.md` + `plan.fileshards.json` + `plan.taskgraph.json` + `baseline.md`
- Plan: `goals/riso-lanes-assurance/plan.md` (SYS sub-graph)
- Graph: `goals/riso-lanes-assurance/plan.taskgraph.json`
- Board: `goals/riso-lanes-assurance/handoffs-board.md`
- Dirty map: `goals/riso-lanes-assurance/inventory-dirty.md`

## Plan tasks this agent owns (IDs)
**Barrier:** W1-OUT. GO and RS may run in parallel.

| ID | Work | parallel_group |
|----|------|----------------|
| SYS-GO-01 | Go shared foundation (API not depending on cli/internal) | G1 |
| SYS-GO-02 | Go API ×4 frameworks (gin/fiber/echo/chi) | G2 |
| SYS-GO-03 | Go CLI Cobra | G2 |
| SYS-GO-04 | Go MCP | G2 |
| SYS-GO-05 | Go root Makefile/justfile/mod/work/Dockerfile | G3 |
| SYS-RS-01 | Rust root Cargo/tooling/MSRV | R1 |
| SYS-RS-02 | Rust API Actix | R2 |
| SYS-RS-03 | Rust CLI Clap | R2 |
| SYS-RS-04 | Rust MCP | R2 |
| SYS-RS-05 | Rust docs/tests | R3 |
| SYS-JOIN | validate go-api/cli/mcp + pytest test_go_templates + jinja go/rust | SJ |
| SYS-H | PLATFORM handoffs still needed? update board | SJ |

Open handoffs (COORD apply in W1; PLATFORM in W3):
- `COORD-go-version-mcp` → W1-H02
- `COORD-rust-module-excludes` → W1-H03
- `PLATFORM-rust-samples` → PL-T03
- `PLATFORM-go-api-features-answers` → PL-T02* (monitor)
- `QUAL-go-template-tests` → PL-T04 / SYS-JOIN

## COORD outbox paths to read
- `goals/riso-lane-coord/outbox/` for go_version + rust excludes after W1
- Filed handoffs:
  - `goals/riso-lane-sys/handoffs/COORD-go-version-mcp.md`
  - `goals/riso-lane-sys/handoffs/COORD-rust-module-excludes.md`
  - `goals/riso-lane-sys/handoffs/PLATFORM-rust-samples.md`
  - `goals/riso-lane-sys/handoffs/PLATFORM-go-api-features-answers.md`
  - `goals/riso-lane-sys/handoffs/QUAL-go-template-tests.md`

## Dirty paths assigned
From inventory (41 paths — bulk of product dirty work):
- Package: `goals/riso-lane-sys/**` (facts*, goal, plan*, handoffs/*, baseline)
- Go (M/D/??): air.toml, Makefile, api server/main, cli cmd root/serve, deleted cli/internal/{config,logger}, go.work, new `go/internal/{config,logger}`, justfile, mcp README/go.mod
- Rust (M): ARCHITECTURE, Cargo.toml, Makefile, QUICKSTART, README, api/handlers/health, build.rs, justfile, mcp/Cargo.toml, src/main.rs

## Verify commands (copy-paste)
```bash
uv run riso validate --answers-file samples/go-api/copier-answers.yml --json
uv run riso validate --answers-file samples/go-cli/copier-answers.yml --json
uv run riso validate --answers-file samples/go-mcp/copier-answers.yml --json   # needs W1-H02
uv run pytest tests/unit/test_go_templates.py -q                              # read-only for SYS; PLATFORM owns edits
uv run python scripts/ci/validate_jinja_templates.py
```

## Handoff template path if blocked
- Residual: `goals/riso-lanes-assurance/residuals/SYS.md`
- Evidence: `goals/riso-lanes-assurance/evidence/`
- Contract excludes / go_version → COORD; answers/samples/QUAL tests → PLATFORM

## Done =
SYS-GO-* + SYS-RS-* + SYS-JOIN + SYS-H green or residualed; board updated for remaining PLATFORM handoffs; evidence under `goals/riso-lanes-assurance/evidence/`.
