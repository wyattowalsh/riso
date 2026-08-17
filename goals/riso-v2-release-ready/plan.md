# Plan — Riso 2.0 release-ready (v3)

Companion DAG: [`plan.taskgraph.json`](./plan.taskgraph.json)

## Critique of v1/v2 (why this rewrite)

Repo-traced gaps the earlier wave tables missed:

| Gap | Evidence | Fix in this plan |
| --- | --- | --- |
| Remap is not a table yet | `REMOVED_ANSWER_KEYS` values are **human strings**; `reject_removed_answer_keys` only errors | Add `ANSWER_KEY_REMAPS` + `apply_removed_key_remaps` |
| `update --dry-run` already **rejects** old keys | `src/riso/cli/commands/update.py` | Remap **before** reject; print preview |
| Reject is called in **many** places, not just update | `helpers.resolve_answers`, `validate_and_raise`, `recopy`, `diff`, `generation_gates`, hooks `pre_gen`/`post_gen`, web `formatRemovedAnswerKeyErrors` | One apply-then-reject choke point; wire **every** site |
| No `riso migrate` command | `app.py` commands: doctor/validate/copy/update/recopy/diff/export-* | Add `riso migrate` that only remaps answers; `update` reuses it |
| Release skill forbids migrate | `.agents/skills/riso-release-readiness/references/no-legacy-answer-policy.md` says “do not convert” and lists **5** keys (missing `saas_auth`/`saas_billing`/`include_admin`) | Rewrite policy: remap known → fail-closed leftovers; 8 keys |
| `generation_gates` still reads `saas_auth` | `_collect_saas_selected` in `src/riso/core/generation_gates.py` | COORD/CLI: drop leftover old key from gates |
| W2 was lumpy | One NODE/SAAS/SYS task each | Per-file / per-operator / per-shard IDs |
| PL-T08 ↔ W4-D01 cycle | sphinx-W depended on docs that were in the next wave | Docs draft after CLI-JOIN; `sphinx -W` after W4-D*; assurance last |
| `render_matrix` residual is **not** done | `goals/riso-lanes-assurance/residuals/PLATFORM.md` R1 | Blocking PL-T06; do not kill; require `samples/metadata/render_matrix.json` |
| Three-way SSOT can drift | Python core, `scripts/lib` fallback dict, TS | Parity tests + `check_removed_key_ssot.py` |
| Same-file parallel writers | `copier.yml`, `removed_answer_keys.py`, `removedAnswerKeys.ts`, `helpers.py` | Exclusive locks; serial on those files |
| No `test_update.py` | `tests/unit/test_cli/` has no update module | Add fixtures + tests |

**What stays from the dirty tree (do not rewrite):** `--skip-post-gen` in `_GLOBAL_FLAGS`; `iter_sample_answer_files` pruned walk; `list_sample_variants` `os.scandir` CM; `go.work` `.`+`./mcp`; `BaseCommand.execute()`; electron-store `externalizeDepsPlugin({exclude})`; ESLint 9 + `env.d.ts` / `vite-env.d.ts`; no clang/lld; DESIGN + mermaid + mpl/plotly; `custom.js.jinja`; SaaS `runtime/{nextjs,remix}` restored; pytest `python_files` = `test_*.py` only.

**What stays dropped:** SaaS Next/Remix flatten copies; idle-gate pytest collection hack; maintainer `riso-mcp`.

---

## Solution approach

Integrator over exclusive-write lanes. **Hard major** (keys/flags/layout may change). **No new languages/runtimes/vendors.** **No tag/push/PyPI.**

1. Inventory dirty tree + 8-key hit list.
2. Serial COORD/CLI SSOT: machine remap table, hook twin, Copier extras (`openspec_extra` default off; always-on generated `mise.toml`).
3. Parallel lanes: wire remap at every call site; `riso migrate`; wizard twin; PY hypothesis+respx; keep desktop/go/saas-runtime; mise pins.
4. PLATFORM: shard 37 answer files → validate → `just quality` → **full** `render_matrix.py`.
5. Docs + two dry review passes + `ASSURANCE.md`.

**Engine:** grok-4.6 subagents, worktree isolation, disjoint locks. Serial only on `copier.yml` / hooks / remap SSOT files.

