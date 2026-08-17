# W5-AUDIT-samples — leftover removed keys in `samples/**/copier-answers.yml`

- Task: `W5-AUDIT-samples`
- Wave: W5
- Lane: **samples** (inspect-only; this file only)
- Date (UTC): 2026-08-14
- Repo: `/Users/ww/dev/projects/riso`
- Branch: current (no checkout / stash / reset). `.git/HEAD` read denied by hook. `refs/heads/main` and last `logs/HEAD` entry: `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b`
- `git rev-parse --show-toplevel`: not executed (no shell in this subagent). Workspace + `.git` confirm `/Users/ww/dev/projects/riso`
- Answers edited: **0**
- `samples/*/render/**` writes: **0**
- Product-code edits: **0**

Remap contract (not re-implemented): `apply_removed_key_remaps` then `reject_removed_answer_keys`. No dest overwrite. Idempotent. No dual-path after remap.

## Verdict

**37/37** official `samples/**/copier-answers.yml` files exist (matches `plan.taskgraph.json` `sample_shards` S0–S5). **Zero leftover `REMOVED_ANSWER_KEYS`** as YAML keys or word-boundary tokens. `samples/default/render` **does not exist** (matrix `default` `render_status=failed`; already `residuals/PLATFORM.md` R4).

No P0 leftover-key gap in source answers. Dest absence is a still-open verification / `validate-agents` gap, not an answers remap miss.

## Removed-key SSOT (live)

`src/riso/core/removed_answer_keys.py` `REMOVED_ANSWER_KEYS` / `ANSWER_KEY_REMAPS` (8 keys):

| # | old key | action | dest keys |
| --- | --- | --- | --- |
| 1 | `api_tracks` | derive | `api_module`, `api_languages` |
| 2 | `api_language` | wrap-list | `api_languages` |
| 3 | `docs_site` | derive | `docs_module`, `docs_framework` |
| 4 | `mcp_language` | wrap-list | `mcp_languages` |
| 5 | `saas_starter_module` | rename | `saas_infra_module` |
| 6 | `saas_auth` | split | `saas_auth_module`, `saas_auth_provider` |
| 7 | `saas_billing` | split | `saas_billing_module`, `saas_billing_provider` |
| 8 | `include_admin` | rename-bool | `saas_admin_dashboard` |

`plan.taskgraph.json` `remap_keys` matches this set. `scripts/ci/check_removed_key_ssot.py` `scan_sample_answers_for_removed_keys()` walks `iter_sample_answer_files()` (skips `render/`, `metadata/`, `node_modules`) and intersects YAML roots with `REMOVED_ANSWER_KEYS`. This audit did **not** re-run `uv run` (no shell); live reads + rg are the evidence.

## Queries (live)

Scope: `samples/**/copier-answers.yml` only (not `samples/*/render/**`).

A. Exact YAML key (optional indent):

```text
^\s*(api_tracks|api_language|docs_site|mcp_language|saas_starter_module|saas_auth|saas_billing|include_admin)\s*:
```

hits: **0**

B. Word-boundary (`\bKEY\b`) across those eight names under the same glob: **0** (no comments either). Prefix-safe: does not match `api_languages`, `mcp_languages`, `saas_auth_module` / `_provider`, `saas_billing_module` / `_provider`.

C. Extra historical names (not in current 8-key SSOT; diligence only):

```text
^\s*(include_adr|include_architecture|include_deployment|include_adr_architecture|include_ci|include_precommit|include_release_please|include_semantic_release|graphql_api_module|websocket_module)\s*:
```

hits: **0**

D. `^project_name:` file count: **37**. `^_commit:`: **36** (`samples/circleci-node/copier-answers.yml` has no `_commit`; file is present and clean).

## File inventory (37)

Every path below was opened. Canonical dest keys only.

### S0 (6)

| path | leftover keys |
| --- | --- |
| `samples/default/copier-answers.yml` | none (`docs_module` / `docs_framework: fumadocs`) |
| `samples/ai-tools-off/copier-answers.yml` | none |
| `samples/makefile-runner/copier-answers.yml` | none |
| `samples/cli-docs/copier-answers.yml` | none |
| `samples/rag-enabled/copier-answers.yml` | none (`saas_infra_module`, `saas_auth_module`/`provider`, `saas_billing_module`/`provider`, `saas_admin_dashboard`) |
| `samples/gitlab-ci-python/copier-answers.yml` | none (`api_languages: [python]`) |

### S1 (6)

