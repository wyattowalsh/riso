# W2 SYS-T01 — keep `go.work` `.` + `./mcp`

- Task: `SYS-T01`
- Wave: W2 / lane SYS
- Deps: `W1-OUT` (present under `evidence/coord-outbox/`)
- Exclusive write roots: `template/files/go/**` (this task)
- Verify: `uv run pytest tests/unit/test_go_templates.py -q -n 0`
- Status: **green**
- `samples/*/render/**` writes: **0**

## Repo identity

| Field | Value |
| --- | --- |
| CWD / toplevel | `/Users/ww/dev/projects/riso` (`git rev-parse --show-toplevel`) |
| Branch | `main` (unchanged; no checkout / stash / reset) |
| HEAD | `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b` |

## Contract

`plan.md` keep list + W2 `SYS-T01`: generated `go.work` lists workspace modules `.` and `./mcp` only. Never `./cli` or `./api` (those are packages under the root module).

`template/files/go/go.work.jinja` vs HEAD: **identical** (no SYS rewrite required).

```text
use (
{%- if _has_root %}
	.
{%- endif %}
{%- if _has_mcp %}
	./mcp
{%- endif %}
)
```

Comment in-file: “Do not list ./cli or ./api — those directories are packages, not modules.”

`template/files/go/cli/internal/**` stays **absent** (W0 drop).

## Verify

| Command | Result |
| --- | --- |
| `uv run pytest tests/unit/test_go_templates.py -q -n 0` | **49 passed** — log `W2-SYS-pytest-go-templates.txt` |
| `TestGoWorkTemplate::test_go_work_monorepo_cli_api_mcp_lists_root_and_mcp` | passed (`.` + `./mcp`; no `./cli`/`./api`) |
| `test_go_work_monorepo_mcp_only_lists_mcp` | passed |
| `test_go_work_monorepo_cli_only_lists_root` | passed |
| `test_go_work_single_package_cli_is_empty` | passed |

No payload edit. Existing dirty go polish left in place (W0 KEEP).
