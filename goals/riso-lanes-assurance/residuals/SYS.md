# Residual — SYS (W2)

## Status

SYS payload trees (`template/files/go/**`, `template/files/rust/**`) modernized and committed.
SYS-JOIN is **partially residualed** on sample answers outside SYS write lock.

## Residual items

### 1. `go-api` validate — `api_features: none` string

| Field | Value |
| ----- | ----- |
| **task_id** | SYS-JOIN / PLATFORM-go-api-features-answers |
| **owner** | PLATFORM |
| **command** | `uv run riso validate --answers-file samples/go-api/copier-answers.yml --json` |
| **blocking reason** | Answers file has `api_features: none` (string). Multiselect expects a list after W1-H05 normalize. SYS must not edit `samples/*/copier-answers.yml`. |
| **redacted log** | `errors: ["api_features: expected list for multiselect"]` |
| **evidence** | `goals/riso-lanes-assurance/evidence/W2-SYS-validate-go-api.json` |
| **fix** | Change to list form (e.g. `api_features: []` or omit / use allowed tokens). PLATFORM PL-T02*. |

### 2. `PLATFORM-rust-samples` (still open)

| Field | Value |
| ----- | ----- |
| **task_id** | SYS-H / PL-T03 |
| **owner** | PLATFORM |
| **command** | create `samples/rust-{api,cli,mcp}/copier-answers.yml` then validate |
| **blocking reason** | No rust sample answers; template payload is ready (Cargo/MCP MSRV 1.81, excludes applied). |
| **source** | `goals/riso-lane-sys/handoffs/PLATFORM-rust-samples.md` |

### 3. `QUAL-go-template-tests` (optional P3)

| Field | Value |
| ----- | ----- |
| **task_id** | SYS-JOIN / PL-T04 |
| **owner** | PLATFORM |
| **command** | `uv run pytest tests/unit/test_go_templates.py -q` (currently **42 passed**) |
| **blocking reason** | Test file outside SYS write root. Optional: assert no `cli/internal` imports; shared `go/internal/*` existence; MCP default 1.24 when raised. |
| **source** | `goals/riso-lane-sys/handoffs/QUAL-go-template-tests.md` |

## SYS-owned gates (green)

| Check | Result |
| ----- | ------ |
| go-cli validate | ok:true |
| go-mcp validate | ok:true |
| pytest `test_go_templates.py` | 42 passed |
| jinja go+rust (79 files) | all OK |
| Commits | `33e544e` modernize; `abcb762` drop reintroduced cli/internal |

## Not residuals

- COORD `go_version`+MCP and rust `_exclude` — **applied** in W1.
