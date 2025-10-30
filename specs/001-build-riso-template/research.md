# Research: Riso Template Foundation

## Decision 1: Python Toolchain Baseline
- **Decision**: Use uv to manage Python 3.11 environments with pytest for testing, nbclient for notebook smoke checks, and enforce ruff, mypy, and pylint in the CI pipeline.
- **Rationale**: uv provides reproducible, cross-platform installs with lock files; pytest covers unit + integration cases; nbclient ensures notebooks embedded in quickstarts remain executable; ruff, mypy, and pylint jointly cover style, typing, and lint expectations requested by the user.
- **Alternatives Considered**:
  - `pip + virtualenv`: Familiar but lacks uv’s performance and lockfile guarantees.
  - `tox`: Great for matrix testing but adds complexity over uv’s built-in environments for the baseline.
  - `black + flake8`: Common but ruff supersedes both with faster linting and rule coverage.

## Decision 2: TypeScript Testing & Automation Stack
- **Decision**: Adopt pnpm workspaces with TypeScript 5.x, Vitest for unit/integration tests, and Playwright for optional end-to-end flows when docs or API modules need browser automation.
- **Rationale**: pnpm aligns with user requirement and handles multi-package layouts; Vitest offers Jest-compatible APIs with faster execution and built-in TypeScript support; Playwright integrates cleanly with GitHub Actions for deterministic browser checks when needed.
- **Alternatives Considered**:
  - `Jest`: Mature but slower with ESM and requires extra config in pnpm monorepos.
  - `Mocha + Chai`: Flexible but lacks built-in snapshot testing and TypeScript ergonomics.
  - `Cypress`: Powerful UX testing but heavier infrastructure and license considerations; Playwright provides comparable coverage with OSS license.

## Decision 3: Documentation Strategy
- **Decision**: Provide Shibuya/Sphinx as the Python-first documentation default and Fumadocs as the TypeScript/Node documentation option, both wired to CI builds and deployment workflows.
- **Rationale**: Shibuya (Sphinx theme) pairs naturally with Python quickstarts and can compile API docs from docstrings; Fumadocs caters to TypeScript ecosystems and generates static sites with MDX/React-friendly layouts; both have GitHub Actions recipes for deterministic builds.
- **Alternatives Considered**:
  - `MkDocs Material`: Excellent cross-language docs but duplicates functionality covered by the requested stacks.
  - `Docusaurus`: Popular but heavier React dependency and less aligned with Python doc-generation workflows.
  - `Sphinx Classic`: Stable but lacks the modern UI/UX expected for “ultimate” template branding.

## Decision 4: Optional Module Prompting & Samples
- **Decision**: Gate every optional capability (CLI, Python API, Node API, MCP, Docs, shared logic) behind explicit prompts with defaults that keep the baseline minimal; maintain four curated sample renders (default, cli-docs, api-monorepo, full-stack) that regenerate in CI.
- **Rationale**: Explicit prompts prevent accidental inclusion of heavyweight modules; curated samples provide coverage across permutations without exploding matrix size; keeping baseline minimal ensures adoption friction stays low.
- **Alternatives Considered**:
  - Single prompt toggling “advanced mode”: Too coarse—doesn’t let teams mix modules selectively.
  - Generating all permutations: Combinatorial explosion in CI time and maintenance.
  - Manual sample curation outside CI: Risks divergence and violates Automation-Governed Compliance.

## Decision 5: Resilience & Observability Tooling
- **Decision**: Bundle tenacity for retry/backoff patterns in generated scripts and loguru for structured logging across Python modules, both wired behind optional imports so baseline costs stay minimal.
- **Rationale**: Tenacity provides declarative retry policies that template consumers can adopt for network-bound tasks, while loguru offers batteries-included structured logging without complex setup—aligning with the “ultimate template” goal.
- **Alternatives Considered**:
  - `retrying`: Older library, less maintained than tenacity.
  - Standard `logging`: More verbose; loguru simplifies defaults while remaining flexible.

## Decision 6: Configuration Management Strategy
- **Decision**: Use pydantic and pydantic-settings for typed configuration models that lift environment variables into application settings across CLI/API modules.
- **Rationale**: pydantic integrates cleanly with FastAPI and general Python modules; pydantic-settings provides declarative environment loading that works in both single-package and monorepo renders.
- **Alternatives Considered**:
  - `dynaconf`: Rich features but heavier dependency surface area for baseline.
  - Manual `os.environ` parsing: Error-prone and lacks validation.

## Decision 7: Command-Line Interface Foundation
- **Decision**: Standardize on Typer for optional CLI scaffolds, exposing asyncio-friendly commands and docstring-driven help output.
- **Rationale**: Typer builds on Click with modern type hints, integrates with pydantic models, and matches community best practices referenced in `.github/context/`.
- **Alternatives Considered**:
  - `argparse`: Batteries-included but lacks ergonomic developer UX for expanding command sets.
  - `click` directly: Powerful but Typer wraps it with better typing support and auto docs generation.

## Decision 8: MCP Integration Approach
- **Decision**: Leverage FastMCP (>=2.0.0) as the optional MCP module backbone, providing sample tools, contracts, and compliance hooks.
- **Rationale**: FastMCP 2.x fits the project’s cutting-edge positioning, includes async support, and already integrates with GitHub automation.
- **Alternatives Considered**:
  - Custom MCP scaffolding: Higher maintenance overhead; re-implements building blocks FastMCP already solves.
  - Earlier FastMCP releases: Lacks governance features and would require manual patches.
