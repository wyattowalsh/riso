# inventory-dirty.md — W0-T03

Map of every dirty path in the maintainer worktree → exactly one lane.

## Snapshot

| Field | Value |
|-------|-------|
| Captured (UTC) | `2026-07-29T01:21:58Z` |
| Repo root | `/Users/ww/dev/projects/riso` |
| Branch | `main` |
| HEAD | `9b62b31` |
| Commands | `git status --short`, `git diff --name-only`, `git ls-files --others --exclude-standard` |
| Total dirty leaf paths | **222** |
| Tracked modified/deleted | 54 |
| Untracked | 168 |

## Classification rules (priority order)

Source: `goals/riso-lanes-assurance/plan.md` exclusive write locks + per-lane OPERATING/facts + goal packages.

| Lane | Roots / rule |
|------|--------------|
| **COORD** | `template/copier.yml`, `template/hooks/**`, `template/macros/**`, `template/files/module_catalog.json.jinja`, `template/prompts/**`, `.github/context/**`, `template/files/.github/context/**`, `goals/riso-lane-coord/**` |
| **PY** | `template/files/python/**`, `goals/riso-lane-py/**` |
| **NODE** | `template/files/node/**` except `node/saas/**`, `goals/riso-lane-node/**` |
| **SAAS** | `template/files/node/saas/**`, `template/files/saas-starter/**`, `goals/riso-lane-saas/**` |
| **SYS** | `template/files/go/**`, `template/files/rust/**`, `goals/riso-lane-sys/**` |
| **DESKTOP** | `template/files/electron/**`, `template/files/tauri/**`, `goals/riso-lane-desktop/**` |
| **CLI** | `src/riso/**`, `tests/unit/test_cli/**`, `goals/riso-lane-cli/**` |
| **PLATFORM** | `scripts/ci/**`, `scripts/render-samples.sh`, `scripts/hooks/**` (affinity/audit), `template/files/quality/**`, `template/files/testing/**`, `samples/*/copier-answers.yml`, `samples/metadata/**`, `tests/unit/ci/**`, `tests/unit/test_go_templates.py` (QUAL gate), minimal `.github/workflows/**`, `goals/riso-lane-platform/**` |
| **ASSURANCE** | `goals/riso-lanes-assurance/**` (integrator package; report-only on product trees) |
| **OUT-OF-SCOPE** | Local harness/tooling outside exclusive roots (e.g. `.claude/**`, `.grok/**`); not owned by payload/COORD/PLATFORM write locks |

Hard forbid (never hand-edit regardless of lane): `samples/*/render/**`, lockfile hand-edits, secrets, reintroduce `riso-mcp`.

## Counts by lane

| Lane | Paths | M | D | ?? |
|------|------:|--:|--:|---:|
| COORD | 19 | 0 | 0 | 19 |
| PY | 26 | 12 | 0 | 14 |
| NODE | 8 | 0 | 0 | 8 |
| SAAS | 8 | 0 | 0 | 8 |
| SYS | 41 | 20 | 2 | 19 |
| DESKTOP | 9 | 0 | 0 | 9 |
| CLI | 18 | 3 | 0 | 15 |
| PLATFORM | 67 | 17 | 0 | 50 |
| ASSURANCE | 24 | 0 | 0 | 24 |
| OUT-OF-SCOPE | 2 | 0 | 0 | 2 |
| **TOTAL** | **222** | | | |

## Path → lane (complete)

Status codes: `M` modified tracked · `D` deleted tracked · `??` untracked.

### COORD (19)

