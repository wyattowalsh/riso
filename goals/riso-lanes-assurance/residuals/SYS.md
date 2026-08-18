# Residual — SYS (W2)

## Status

SYS payload trees (`template/files/go/**`, `template/files/rust/**`) modernized and committed.
SYS-JOIN answer/sample follow-through is **historical / closed** (W3 PLATFORM). Rechecked 2026-08-18: `samples/go-api` has `api_features: []`; `samples/rust-{api,cli,mcp}/copier-answers.yml` exist.

**Active bar residual (not SYS-owned):** PLATFORM R1 full `render_matrix` — [`PLATFORM.md`](./PLATFORM.md). See [`ASSURANCE.md`](../ASSURANCE.md).

## Residual items

### 1. `go-api` validate — `api_features` list shape — **CLOSED (W3)**

| Field | Value |
| ----- | ----- |
| **status** | historical / closed |
| **task_id** | SYS-JOIN / PLATFORM-go-api-features-answers · PL-T02 / PL-T05 |
| **owner** | PLATFORM |
| **blocking** | No — W3 answers list-normalize landed; go-api validate ok |
| **applied** | `samples/go-api/copier-answers.yml` is `api_features: []` (not scalar `none`). |
| **evidence** | [`ASSURANCE.md`](../ASSURANCE.md) A-T02 · `evidence/W5-validate-37.json` · `evidence/W3-PL-T05-validate-summary.json` · `evidence/W4-A-T01-validate-spot.json` · historical W2: `evidence/W2-SYS-validate-go-api.json` |

### 2. `PLATFORM-rust-samples` — **CLOSED (W3)**

| Field | Value |
| ----- | ----- |
| **status** | historical / closed |
| **task_id** | SYS-H / PL-T03 |
| **owner** | PLATFORM |
| **applied** | `samples/rust-api`, `samples/rust-cli`, `samples/rust-mcp` each have `copier-answers.yml` (rust-api `api_features: []`). Included in W3-PL-T05 / W5 37/37 validate. |
| **source** | `goals/riso-lane-sys/handoffs/PLATFORM-rust-samples.md` |
| **evidence** | [`ASSURANCE.md`](../ASSURANCE.md) A-T02 · `evidence/W5-validate-37.json` · `evidence/W3-PL-T05-validate-summary.json` |

### 3. `QUAL-go-template-tests` — **CLOSED (W3)**

| Field | Value |
| ----- | ----- |
| **status** | historical / closed (optional P3; applied) |
| **task_id** | SYS-JOIN / PL-T04 |
| **owner** | PLATFORM |
| **applied** | QUAL shared-internal asserts landed. W3-PL-T04 / `W3-PL-T07-quality-tool-fix.txt`: go template tests green including `TestGoSharedInternalPackages` (no `cli/internal` imports; shared `go/internal/*`). |
| **source** | `goals/riso-lane-sys/handoffs/QUAL-go-template-tests.md` |
| **evidence** | [`ASSURANCE.md`](../ASSURANCE.md) A-T02 · `evidence/W3-PL-T04-go-templates.txt` · `evidence/W3-PL-T07-quality-tool-fix.txt` |

## SYS-owned gates (green)

| Check | Result |
| ----- | ------ |
| go-cli validate | ok:true |
| go-mcp validate | ok:true |
| pytest `test_go_templates.py` | 42 passed (W2); 45 + QUAL after PL-T04 |
| jinja go+rust (79 files) | all OK |
| Commits | `33e544e` modernize; `abcb762` drop reintroduced cli/internal |

## Not residuals

- COORD `go_version`+MCP and rust `_exclude` — **applied** in W1.
- go-api answers, rust sample answers, QUAL go asserts — **applied** in W3.
