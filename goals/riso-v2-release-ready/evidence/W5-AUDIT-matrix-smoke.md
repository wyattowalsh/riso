# W5-AUDIT — matrix-smoke

- **Mission:** `AUDIT-matrix-smoke` (read-only)
- **Lane:** `matrix-smoke`
- **Date:** 2026-08-14
- **Repo:** `/Users/ww/dev/projects/riso` (workspace = maintainer root)
- **Branch / HEAD:** `refs/heads/main` = `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b` (`.git/HEAD` hook-denied; `git rev-parse --show-toplevel` not executed — no shell in this subagent)
- **Write root:** this file only
- **Product-code edits:** **0**
- **`samples/*/render/**` writes:** **0** (dests read only)
- **Python:** not invoked
- **`render_matrix.py`:** not started; no live matrix process observed or killed

SSOT read first: `goal.md`, `facts.md`, `plan.md`, `ASSURANCE.md`, `residuals/{GOAL,PLATFORM,CLI,OPENSPEC,SKILL}.md`. ASSURANCE `render_matrix_green=true` is **JSON existence only** — do not treat it as smoke-green.

## Method

- `read_file` `samples/metadata/render_matrix.json` (header + every variant `render_status` / SaaS block / `module_success`)
- `grep` failed modules + error signatures in the matrix JSON, `samples/**/smoke-results.json`, `evidence/W3-PL-T06.log`
- Live dest probes: `samples/default/render` (absent), SaaS dests (absent), fumadocs dest `next.config.ts`, rust-api/go-api dest workflows, mcp-typescript dest `package.json`
- Live template probes: fumadocs `next.config.ts.jinja`, docusaurus `docusaurus.config.ts.jinja`, python `Makefile.jinja` / `justfile.jinja`, container-build/publish jinja, `scripts/render-samples.sh` variant regex, `justfile` `validate-agents`

## Matrix rollup (live JSON)

`samples/metadata/render_matrix.json` exists (W3-PL-T06.log L9627 “Render matrix complete”; L9633 **137544** bytes; L9636 **37** variants). `render_matrix.py` L333–340 then `SystemExit(1)` when any `render_status=failed`.

| Class | Count | How distinguished |
| --- | --- | --- |
| **copy-success + smoke-fail** | **23** | dest exists (except `default`, see below); `smoke_results` present; at least one module `failed`; `render_returncode=1` because `render-samples.sh` L643–645 exits 1 on smoke |
| **copy-fail** | **11** | all `saas-starter/*`; `smoke_results: null`; `workflow_validation: unknown`; **no** `render/` dest |
| **copy-success + smoke-ok** | **3** | `electron-app`, `mcp-typescript`, `tauri-app` — `render_status=ok` / `returncode=0` |

`module_success.docs`: **0 passed / 23 failed**. `quality_just`: 1/6. `quality_uv_task`: 2/5. `workflow_generation`: **22 pass / 2 fail**. `cli` / `api_python` / `api_node` smokes that ran all **passed**.

`mcp-typescript` is a **false green** (see pnpm cluster): copy ran, `pnpm install` failed, every smoke module skipped, script still exited 0.

## Cluster A — fumadocs NextConfig `output: string` (20, copy+smoke)

Smoke `docs` = `pnpm --filter docs-fumadocs build` → Next 16 typecheck **TS2345** (`output: string` not `"export" | "standalone"`). Dest `samples/docs-fumadocs/render/node/docs/fumadocs/next.config.ts` L12 is still `output: 'export'` **without** `as const`.

Variants (20): `ai-tools-off`, `api-monorepo`, `api-python`, `changelog-full-stack`, `changelog-monorepo`, `circleci-node`, `cli-docs`, `default`, `docs-fumadocs`, `docs-fumadocs-full`, `full-stack`, `gitlab-ci-python`, `go-api`, `go-cli`, `go-mcp`, `makefile-runner`, `rag-enabled`, `rust-api`, `rust-cli`, `rust-mcp`.