**Refine:** correctness green first; stop after **two consecutive review passes with no new P0/P1** and the official ladder green.

---

## Exclusive write locks

| Lane | Write roots | Same-file serial |
| --- | --- | --- |
| COORD | `template/copier.yml`, `template/hooks/**`, `template/macros/**`, `template/prompts/**`, `template/files/module_catalog.json.jinja`, `.github/context/**`, `template/files/.github/context/**` | `copier.yml`, hooks |
| CLI | `src/riso/**`, `tests/unit/test_cli/**` | `removed_answer_keys.py`, `answers.py`, `helpers.py`, `app.py` |
| PY | `template/files/python/**` | `pyproject.toml.jinja` |
| NODE | `template/files/node/**` except `node/saas/**` | — |
| SAAS | `template/files/node/saas/**`, `template/files/saas-starter/**` | — |
| SYS | `template/files/go/**`, `template/files/rust/**` | `go.work.jinja` |
| DESKTOP | `template/files/electron/**`, `template/files/tauri/**` | — |
| WEB | `web/src/**`, `web/tests/**` | `removedAnswerKeys.ts` |
| PLATFORM | `scripts/ci/**`, `scripts/lib/**`, `scripts/render-samples.sh`, `template/files/quality/**`, `samples/**/copier-answers.yml`, `samples/metadata/**` | `scripts/lib/removed_answer_keys.py` after W1-M01 |
| DOCS | `docs/**`, `CHANGELOG.md`, `template/files/docs/**`, `template/files/AGENTS.md.jinja` | `docs/guides/index.md` |
| MISE | `template/files/mise.toml.jinja` (new), maintainer `.mise.toml` only if pin sync required | — |
| SKILL | `.agents/skills/riso-release-readiness/**` | no-legacy policy |
| GOAL | `goals/riso-v2-release-ready/**` | — |

Hard forbid: hand-edit `samples/*/render/**`; lockfile hand-edits; secrets; reintroduce `riso-mcp`.

---

## Remap contract (SSOT)

Today the three dicts only store **replacement prose**. Add a machine table next to them.

### Operators (implement + table-test each)

Do **not** overwrite a destination key that is already set. Drop the old key after a successful apply. Second apply is a no-op (idempotent).

| Old key | Operator | Value rules (historical → current Copier) |
| --- | --- | --- |
| `api_language` | wrap-list | scalar `python`/`node`/`rust`/`go` → `api_languages: [that]`; already-list → keep |
| `mcp_language` | wrap-list | scalar `python`/`typescript`/`rust`/`go` → `mcp_languages`; map `node`/`js` → `typescript` |
| `api_tracks` | derive | empty/`none`/`disabled` → `api_module=disabled`; else `api_module=enabled` and languages = intersection of tokens with `{python,node,rust,go}` (also accept `fastapi`→python, `fastify`→node, `actix`→rust) |
| `docs_site` | derive | `none`/`false`/`disabled`/`off` → `docs_module=disabled`; `sphinx`/`sphinx-shibuya` → enabled + `sphinx-shibuya`; `docusaurus` → enabled + `docusaurus`; `fumadocs` → enabled + `fumadocs` |
| `saas_starter_module` | rename | copy value → `saas_infra_module` (`enabled`/`disabled`) |
| `saas_auth` | split | `none`/`disabled`/`false`/`off` → `saas_auth_module=disabled`; `clerk`/`authjs`/`lucia` → module enabled + that `saas_auth_provider` |
| `saas_billing` | split | `none`/`disabled`/`false`/`off` → `saas_billing_module=disabled`; `stripe`/`paddle`/`lemonsqueezy` → module enabled + that provider |
| `include_admin` | rename-bool | truthy/falsey → `saas_admin_dashboard` bool |

Unknown leftover removed keys (or unmapped values): **fail closed** with pointer to the human replacement string. No dual-path, no hidden aliases after remap.

### Apply API

```text
apply_removed_key_remaps(answers) -> RemapResult(answers, ops)
# ops: [{old, new_keys, action, before, after}]
reject_removed_answer_keys(answers)  # leftovers only; same error shape as today
```

`resolve_answers` / `validate_and_raise` / `update` / `recopy` / `diff` / `copy` / `generation_gates` / hooks / wizard import: **apply then reject**.

