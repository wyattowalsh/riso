# W2 SYS-T02 — rust module excludes unchanged

- Task: `SYS-T02`
- Wave: W2 / lane SYS
- Deps: `W1-OUT`
- Exclusive write roots: `template/files/rust/**` (this task)
- Verify: rust sample `riso validate --json`
- Status: **green**
- `samples/*/render/**` writes: **0**

## Repo identity

| Field | Value |
| --- | --- |
| CWD / toplevel | `/Users/ww/dev/projects/riso` |
| Branch | `main` (unchanged) |
| HEAD | `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b` |

## COORD outbox

No W1-OUT CID requests a rust `_exclude` change.

| Outbox | SYS instruction |
| --- | --- |
| `coord-outbox/remap-ssot.md` | rust excludes **unchanged** unless a later COORD outbox says otherwise |
| `coord-outbox/openspec-extra.md` | “Rust / other module excludes are **unchanged** by this CID (SYS-T02).” |
| other CIDs (`hooks-apply`, `mise-always`, `generation-gates-saas-auth`, `policy-8keys`) | no rust exclude delta |

SYS does **not** own `template/copier.yml` (COORD lock). No silent cross-lane edit.

## Excludes (read-only audit)

Worktree rust `_exclude` lines **equal** `HEAD:template/copier.yml` (7/7). Snapshot: `W2-SYS-rust-excludes.txt`.

| Path excluded when | Line (content) |
| --- | --- |
| `task_runner` in `just`/`none` | `rust/Makefile` |
| `task_runner` in `makefile`/`none` | `rust/justfile` |
| no rust CLI/API/MCP | `rust/` |
| rust MCP off | `rust/mcp/` |
| rust CLI off | `rust/cli/` |
| rust API off | `rust/api/` |
| no rust CLI/API/MCP | `rust/Cargo.toml` |

## Verify

| Sample | Command | `ok` |
| --- | --- | --- |
| rust-api | `uv run riso validate --answers-file samples/rust-api/copier-answers.yml --json` | **true** (`W2-SYS-validate-rust-api.json`) |
| rust-cli | `uv run riso validate --answers-file samples/rust-cli/copier-answers.yml --json` | **true** (`W2-SYS-validate-rust-cli.json`) |
| rust-mcp | `uv run riso validate --answers-file samples/rust-mcp/copier-answers.yml --json` | **true** (`W2-SYS-validate-rust-mcp.json`) |

Warnings only: `_commit` / `_src_path` unknown keys (Copier metadata). No removed-key errors.

Sample answers were **not** edited (PLATFORM lock). No rust payload rewrite for excludes.