**Live template is fixed:** `template/files/node/docs/fumadocs/next.config.ts.jinja` L13 `output: 'export' as const`. Dest-stale. Do not hand-edit dests. Official re-render required.

## Cluster B — Sphinx `make linkcheck` missing (2, copy+smoke)

`changelog-python`, `docs-sphinx`. Smoke (`render-samples.sh` L169–173): `uv run make linkcheck` from `python/` cwd → `make: *** No rule to make target 'linkcheck'. Stop.` (returncode 2).

**Still open in template:**

- `template/files/python/Makefile.jinja` PHONY/forward list has **no** `linkcheck`.
- `template/files/python/justfile.jinja` only `import '../quality/justfile.quality'`.
- `copier.yml` L1910 **excludes** `python/Makefile` when `task_runner in ['just', 'none']`. Dest `samples/docs-sphinx/render/python/Makefile` **does not exist**.
- Only `linkcheck` string under `template/files` is `python/docs/conf.py.jinja` L403 `linkcheck_ignore`.

## Cluster C — Docusaurus `gen-api-docs` (1, copy+smoke)

`docs-docusaurus`. `prebuild` → `docusaurus gen-api-docs api` exit 1. Stderr (live `samples/docs-docusaurus/smoke-results.json`):

```text
[ERROR] Error: These field(s) ("mermaidThemeByColorMode",) are not recognized in docusaurus.config.ts.
```

**Still open:** `template/files/node/docs/docusaurus/docusaurus.config.ts.jinja` L91–96 named-exports `mermaidThemeByColorMode`. Docusaurus treats every named export of that module as a config key.

## Cluster D — empty workflow `needs` (2 overlay; copy succeeded)

`workflow_validation=fail` only on **`go-api`** and **`rust-api`** (matrix JSON L1116, L1467). `api_module: enabled` + `api_languages: [go]` / `[rust]`. W3-PL-T06.log L6742–6753 / L8692–8703: actionlint `"needs" section should not be empty` + empty publish `matrix.target`. Validator **continued**; those dests still exist and then **failed fumadocs smoke**.

Dest still stale:

```52:58:samples/rust-api/render/.github/workflows/riso-container-build.yml
  scan:
    name: Security Scan
    runs-on: ubuntu-latest
    needs: []
    strategy:
      matrix:
        target:
```

`samples/go-api/render/.github/workflows/riso-container-build.yml` L55 same `needs: []`.

**Live template is fixed** (parent closeout; W5-AUDIT-gates L103–107 is stale vs this tree):

- `riso-container-build.yml.jinja` L180 wraps `scan` in `api_module == enabled` **and** python-or-node; L236 summary `needs: [hadolint]` otherwise.
- `riso-container-publish.yml.jinja` L24 wraps `publish-ghcr` in the same python-or-node guard.

`W5-AUDIT-gates` claimed scan was unconditional — live L180 `if` contradicts that. Implementation **closed**; dest proof pending official re-render.

## Cluster E — pylint (overlay on 5 copy+smoke variants)

`quality_uv_task` / `quality_just` pylint exit 16/18 after ruff+ty green. `quality/justfile.quality.jinja` L22 runs pylint on `standard` (not `--errors-only`).

| Variant | pylint signal |
| --- | --- |
| `api-monorepo` | `cli/__main__.py:3` C0301 105/100 (`quality_just` + `quality_uv_task`) |
| `api-python` | same C0301 on `src/riso_api_sample` |
| `changelog-monorepo` | `quality_uv_task` C0301 `plugin_manager.py:23` 101/100 (`quality_just` died earlier on **ruff**) |
| `docs-fumadocs-full` | pylint after `quality_just` died on **mise trust** |
| `docs-sphinx` | C0301 `cli/__main__.py:3` after mise-trust on `just quality` |