| Status | Path | Rule |
|--------|------|------|
| `??` | `goals/riso-lane-coord/APPLY-CHECKLIST.md` | lane package goals/riso-lane-coord/** |
| `??` | `goals/riso-lane-coord/LANE.md` | lane package goals/riso-lane-coord/** |
| `??` | `goals/riso-lane-coord/README.md` | lane package goals/riso-lane-coord/** |
| `??` | `goals/riso-lane-coord/examples/minimal-handoff.md` | lane package goals/riso-lane-coord/** |
| `??` | `goals/riso-lane-coord/examples/minimal-outbox.md` | lane package goals/riso-lane-coord/** |
| `??` | `goals/riso-lane-coord/facts-result.json` | lane package goals/riso-lane-coord/** |
| `??` | `goals/riso-lane-coord/facts-review.json` | lane package goals/riso-lane-coord/** |
| `??` | `goals/riso-lane-coord/facts.md` | lane package goals/riso-lane-coord/** |
| `??` | `goals/riso-lane-coord/facts.meta.json` | lane package goals/riso-lane-coord/** |
| `??` | `goals/riso-lane-coord/goal.md` | lane package goals/riso-lane-coord/** |
| `??` | `goals/riso-lane-coord/handoff-template.md` | lane package goals/riso-lane-coord/** |
| `??` | `goals/riso-lane-coord/inbox/.gitkeep` | lane package goals/riso-lane-coord/** |
| `??` | `goals/riso-lane-coord/interview-result.json` | lane package goals/riso-lane-coord/** |
| `??` | `goals/riso-lane-coord/interview.json` | lane package goals/riso-lane-coord/** |
| `??` | `goals/riso-lane-coord/outbox-template.md` | lane package goals/riso-lane-coord/** |
| `??` | `goals/riso-lane-coord/outbox/.gitkeep` | lane package goals/riso-lane-coord/** |
| `??` | `goals/riso-lane-coord/outbox/bootstrap-verify.md` | lane package goals/riso-lane-coord/** |
| `??` | `goals/riso-lane-coord/plan-gate-result.json` | lane package goals/riso-lane-coord/** |
| `??` | `goals/riso-lane-coord/plan.md` | lane package goals/riso-lane-coord/** |

### PY (26)

| Status | Path | Rule |
|--------|------|------|
| `??` | `goals/riso-lane-py/facts-result.json` | lane package goals/riso-lane-py/** |
| `??` | `goals/riso-lane-py/facts-review.json` | lane package goals/riso-lane-py/** |
| `??` | `goals/riso-lane-py/facts.md` | lane package goals/riso-lane-py/** |
| `??` | `goals/riso-lane-py/facts.meta.json` | lane package goals/riso-lane-py/** |
| `??` | `goals/riso-lane-py/goal.md` | lane package goals/riso-lane-py/** |
| `??` | `goals/riso-lane-py/handoffs/README.md` | lane package goals/riso-lane-py/** |
| `??` | `goals/riso-lane-py/handoffs/api-features-normalize.md` | lane package goals/riso-lane-py/** |
| `??` | `goals/riso-lane-py/handoffs/exclude-empty-dirs.md` | lane package goals/riso-lane-py/** |
| `??` | `goals/riso-lane-py/handoffs/graphql-sample-coverage.md` | lane package goals/riso-lane-py/** |
| `??` | `goals/riso-lane-py/interview-result.json` | lane package goals/riso-lane-py/** |
| `??` | `goals/riso-lane-py/interview.json` | lane package goals/riso-lane-py/** |
| `??` | `goals/riso-lane-py/plan-gate-result.json` | lane package goals/riso-lane-py/** |
| `??` | `goals/riso-lane-py/plan.md` | lane package goals/riso-lane-py/** |
| `??` | `goals/riso-lane-py/scripts/check_dual_gates.py` | lane package goals/riso-lane-py/** |
| `M` | `template/files/python/src/{{ package_name }}/cli/__init__.py.jinja` | write-root template/files/python/** |
| `M` | `template/files/python/src/{{ package_name }}/graphql_api/auth.py.jinja` | write-root template/files/python/** |
| `M` | `template/files/python/src/{{ package_name }}/graphql_api/complexity.py.jinja` | write-root template/files/python/** |
| `M` | `template/files/python/src/{{ package_name }}/graphql_api/context.py.jinja` | write-root template/files/python/** |
| `M` | `template/files/python/src/{{ package_name }}/graphql_api/dataloaders.py.jinja` | write-root template/files/python/** |
| `M` | `template/files/python/src/{{ package_name }}/graphql_api/errors.py.jinja` | write-root template/files/python/** |
| `M` | `template/files/python/src/{{ package_name }}/graphql_api/mutations/user_mutations.py.jinja` | write-root template/files/python/** |
| `M` | `template/files/python/src/{{ package_name }}/graphql_api/pagination.py.jinja` | write-root template/files/python/** |
| `M` | `template/files/python/src/{{ package_name }}/graphql_api/queries/user_queries.py.jinja` | write-root template/files/python/** |
| `M` | `template/files/python/src/{{ package_name }}/graphql_api/subscriptions/user_subscriptions.py.jinja` | write-root template/files/python/** |
| `M` | `template/files/python/src/{{ package_name }}/graphql_api/types/post.py.jinja` | write-root template/files/python/** |
| `M` | `template/files/python/src/{{ package_name }}/graphql_api/types/user.py.jinja` | write-root template/files/python/** |

### NODE (8)

| Status | Path | Rule |
|--------|------|------|
| `??` | `goals/riso-lane-node/facts-result.json` | lane package goals/riso-lane-node/** |
| `??` | `goals/riso-lane-node/facts-review.json` | lane package goals/riso-lane-node/** |
| `??` | `goals/riso-lane-node/facts.md` | lane package goals/riso-lane-node/** |
| `??` | `goals/riso-lane-node/facts.meta.json` | lane package goals/riso-lane-node/** |
| `??` | `goals/riso-lane-node/goal.md` | lane package goals/riso-lane-node/** |
| `??` | `goals/riso-lane-node/interview-result.json` | lane package goals/riso-lane-node/** |
| `??` | `goals/riso-lane-node/interview.json` | lane package goals/riso-lane-node/** |
| `??` | `goals/riso-lane-node/plan.md` | lane package goals/riso-lane-node/** |

### SAAS (8)

| Status | Path | Rule |
|--------|------|------|
| `??` | `goals/riso-lane-saas/facts-result.json` | lane package goals/riso-lane-saas/** |
| `??` | `goals/riso-lane-saas/facts-review.json` | lane package goals/riso-lane-saas/** |
| `??` | `goals/riso-lane-saas/facts.md` | lane package goals/riso-lane-saas/** |
| `??` | `goals/riso-lane-saas/facts.meta.json` | lane package goals/riso-lane-saas/** |
| `??` | `goals/riso-lane-saas/goal.md` | lane package goals/riso-lane-saas/** |
| `??` | `goals/riso-lane-saas/interview-result.json` | lane package goals/riso-lane-saas/** |
| `??` | `goals/riso-lane-saas/interview.json` | lane package goals/riso-lane-saas/** |
| `??` | `goals/riso-lane-saas/plan.md` | lane package goals/riso-lane-saas/** |

### SYS (41)

| Status | Path | Rule |
|--------|------|------|
| `??` | `goals/riso-lane-sys/baseline.md` | lane package goals/riso-lane-sys/** |
| `??` | `goals/riso-lane-sys/facts-result.json` | lane package goals/riso-lane-sys/** |
| `??` | `goals/riso-lane-sys/facts-review.json` | lane package goals/riso-lane-sys/** |
| `??` | `goals/riso-lane-sys/facts.md` | lane package goals/riso-lane-sys/** |
| `??` | `goals/riso-lane-sys/facts.meta.json` | lane package goals/riso-lane-sys/** |
| `??` | `goals/riso-lane-sys/goal.md` | lane package goals/riso-lane-sys/** |
| `??` | `goals/riso-lane-sys/handoffs/COORD-go-version-mcp.md` | lane package goals/riso-lane-sys/** |
| `??` | `goals/riso-lane-sys/handoffs/COORD-rust-module-excludes.md` | lane package goals/riso-lane-sys/** |
| `??` | `goals/riso-lane-sys/handoffs/PLATFORM-go-api-features-answers.md` | lane package goals/riso-lane-sys/** |
| `??` | `goals/riso-lane-sys/handoffs/PLATFORM-rust-samples.md` | lane package goals/riso-lane-sys/** |
| `??` | `goals/riso-lane-sys/handoffs/QUAL-go-template-tests.md` | lane package goals/riso-lane-sys/** |
| `??` | `goals/riso-lane-sys/interview-result.json` | lane package goals/riso-lane-sys/** |
| `??` | `goals/riso-lane-sys/interview.json` | lane package goals/riso-lane-sys/** |
| `??` | `goals/riso-lane-sys/plan-gate-result.json` | lane package goals/riso-lane-sys/** |
| `??` | `goals/riso-lane-sys/plan.fileshards.json` | lane package goals/riso-lane-sys/** |
| `??` | `goals/riso-lane-sys/plan.md` | lane package goals/riso-lane-sys/** |
| `??` | `goals/riso-lane-sys/plan.taskgraph.json` | lane package goals/riso-lane-sys/** |
| `M` | `template/files/go/.air.toml.jinja` | write-root template/files/{go,rust}/** |
| `M` | `template/files/go/Makefile.jinja` | write-root template/files/{go,rust}/** |
| `M` | `template/files/go/api/internal/server/server.go.jinja` | write-root template/files/{go,rust}/** |
| `M` | `template/files/go/api/main.go.jinja` | write-root template/files/{go,rust}/** |
| `M` | `template/files/go/cli/cmd/root.go.jinja` | write-root template/files/{go,rust}/** |
| `M` | `template/files/go/cli/cmd/serve.go.jinja` | write-root template/files/{go,rust}/** |
| `D` | `template/files/go/cli/internal/config/config.go.jinja` | write-root template/files/{go,rust}/** |
| `D` | `template/files/go/cli/internal/logger/logger.go.jinja` | write-root template/files/{go,rust}/** |
| `M` | `template/files/go/go.work.jinja` | write-root template/files/{go,rust}/** |
| `??` | `template/files/go/internal/config/config.go.jinja` | write-root template/files/{go,rust}/** |
| `??` | `template/files/go/internal/logger/logger.go.jinja` | write-root template/files/{go,rust}/** |
| `M` | `template/files/go/justfile.jinja` | write-root template/files/{go,rust}/** |
| `M` | `template/files/go/mcp/README.md.jinja` | write-root template/files/{go,rust}/** |
| `M` | `template/files/go/mcp/go.mod.jinja` | write-root template/files/{go,rust}/** |
| `M` | `template/files/rust/ARCHITECTURE.md.jinja` | write-root template/files/{go,rust}/** |
| `M` | `template/files/rust/Cargo.toml.jinja` | write-root template/files/{go,rust}/** |
| `M` | `template/files/rust/Makefile.jinja` | write-root template/files/{go,rust}/** |
| `M` | `template/files/rust/QUICKSTART.md.jinja` | write-root template/files/{go,rust}/** |
| `M` | `template/files/rust/README.md.jinja` | write-root template/files/{go,rust}/** |
| `M` | `template/files/rust/api/handlers/health.rs.jinja` | write-root template/files/{go,rust}/** |
| `M` | `template/files/rust/build.rs.jinja` | write-root template/files/{go,rust}/** |
| `M` | `template/files/rust/justfile.jinja` | write-root template/files/{go,rust}/** |
| `M` | `template/files/rust/mcp/Cargo.toml.jinja` | write-root template/files/{go,rust}/** |
| `M` | `template/files/rust/src/main.rs.jinja` | write-root template/files/{go,rust}/** |

### DESKTOP (9)

| Status | Path | Rule |
|--------|------|------|
| `??` | `goals/riso-lane-desktop/facts-result.json` | lane package goals/riso-lane-desktop/** |
| `??` | `goals/riso-lane-desktop/facts-review.json` | lane package goals/riso-lane-desktop/** |
| `??` | `goals/riso-lane-desktop/facts.md` | lane package goals/riso-lane-desktop/** |
| `??` | `goals/riso-lane-desktop/facts.meta.json` | lane package goals/riso-lane-desktop/** |
| `??` | `goals/riso-lane-desktop/goal.md` | lane package goals/riso-lane-desktop/** |
| `??` | `goals/riso-lane-desktop/interview-result.json` | lane package goals/riso-lane-desktop/** |
| `??` | `goals/riso-lane-desktop/interview.json` | lane package goals/riso-lane-desktop/** |
| `??` | `goals/riso-lane-desktop/plan-gate-result.json` | lane package goals/riso-lane-desktop/** |
| `??` | `goals/riso-lane-desktop/plan.md` | lane package goals/riso-lane-desktop/** |

### CLI (18)

| Status | Path | Rule |
|--------|------|------|
| `??` | `goals/riso-lane-cli/facts-result.json` | lane package goals/riso-lane-cli/** |
| `??` | `goals/riso-lane-cli/facts-review.json` | lane package goals/riso-lane-cli/** |
| `??` | `goals/riso-lane-cli/facts.md` | lane package goals/riso-lane-cli/** |
| `??` | `goals/riso-lane-cli/facts.meta.json` | lane package goals/riso-lane-cli/** |
| `??` | `goals/riso-lane-cli/goal.md` | lane package goals/riso-lane-cli/** |
| `??` | `goals/riso-lane-cli/interview-result.json` | lane package goals/riso-lane-cli/** |
| `??` | `goals/riso-lane-cli/interview.json` | lane package goals/riso-lane-cli/** |
| `??` | `goals/riso-lane-cli/plan-gate-result.json` | lane package goals/riso-lane-cli/** |
| `??` | `goals/riso-lane-cli/plan.md` | lane package goals/riso-lane-cli/** |
| `??` | `goals/riso-lane-cli/tasks.graph.json` | lane package goals/riso-lane-cli/** |
| `M` | `src/riso/cli/commands/doctor.py` | write-root src/riso/** | tests/unit/test_cli/** |
| `??` | `tests/unit/test_cli/test_argv_normalize.py` | write-root src/riso/** | tests/unit/test_cli/** |
| `M` | `tests/unit/test_cli/test_doctor.py` | write-root src/riso/** | tests/unit/test_cli/** |
| `M` | `tests/unit/test_cli/test_output.py` | write-root src/riso/** | tests/unit/test_cli/** |
| `??` | `tests/unit/test_cli/test_prompts.py` | write-root src/riso/** | tests/unit/test_cli/** |
| `??` | `tests/unit/test_cli/test_recopy.py` | write-root src/riso/** | tests/unit/test_cli/** |
| `??` | `tests/unit/test_cli/test_validate.py` | write-root src/riso/** | tests/unit/test_cli/** |
| `??` | `tests/unit/test_cli/test_variants.py` | write-root src/riso/** | tests/unit/test_cli/** |

### PLATFORM (67)

| Status | Path | Rule |
|--------|------|------|
| `??` | `goals/riso-lane-platform/OPERATING.md` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/audit/AUDIT-20260725.md` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/audit/COVERAGE_GAPS.md` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/audit/answers-drift.md` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/audit/matrix-decision.md` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/audit/quality-review.md` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/audit/testing-review.md` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/audit/validate/ai-tools-off.json` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/audit/validate/api-monorepo.json` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/audit/validate/api-python.json` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/audit/validate/changelog-full-stack.json` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/audit/validate/changelog-monorepo.json` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/audit/validate/changelog-python.json` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/audit/validate/circleci-node.json` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/audit/validate/cli-docs.json` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/audit/validate/default.json` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/audit/validate/docs-docusaurus.json` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/audit/validate/docs-fumadocs-full.json` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/audit/validate/docs-fumadocs.json` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/audit/validate/docs-sphinx.json` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/audit/validate/electron-app.json` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/audit/validate/full-stack.json` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/audit/validate/gitlab-ci-python.json` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/audit/validate/go-api.json` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/audit/validate/go-cli.json` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/audit/validate/go-mcp.json` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/audit/validate/makefile-runner.json` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/audit/validate/mcp-typescript.json` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/audit/validate/rag-enabled.json` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/audit/validate/tauri-app.json` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/facts-result.json` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/facts-review.json` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/facts.md` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/facts.meta.json` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/goal.md` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/inbox/README.md` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/inbox/_TEMPLATE.md` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/interview-result.json` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/interview.json` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/outbox/README.md` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/outbox/_TEMPLATE.md` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/outbox/coord-mcp-languages-typescript.md` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/plan-gate-result.json` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/plan.md` | lane package goals/riso-lane-platform/** |
| `??` | `goals/riso-lane-platform/plan.taskgraph.json` | lane package goals/riso-lane-platform/** |
| `M` | `samples/api-monorepo/copier-answers.yml` | write-root samples/*/copier-answers.yml |
| `M` | `samples/api-python/copier-answers.yml` | write-root samples/*/copier-answers.yml |
| `M` | `samples/changelog-full-stack/copier-answers.yml` | write-root samples/*/copier-answers.yml |
| `M` | `samples/changelog-monorepo/copier-answers.yml` | write-root samples/*/copier-answers.yml |
| `M` | `samples/changelog-python/copier-answers.yml` | write-root samples/*/copier-answers.yml |
| `M` | `samples/circleci-node/copier-answers.yml` | write-root samples/*/copier-answers.yml |
| `M` | `samples/docs-docusaurus/copier-answers.yml` | write-root samples/*/copier-answers.yml |
| `M` | `samples/docs-fumadocs-full/copier-answers.yml` | write-root samples/*/copier-answers.yml |
| `M` | `samples/docs-sphinx/copier-answers.yml` | write-root samples/*/copier-answers.yml |
| `M` | `samples/full-stack/copier-answers.yml` | write-root samples/*/copier-answers.yml |
| `M` | `samples/gitlab-ci-python/copier-answers.yml` | write-root samples/*/copier-answers.yml |
| `M` | `samples/go-api/copier-answers.yml` | write-root samples/*/copier-answers.yml |
| `M` | `scripts/ci/render_matrix.py` | write-root scripts/ci/** | render-samples.sh |
| `M` | `scripts/hooks/quality_tool_check.py` | affinity: PLATFORM quality tooling (audit-owned; adjacent to scripts/ci) |
| `M` | `scripts/hooks/workflow_validator.py` | affinity: PLATFORM quality tooling (audit-owned; adjacent to scripts/ci) |
| `M` | `scripts/render-samples.sh` | write-root scripts/ci/** | render-samples.sh |
| `??` | `tests/unit/ci/test_generate_matrix_data.py` | write-root tests/unit/ci/** (OPERATING.md) |
| `??` | `tests/unit/ci/test_quality_tool_check.py` | write-root tests/unit/ci/** (OPERATING.md) |
| `??` | `tests/unit/ci/test_run_quality_suite.py` | write-root tests/unit/ci/** (OPERATING.md) |
| `??` | `tests/unit/ci/test_verify_version_sync.py` | write-root tests/unit/ci/** (OPERATING.md) |
| `??` | `tests/unit/ci/test_workflow_validator_import.py` | write-root tests/unit/ci/** (OPERATING.md) |
| `M` | `tests/unit/test_go_templates.py` | QUAL gate outside SYS; PL-T04 / SYS QUAL handoff → PLATFORM |

### ASSURANCE (24)

| Status | Path | Rule |
|--------|------|------|
| `??` | `goals/riso-lanes-assurance/evidence/W0-T01-node-goal.md` | integrator package goals/riso-lanes-assurance/** |
| `??` | `goals/riso-lanes-assurance/evidence/W0-T02-saas-goal.md` | integrator package goals/riso-lanes-assurance/** |
| `??` | `goals/riso-lanes-assurance/evidence/W0-T03-inventory.md` | integrator package goals/riso-lanes-assurance/** |
| `??` | `goals/riso-lanes-assurance/facts-result.json` | integrator package goals/riso-lanes-assurance/** |
| `??` | `goals/riso-lanes-assurance/facts-review.json` | integrator package goals/riso-lanes-assurance/** |
| `??` | `goals/riso-lanes-assurance/facts.md` | integrator package goals/riso-lanes-assurance/** |
| `??` | `goals/riso-lanes-assurance/facts.meta.json` | integrator package goals/riso-lanes-assurance/** |
| `??` | `goals/riso-lanes-assurance/goal.md` | integrator package goals/riso-lanes-assurance/** |
| `??` | `goals/riso-lanes-assurance/grok-context/ASSURANCE.md` | integrator package goals/riso-lanes-assurance/** |
| `??` | `goals/riso-lanes-assurance/grok-context/CLI.md` | integrator package goals/riso-lanes-assurance/** |
| `??` | `goals/riso-lanes-assurance/grok-context/COORD.md` | integrator package goals/riso-lanes-assurance/** |
| `??` | `goals/riso-lanes-assurance/grok-context/DESKTOP.md` | integrator package goals/riso-lanes-assurance/** |
| `??` | `goals/riso-lanes-assurance/grok-context/NODE.md` | integrator package goals/riso-lanes-assurance/** |
| `??` | `goals/riso-lanes-assurance/grok-context/PLATFORM.md` | integrator package goals/riso-lanes-assurance/** |
| `??` | `goals/riso-lanes-assurance/grok-context/PY.md` | integrator package goals/riso-lanes-assurance/** |
| `??` | `goals/riso-lanes-assurance/grok-context/SAAS.md` | integrator package goals/riso-lanes-assurance/** |
| `??` | `goals/riso-lanes-assurance/grok-context/SYS.md` | integrator package goals/riso-lanes-assurance/** |
| `??` | `goals/riso-lanes-assurance/handoffs-board.md` | integrator package goals/riso-lanes-assurance/** |
| `??` | `goals/riso-lanes-assurance/interview-result.json` | integrator package goals/riso-lanes-assurance/** |
| `??` | `goals/riso-lanes-assurance/interview.json` | integrator package goals/riso-lanes-assurance/** |
| `??` | `goals/riso-lanes-assurance/inventory-dirty.md` | integrator package goals/riso-lanes-assurance/** |
| `??` | `goals/riso-lanes-assurance/plan-gate-result.json` | integrator package goals/riso-lanes-assurance/** |
| `??` | `goals/riso-lanes-assurance/plan.md` | integrator package goals/riso-lanes-assurance/** |
| `??` | `goals/riso-lanes-assurance/plan.taskgraph.json` | integrator package goals/riso-lanes-assurance/** |

### OUT-OF-SCOPE (2)

| Status | Path | Rule |
|--------|------|------|
| `??` | `.claude/skills/mcp-installer/uv.lock` | local harness/tooling outside exclusive lane roots |
| `??` | `.grok/workflows/riso-lanes-assurance.rhai` | local harness/tooling outside exclusive lane roots |

## Notes

1. **No dirty NODE/SAAS/DESKTOP product trees** — only their untracked `goals/riso-lane-*` packages appear under those lanes.
2. **SYS** carries the bulk of product dirty work (Go shared `internal/` move, CLI/API/MCP, Rust root/MCP/API).
3. **PY** dirty set is GraphQL dual-gate + CLI package init under `template/files/python/**`.
4. **PLATFORM** owns all dirty `samples/*/copier-answers.yml`, CI scripts, hooks affinity, CI unit tests, and `test_go_templates.py` (SYS QUAL handoff).
5. **CLI** owns doctor + test_cli expansions.
6. **COORD** dirty set today is package-only (`goals/riso-lane-coord/**`); no contract tree edits yet (W1 applies handoffs).
7. **OUT-OF-SCOPE**: `.claude/skills/mcp-installer/uv.lock` (local skill lock; never hand-edit locks) and `.grok/workflows/riso-lanes-assurance.rhai` (local Grok harness workflow). Neither blocks lane execution.
8. This file and `evidence/W0-T03-inventory.md` are dirty under **ASSURANCE** after write; expected.

## Ownership completeness check

- Dirty leaf paths observed: `222`
- Paths with exactly one lane: `222`
- Unowned paths: `0`
- Multi-owned paths: `0`

Evidence: [`evidence/W0-T03-inventory.md`](./evidence/W0-T03-inventory.md)
