# W2-MISE — generated mise pins (T01–T04)

- Tasks: `MISE-T01`, `MISE-T02`, `MISE-T03`, `MISE-T04`
- Wave: W2 / lane MISE
- Deps: `W1-C02` (T01/T02/T04), `W1-OUT` (T03)
- Repo: `/Users/ww/dev/projects/riso`
- Branch: `main` (no checkout / stash / reset / commit)
- Exclusive writes: `template/files/mise.toml.jinja`; maintainer `.mise.toml` only if pin sync required (not required)
- Also allowed: this file; `goals/riso-v2-release-ready/residuals/MISE.md` (not written — no residual)
- `samples/*/render/**` writes: **0**
- Status: **green**

## Contract (from plan + W1 outbox `mise-always`)

Generated projects always ship `mise.toml` (not a Copier extra). MISE fills pins. Generated Node floor stays **20+** and is **not** raised to maintainer **22**.

| Task | Result |
| --- | --- |
| MISE-T01 | `template/files/mise.toml.jinja` pins `python = "3.11"`, `node = "20"`, `pnpm = "9.15.0"`, `uv = "0.4.30"` |
| MISE-T02 | generated Node pin string is `20` (not `22` / `22.23.1`) |
| MISE-T03 | maintainer `.mise.toml` unchanged; still `node = "22.23.1"` |
| MISE-T04 | `mise install` already present in `scripts/setup/lib/install-tools.sh` (5 calls); also one comment in generated `mise.toml.jinja`. `scripts/setup/README.md` not edited (foreign tree; mention not needed) |

## T01 — pin fill

`template/files/mise.toml.jinja` (W1-C02 stub replaced):

```toml
[tools]
python = "3.11"
node = "20"
pnpm = "9.15.0"
uv = "0.4.30"

[settings]
auto_install = true
```

pnpm/uv match existing generated `template/files/.mise.toml.jinja` (`pnpm = "9.15.0"`, `uv = "0.4.30"`) and generated `package.json` `packageManager` / `engines.pnpm`. Python/Node match generated floors (`requires-python = ">=3.11"`, `engines.node = ">=20.0.0"`). No rust/just/new vendors added.

COORD left `template/files/.mise.toml.jinja` in place (both always render). This lane did **not** edit that file (not a MISE write root). Overlapping node/pnpm/uv pins are the same major/floor values.

## T02 — generated Node is 20, not 22

```text
rg -n 'node\s*=' template/files/mise.toml.jinja
template/files/mise.toml.jinja:7:node = "20"

rg -n '22' template/files/mise.toml.jinja
(no matches)
```

Generated `package.json.jinja` engines remain `>=20.0.0` (NODE/SAAS/DESKTOP; not edited here).

## T03 — maintainer `.mise.toml` stays Node 22

```text
git diff -- .mise.toml
(empty)

.mise.toml [tools]
python = "3.11"
node = "22.23.1"
pnpm = "11.11.0"
uv = "0.11.26"
```

No pin sync required; file not written.

## T04 — `mise install` mention

Already in `scripts/setup` (verify: “scripts/setup or generated README”). No README edit.

```text
scripts/setup/lib/install-tools.sh:243: mise install uv@latest
scripts/setup/lib/install-tools.sh:345: mise install "python@${PYTHON_MIN_VERSION}"
scripts/setup/lib/install-tools.sh:530: mise install "node@${NODE_MIN_VERSION}"
scripts/setup/lib/install-tools.sh:686: mise install pnpm@latest
scripts/setup/lib/install-tools.sh:889: mise install actionlint@latest
```

Generated `mise.toml.jinja` also comments: `After clone: \`mise install\``.

## Verify

```text
uv run python scripts/ci/validate_jinja_templates.py template/files/mise.toml.jinja
Validated 1 Jinja template(s): all OK

git rev-parse --abbrev-ref HEAD
main

git status --short -- template/files/mise.toml.jinja .mise.toml
?? template/files/mise.toml.jinja

git status --short -- 'samples/*/render'
(empty; write count 0)
```

## Residual risks (not blocking; no residual file)

- Dual generated configs: `mise.toml` (this lane) and existing `.mise.toml.jinja` (COORD left always-on). Align or drop the dotted file only if COORD/PLATFORM expands lock.
- `template/hooks/pre_gen_project.py` still provisions Node 22 for some generate-time docs/saas paths (COORD/hooks; not this lane).
- `scripts/ci/verify_version_sync.py` still parses `.mise.toml.jinja` only (PLATFORM).

## Not this slice

- `template/copier.yml` exclude / catalog (COORD)
- `template/files/.mise.toml.jinja` (not MISE lock)
- `scripts/setup/README.md` (foreign; T04 already satisfied)
- Sample answers / `render_matrix.py` (PLATFORM)
