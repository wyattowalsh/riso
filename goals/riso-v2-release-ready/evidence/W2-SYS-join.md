# W2-SYS join

- Wave: W2 / lane SYS
- Tasks: `SYS-T01`, `SYS-T02`
- Status: **green**
- Repo: `/Users/ww/dev/projects/riso` branch `main` HEAD `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b`
- Exclusive writes this wave: **evidence only** (no `template/files/go/**` or `template/files/rust/**` rewrite)
- `samples/*/render/**` writes: **0**
- Residual file: none (`residuals/SYS.md` not created)

## Task results

| ID | Decision | Verify | Status |
| --- | --- | --- | --- |
| SYS-T01 | keep `go.work` `.` + `./mcp` (file identical to HEAD) | `uv run pytest tests/unit/test_go_templates.py -q -n 0` → **49 passed** | green |
| SYS-T02 | rust `_exclude`s unchanged (COORD outbox: no change; 7/7 equal HEAD) | rust-api / rust-cli / rust-mcp `riso validate --json` → **ok:true** | green |

## Extra (owned trees, not a write)

| Check | Result |
| --- | --- |
| `find template/files/go template/files/rust -name '*.jinja' \| xargs uv run python scripts/ci/validate_jinja_templates.py` | **80** templates all OK |
| `go/cli/internal/**` | still absent |
| COORD `copier.yml` | not edited |

Pre-existing dirty go/rust polish (W0 KEEP, including untracked `template/files/rust/mcp/src/server.rs.jinja`) left untouched.

## Not SYS (do not residual here)

- `samples/*/copier-answers.yml` edits → PLATFORM
- rust `_exclude` line edits → COORD (`copier.yml`)
- go-api `api_features` historical residual (prior lane) is answers-lock, not SYS-T01/T02
