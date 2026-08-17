# Testing payload review

## Inventory

- `template/files/testing/python/**` — API pytest helpers when python API enabled
- `template/files/testing/node/**` — node test helpers when node API enabled
- `template/files/testing/e2e/**` — Playwright e2e; conditions on `quality_profile`, `api_module`, `saas_*`

## Sample profile distribution (answers)

- Most variants: `quality_profile: standard`
- Strict samples: `full-stack`, `gitlab-ci-python`, `changelog-full-stack` (and similar)
- `makefile-runner`: `task_runner: makefile`

## Assessment

No PLATFORM-owned structural defects found in this pass. E2E jinja conditionals are intentional product gates; SaaS auth/dashboard specs belong to SAAS payload behavior (foreign if missing product modules).

## Action

No testing/** edits required this run.