**Still open:** `template/files/python/src/{{ package_name }}/cli/__main__.py.jinja` L3 is the 105-col placeholder (“Re-render the template with `cli_module=enabled`…”).

Adjacent (not pylint; do not merge): `changelog-python` / `changelog-monorepo` `quality_just` fail **ruff** (`docs/conf.py` E402, `release/models.py` UP042/SIM102) — owned by PY (`W5-AUDIT-payloads-py` PAY-P1-ruff-conf-release). `docs-sphinx` / `docs-fumadocs-full` `just quality` also hit **mise trust** on dest `.mise.toml` (env, not payload).

## Cluster F — pnpm install (0 of the 34 failed)

The only `pnpm install failed` in `W3-PL-T06.log` is **`mcp-typescript`** (L7814–7815: `Invalid package.json in package.json`) — and that variant is `render_status=ok`.

- Dest `samples/mcp-typescript/render/package.json` is a **blank line** (invalid JSON). Workspace `node/mcp/package.json` is valid.
- Live `template/files/package.json.jinja` L1 **does** include `mcp_module == "enabled" and "typescript" in mcp_languages`. Answers have that pair. Re-render should emit JSON.
- `render-samples.sh` L576–579 logs bootstrap failure and **continues**. Smoke then skips every node module (`pnpm dependencies not installed`). All-skipped → exit 0. **False green.**

None of the 34 `render_status=failed` rows are a pnpm-install copy/smoke root cause.

## Cluster G — SaaS copy-fail, slashed variant names (11)

All 11 `saas-starter/*` dests **do not exist**. Matrix: `smoke_results: null`, `render_status=failed`. W3-PL-T06.log L9356–9376:

```text
[render-samples] ERROR: Invalid variant name: saas-starter/all-in-one
… (all 11) …
[render-samples] ERROR: Invalid variant name: saas-starter/vercel-starter
```

`validate_render_paths` runs **before** `rm -rf` (L627–632), so dests were never created.

**Live script accepts nested names:** `scripts/render-samples.sh` L588 `^[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)*$`. `tests/unit/ci/test_render_samples_variant_names.py` asserts `saas-starter/vercel-starter`. Name-regex implementation is **stale/fixed**. Dests still missing until official `render_matrix.py` / `render-samples.sh`. Post-copy SaaS smoke may still be red (payload flatten leftovers are a foreign NODE/SAAS lane).

`samples/saas-starter/render-results.json` (`Rendering not yet implemented`) is an older skipped-render artifact — not the W3 copy-fail reason.

## `samples/default/render` is missing (ladder)

`justfile` L217–226 `validate-agents` requires `--render-enabled samples/default/render` and `agent_smoke_agents_md.py samples/default/render`.

Live: `samples/default/` has `copier-answers.yml`, `smoke-results.json`, `baseline_quickstart_metrics.json` only. `read_file` `samples/default/render/AGENTS.md` → does not exist. `list_dir` `samples/default/render` → does not exist.

Matrix `default` was **copy-success + fumadocs smoke-fail** at `2026-08-14T00:00:17Z` (stdout path `samples/default/render/node/docs/fumadocs`). Dest existed then; it is gone now. `residuals/PLATFORM.md` R4 / `GOAL.md` R1 already own this. **Never hand-create.** Restore only via `./scripts/render-samples.sh --variant default --answers samples/default/copier-answers.yml` after payload fixes (fumadocs `as const` is already in template).

JSON existence still satisfies `fact-render-matrix` write. It does **not** satisfy `just validate-agents` or smoke-green.

## Copy vs smoke map (34 failed)

