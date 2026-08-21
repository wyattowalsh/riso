# Riso 2.0 answers migration

Riso 2.0 is a hard major for Copier answers. Eight 1.x keys are removed and
remapped to component-first keys. After a successful remap, the old keys are
not kept as aliases.

This page is the operator guide for that remap. It does **not** create a git
tag, push, or PyPI publish.

The maintainer `riso-mcp` removal is a separate 1.x change. See
{doc}`mcp-to-cli-migration`.

## Apply then reject

Every answers path uses the same contract. Do not invert the order.

1. `apply_removed_key_remaps` remaps every known removed key that has a mapped
   value.
1. `reject_removed_answer_keys` fail-closes leftovers (unknown removed keys, or
   known keys whose values could not be remapped).

Rules:

- Do **not** overwrite a destination key that is already set. Keep the dest
  value; still drop the old key after a successful apply.
- Drop the old key only after a successful apply.
- A second apply is a no-op (idempotent). Already-canonical answers exit 0.
- Unmapped values stay on the old key so reject stays fail-closed.
- After remap, hooks, CLI, wizard, gates, and generated defaults must not
  read or write both old and new keys.

SSOT: `src/riso/core/removed_answer_keys.py` (twins in `scripts/lib` and
`web/src/lib/removedAnswerKeys.ts`).

## Remap table

These are the only remappable removed keys.

| Old key               | Operator                                 | Canonical dest                                 |
| --------------------- | ---------------------------------------- | ---------------------------------------------- |
| `api_tracks`          | derive                                   | `api_module`, `api_languages`                  |
| `api_language`        | wrap-list                                | `api_languages`                                |
| `docs_site`           | derive                                   | `docs_module`, `docs_framework`                |
| `mcp_language`        | wrap-list (`node` / `js` → `typescript`) | `mcp_languages`                                |
| `saas_starter_module` | rename                                   | `saas_infra_module`                            |
| `saas_auth`           | split                                    | `saas_auth_module`, `saas_auth_provider`       |
| `saas_billing`        | split                                    | `saas_billing_module`, `saas_billing_provider` |
| `include_admin`       | rename-bool                              | `saas_admin_dashboard`                         |

`graphql_api_module` and `websocket_module` are derived Jinja flags, not
removed user keys. They are not remapped. Enable GraphQL/WebSocket with
the Copier prompt `api_features` (`graphql`, `websocket`) when
`api_module=enabled`.

## Value rules

Historical values map to current Copier answers as follows. Anything else is
unmapped and fail-closes.

| Old key               | Mapped values                                                                                                                                                                                                                                             |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `api_tracks`          | empty / `none` / `disabled` / `[]` → `api_module=disabled`. Otherwise `api_module=enabled` and `api_languages` is the intersection of tokens with `python`, `node`, `rust`, `go`. Also accept `fastapi` → `python`, `fastify` → `node`, `actix` → `rust`. |
| `api_language`        | scalar `python` / `node` / `rust` / `go` → a one-item list. Already a list → keep (empty items dropped).                                                                                                                                                  |
| `docs_site`           | `none` / `false` / `disabled` / `off` → `docs_module=disabled`. `sphinx` / `sphinx-shibuya` → enabled + `sphinx-shibuya`. `docusaurus` / `fumadocs` → enabled + that framework.                                                                           |
| `mcp_language`        | scalar `python` / `typescript` / `rust` / `go` → a one-item list. `node` / `js` → `typescript`. Already a list → keep the list shape, drop empty items, and still apply `node`/`js` → `typescript`.                                                       |
| `saas_starter_module` | copy `enabled` / `disabled` (also common truthy/falsey tokens) → `saas_infra_module`.                                                                                                                                                                     |
| `saas_auth`           | `none` / `disabled` / `false` / `off` → `saas_auth_module=disabled`. `clerk` / `authjs` → module enabled + that `saas_auth_provider`. `lucia` has no payload and fail-closes.                                                                             |
| `saas_billing`        | `none` / `disabled` / `false` / `off` → `saas_billing_module=disabled`. `stripe` / `paddle` / `lemonsqueezy` → module enabled + that `saas_billing_provider`.                                                                                             |
| `include_admin`       | truthy/falsey → `saas_admin_dashboard` bool.                                                                                                                                                                                                              |

Do not guess unmapped historical values (for example `saas_auth: firebase` or
`docs_site: mkdocs`). Fix the answers to a mapped value, then remigrate.

## Preview with `riso migrate --dry-run`

Provide exactly one target: a project directory that contains
`.copier-answers.yml`, or an answers YAML via `--answers-file` / `-f`.
`--json` is a global flag.

