# Handoff: GraphQL sample coverage

- **Need:** A primary sample (or matrix variant) with `api_module=enabled`, `python` in `api_languages`, and `graphql` in `api_features` (or `graphql_api_module=enabled`) so PY GraphQL payload is exercised by sample validation/render smoke.
- **Why PY needs it:** In-file dual-gates and Jinja syntax can pass without any sample selecting GraphQL; regressions in `graphql_api/**` may not fail default python-heavy validates.
- **Proposed contract (non-binding):** PLATFORM adds or extends a sample answers file (e.g. `samples/api-python-graphql` or enable graphql on an existing combo such as `changelog-full-stack` already partially does).
- **Consuming paths under `template/files/python/`:** `src/{{ package_name }}/graphql_api/**`, `tests/graphql/**`, GraphQL mount in `api/main.py.jinja`, optional `graphql_api` dep group in `pyproject.toml.jinja`.
- **Evidence:** `rg -n 'graphql' samples/*/copier-answers.yml` — only `changelog-full-stack` lists graphql; core python-heavy set (`api-python`, `docs-sphinx`, `changelog-python`, `full-stack`, `cli-docs`) does not enable GraphQL.
- **Owner:** PLATFORM
