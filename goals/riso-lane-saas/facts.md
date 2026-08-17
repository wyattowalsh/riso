# Facts

- SAAS lane may write only under template/files/node/saas/** and template/files/saas-starter/**.
- SAAS lane never writes template/copier.yml, template/hooks/**, template/macros/**, module_catalog.json.jinja, non-SaaS node trees outside node/saas/, python/go/rust/frontend/electron/tauri, src/riso/**, web/**, samples/*/render/**, or samples/*/copier-answers.yml.
- SAAS lane does not create branches, worktrees, commits, or pushes unless the human explicitly asks.
- SAAS lane never hand-edits uv.lock or pnpm-lock.yaml and never commits, prints, or persists secrets.
- First /goal execution performs a full module sweep of the SaaS scaffold under owned paths: runtime, hosting/DB/ORM wiring, auth, billing, remaining integrations, UI/marketing, compliance, observability, and tests.
- Large SAAS work is sequenced as runtime → hosting/ORM/db → auth → billing → remaining integrations → UI/marketing → compliance/observability/tests, resolving shared package.json and lib collisions before parallel sub-work.
- Template gates under owned paths stay coherent with layered answers: saas_infra_module before auth before billing (and dependent app/integration modules as already expressed in templates).
- SaaS-enabled answers produce a coherent file tree from owned paths (no obvious broken Jinja, missing shared roots, or layering contradictions for enabled modules).
- SaaS-only files under owned paths are gated so non-SaaS variants are not broken by incorrect leakage of SaaS scaffold content (within gates SAAS controls).
- Verification uses a strict matrix: uv run riso validate --json against every samples/saas-starter/*/copier-answers.yml variant (currently 11 variants).
- When available, uv run python scripts/ci/validate_saas_combinations.py must pass (or SAAS documents owned-path failures with fixes; contract gaps go to COORD handoffs).
- When available, uv run python scripts/ci/validate_jinja_templates.py must pass for SaaS-touched templates (or failures under owned paths are fixed).
- samples/*/render/ is never hand-edited; regeneration is only via render scripts when PLATFORM/integrator requests it.
- Any needed saas_* prompt, when-condition, hook validation, or catalog change is proposed only via goals/riso-lane-saas/handoffs/*.md structured handoffs — never by editing Copier contract files from this lane.
- Python tooling runs via uv run; pnpm is used only when needed for SaaS package surfaces under owned paths.
- template/files/saas-starter/** stays aligned with the layered SaaS scaffold it documents/configures (e.g. saas-starter.config.ts.jinja and README).
- Done when: full-module sweep work under owned paths is coherent, strict-matrix validation + combination/jinja scripts pass or residual non-owned gaps are listed as COORD/PLATFORM handoffs, and no writes occurred outside owned paths.