### `riso migrate`

New command (facts: “CLI including migrate” + “update remaps”):

```bash
uv run riso migrate DEST|--answers-file PATH [--dry-run] [--json]
```

- Reads YAML, applies remaps, prints preview, writes unless `--dry-run`.
- Idempotent; exit 0 if already clean.
- Fail-closed on leftover removed keys or unmapped values.
- `riso update` runs the same apply on `.copier-answers.yml` before Copier (including `--dry-run` preview).

### Fixtures

`tests/unit/test_cli/fixtures/remap/` — one YAML per old key + one mixed + one already-canonical + one unknown leftover. WEB mirrors with TS fixtures.

---

## Sample shards (37 files)

Use `iter_sample_answer_files()` (already pruned). Six exclusive shards for PL-T01/T02:

| Shard | Variants |
| --- | --- |
| S0 | `default`, `ai-tools-off`, `makefile-runner`, `cli-docs`, `rag-enabled`, `gitlab-ci-python` |
| S1 | `api-python`, `api-monorepo`, `full-stack`, `changelog-python`, `changelog-full-stack`, `changelog-monorepo` |
| S2 | `docs-sphinx`, `docs-docusaurus`, `docs-fumadocs`, `docs-fumadocs-full`, `circleci-node`, `mcp-typescript` |
| S3 | `go-api`, `go-cli`, `go-mcp`, `rust-api`, `rust-cli`, `rust-mcp` |
| S4 | `electron-app`, `tauri-app` + saas `all-in-one`, `b2b-teams-full`, `b2c-consumer-app`, `edge-optimized` |
| S5 | saas `enterprise-ready`, `nextjs-vercel-neon-clerk-workos`, `nextjs-vercel-neon-clerk`, `nextjs-vercel-supabase-clerk`, `prelaunch-waitlist`, `remix-cloudflare-neon-drizzle`, `vercel-starter` |

---

## Hyperfine task graph

IDs are stable. Same `group` may run together **only** if locks are disjoint. `deps` are hard barriers.

### W0 — Inventory (parallel docs)

| ID | Task | deps | group | lock | verify |
| --- | --- | --- | --- | --- | --- |
| W0-T01a | Dirty map PY | — | W0A | `evidence/W0-dirty-py.md` | every dirty `template/files/python/**` owned |
| W0-T01b | Dirty map NODE | — | W0A | `evidence/W0-dirty-node.md` | node except saas |
| W0-T01c | Dirty map SAAS | — | W0A | `evidence/W0-dirty-saas.md` | `runtime/{nextjs,remix}` noted present |
| W0-T01d | Dirty map SYS | — | W0A | `evidence/W0-dirty-sys.md` | go/rust |
| W0-T01e | Dirty map DESKTOP | — | W0A | `evidence/W0-dirty-desktop.md` | electron/tauri |
| W0-T01f | Dirty map CLI+WEB+PLATFORM+DOCS | — | W0A | `evidence/W0-dirty-cross.md` | `src/riso`, `web`, `scripts`, `docs` |
| W0-T01j | Join dirty map; assert no planned writes under `samples/*/render/` | W0-T01a…f | W0B | `evidence/W0-inventory.md` | render/ = 0 |
| W0-T02a | Diff 3 SSOT dicts (core / scripts.lib / TS) | — | W0A | `evidence/W0-ssot-diff.md` | 8 keys identical |
| W0-T02b | `rg` old keys in `samples/**/copier-answers.yml` | — | W0A | `evidence/W0-rg-samples.txt` | cited or empty |
| W0-T02c | `rg` old keys in `web/src` presets/store/tests | — | W0A | `evidence/W0-rg-web.txt` | cited |
| W0-T02d | `rg` old keys in hooks, docs, skill, `generation_gates` | — | W0A | `evidence/W0-rg-gates.txt` | `saas_auth` hit in gates cited |
| W0-T03 | Keep/drop list per lane | W0-T01j | W0B | `evidence/W0-keep-drop.md` | flatten stays dropped |
| W0-T04 | Refresh `plan.taskgraph.json` lock checksum | W0-T01j | W0B | `plan.taskgraph.json` | JSON valid |