| path | leftover keys |
| --- | --- |
| `samples/api-python/copier-answers.yml` | none |
| `samples/api-monorepo/copier-answers.yml` | none |
| `samples/full-stack/copier-answers.yml` | none (`api_languages`, `mcp_languages`) |
| `samples/changelog-python/copier-answers.yml` | none |
| `samples/changelog-full-stack/copier-answers.yml` | none |
| `samples/changelog-monorepo/copier-answers.yml` | none |

### S2 (6)

| path | leftover keys |
| --- | --- |
| `samples/docs-sphinx/copier-answers.yml` | none (`docs_framework: sphinx-shibuya`) |
| `samples/docs-docusaurus/copier-answers.yml` | none (`docs_framework: docusaurus`) |
| `samples/docs-fumadocs/copier-answers.yml` | none |
| `samples/docs-fumadocs-full/copier-answers.yml` | none |
| `samples/circleci-node/copier-answers.yml` | none (`saas_infra_module: disabled`) |
| `samples/mcp-typescript/copier-answers.yml` | none (`mcp_languages: [typescript]`) |

### S3 (6)

| path | leftover keys |
| --- | --- |
| `samples/go-api/copier-answers.yml` | none |
| `samples/go-cli/copier-answers.yml` | none |
| `samples/go-mcp/copier-answers.yml` | none |
| `samples/rust-api/copier-answers.yml` | none |
| `samples/rust-cli/copier-answers.yml` | none |
| `samples/rust-mcp/copier-answers.yml` | none |

### S4 (6)

| path | leftover keys |
| --- | --- |
| `samples/electron-app/copier-answers.yml` | none |
| `samples/tauri-app/copier-answers.yml` | none |
| `samples/saas-starter/all-in-one/copier-answers.yml` | none (canonical SaaS dests) |
| `samples/saas-starter/b2b-teams-full/copier-answers.yml` | none |
| `samples/saas-starter/b2c-consumer-app/copier-answers.yml` | none |
| `samples/saas-starter/edge-optimized/copier-answers.yml` | none |

### S5 (7)

| path | leftover keys |
| --- | --- |
| `samples/saas-starter/enterprise-ready/copier-answers.yml` | none |
| `samples/saas-starter/nextjs-vercel-neon-clerk-workos/copier-answers.yml` | none |
| `samples/saas-starter/nextjs-vercel-neon-clerk/copier-answers.yml` | none |
| `samples/saas-starter/nextjs-vercel-supabase-clerk/copier-answers.yml` | none |
| `samples/saas-starter/prelaunch-waitlist/copier-answers.yml` | none |
| `samples/saas-starter/remix-cloudflare-neon-drizzle/copier-answers.yml` | none |
| `samples/saas-starter/vercel-starter/copier-answers.yml` | none |

Count: 6+6+6+6+6+7 = **37**. Extra `copier-answers.yml` under `samples/` (outside `render/`): **0**.

## Default dest

| Check | Result |
| --- | --- |
| `samples/default/copier-answers.yml` | present, no leftover keys |
| `samples/default/render` | **absent** (`read_file` / `list_dir`: only `copier-answers.yml`, `smoke-results.json`, `baseline_quickstart_metrics.json`) |
| `samples/metadata/render_matrix.json` `variant=default` | `destination` = `…/samples/default/render`; `render_status=failed`; `render_returncode=1` (fumadocs `next build` TS `output` type) |

`fact-no-legacy-answers` source-answers half is green on live files. Generated default `.copier-answers.yml` cannot be inspected because the dest is gone. Spot-check of existing dests (read-only; not the mission glob): `samples/{electron-app,ai-tools-off,mcp-typescript}/render/.copier-answers.yml` use dest keys only (`api_module`, `mcp_languages`, `saas_infra_module`, `openspec_extra: disabled`). Do **not** hand-create `samples/default/render`. Owner: PLATFORM official `render-samples.sh` / later matrix after payload smoke.

## Findings

| id | severity | file | issue | fix |
| --- | --- | --- | --- | --- |
| SAMP-CLOSED-37-NO-LEFTOVERS | closed | `samples/**/copier-answers.yml` | All 37 official answers files inspected; none contain a `REMOVED_ANSWER_KEYS` YAML key | none |
| SAMP-P1-DEFAULT-DEST-ABSENT | P1 | `samples/default/render` | Default dest missing; cannot inspect generated default answers; `just validate-agents` residual (PLATFORM R4) | Official re-render only. Do not edit answers. Do not hand-edit dest. |

## Writes

This evidence file only. No commit / tag / push / PyPI. No `render_matrix` start/kill.