| Variant | Class | Primary cluster | Overlays |
| --- | --- | --- | --- |
| ai-tools-off | copy+smoke | fumadocs | — |
| api-monorepo | copy+smoke | fumadocs | pylint |
| api-python | copy+smoke | fumadocs | pylint |
| changelog-full-stack | copy+smoke | fumadocs | — |
| changelog-monorepo | copy+smoke | fumadocs | ruff then pylint |
| changelog-python | copy+smoke | sphinx linkcheck | ruff (`quality_just`) |
| circleci-node | copy+smoke | fumadocs | — |
| cli-docs | copy+smoke | fumadocs | — |
| default | copy+smoke → dest **now absent** | fumadocs | validate-agents blocker |
| docs-docusaurus | copy+smoke | gen-api-docs | — |
| docs-fumadocs | copy+smoke | fumadocs | — |
| docs-fumadocs-full | copy+smoke | fumadocs | mise trust + pylint |
| docs-sphinx | copy+smoke | sphinx linkcheck | mise trust + pylint |
| full-stack | copy+smoke | fumadocs | — |
| gitlab-ci-python | copy+smoke | fumadocs | — |
| go-api | copy+smoke | fumadocs | empty `needs` (workflow fail, continued) |
| go-cli | copy+smoke | fumadocs | — |
| go-mcp | copy+smoke | fumadocs | — |
| makefile-runner | copy+smoke | fumadocs | — |
| rag-enabled | copy+smoke | fumadocs | — |
| rust-api | copy+smoke | fumadocs | empty `needs` |
| rust-cli | copy+smoke | fumadocs | — |
| rust-mcp | copy+smoke | fumadocs | — |
| saas-starter/all-in-one | **copy-fail** | slash name | dest never created |
| saas-starter/b2b-teams-full | copy-fail | slash name | dest never created |
| saas-starter/b2c-consumer-app | copy-fail | slash name | dest never created |
| saas-starter/edge-optimized | copy-fail | slash name | dest never created |
| saas-starter/enterprise-ready | copy-fail | slash name | dest never created |
| saas-starter/nextjs-vercel-neon-clerk | copy-fail | slash name | dest never created |
| saas-starter/nextjs-vercel-neon-clerk-workos | copy-fail | slash name | dest never created |
| saas-starter/nextjs-vercel-supabase-clerk | copy-fail | slash name | dest never created |
| saas-starter/prelaunch-waitlist | copy-fail | slash name | dest never created |
| saas-starter/remix-cloudflare-neon-drizzle | copy-fail | slash name | dest never created |
| saas-starter/vercel-starter | copy-fail | slash name | dest never created |

## Ok variants (not in the 34)

| Variant | Notes |
| --- | --- |
| electron-app | `render_status=ok`; dest present; docs skipped (`docs_module=disabled`) |
| tauri-app | same |
| mcp-typescript | `render_status=ok` but pnpm bootstrap failed (false green) |

## Findings

### MS-P0-default-dest — P0

- **File:** `samples/default/render` (absent); `justfile` L221–226
- **Issue:** Official default dest is missing. `just validate-agents` cannot pass. Matrix `default` was copy+fumadocs-smoke-fail; dest has since disappeared. JSON write does not restore the dest.
- **Fix:** After payload re-render is safe (fumadocs `as const` already in template), restore **only** via `./scripts/render-samples.sh --variant default --answers samples/default/copier-answers.yml`. Never hand-create `AGENTS.md` or any dest file.

### MS-P0-docusaurus-gen-api-docs — P0

- **File:** `template/files/node/docs/docusaurus/docusaurus.config.ts.jinja`
- **Issue:** Live L96 `export { mermaidThemeByColorMode };` still breaks `docs-docusaurus` `prebuild` (`gen-api-docs`). Copy succeeded; dest exists.
- **Fix:** NODE lane — stop named-exporting from `docusaurus.config.ts` (file-local const or sibling module). Then official re-render. Do not hand-edit dest.

### MS-P0-sphinx-linkcheck — P0

