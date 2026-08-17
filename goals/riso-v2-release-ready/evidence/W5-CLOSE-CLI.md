# W5 CLOSE-CLI — remap contract + JOIN leftover re-verify

- Wave: **CLOSE-CLI**
- Lane: **CLI**
- Date: 2026-08-14
- Repo: `/Users/ww/dev/projects/riso`
- Branch: `main` · HEAD `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b`
- Exclusive write roots: `src/riso/cli/**`, `src/riso/core/**`, `src/riso/template/**`, `tests/unit/test_cli/**`, `tests/integration/test_riso_cli.py`, `tests/integration/test_control_plane_gates.py`, this file, `residuals/CLI.md`
- Product-code edits this session: **0**
- `samples/*/render/**` writes: **0**
- Status: **green** — lock has no remaining P0/P1

## Contract (live)

`apply_removed_key_remaps` then `reject_removed_answer_keys` (`src/riso/core/answers.py` `apply_then_reject_removed_keys`). No dest overwrite if dest is set. Idempotent second apply. Unmapped leftovers stay on the old key and fail closed. No dual-path aliases after remap.

Eight keys: `api_tracks`, `api_language`, `docs_site`, `mcp_language`, `saas_starter_module`, `saas_auth`, `saas_billing`, `include_admin`.

`saas_auth=lucia` and `saas_auth=firebase` are unmapped leftovers (`_SAAS_AUTH_PROVIDERS` = `clerk`|`authjs` only). Remappable `api_tracks=python` must not fail closed.

## JOIN leftover (must not restore reject-before-remap)

Live source, not remappable `api_tracks`:

- `tests/integration/test_riso_cli.py::test_validate_rejects_removed_key` — `--data saas_auth=firebase`, exit 2, `saas_auth` in errors.
- `tests/integration/test_control_plane_gates.py::test_run_generator_rejects_removed_keys_before_worker` — `data={"saas_auth": "firebase", ...}`, `ValidationFailedError`, worker not called.

W4-A01 / W2-CLI-JOIN narratives that those tests still send `api_tracks=python` are **stale**.

## Confirmed P0/P1 vs this lock

None of the verified-gap / audit P0/P1 files sit in the CLOSE-CLI exclusive write roots. Foreign items (default dest, Fumadocs, Docusaurus, Sphinx linkcheck, wizard lucia dest, container workflows, `just validate-agents`) were not edited.

## Command

```text
uv run pytest \
  tests/unit/test_cli/test_remap.py \
  tests/unit/test_cli/test_migrate.py \
  tests/unit/test_cli/test_update.py \
  tests/integration/test_riso_cli.py::test_validate_rejects_removed_key \
  tests/integration/test_control_plane_gates.py::test_run_generator_rejects_removed_keys_before_worker \
  -q -n 0 --tb=short
```

## Result

```text
============================= 100 passed in 1.25s ==============================
```

No tag / commit / push / PyPI. Maintainer `riso-mcp` not reintroduced.
