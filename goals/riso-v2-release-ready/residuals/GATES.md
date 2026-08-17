# Residual — Lane GATES (W5-CLOSE-GATES)

## Summary

Lock P0/P1 are closed in `template/files/.github/workflows/**`, `scripts/render-samples.sh`, `justfile` ssot wiring, jinja dir-walk, and skill mirrors. Official dests for `rust-api` / `go-api` no longer emit empty `needs` / empty publish matrix. `just validate-agents` is green.

Open items below are environmental, dest-stale, or foreign-tree.

## Residuals

### R1 — dest `mise.toml` untrusted during official rust-api/go-api bootstrap

| Field | Value |
| --- | --- |
| **task_id** | GATES-R1-mise-trust |
| **owner** | MISE / PLATFORM |
| **status** | open |
| **command** | `mise trust samples/rust-api/render/mise.toml && ./scripts/render-samples.sh --variant rust-api --answers samples/rust-api/copier-answers.yml` |
| **blocking reason** | Official re-render copy succeeded (container workflows correct). `pnpm install` failed because dest `mise.toml` is not trusted (`mise ERROR Config files … are not trusted`). Fail-closed bootstrap is intentional. |
| **redacted log** | `mise ERROR error parsing config file: …/samples/rust-api/render/mise.toml` / `Config files … are not trusted.` / `ERROR: bootstrap failed for variant 'rust-api'` (same for go-api). |
| **fix** | Trust dest mise pins in the render harness, or document `mise trust` before bootstrap. Do not hand-edit dest. |
| **evidence** | `goals/riso-v2-release-ready/evidence/W5-CLOSE-GATES.md` |

### R2 — default dest smoke still red (Fumadocs sitemap + static export)

| Field | Value |
| --- | --- |
| **task_id** | GATES-R2-default-fumadocs-smoke |
| **owner** | NODE |
| **status** | open |
| **command** | `./scripts/render-samples.sh --variant default --answers samples/default/copier-answers.yml` |
| **blocking reason** | Dest exists (`AGENTS.md` present; `just validate-agents` 0). Docs smoke still fails: `/sitemap.xml` missing `dynamic = "force-static"` / `revalidate` with `output: export`. |
| **redacted log** | `Failed to collect configuration for /sitemap.xml` / `export const dynamic = "force-static"/export const revalidate not configured on route "/sitemap.xml" with "output: export"`. |
| **fix** | Fix `template/files/node/docs/fumadocs/` sitemap for static export. Re-render via official script. Never hand-edit dest. |
| **evidence** | `samples/default/smoke-results.json`; `evidence/W5-CLOSE-GATES.md` |

### R3 — Circle/GitLab dest-root `uv sync` (foreign)

| Field | Value |
| --- | --- |
| **task_id** | GATES-R3-circle-gitlab-uv-root |
| **owner** | COORD / payload owners of `template/files/.circleci/**` and `template/files/.gitlab/**` |
| **status** | open |
| **command** | inspect `template/files/.circleci/config.yml.jinja` L82 and `template/files/.gitlab/.gitlab-ci.yml.jinja` L51 |
| **blocking reason** | Same class as PAY-P1-gha-uv-root. GHA jinja is fixed. Circle setup and GitLab `.python-base` still `uv sync` at dest root. Exclusive write did not include those trees. |
| **redacted log** | `.circleci/config.yml.jinja:82 uv sync`; `.gitlab/.gitlab-ci.yml.jinja:51 uv sync` (CLI/MCP steps already `cd python`). |
| **fix** | `cd python && uv sync` or `uv --directory python sync` in those templates. |
| **evidence** | `evidence/W5-CLOSE-GATES.md` |

### R4 — python-enabled dest quality.yml stale until official re-render

| Field | Value |
| --- | --- |
| **task_id** | GATES-R4-dest-quality-stale |
| **owner** | PLATFORM |
| **status** | open |
| **command** | `./scripts/render-samples.sh --variant api-python --answers samples/api-python/copier-answers.yml` (or later `render_matrix.py`) |
| **blocking reason** | Live jinja uses `working-directory: python` + `uv --directory python`. `samples/api-python/render/.github/workflows/riso-quality.yml` still dest-root `uv sync`. Do not hand-edit dest. |
| **redacted log** | dest L52–66 still `uv sync` / `uv run task quality`. |
| **fix** | Official re-render after payload smoke is safe. |
| **evidence** | `evidence/W5-CLOSE-GATES.md` |