**W0 join:** T01j + T02a–d + T03 + T04.

### W1 — Remap SSOT + COORD extras (serial)

One writer. Do not parallelize these file sets.

| ID | Task | deps | lock | verify |
| --- | --- | --- | --- | --- |
| W1-M01 | `RemapOp` + `ANSWER_KEY_REMAPS` + `apply_removed_key_remaps` in `src/riso/core/removed_answer_keys.py` | W0 | that file | importable |
| W1-M01b | Table tests: wrap `api_language`, `mcp_language` (+ `node`→`typescript`) | W1-M01 | `tests/unit/test_cli/test_remap.py` | pass |
| W1-M01c | Table tests: `api_tracks`, `docs_site` | W1-M01 | same test file | pass |
| W1-M01d | Table tests: saas rename/split + `include_admin` | W1-M01 | same | pass |
| W1-M01e | Tests: idempotent, do-not-overwrite dest, unknown leftover raises | W1-M01 | same | pass |
| W1-M02 | Hook-safe twin + apply in `scripts/lib/removed_answer_keys.py` | W1-M01e | that file | fallback dict + apply |
| W1-M03 | Parity test core ↔ scripts.lib ↔ (later) TS | W1-M02 | `test_removed_keys_packaging.py` | keys+ops match |
| W1-C06 | `generation_gates._collect_saas_selected`: drop `saas_auth`; use module/provider | W1-M03 | `generation_gates.py` | existing gate tests |
| W1-C07 | Hooks: apply then reject leftovers (`pre_gen` + `post_gen`) | W1-M02 | `template/hooks/*.py` | `test_pre_gen_project.py` |
| W1-C01 | Copier: `openspec_extra` default `disabled`; exclude `openspec/**` unless enabled | W1-M03 | `template/copier.yml` | `riso validate` default |
| W1-C02 | Always render generated `mise.toml.jinja` (no exclude) | W1-C01 | `copier.yml` + new file stub ok | default answers include mise path |
| W1-C03 | Prompts/help: extras + 2.0 remap wording | W1-C01 | `template/prompts/**` | `uv run riso prompts` |
| W1-C04 | Catalog: ty not mypy; mise; OpenSpec optional | W1-C03 | `module_catalog.json.jinja` | `uv run riso catalog` |
| W1-C05 | Context parity if context touched | W1-C04 | context dirs | `verify_context_sync.py` |
| W1-C08 | Rewrite no-legacy policy: remap then fail-closed; list all 8 keys | W1-M03 | skill `no-legacy-answer-policy.md` | 8 keys; no “do not convert” |
| W1-OUT | Outbox md per contract id under `evidence/coord-outbox/` | W1-C05, W1-C07, W1-C08 | evidence | one md per CID |

**W1 join:** W1-OUT. Default `riso validate` still green.

### W2 — Parallel lanes (barrier: W1-OUT)

Launch **nine** lane leaders in one wave. Inside a lane, same-file tasks stay sequential.

#### CLI (`src/riso/**`, `tests/unit/test_cli/**`) — one leader, sequential call-site wiring

| ID | Task | deps | verify |
| --- | --- | --- | --- |
| CLI-T10 | `resolve_answers`: apply then reject | W1-OUT | `test_helpers.py` / `test_answers.py` |
| CLI-T11 | `validate_and_raise`: apply then reject | CLI-T10 | `test_validate.py` |
| CLI-T12 | `update` dry-run + live: remap `.copier-answers.yml`, preview, then Copier | CLI-T10 | **new** `test_update.py` |
| CLI-T13 | `recopy` apply then reject | CLI-T10 | `test_recopy.py` |
| CLI-T14 | `diff` apply then reject | CLI-T10 | `test_diff_ignore.py` or new |
| CLI-T15 | `generation_gates` apply before leftover errors | W1-C06 | `test_generation_gates.py` |
| CLI-T16 | `riso migrate` command + `--json` + `--dry-run` | CLI-T12 | `test_migrate.py`; `riso migrate --help` |
| CLI-T17 | Keep `--skip-post-gen` in `_GLOBAL_FLAGS` | W1-OUT | `test_argv_normalize.py` |
| CLI-T18 | Fixture YAMLs for 8 keys + mixed + leftover | CLI-T16 | fixtures exist; tests load them |
| CLI-JOIN | `uv run pytest tests/unit/test_cli/ tests/integration/test_riso_cli.py tests/integration/test_control_plane_gates.py -q -n 0` | CLI-T11…T18 | green |

