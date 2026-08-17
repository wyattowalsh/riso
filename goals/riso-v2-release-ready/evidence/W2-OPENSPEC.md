# W2-OPENSPEC — optional OpenSpec extra payload

- Lane: **OPENSPEC**
- Tasks: `OS-T01`, `OS-T02`, `OS-T03`
- Wave: W2
- Date: 2026-08-13
- Repo: `/Users/ww/dev/projects/riso`
- Branch: `main` @ `f7951fe` (no checkout / stash / reset / commit)
- Exclusive writes: `template/files/openspec/**`, `goals/riso-v2-release-ready/evidence/W2-OPENSPEC-*`, `goals/riso-v2-release-ready/residuals/OPENSPEC.md`
- `samples/*/render/**` writes: **0**
- Status: **residualed** (payload + enabled copy green; default leftover empty dir + `specs/` exclude are COORD)

## Filter / command

```text
git rev-parse --show-toplevel   # /Users/ww/dev/projects/riso
git rev-parse --abbrev-ref HEAD # main

rg -n 'openspec/' template/copier.yml
# 2106: "{% if openspec_extra != 'enabled' %}openspec/{% endif %}"

rg -n 'openspec' samples/default/copier-answers.yml
# empty (omitted → Copier default disabled)

uv run python scripts/ci/validate_jinja_templates.py \
  template/files/openspec/*.jinja \
  template/files/openspec/changes/*.jinja \
  template/files/openspec/changes/archive/*.jinja \
  template/files/openspec/specs/project/*.jinja
# Validated 6 Jinja template(s): all OK

uv run riso validate --answers-file samples/default/copier-answers.yml --json
# ok: true  → evidence/W2-OPENSPEC-validate-default.json

uv run riso validate --answers-file <throwaway-openspec-enabled.yml> --json
# ok: true  → evidence/W2-OPENSPEC-validate-enabled.json

uv run riso --skip-post-gen copy /tmp/riso-w2-openspec.*/dest-default \
  --answers-file samples/default/copier-answers.yml --json
# dest-default/openspec exists, filecount=0

uv run riso --skip-post-gen copy /tmp/riso-w2-openspec.*/dest-enabled \
  --answers-file <throwaway> --json
# dest-enabled/openspec/{USAGE,AGENTS,config}.md|.yaml + changes/** copy
# dest-enabled/openspec/specs/project/spec.md MISSING
```

Throwaway answers live only under evidence / `/tmp` — **not** `samples/**/copier-answers.yml`.

## OS-T01 — optional files under `template/files/openspec/**`

W1-C01 already set `openspec_extra` default `disabled` and `_exclude`:

```text
{% if openspec_extra != 'enabled' %}openspec/{% endif %}
```

Exclude is **present** (no missing-rule residual for the extra gate itself).

Payload added (exclusive root only):

```text
template/files/openspec/
├── AGENTS.md.jinja
├── USAGE.md.jinja
├── config.yaml.jinja
├── changes/USAGE.md.jinja
├── changes/archive/USAGE.md.jinja
└── specs/project/spec.md.jinja
```

- `schema: spec-driven` + project context from existing Copier keys
- No new languages / runtimes / vendors; no generated OpenSpec CLI dependency
- `githubCopilot.cloudAgent: false`
- `mise.toml` is not gated here

## OS-T02 — default sample has no openspec dir

| Check | Result |
| --- | --- |
| `samples/default/copier-answers.yml` | no `openspec_extra` key (omitted → disabled) |
| `uv run riso validate` default | `ok: true` |
| `samples/default/render` | **absent** |
| `samples/*/render/openspec` count | **0** |
| throwaway default copy (`--skip-post-gen`) | empty leftover `openspec/` (**filecount=0**) |

Default **files** are excluded. An empty `openspec/` shell remains because Copier still creates the dest dir for an excluded template folder, and `template/hooks/post_gen_project.py` `EMPTY_SCAFFOLD_DIRS` does **not** list `openspec`. Hooks are COORD — residual `OS-T02`.

## OS-T03 — `openspec_extra=enabled` copies files

Throwaway answers = default sample YAML + `openspec_extra: enabled` (not a sample variant).

| Dest path | Copied? |
| --- | --- |
| `openspec/USAGE.md` | yes |
| `openspec/AGENTS.md` | yes |
| `openspec/config.yaml` | yes |
| `openspec/changes/USAGE.md` | yes |
| `openspec/changes/archive/USAGE.md` | yes |
| `openspec/specs/project/spec.md` | **no** — blocked by unrooted `_exclude: "specs/"` |

Enabled copy is otherwise green. Official `openspec/specs/**` cannot land until COORD narrows `_exclude`. Residual `OS-T01-specs`.

## Keep / drop vs plan.md

| Item | Decision |
| --- | --- |
| `openspec_extra` default off | KEEP (COORD W1-C01) |
| Exclude `openspec/` unless enabled | KEEP (COORD) |
| SaaS flatten | not this lane |
| New languages/runtimes/vendors | DROP |
| Sample answer key `openspec_extra` | not invented (PLATFORM) |
| `copier.yml` / hooks edits | not touched (COORD) |

## Not this lane

- `template/copier.yml` exclude / prompt (COORD)
- `EMPTY_SCAFFOLD_DIRS` (COORD hooks)
- `samples/**/copier-answers.yml` (PLATFORM)
- Docs / AGENTS pointers (W4 DOCS)
- Wizard store default (WEB-T05)
