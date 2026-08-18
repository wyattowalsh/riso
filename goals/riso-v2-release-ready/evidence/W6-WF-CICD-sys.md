# W6-WF-CICD-sys — GitLab/Circle rust+go cwd

- Wave: W6 / SYS payload workflow
- Task: close `PAY-P1-gitlab-circle-sys-cwd`
- Date: 2026-08-18
- Repo: `/Users/ww/dev/projects/riso` · branch `main` · HEAD `f60fac8ea40e12fb0ad64f6d49ff6bf74b9a1b87`
- Exclusive writes: `template/files/.gitlab/.gitlab-ci.yml.jinja`, `template/files/.circleci/config.yml.jinja`, this file
- `samples/*/render/**` writes: **0**
- Commits / tags / pushes: **0**
- Status: **source-closed**

## Finding (W6-R03)

Rust jobs ran `cargo …` at dest root (crate is `rust/Cargo.toml`). Go jobs ran `go build … ./cmd/...` at dest root (module is `go/`; bins are `./cli` / `./api` per `go/Makefile.jinja` L42–45; there is no `cmd/` at module root). Official `rust-*` / `go-*` dests use `ci_platform: github-actions`, so this is P1 not P0.

## Change

Match generated `go/{Makefile,justfile}.jinja` and `rust/{Makefile,justfile}.jinja`:

1. GitLab `.rust-base` / `.go-base` `before_script`: `cd rust` / `cd go` (same shell as `script`).
1. Circle rust/go `run` steps: `working_directory: rust` / `working_directory: go` (checkout stays dest-root).
1. Go build packages: `./cli`, `./api`, MCP `go -C mcp build … ./cmd/server`. No dest-root `./cmd/...`.
1. Go lint/test: root module when CLI/API; `go -C mcp` when MCP. Output to `go/bin/`.
1. Artifact/cache paths follow the new cwd (`rust/target`, `go/bin`, `go/coverage.txt`). Circle cargo cache keys `rust/Cargo.toml` (lockfile is not shipped).
1. Node/Python jobs untouched (`uv --directory python`, dest-root `pnpm`).

## Live (source)

| Path        | After                                                                                                        |
| ----------- | ------------------------------------------------------------------------------------------------------------ |
| GitLab rust | `.rust-base` L225 `cd rust`; cache/artifacts `rust/target/**`; cargo flags unchanged                         |
| GitLab go   | `.go-base` L279 `cd go`; build L327–333 `./cli` / `./api` / `go -C mcp … ./cmd/server`; artifacts `go/bin/`  |
| Circle rust | every cargo `run` has `working_directory: rust`; cache `rust/target` + checksum `rust/Cargo.toml`            |
| Circle go   | every go `run` has `working_directory: go`; no `go/mod-download` at dest root; same build packages as GitLab |

## Commands

```text
git rev-parse --show-toplevel   # /Users/ww/dev/projects/riso
git branch --show-current       # main
git rev-parse HEAD              # f60fac8ea40e12fb0ad64f6d49ff6bf74b9a1b87
uv run python scripts/ci/validate_jinja_templates.py \
  template/files/.gitlab/.gitlab-ci.yml.jinja \
  template/files/.circleci/config.yml.jinja
# Validated 2 Jinja template(s): all OK
uv run pytest tests/unit/test_gitlab_ci_templates.py tests/unit/test_circleci_templates.py -q -n 0
# 26 passed
# throwaway render: rust-cli → cd rust / working_directory: rust
#   go-cli → ./cli; go-api → ./api; go-mcp → go -C mcp … ./cmd/server
#   ./cmd/... absent; python still uv --directory python; node still pnpm
git status --short -- 'samples/*/render/**'   # empty
```

## Residuals (not this lock)

| Residual                                                                   | Disposition                                                                                           |
| -------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Official `rust-*` / `go-*` dests stay `ci_platform: github-actions`        | no official GitLab/Circle dest to re-render; PLATFORM only if a future sample selects those platforms |
| Circle `go/load-cache` / `go/save-cache` still checksum dest-root `go.sum` | orb default; cache miss only; downloads now run in `go/`                                              |
| GHA rust quality is MCP-only (`rust/mcp`); no rust-api / go-api GHA jobs   | out of this lock; same class as W6-R03 “not elevated”                                                 |

## Path lock

| Class                                   | Count                                                            |
| --------------------------------------- | ---------------------------------------------------------------- |
| Product write                           | 2 — `.gitlab/.gitlab-ci.yml.jinja`, `.circleci/config.yml.jinja` |
| Evidence                                | this file                                                        |
| `samples/*/render/**`                   | 0                                                                |
| Lockfile / secret / commit / tag / push | 0                                                                |

## Verdict

```yaml
id: PAY-P1-gitlab-circle-sys-cwd
status: source-closed
files:
  - template/files/.gitlab/.gitlab-ci.yml.jinja
  - template/files/.circleci/config.yml.jinja
summary: >
  GitLab/Circle rust and go jobs no longer run at dest root. cargo uses
  rust/; go uses go/ with Makefile packages ./cli ./api and go -C mcp
  ./cmd/server. Node and Python jobs unchanged.
```