```bash
uv run riso migrate DEST --dry-run
uv run riso migrate --answers-file path.yml --dry-run
uv run riso migrate --answers-file path.yml --dry-run --json
```

`--dry-run` applies remaps in memory, prints the preview, and does **not**
write. Leftovers still fail closed (exit 2) and the file is left untouched.

Human preview for a mixed 1.x file:

```text
answers_file: /path/to/answers.yml
remap: 7 key(s)
  api_tracks -> api_module, api_languages (derive)
  docs_site -> docs_module, docs_framework (derive)
  mcp_language -> mcp_languages (wrap-list)
  saas_starter_module -> saas_infra_module (rename)
  saas_auth -> saas_auth_module, saas_auth_provider (split)
  saas_billing -> saas_billing_module, saas_billing_provider (split)
  include_admin -> saas_admin_dashboard (rename-bool)
dry_run: true
Remapped 7 key(s)
```

Already-canonical answers print `remap: already canonical` and exit 0.

`--json` uses the stable envelope. `data.written` is false on dry-run.
`data.ops` lists each row (`old`, `new_keys`, `action`, `before`, `after`).
`data.answers` is the remapped mapping (old keys dropped).

```json
{
  "ok": true,
  "command": "riso migrate",
  "data": {
    "answers_file": "/path/to/answers.yml",
    "changed": true,
    "written": false,
    "dry_run": true,
    "ops": [
      {
        "old": "api_tracks",
        "new_keys": ["api_module", "api_languages"],
        "action": "derive",
        "before": "python+go",
        "after": {
          "api_module": "enabled",
          "api_languages": ["python", "go"]
        }
      }
    ],
    "answers": {
      "api_module": "enabled",
      "api_languages": ["python", "go"]
    },
    "template_path": "/path/to/riso/template",
    "message": "Remapped 7 key(s)"
  },
  "errors": [],
  "warnings": []
}
```

## Write remaps

Omit `--dry-run` to rewrite the answers file when at least one key remapped:

```bash
uv run riso migrate DEST
uv run riso migrate --answers-file path.yml --json
```

A second run is a no-op (`changed` / `written` false, empty `ops`, message
`Already canonical`).

## Fail-closed leftovers

If a removed key remains after apply — including an unmapped value — migrate
does not write and exits 2.

Example leftover:

```yaml
project_name: remap-leftover
saas_auth: firebase
```

`firebase` is not a mapped `saas_auth` provider, so the old key stays and
reject fires:

```text
error: saas_auth: removed answer key; use `saas_auth_module` plus `saas_auth_provider`
```

JSON envelope:

```json
{
  "ok": false,
  "command": "riso migrate",
  "data": {},
  "errors": [
    "saas_auth: removed answer key; use `saas_auth_module` plus `saas_auth_provider`"
  ],
  "warnings": []
}
```

The replacement string is the human dest from `REMOVED_ANSWER_KEYS`. Edit the
file to canonical keys (or a mapped 1.x value), then remigrate. Do not add
dual-path aliases to work around leftovers.

:::{warning}
`riso validate`, `copy`, `update`, `recopy`, `diff`, generation gates, Copier
hooks, and the web wizard all apply then reject. A leftover removed key fails
those paths too. There is no hidden fallback.
:::

## `riso update` remaps first

`riso update DEST` remaps `DEST/.copier-answers.yml` with the same
apply-then-reject path **before** Copier. `--dry-run` previews remaps and the
update diff; it does not write the answers file or apply the template update.

Use `riso migrate` when you only need to rewrite answers. Use `riso update`
when you are ready to pull 2.0 template files into an existing project.

## After migrate

1. Confirm the answers file has none of the eight old keys.
1. Validate: `uv run riso validate --answers-file path.yml --json`
1. Update the project when you want the 2.0 payload:
   `uv run riso update DEST`

The web wizard import/paste path remaps 1.x YAML the same way, then fail-closes
leftovers. Export never emits the old keys.

## Related 2.0 defaults

These are not remaps, but they change with 2.0:

- Dual mise: generated projects always ship `mise.toml` (Python 3.11, Node
  **22**, pnpm, uv). The maintainer checkout `.mise.toml` pins a Node **22**
  patch. Do not copy the maintainer patch pin into generated `mise.toml`.
- Optional OpenSpec extra (`openspec_extra`) defaults to off.
- Type checker is **ty**. Do not restore mypy as the default.
- Default task runner is `just`.
- Generated Python `test` extra includes `hypothesis` and `respx`, with shipped
  wiring tests (`test_hypothesis.py`, `test_respx.py`).

## See also

- {doc}`../tools/riso-cli`
- {doc}`mcp-to-cli-migration`
- {doc}`troubleshooting`
- {doc}`quickstart`