#### WEB (`web/src/**`) — one leader

| ID | Task | deps | group | verify |
| --- | --- | --- | --- | --- |
| WEB-T01 | `remapRemovedAnswerKeys` + preview strings; keep 8-key set | W1-OUT | Wb1 | `removedAnswerKeys.test.ts` |
| WEB-T02 | Import YAML / paste: remap then fail-closed leftovers | WEB-T01 | Wb2 | vitest |
| WEB-T03 | `exportConfig` / `export-yaml` never emit old keys | WEB-T01 | Wb2 | vitest |
| WEB-T04 | Presets use canonical keys only | W1-OUT | Wb1 | `rg` old keys empty in presets |
| WEB-T05 | Store defaults: `task_runner=just`, no mypy, OpenSpec off | W1-OUT | Wb1 | `store.test.ts` |
| WEB-T06 | Playwright: import a remapped 1.x YAML (happy) + leftover (error) | WEB-T02 | Wb3 | e2e |
| WEB-JOIN | `pnpm --dir web run test:run` + existing smoke+wizard e2e | WEB-T03…T06 | Wb3 | 215+ vitest; e2e green |

WEB-T01 and CLI-T* both implement remaps — **parity** via W1-M03 + WEB-T01 asserting the same 8 keys and operator names.

#### MISE

| ID | Task | deps | verify |
| --- | --- | --- | --- |
| MISE-T01 | Add `template/files/mise.toml.jinja` pins: python 3.11, node **20**, pnpm, uv | W1-C02 | jinja valid |
| MISE-T02 | Generated Node pin ≥20 and **not** raised to maintainer 22 | MISE-T01 | pin string `20` |
| MISE-T03 | Maintainer `.mise.toml` stays Node 22; no floor raise | W1-OUT | file unchanged unless needed |
| MISE-T04 | Setup docs/scripts mention `mise install` once | MISE-T01 | `scripts/setup` or generated README |

#### PY (`template/files/python/**`)

| ID | Task | deps | group | verify |
| --- | --- | --- | --- | --- |
| PY-T01 | Add `hypothesis` to `[dependency-groups] test` | W1-OUT | P1 | `pyproject.toml.jinja` |
| PY-T02 | Add `respx` to `test` (and keep `httpx` in `api_python_test`) | W1-OUT | P1 | same file — **one writer** with T01 |
| PY-T03 | Shipped hypothesis test (gated on extra/always in tests/) | PY-T01 | P2 | jinja valid |
| PY-T04 | Shipped respx test (HTTP mock) | PY-T02 | P2 | jinja valid |
| PY-T05 | ty/ruff/uv remain; mypy not default | W1-OUT | P1 | `rg mypy` only in “not mypy” docs |
| PY-T06 | Keep DESIGN tokens / mpl / plotly / `custom.js.jinja` | W1-OUT | P2 | files exist |
| PY-T07 | Keep `BaseCommand.execute()` validate+run | W1-OUT | P2 | `test_cli.py.jinja` |
| PY-T08 | Keep pytest `python_files` = `test_*.py`/`*_test.py` | W1-OUT | P1 | no `.jinja` collection |
| PY-JOIN | `validate_jinja_templates.py` on python tree; `riso validate` `docs-sphinx` + `cli-docs` | PY-T03…T08 | P3 | ok:true |

#### NODE / SAAS / SYS / DESKTOP / OPENSPEC (parallel leaders)