- **File:** `template/files/python/Makefile.jinja` (+ `python/justfile.jinja`; smoke argv `scripts/render-samples.sh` L172)
- **Issue:** Smoke runs `uv run make linkcheck`. Generated make/just have no `linkcheck`. Default `task_runner=just` excludes `python/Makefile`. `docs-sphinx` + `changelog-python` docs smoke red.
- **Fix:** PY — add `linkcheck` (`uv run --group docs sphinx-build -b linkcheck docs dist/docs-linkcheck`) on the runner smoke actually invokes, **or** PLATFORM change smoke to `just linkcheck` / bare sphinx-build. Still ship a Makefile when Sphinx is on if smoke stays on `make`.

### MS-P1-pylint-placeholder — P1

- **File:** `template/files/python/src/{{ package_name }}/cli/__main__.py.jinja`
- **Issue:** Disabled-CLI L3 is 105 cols. Standard-profile pylint C0301 fails `api-monorepo`, `api-python`, `docs-sphinx` quality smoke (and similar length hits on changelog plugin_manager).
- **Fix:** Wrap the placeholder to ≤100 cols. Keep `standard` pylint unless COORD changes the profile.

### MS-P1-pnpm-false-green — P1

- **File:** `scripts/render-samples.sh` L576–579; dest `samples/mcp-typescript/render/package.json`
- **Issue:** Not one of the 34 failed. Sole pnpm-install error is `mcp-typescript` (`Invalid package.json`). Dest root manifest is empty. Bootstrap failure does not fail the script; all-skipped smoke → `render_status=ok`.
- **Fix:** PLATFORM — fail the variant on bootstrap error. Re-render so live `package.json.jinja` (typescript MCP gate) lands a real root manifest. Do not hand-edit dest.

### MS-STALE-fumadocs-output — stale

- **File:** `template/files/node/docs/fumadocs/next.config.ts.jinja`
- **Issue:** 20 variants smoke-failed TS2345 on dest `output: 'export'` (unconst). Live jinja L13 already has `as const`.
- **Fix:** none in template. Official re-render only. Do not regress `as const`. Do not restore `rewrites()`.

### MS-STALE-empty-needs — stale

- **File:** `template/files/.github/workflows/riso-container-build.yml.jinja`
- **Issue:** W3 `go-api` / `rust-api` dests still have `scan.needs: []`. Live jinja L180 omits `scan` unless python/node; summary needs `hadolint`. `W5-AUDIT-gates` P0 on unconditional scan is stale vs this tree.
- **Fix:** none in template. Official re-render of go/rust dests.

### MS-STALE-saas-slash-name — stale

- **File:** `scripts/render-samples.sh` L588
- **Issue:** W3 rejected `saas-starter/<name>` before copy (11 copy-fails, dests absent). Live regex + `test_render_samples_variant_names.py` accept nested names.
- **Fix:** none in the validator. Official matrix/re-render to create dests. SaaS payload smoke is a foreign lane after copy.

## Strengths (verified-good)

- `render_matrix.py` completed and wrote `samples/metadata/render_matrix.json` (37 variants). Residualing the matrix is still forbidden.
- Continue-on-fail worked: all 37 were attempted; 3 desktop/MCP dests recorded `ok`.
- Nested variant discovery (`saas-starter/...`) is correct in `render_matrix.py` `discover_variants()`.
- Live fumadocs `as const`, container scan/publish gates, and slash-name regex are in tree.
- `cli` / `api_python` / `api_node` module smokes that actually ran all passed.

## Not this lane

- Product edits (NODE/PY/PLATFORM/SAAS).
- Hand-editing `samples/*/render/**`.
- Starting or killing `render_matrix.py`.
- Residual ledger / ASSURANCE rewrite.

## Verdict

**34 failed = 23 copy+smoke + 11 copy-fail.** Primary open implementation gaps: docusaurus named export, Sphinx `linkcheck` target, pylint C0301, bootstrap-false-green. Fumadocs `output`, empty `needs`, and SaaS slash-name are **fixed in template/script** and need official dest restore. `samples/default/render` is **absent** and blocks `just validate-agents`.
