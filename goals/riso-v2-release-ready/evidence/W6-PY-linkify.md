# W6-PY — MyST linkify extra (`linkify-it-py`)

- Wave: W6 / lane PY (exclusive-write)
- Date: 2026-08-18
- Repo: `/Users/ww/dev/projects/riso` · branch `main` · HEAD `f60fac8`
- Exclusive writes: `template/files/python/pyproject.toml.jinja`, this file
- `template/files/python/docs/conf.py.jinja` writes: **0** (`"linkify"` kept)
- `tests/unit/**` writes: **0** (no existing unit test asserts live `python/pyproject.toml.jinja` docs extras)
- `samples/*/render/**` writes: **0**
- Lockfile / secret / commit / tag / push: **0**
- Status: **green** (source). Official Sphinx dests still need `render-samples.sh` / `render_matrix.py` (not this lock).

## Finding (PAY-P0-sphinx-myst-linkify-dep)

`template/files/python/docs/conf.py.jinja` enables MyST `"linkify"`. Generated `[dependency-groups] docs` shipped `myst-parser>=3.0.1` without `linkify-it-py` and without `myst-parser[linkify]`. MyST raises `ModuleNotFoundError: Linkify enabled but not installed.` Official `changelog-python` `just linkcheck` is red on this import.

Did **not** drop `"linkify"` from `myst_enable_extensions` — the extra can be added.

## Change

`template/files/python/pyproject.toml.jinja` `[dependency-groups] docs`:

```toml
  "myst-parser>=3.0.1",
  "linkify-it-py>=2.1.0",
```

`myst-parser>=3.0.1` kept. Pin is current PyPI 2.x (`2.1.0`, 2026-08-18). myst-parser 5.1.0 extra `linkify` requires `linkify-it-py~=2.0` (`>=2,<3`); `>=2.1.0` matches.

## Commands

```text
rg -n 'linkify-it-py' template/files/python/pyproject.toml.jinja
# 54:  "linkify-it-py>=2.1.0",

rg -n 'linkify' template/files/python/docs/conf.py.jinja template/files/python/pyproject.toml.jinja
# template/files/python/docs/conf.py.jinja:191:    "linkify",
# template/files/python/pyproject.toml.jinja:54:  "linkify-it-py>=2.1.0",

uv run python scripts/ci/validate_jinja_templates.py \
  template/files/python/pyproject.toml.jinja \
  template/files/python/docs/conf.py.jinja
# Validated 2 Jinja template(s): all OK
```

## Residual (not this lock)

Official Sphinx dests (`samples/docs-sphinx`, `samples/changelog-python`) still lack `linkify-it-py` until an official re-render. Do not hand-edit dests.

## Path lock

| Class                                   | Count                                            |
| --------------------------------------- | ------------------------------------------------ |
| This-session product writes             | 1 — `template/files/python/pyproject.toml.jinja` |
| This-session evidence writes            | 1 — this file                                    |
| `samples/*/render/**` hand-edits        | 0                                                |
| Lockfile / secret / commit / tag / push | 0                                                |
| `render_matrix.py` started or killed    | 0                                                |