| ID | lock | deps | verify |
| --- | --- | --- | --- |
| NODE-T01 mermaid/docs docusaurus | NODE | W1-OUT | jinja `node/docs/docusaurus` |
| NODE-T02 mermaid/docs fumadocs | NODE | W1-OUT | jinja `node/docs/fumadocs` |
| NODE-T03 leftover `tailwind.config.ts` absence is intentional | NODE | W1-OUT | file stays deleted |
| NODE-JOIN | NODE | T01–T03 | jinja node/docs |
| SAAS-T01 `runtime/nextjs` present | SAAS | W1-OUT | path exists |
| SAAS-T02 `runtime/remix` present | SAAS | W1-OUT | path exists |
| SAAS-T03 no flatten copies at saas app root | SAAS | T01,T02 | no mixed Next+Remix at root |
| SAAS-T04 token/a11y polish only (no new vendors) | SAAS | T03 | no new runtime/host |
| SYS-T01 keep `go.work` `.` + `./mcp` | SYS | W1-OUT | `test_go_templates.py` |
| SYS-T02 rust module excludes unchanged unless COORD outbox | SYS | W1-OUT | rust samples validate |
| DESK-T01 electron-store exclude plugin | DESKTOP | W1-OUT | `test_electron_templates.py` |
| DESK-T02 ESLint 9 + `ESLINT_USE_FLAT_CONFIG=false` + plugins | DESKTOP | T01 | jinja package/eslint |
| DESK-T03 `env.d.ts.jinja` + Tauri `vite-env.d.ts.jinja` | DESKTOP | T01 | files exist |
| DESK-T04 no clang/lld in Tauri cargo config | DESKTOP | T01 | `rg lld` empty |
| DESK-JOIN | DESKTOP | T01–T04 | electron + go/new-template tests |
| OS-T01 optional OpenSpec files under `template/files/openspec/**` | COORD leftover or new dir | W1-C01 | excluded by default |
| OS-T02 default sample render/validate has **no** openspec dir | OS-T01 | `samples/default` answers | |
| OS-T03 `openspec_extra=enabled` copies files | OS-T01 | validate a throwaway answers file | |

**W2 join:** CLI-JOIN + WEB-JOIN + PY-JOIN + NODE-JOIN + SAAS-T03 + SYS-T01 + DESK-JOIN + MISE-T02 + OS-T02.

### W3 — PLATFORM (barrier: W2 join)

| ID | Task | deps | group | verify |
| --- | --- | --- | --- | --- |
| PL-T01.S0…S5 | Scan/fix removed keys in shard answers | W2 | PL1 | per-shard `rg` empty |
| PL-T01 | Join shards | T01.S* | PL1 | all 37 scanned |
| PL-T02.S0…S5 | `riso validate --json` per shard (max 6) | PL-T01 | PL2 | each ok:true |
| PL-T02 | 37/37 summary JSON | T02.S* | PL2 | `evidence/W3-validate-summary.json` |
| PL-T03 | `just quality` | PL-T02 | PL3 | lint+ty+pytest |
| PL-T04 | `validate_jinja_templates.py template/files` | W2 | PL3 | exit 0 |
| PL-T05 | `verify_context_sync.py` + `just validate-agents` if those surfaces changed | W1-C05 | PL3 | exit 0 |
| PL-T06 | **Full** `uv run python scripts/ci/render_matrix.py` | PL-T02 | PL4 | writes `samples/metadata/render_matrix.json`; residual **not** allowed; log `evidence/W3-PL-T06.log`; do not kill |
| PL-T07 | `validate_release_readiness_skill.py` + `validate_workflows.py` + `validate_release_configs.py` | PL-T03, W1-C08 | PL3 | all exit 0 |
| PL-T09 | `rg riso-mcp src/riso template` empty | W2 | PL3 | no matches |
| PL-T10 | `scripts/ci/check_removed_key_ssot.py` (new): 3-way key+op parity | W2 WEB+CLI | PL3 | exit 0 |

T03/T04/T05/T09/T10 parallel after T02. T06 long-running **solo** (own agent). T08 is in W4.

### W4 — Docs, sphinx-W, refine, assurance

