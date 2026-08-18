# W10-TESTS — analytics provider + theme-toggle + recopy dest locks

- **Wave:** W10 / PAYLOAD tests
- **Task:** lock dest-root PostHog/Amplitude providers, ThemeToggle, and recopy dry-run dest
- **Lane:** tests only (exclusive write `tests/unit/test_saas_template_clients.py`, this file)
- **Date (UTC):** 2026-08-18T14:32:03Z
- **Repo:** `/Users/ww/dev/projects/riso`
- **Branch:** `main`
- **HEAD:** `89882fff946e10692de1e1eb634ad4aa355ed694` (worktree dirty; this session did not commit)
- **Product / template writes:** 0
- **`samples/*/render/**` writes:** 0
- **Lockfile / secrets / tag / push:** 0
- **Status:** **green** — 17 passed

## Sibling wait

Polled product files three times (read, not sleep-loop). First two rereads: all three templates missing. Third reread: all three present (untracked sibling writes). Recopy dest was already moved off `samples/default/render` before assertions were written.

| Surface                                                        | Live at write time                                                                                         |
| -------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `node/saas/lib/analytics/posthog-provider.ts.jinja`            | untracked; `export function PostHogProvider`; `{% if saas_infra_module and saas_analytics == "posthog" %}` |
| `node/saas/lib/analytics/amplitude-provider.ts.jinja`          | untracked; `export function AmplitudeProvider`                                                             |
| `node/saas/components/theme-toggle.tsx.jinja`                  | untracked; `export function ThemeToggle`                                                                   |
| `tests/integration/test_riso_cli.py::test_recopy_dry_run_json` | sibling-edited; dest is `tmp_path / "proj"`, not `samples/default/render`                                  |

Did not edit product templates or the integration suite.

## Added

Extended `tests/unit/test_saas_template_clients.py` (kept pylint disable header; new helpers have docstrings).

| Contract                                    | Assertion                                                                                                              |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `lib/analytics/posthog-provider.ts.jinja`   | file exists; source exports `PostHogProvider`; Jinja-gated on `saas_analytics == posthog`; off-render omits the symbol |
| `lib/analytics/amplitude-provider.ts.jinja` | file exists; source exports `AmplitudeProvider`                                                                        |
| `components/theme-toggle.tsx.jinja`         | file exists; source exports `ThemeToggle`                                                                              |
| Recopy dry-run integration dest             | `test_recopy_dry_run_json` source does not contain `samples/default/render`                                            |

## Verify

```text
uv run pytest tests/unit/test_saas_template_clients.py -q -n 0
# 17 passed in 3.51s

uv run ruff check tests/unit/test_saas_template_clients.py
# All checks passed!

uv run ruff format --check tests/unit/test_saas_template_clients.py
# 1 file already formatted

uv run pylint --rcfile=pyproject.toml tests/unit/test_saas_template_clients.py
# Your code has been rated at 10.00/10
```

**Pass count: 17 passed / 0 failed / 0 skipped.** (9 prior SaaS client/CI tests + 3 PostHog + 2 Amplitude + 2 ThemeToggle + 1 recopy dest)

## Path lock

| Class                     | Count                                      |
| ------------------------- | ------------------------------------------ |
| Product / template writes | 0                                          |
| Test writes               | `tests/unit/test_saas_template_clients.py` |
| Evidence                  | this file                                  |
| `residuals/**`            | 0                                          |
| `samples/*/render/**`     | 0                                          |

## Not this lane

- Editing analytics/theme-toggle product templates
- Editing `tests/integration/test_riso_cli.py`
- Official dest re-render
- Commit / tag / push
