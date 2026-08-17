# W1-C01..C05 — Copier extras + catalog + context

- Tasks: `W1-C01`, `W1-C02`, `W1-C03`, `W1-C04`, `W1-C05`
- Wave: W1
- Repo: `/Users/ww/dev/projects/riso`
- Branch: `main` (no checkout / stash / reset)
- Exclusive writes: `template/copier.yml`, `template/prompts/**`, `template/files/module_catalog.json.jinja`, `template/files/mise.toml.jinja` (C02 stub), `.github/context/**`, `template/files/.github/context/**`, this file
- `samples/*/render/**` writes: **0**
- Status: **green**

## C01 — `openspec_extra` default disabled

- `_defaults.openspec_extra: "disabled"`
- Prompt `openspec_extra` choices `disabled` / `enabled`, default `disabled`
- `_exclude`: `{% if openspec_extra != 'enabled' %}openspec/{% endif %}`
- `template/files/openspec/**` is not created here (OS-T01). Exclude is in place for when that tree lands.

## C02 — always render generated `mise.toml`

- No `_exclude` entry for `mise.toml` or `.mise.toml` (comment documents always-on)
- Stub added: `template/files/mise.toml.jinja` (MISE-T01 fills pins: python 3.11 / node 20 / pnpm / uv)
- Existing `template/files/.mise.toml.jinja` left untouched (not this lane)

## C03 — prompts/help mention 2.0 remap + extras

- `template/copier.yml` `_metadata.description`, `quality_profile.help`, and `openspec_extra.help` name ty-not-mypy, always-on mise, optional OpenSpec, and the 8 remapped 1.x keys + `riso migrate` / `riso update` fail-closed contract
- `template/prompts/options.yml.jinja` — `quality_profile` + `openspec_extra`
- `template/prompts/v2.yml.jinja` — remap table + extras SSOT for docs/automation

`uv run riso prompts --json`: `ok true`; `openspec_extra` present; default `disabled`; help includes remap + extras.

## C04 — catalog: ty not mypy; mise; OpenSpec optional

`template/files/module_catalog.json.jinja`:

| name | default | selected (defaults) | notes |
| --- | --- | --- | --- |
| `quality` | standard | `quality_profile` | description now “ty, not mypy”; deps include `ty` + `mise` |
| `mise` | enabled | enabled | always-on; not a Copier extra |
| `openspec_extra` | disabled | disabled | optional extra |

`uv run riso catalog modules --json`: `ok true`; no render error.

## C05 — context parity

Touched `.github/context/quality.md` and `template/files/.github/context/quality.md` (ty not mypy; mise always-on; OpenSpec extra default off).

```text
uv run python scripts/ci/verify_context_sync.py
Context directories are in sync.
```

## Verify

```text
uv run riso validate --answers-file samples/default/copier-answers.yml --json
{"ok": true, "data": {"valid": true, "errors": []}, ...}

uv run riso validate --answers-file samples/makefile-runner/copier-answers.yml --json
{"ok": true, "data": {"valid": true, "errors": []}, ...}

uv run riso prompts --json
ok True; openspec_extra default disabled; remap wording present

uv run riso catalog modules --json
ok True; quality/mise/openspec_extra rows present

uv run python scripts/ci/verify_context_sync.py
exit 0

uv run pytest tests/unit/test_cli/test_catalog.py tests/unit/test_cli/test_prompts.py \
  tests/unit/test_task_runner_templates.py tests/unit/ci/test_validate_agents_ecosystem.py -q -n 0
============================== 15 passed in 2.02s ==============================
```

Validate warnings are only Copier metadata keys `_commit` / `_src_path` (pre-existing; not extras).

## Not this slice

- OS-T01/T02/T03 (`template/files/openspec/**` payload + enabled copy)
- MISE-T01 pin values in the stub
- W1-C06/C07/C08, W1-OUT, sample answers (`openspec_extra` omitted → default disabled)
