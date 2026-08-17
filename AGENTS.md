# AGENTS.md

> **Maintainer repo** — AI agent instructions for working on the **Riso Copier template** itself.
> Human docs: [README.md](./README.md) · Sphinx: [docs/](./docs/)

**Read [Quick Reference](#quick-reference) first.** Depth lives in `docs/`, `README.md`, and skill `references/` — not here.

## Project Overview

<!-- agents-md:auto -->

**Riso** is the **template maintainer repository** — not a rendered application. You edit `template/`, hooks, CI scripts, and samples metadata; generated apps land in `samples/*/render/` (regenerate only).

- **Type**: Copier template + maintainer automation (`src/riso/cli/`, `scripts/ci/`)
- **Languages**: Python 3.11+ (primary), TypeScript/Node.js (docs, web wizard, template tracks)
- **Package managers**: uv (Python), pnpm (Node.js)
- **Scaffold API**: `riso` CLI (replaces removed maintainer `riso-mcp` — see [docs/guides/mcp-to-cli-migration.md](docs/guides/mcp-to-cli-migration.md))
- **License**: MIT

| Context                                    | Audience             | Quality                          | Tests                                   |
| ------------------------------------------ | -------------------- | -------------------------------- | --------------------------------------- |
| **This repo** (`riso/`)                    | Template maintainers | `just quality`                   | `tests/`, `scripts/`, `template/hooks/` |
| **Rendered project** (`samples/*/render/`) | Generated app users  | `just quality` or `make quality` | Package-specific                        |

## Quick Reference

<!-- agents-md:auto -->

Maintainer commands — authoritative source: `just --list` (`justfile`). `make <target>` forwards to `just` for compatibility.

| Task                      | Command                                              |
| ------------------------- | ---------------------------------------------------- |
| Install all deps          | `just install` or `uv sync --group dev --group docs` |
| Full setup (deps + hooks) | `just setup`                                         |
| Check tooling             | `just setup-check`                                   |
| Bootstrap dev tools       | `just bootstrap`                                     |
| **Quality suite**         | `just quality`                                       |
| Lint                      | `just lint`                                          |
| Typecheck (ty)            | `just typecheck`                                     |
| Test                      | `just test`                                          |
| Test + coverage           | `just test-cov`                                      |
| Pre-commit (all)          | `just hooks`                                         |
| Render samples            | `just samples` or `./scripts/render-samples.sh`      |
| Docs dev server           | `just docs`                                          |
| Docs build                | `just docs-build`                                    |
| CI locally                | `just ci`                                            |
| Riso CLI                  | `uv sync --group cli` then `uv run riso --help`      |
| Render matrix             | `uv run python scripts/ci/render_matrix.py`          |
| Context sync check        | `uv run python scripts/ci/verify_context_sync.py`    |
| Validate AGENTS ecosystem | `just validate-agents`                               |

**Riso CLI** (template operations):

```bash
uv sync --group cli
uv run riso doctor --json
uv run riso validate --answers-file path.yml --json
uv run riso copy ./dest --answers-file path.yml
```

## Setup

<!-- agents-md:auto -->

```bash
git clone https://github.com/wyattowalsh/riso.git && cd riso
just setup                    # install + pre-commit hooks
just setup-check              # verify tooling (via scripts/setup/setup.sh)
uv run pytest tests/ -x -q    # smoke test
```

Bootstrap tooling: [scripts/setup/README.md](scripts/setup/README.md). Windows: `.\scripts\setup\setup.ps1 -Install`.

## Testing

**Coverage floors:** maintainer CI uses `--cov-fail-under=70` (see `just ci-full`); rendered sample projects may enforce 90 via template quality profiles. Do not conflate the two.

<!-- agents-md:auto -->

- **Framework**: pytest (xdist parallel, cov, randomly)
- **Paths**: `tests/unit/`, `tests/integration/`, `tests/automation/`
- **Markers**: `slow`, `integration`, `unit`

```bash
just test                              # preferred
uv run pytest                          # equivalent
uv run pytest tests/unit/test_cli/ -v  # CLI only
uv run pytest -m "not slow"            # skip slow
uv run pytest -m integration           # integration only
```

**CRITICAL**: Always prefix Python with `uv run` (never bare `python` or `pytest`).

## Code Quality (maintainer repo)

<!-- agents-md:auto -->

`just quality` runs **lint → typecheck → test** per `justfile`:

| Target      | Command scope                                                                   |
| ----------- | ------------------------------------------------------------------------------- |
| `lint`      | `ruff check` + `ruff format --check` on `scripts/`, `template/hooks/`, `tests/` |
| `typecheck` | `ty check scripts template/hooks src`                                           |
| `test`      | `pytest tests`                                                                  |

Pylint runs via **pre-commit**, not `just quality`. Config: `pyproject.toml`
(`[tool.ty]`, `[tool.pylint]`; maintainer `[tool.ruff]` already uses
`select = ["E4", "E7", "E9", "F"]`).

```bash
just quality      # full suite
just lint-fix     # auto-fix ruff issues
just security     # pip-audit
```

For **rendered projects** inside `samples/*/render/`, quality tooling is template-generated — see [docs/guides/quickstart.md](docs/guides/quickstart.md).

## Pre-commit Hooks

<!-- agents-md:auto -->

| Stage          | Hooks                                                                                            | Purpose               |
| -------------- | ------------------------------------------------------------------------------------------------ | --------------------- |
| **pre-commit** | ruff, ty, pylint, vulture, gitleaks, shellcheck, codespell, actionlint, mdformat, YAML/TOML/JSON | Code quality          |
| **commit-msg** | commitlint, conventional-pre-commit                                                              | Conventional commits  |
| **pre-push**   | pytest, pip-audit                                                                                | Full tests + security |

```bash
uv run pre-commit install --install-hooks
just hooks
```

CI skips some hooks locally enforced (ty, pylint, pytest, vulture); gitleaks runs in `.github/workflows/gitleaks.yml`.

## CI/CD Context

<!-- agents-md:auto -->

- **Platform**: GitHub Actions — `.github/workflows/quality.yml` (maintainer)
- **Rendered template workflows**: `template/files/.github/workflows/riso-*.yml.jinja`

| Job                         | Purpose                                                                        |
| --------------------------- | ------------------------------------------------------------------------------ |
| `quality`                   | Matrix: Python 3.11–3.13 × standard/strict profiles via `run_quality_suite.py` |
| `sync-test`                 | Makefile ↔ uv task parity in rendered default sample                           |
| `lint-workflows`            | actionlint on workflow YAML                                                    |
| `cli-tests`                 | `tests/unit/test_cli/` + `riso doctor`                                         |
| `security-scan`             | pip-audit                                                                      |
| `docs-build`                | Sphinx build + linkcheck                                                       |
| `validate-samples`          | Render + smoke-test sample variants                                            |
| `validate-agents-ecosystem` | AGENTS.md bridges, render smoke, quality parity in samples                     |
| `verify-context-sync`       | `.github/context/` ↔ template context byte parity                              |
| `web-tests`                 | Web wizard unit/lint/build + Playwright E2E (`web/`)                           |

Other workflows: `gitleaks.yml`, `codeql.yml`, `release.yml`, `matrix-data.yml`, `pre-commit.yml`, `sbom.yml`.

**PR checks** (`.github/workflows/quality.yml` — configure required status in GitHub branch protection):

- `quality` (matrix across Python 3.11–3.13 × standard/strict)
- `sync-test`, `lint-workflows`, `cli-tests`, `security-scan`, `docs-build`, `validate-samples`, `validate-agents-ecosystem`, `verify-context-sync`, `web-tests`

**Local CI parity**:

| Recipe           | Scope                                                                 |
| ---------------- | --------------------------------------------------------------------- |
| `just quality`   | Maintainer lint + typecheck + pytest (fast default)                   |
| `just ci`        | `install` + `just quality`                                            |
| `just ci-full`   | `run_quality_suite.py` (standard) + pytest with `--cov-fail-under=70` |
| `just ci-strict` | `run_quality_suite.py` (strict profile, adds pylint)                  |

`sync-test` validates **rendered** sample just/make parity (`samples/api-python/render/python`), not the maintainer Makefile shim.

## CI Scripts Reference

<!-- agents-md:auto -->

| Script                                | Purpose                                                               |
| ------------------------------------- | --------------------------------------------------------------------- |
| `render_matrix.py`                    | Render all sample variants, update metadata                           |
| `generate_matrix_data.py`             | Regenerate `web/src/data/matrix-data.json`                            |
| `record_module_success.py`            | Aggregate smoke results → `samples/metadata/`                         |
| `run_quality_suite.py`                | CI quality orchestration (profiles)                                   |
| `check_quality_parity.py`             | Makefile/uv task sync validation                                      |
| `verify_context_sync.py`              | `.github/context/` ↔ template context byte parity                     |
| `validate_workflows.py`               | GitHub workflow template validation                                   |
| `validate_dockerfiles.py`             | Dockerfile lint/validation                                            |
| `validate_release_configs.py`         | Release config validation                                             |
| `run_baseline_quickstart.py`          | Quickstart timing evidence                                            |
| `bump_template_npm_deps.py`           | Audit/bump npm pins via `npm_surfaces.json` (`--parallel`, `--apply`) |
| `sync_template_shadcn_components.py`  | Refresh SaaS shadcn/ui components from probe project                  |
| `validate_jinja_templates.py`         | Jinja syntax validation (pre-commit)                                  |
| `validate_saas_combinations.py`       | SaaS starter combination smoke renders                                |
| `validate_release_readiness_skill.py` | Mirror check for release-readiness skill                              |
| `track_doc_publish.py`                | Doc publish timestamp governance                                      |
| `verify_version_sync.py`              | Version constant sync across template/setup                           |
| `validate_agents_ecosystem.py`        | AGENTS.md template bridges + pointer file limits                      |
| `agent_smoke_agents_md.py`            | Smoke-test rendered AGENTS.md onboarding questions                    |
| `render_precommit_configs.py`         | Validate pre-commit layout in rendered samples                        |

Run with `uv run python scripts/ci/<script>.py`.

## Gotchas & Edge Cases

<!-- agents-md:auto -->

- **uv run** — mandatory for all Python commands
- **Parallel tests** — default `-n auto`; use `-n 0` for sequential debugging
- **Sample renders** — never edit `samples/*/render/`; regenerate via `./scripts/render-samples.sh`
- **Lock files** — never hand-edit `uv.lock` or `pnpm-lock.yaml`
- **Jinja** — template files use `.jinja` extension under `template/files/`
- **COPIER_CMD** — optional env var for non-default Copier binary in automation
- **Context sync** — `.github/context/` must match `template/files/.github/context/`

## Repository Map

```
riso/
├── .agents/skills/          # Cross-platform agent skills (riso-scaffold, release-readiness)
├── .claude/skills/          # Claude Code skills (mcp-installer; agents-md-manager placeholder)
├── .cursor/commands/        # Spec Kit slash commands (speckit.*)
├── .github/
│   ├── workflows/           # Maintainer CI (quality.yml, gitleaks, release, …)
│   └── context/             # Canonical context snippets (synced to template)
├── src/riso/
│   ├── cli/                 # riso CLI (copy, validate, doctor, variants, …)
│   ├── core/                # Shared CLI logic (answers, paths, diff)
│   └── template/            # Template introspection helpers
├── template/                # Copier payload
│   ├── copier.yml           # Prompt definitions
│   ├── hooks/               # pre_gen / post_gen (security-critical)
│   ├── files/               # Jinja-rendered project files
│   └── prompts/             # Copier prompt YAML
├── scripts/
│   ├── render-samples.sh    # Primary sample render automation
│   ├── setup/               # Dev environment bootstrap
│   └── ci/                  # CI automation scripts
├── samples/                 # copier-answers.yml per variant + render/ output
├── tests/                   # Maintainer test suite
├── docs/                    # Sphinx maintainer documentation
├── specs/                   # Spec Kit feature workspace
├── web/                     # Template configurator (pnpm; optional for template work)
├── pyproject.toml           # Maintainer Python config + dependency groups
├── justfile                 # Command SSOT for maintainers
└── Makefile                 # Thin shim → `just` (template tracks still ship both)
```

**Security-critical**: `template/hooks/`, `scripts/ci/verify_context_sync.py`

## Maintainer Workflows

### Render & validate samples

```bash
./scripts/render-samples.sh                              # default variant
./scripts/render-samples.sh --variant full-stack \
  --answers samples/full-stack/copier-answers.yml
uv run python scripts/ci/render_matrix.py              # all variants
uv run python scripts/ci/verify_context_sync.py        # context parity
```

Smoke logs: `samples/<variant>/smoke-results.json` · Matrix: `samples/metadata/render_matrix.json`

### Validating renders (summary)

Inside `samples/<variant>/render/` only — full matrix: [docs/guides/testing-strategy.md](docs/guides/testing-strategy.md).

```bash
cd samples/default/render
uv sync && just quality
```

Do **not** copy rendered-project quality patterns into maintainer `just quality` expectations.

### Spec Kit

Feature specs live in `specs/`. Cursor commands: `.cursor/commands/speckit.*` (specify → plan → tasks → implement).

### Web wizard (optional)

```bash
cd web && pnpm install && pnpm dev
```

## Code Style

Brief conventions — examples in existing code:

- **Python**: 4 spaces, 88 cols, ruff format; import order stdlib → third-party → local
- **TypeScript/Node**: 2 spaces, Prettier; pnpm workspaces in template tracks
- **Jinja**: match target file format; files end in `.jinja`
- **Shell**: kebab-case scripts; ShellCheck in pre-commit

## Security

- Never commit secrets; use env vars
- `template/hooks/pre_gen_project.py` validates tooling before render
- `post_gen_project.py` writes `.riso/post_gen_metadata.json` (auto-generated, do not hand-edit)
- gitleaks in pre-commit + dedicated workflow

## Git Workflow

<!-- agents-md:auto -->

**Branches**: `main` (protected), `feat/*`, `fix/*`, `docs/*`, `claude/*`

**Commits**: [Conventional Commits](https://www.conventionalcommits.org/) — `feat(template): …`, `fix(hooks): …`, `docs(agents): …`

**Pull requests**:

1. Branch from `main`
1. `just hooks` or `uv run pre-commit run --all-files`
1. `just quality`
1. Squash merge; delete branch

## Boundaries

<!-- agents-md:auto -->

### Always Do

- `just quality` before pushing maintainer changes
- `uv run` for all Python commands
- Update tests when changing behavior
- Keep `.github/context/` synced with template (`verify_context_sync.py`)
- Conventional commit messages

### Ask First

- New dependencies in `pyproject.toml`
- `.github/workflows/` changes
- `template/prompts/` or `template/copier.yml` changes
- Pre/post generation hooks
- New sample variants
- `.pre-commit-config.yaml` changes

### Never Touch

- `.env*` (secrets)
- `samples/*/render/` (regenerate via script)
- `node_modules/`, `.venv/`, `__pycache__/`
- `.riso/post_gen_metadata.json` in renders
- `uv.lock`, `pnpm-lock.yaml` (use package managers)
- `dist/`, `build/`, `.next/`, `web/public/docs/` (generated)
- GitHub Actions secrets or repo settings

### Avoid

- Bare `python` / `pytest`
- Duplicating AGENTS body in pointer files (`.github/copilot-instructions.md`, `CLAUDE.md`)
- Inlining full skill bodies — invoke skills, link to `SKILL.md`

<!-- MANUAL ADDITIONS START -->

### Docs Stewardship

- Maintainer docs: `docs/` (Sphinx Shibuya) — `just docs` / `just docs-build`
- Mirror navigation/config changes to `template/files/python/docs/`
- Doc deps: `uv sync --group docs` (`pyproject.toml` `[dependency-groups.docs]`)

### Skills & Agent Tooling

Invoke by description; read `SKILL.md` when triggered — do not inline here.

| Skill                    | Location                                 | When to use                                                            |
| ------------------------ | ---------------------------------------- | ---------------------------------------------------------------------- |
| `riso-scaffold`          | `.agents/skills/riso-scaffold/`          | Scaffold/copy/update via `riso` CLI                                    |
| `riso-release-readiness` | `.agents/skills/riso-release-readiness/` | Pre-release gates, render validation                                   |
| `agents-md-manager`      | `.claude/skills/agents-md-manager/`      | AGENTS.md analysis, platform pointer sync (restore payload before use) |
| `mcp-installer`          | `.claude/skills/mcp-installer/`          | Stub — MCP server install/sync (payload not shipped)                   |
| `agents` plugin          | `github.com/wyattowalsh/agents`          | Portable skills/subagents via `/add-plugin github.com/wyattowalsh/agents` |

Enable the Agents plugin in project settings (do not vendor skill bodies):

- Cursor: `.cursor/settings.json` (`plugins.agents.enabled`)
- Claude Code: `.claude/settings.json` (`enabledPlugins` + `extraKnownMarketplaces`)
- GitHub Copilot: `.github/copilot/settings.json` (workspace recommendation)

`agents-md-manager` scripts run from `.claude/skills/agents-md-manager/` when the skill payload is present. Until restored, maintain pointers manually (this file + `CLAUDE.md` + `.cursor/rules` + `.github/copilot-instructions.md`).

`mcp-installer` is a stub (lockfile only under `.claude/skills/mcp-installer/` until the skill payload is restored). `just tui` is not shipped (`riso tui` is not a CLI command).

Template skill propagation: `template/files/.claude/skills/` when present in payload.

### Harness (no duplication)

- **Copilot**: `.github/copilot-instructions.md` → pointer to this file
- **Claude**: `CLAUDE.md` → pointer to this file
- **Cursor**: `.cursor/rules` → pointer; Spec Kit in `.cursor/commands/`; Agents plugin in `.cursor/settings.json`
- **Gemini**: `.gemini/commands/update.AGENTSmd.toml` — internal AGENTS maintainer playbook
- **Validation**: `uv run python scripts/ci/validate_agents_ecosystem.py`

<!-- MANUAL ADDITIONS END -->

## Recent Changes

- **CLI migration**: Maintainer `riso-mcp` removed → `riso` CLI + `riso-scaffold` skill ([migration guide](docs/guides/mcp-to-cli-migration.md))
- **Type checker**: `ty` replaces mypy for maintainer repo quality
- **Agent skills**: `riso-scaffold`, `riso-release-readiness` under `.agents/skills/`
- **Agents plugin**: project enablement for `github.com/wyattowalsh/agents` (`/add-plugin github.com/wyattowalsh/agents`)
- **Release automation**: Conventional commits, semantic-release, `release.yml` workflow
- Full history: [docs/changelog.md](docs/changelog.md) · [CHANGELOG.md](./CHANGELOG.md)

## Active Technologies

Maintainer stack: Python 3.11+ · uv · ruff · ty · pylint · pytest · Copier ≥9 · Typer CLI · Sphinx/Shibuya · GitHub Actions · pre-commit.

Template modules (WebSocket, containers, SaaS, changelog, etc.): see [docs/changelog.md](docs/changelog.md) and `specs/`.

## References

| Topic               | Location                                                                   |
| ------------------- | -------------------------------------------------------------------------- |
| Human quickstart    | [README.md](./README.md)                                                   |
| Contributor guide   | [CONTRIBUTING.md](./CONTRIBUTING.md)                                       |
| Agent scaffolding   | [docs/guides/agent-scaffolding.md](docs/guides/agent-scaffolding.md)       |
| MCP → CLI migration | [docs/guides/mcp-to-cli-migration.md](docs/guides/mcp-to-cli-migration.md) |
| Testing strategy    | [docs/guides/testing-strategy.md](docs/guides/testing-strategy.md)         |
| Troubleshooting     | [docs/guides/troubleshooting.md](docs/guides/troubleshooting.md)           |
| Riso CLI            | [docs/tools/riso-cli.md](docs/tools/riso-cli.md)                           |
| Setup scripts       | [scripts/setup/README.md](scripts/setup/README.md)                         |
| Module catalog      | `template/files/module_catalog.json.jinja`                                 |
| Render automation   | `scripts/render-samples.sh`                                                |