| ID | Task | deps | lock | verify |
| --- | --- | --- | --- | --- |
| W4-D01 | `docs/guides/v2-migration.md`: remap table, `riso migrate --dry-run`, fail-closed | CLI-JOIN | docs | page exists |
| W4-D02 | Add to `docs/guides/index.md` toctree | W4-D01 | that file | toctree lists it |
| W4-D03 | CHANGELOG **Unreleased 2.0.0** breaking remaps; **no tag** | W4-D01 | CHANGELOG.md | section exists |
| W4-D04 | `template/files/docs/upgrade-guide.md.jinja` lockstep (keys, mise, OpenSpec extra) | W4-D01 | that jinja | mentions remaps |
| W4-D05 | AGENTS/DESIGN pointers: mise, OpenSpec extra, ty/just/pnpm | W2 | `AGENTS.md.jinja` | jinja valid |
| PL-T08 | `uv run --group docs sphinx-build -W -b html docs` | W4-D02 | — | exit 0 |
| W4-R01 | Review pass 1 on required surfaces (payloads, CLI, wizard, docs, gates) | W3 join + PL-T08 | — | P0/P1 list or empty |
| W4-R02 | Fix any P0/P1 from R01 (owning lane locks) | W4-R01 | owning lane | tests for those fixes |
| W4-R03 | Review pass 2 | W4-R02 | — | **no new P0/P1** |
| W4-A01 | `ASSURANCE.md` + `evidence/` map **every** accepted fact | W4-R03, PL-T06 | GOAL | 25 facts mapped |

If R03 finds P0/P1: fix, then another pair of review passes (reset dry counter).

---

## Parallel dispatch

```text
W0A: T01a∥T01b∥T01c∥T01d∥T01e∥T01f ∥ T02a∥T02b∥T02c∥T02d
W0B: T01j → (T03 ∥ T04)
W1:  strictly serial (remap file → twin → gates → hooks → copier extras → outbox)
W2:  9 leaders in one wave
     CLI sequential call sites after W1-OUT
     WEB T01∥T04∥T05 then T02∥T03 then T06
     PY  T01+T02 one writer; T03∥T04∥T06∥T07; T05∥T08
     NODE T01∥T02∥T03
     SAAS T01∥T02 → T03 → T04
     SYS  T01∥T02
     DESK T01 then T02∥T03∥T04
     MISE T01 → T02∥T04; T03 independent
     OS   after W1-C01
W3:  T01.S0–S5 ∥ → T02.S0–S5 ∥ → (T03∥T04∥T05∥T09∥T10) ; T06 solo
W4:  D01 → D02∥D03∥D04 ; D05 ∥ ; PL-T08 after D02 ; R01→R02→R03→A01
```

Never two writers on `copier.yml`, `src/riso/core/removed_answer_keys.py`, `scripts/lib/removed_answer_keys.py`, or `web/src/lib/removedAnswerKeys.ts`.

---

## Official ladder (blocking)

```bash
just quality
# all 37:
uv run riso validate --answers-file samples/<v>/copier-answers.yml --json
uv run python scripts/ci/validate_jinja_templates.py template/files
uv run python scripts/ci/verify_context_sync.py   # if context touched
just validate-agents                              # if agents surfaces touched
uv run python scripts/ci/check_removed_key_ssot.py
uv run python scripts/ci/render_matrix.py         # must write samples/metadata/render_matrix.json
uv run --group docs sphinx-build -W -b html docs
uv run python scripts/ci/validate_release_readiness_skill.py
uv run python scripts/ci/validate_workflows.py
uv run python scripts/ci/validate_release_configs.py
rg 'api_tracks|api_language|docs_site|mcp_language|saas_starter_module|^saas_auth:|^saas_billing:|include_admin' samples --glob '**/copier-answers.yml'
rg riso-mcp src/riso template
```

---

## Risks

| Risk | Mitigation |
| --- | --- |
| `render_matrix` wall-clock (fumadocs `next build`, pnpm) | Solo agent; log + pid; continue-on-fail per variant; **must** write JSON; do not residual |
| Remap vs reject race if a site is missed | Call-site checklist in W2 CLI/WEB/hooks; integration tests that load fixture YAML through `resolve_answers` |
| Skill policy still forbids convert | W1-C08 before PL-T07 |
| Node 22 vs generated 20 | MISE-T02/T03; do not unify floors |
| Dirty tree fights (SaaS flatten) | W0-T03; flatten stays dropped |
| Three-way SSOT drift | W1-M03 + PL-T10 |
| `generation_gates` leftover `saas_auth` | W1-C06 |
| Unmapped historical values | Fail closed; document in v2-migration; do not guess |

**Out of scope:** git tag, push, PyPI, new languages/runtimes/vendors, bun/nix/wagents/Nx/Turbo as defaults, reintroducing `riso-mcp`, hand-editing renders.
