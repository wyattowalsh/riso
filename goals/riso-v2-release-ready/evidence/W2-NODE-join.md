# W2-NODE join

- Wave: W2 / lane NODE
- Tasks: `NODE-T01`, `NODE-T02`, `NODE-T03`, `NODE-JOIN`
- Status: **green**
- Repo: `/Users/ww/dev/projects/riso` branch `main` HEAD `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b`
- Exclusive write root: `template/files/node/**` except `node/saas/**`
- `samples/*/render/**` writes: **0**
- Residual file: none (`residuals/NODE.md` not created)

## Task results

| ID | Decision | Verify | Status |
| --- | --- | --- | --- |
| NODE-T01 | mermaid/docs docusaurus DESIGN tokens + mermaid `base`/`strict` | jinja node/docs + `docs-docusaurus` validate **ok:true** | green |
| NODE-T02 | mermaid/docs fumadocs theme adapter + gated diagrams; no export rewrites | jinja node/docs + fumadocs / fumadocs-full **ok:true** | green |
| NODE-T03 | leftover `tailwind.config.ts.jinja` stays deleted | path absent; `rg tailwind.config` empty under `node/docs` | green |
| NODE-JOIN | jinja `template/files/node/docs` | **108** templates all OK | green |

## Commands

```text
find template/files/node/docs -name '*.jinja' -type f -print0 \
  | xargs -0 uv run python scripts/ci/validate_jinja_templates.py
# Validated 108 Jinja template(s): all OK

uv run riso validate --answers-file samples/docs-docusaurus/copier-answers.yml --json
# ok: true

uv run riso validate --answers-file samples/docs-fumadocs/copier-answers.yml --json
# ok: true

uv run riso validate --answers-file samples/docs-fumadocs-full/copier-answers.yml --json
# ok: true
```

Warnings on all three validates are only Copier metadata keys `_commit` / `_src_path`.

## Audit

- No writes under `template/files/node/saas/**`, `copier.yml`, hooks, `samples/*/copier-answers.yml`, `samples/*/render/**`, lockfiles.
- Pre-existing dirty saas / copier / hooks belong to other lanes; not touched.
- `template/files/node/apps/api-node/**` not part of T01–T03; not edited this wave.

## Not NODE

- Sample answers edits → PLATFORM
- `copier.yml` mermaid exclude granularity → COORD
- SaaS flatten / runtime → SAAS

## Foreign lastfailed (CLI lock — not edited)

`.pytest_cache` lastfailed is four **CLI** tests. They fail because W1 remap now applies `api_tracks` / `saas_auth` before reject (CLI-T11 / T13 / T15 still in flight). NODE did not touch `tests/unit/test_cli/**` or `src/riso/**`.

```text
uv run pytest \
  tests/unit/test_cli/test_validate.py::test_validate_rejects_removed_answer_keys \
  tests/unit/test_cli/test_generation_gates.py::test_leftover_saas_auth_still_rejected_as_removed_key \
  tests/unit/test_cli/test_generation_gates.py::test_removed_keys_block \
  tests/unit/test_cli/test_recopy.py::test_recopy_rejects_removed_answer_keys \
  -q -n 0
# 4 failed — owner CLI
```

NODE-adjacent pytest this wave: `test_new_templates`, `test_template_validate`, `test_validate_workflows`, `test_agents_md_render`, fumadocs/docusaurus post_gen guidance — **46 passed** (+ 10 docs-keyword).
