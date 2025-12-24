# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                              RISO MAKEFILE                                   ║
# ║            Modular Copier Template for Python & Node.js                      ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

.DEFAULT_GOAL := help
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

# ─────────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────────
DOCS_PORT    ?= 3141
DOCS_DIR     := docs
DOCS_BUILD   := docs/_build
DEST         ?= ./riso-demo
ANSWERS      ?=
QUALITY_PROFILE ?= standard

# Colors & Formatting
BOLD   := \033[1m
DIM    := \033[2m
BLUE   := \033[34m
GREEN  := \033[32m
YELLOW := \033[33m
RED    := \033[31m
CYAN   := \033[36m
RESET  := \033[0m

# ─────────────────────────────────────────────────────────────────────────────────
# Help
# ─────────────────────────────────────────────────────────────────────────────────
.PHONY: help
help: ## Show this help
	@printf "\n$(BOLD)$(BLUE)╭─────────────────────────────────────────────────────────╮$(RESET)\n"
	@printf "$(BOLD)$(BLUE)│$(RESET)  $(BOLD)Riso$(RESET) — Modular Project Template                      $(BOLD)$(BLUE)│$(RESET)\n"
	@printf "$(BOLD)$(BLUE)╰─────────────────────────────────────────────────────────╯$(RESET)\n\n"
	@printf "$(DIM)Usage:$(RESET) make $(CYAN)<target>$(RESET)\n\n"
	@awk 'BEGIN {FS = ":.*##"; section=""} \
		/^## [A-Z]/ { section=substr($$0,4); printf "\n$(BOLD)$(YELLOW)%s$(RESET)\n", section } \
		/^[a-zA-Z_-]+:.*?##/ { printf "  $(GREEN)%-18s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@printf "\n"

# ═══════════════════════════════════════════════════════════════════════════════
## Setup & Installation
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: install
install: ## Install all dependencies (dev + docs)
	@printf "$(BLUE)▸ Installing dependencies...$(RESET)\n"
	uv sync --group dev --group docs
	@printf "$(GREEN)✓ Dependencies installed$(RESET)\n"

.PHONY: install-dev
install-dev: ## Install dev dependencies only
	@printf "$(BLUE)▸ Installing dev dependencies...$(RESET)\n"
	uv sync --group dev
	@printf "$(GREEN)✓ Dev dependencies installed$(RESET)\n"

.PHONY: install-docs
install-docs: ## Install docs dependencies only
	@printf "$(BLUE)▸ Installing docs dependencies...$(RESET)\n"
	uv sync --group docs
	@printf "$(GREEN)✓ Docs dependencies installed$(RESET)\n"

.PHONY: setup
setup: install ## Full setup (deps + pre-commit hooks)
	@printf "$(BLUE)▸ Setting up pre-commit hooks...$(RESET)\n"
	uv run pre-commit install --install-hooks
	uv run pre-commit install --hook-type commit-msg
	uv run pre-commit install --hook-type pre-push
	@printf "$(GREEN)✓ Setup complete$(RESET)\n"

.PHONY: hooks
hooks: ## Run all pre-commit hooks manually
	@printf "$(BLUE)▸ Running pre-commit hooks...$(RESET)\n"
	uv run pre-commit run --all-files
	@printf "$(GREEN)✓ Hooks passed$(RESET)\n"

.PHONY: hooks-update
hooks-update: ## Update pre-commit hook versions
	@printf "$(BLUE)▸ Updating pre-commit hooks...$(RESET)\n"
	uv run pre-commit autoupdate
	@printf "$(GREEN)✓ Hooks updated$(RESET)\n"

# ═══════════════════════════════════════════════════════════════════════════════
## Documentation
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: docs
docs: install-docs ## Serve docs with live reload (port 3141)
	@printf "$(BLUE)▸ Starting docs server on http://localhost:$(DOCS_PORT)$(RESET)\n"
	uv run sphinx-autobuild $(DOCS_DIR) $(DOCS_BUILD) \
		--port $(DOCS_PORT) \
		--open-browser \
		--watch $(DOCS_DIR) \
		--ignore "*.pyc" \
		--ignore "__pycache__"

.PHONY: docs-build
docs-build: install-docs ## Build docs (static HTML)
	@printf "$(BLUE)▸ Building documentation...$(RESET)\n"
	uv run sphinx-build -b html $(DOCS_DIR) $(DOCS_BUILD)
	@printf "$(GREEN)✓ Docs built at $(DOCS_BUILD)/index.html$(RESET)\n"

.PHONY: docs-clean
docs-clean: ## Clean docs build artifacts
	@printf "$(BLUE)▸ Cleaning docs build...$(RESET)\n"
	rm -rf $(DOCS_BUILD)
	@printf "$(GREEN)✓ Docs cleaned$(RESET)\n"

.PHONY: docs-linkcheck
docs-linkcheck: install-docs ## Check for broken links in docs
	@printf "$(BLUE)▸ Checking documentation links...$(RESET)\n"
	uv run sphinx-build -b linkcheck $(DOCS_DIR) $(DOCS_BUILD)/linkcheck
	@printf "$(GREEN)✓ Link check complete$(RESET)\n"

# ═══════════════════════════════════════════════════════════════════════════════
## Code Quality
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: quality
quality: lint typecheck test ## Run full quality suite (lint + typecheck + test)
	@printf "$(GREEN)✓ All quality checks passed$(RESET)\n"

.PHONY: lint
lint: ## Run ruff linter
	@printf "$(BLUE)▸ Running ruff...$(RESET)\n"
	uv run ruff check scripts template/hooks tests
	uv run ruff format --check scripts template/hooks tests
	@printf "$(GREEN)✓ Lint passed$(RESET)\n"

.PHONY: lint-fix
lint-fix: ## Auto-fix linting issues
	@printf "$(BLUE)▸ Fixing lint issues...$(RESET)\n"
	uv run ruff check --fix scripts template/hooks tests
	uv run ruff format scripts template/hooks tests
	@printf "$(GREEN)✓ Lint fixes applied$(RESET)\n"

.PHONY: typecheck
typecheck: ## Run ty type checker
	@printf "$(BLUE)▸ Running ty...$(RESET)\n"
	uv run ty check scripts template/hooks
	@printf "$(GREEN)✓ Type check passed$(RESET)\n"

.PHONY: test
test: ## Run pytest
	@printf "$(BLUE)▸ Running tests...$(RESET)\n"
	uv run pytest tests -v
	@printf "$(GREEN)✓ Tests passed$(RESET)\n"

.PHONY: test-cov
test-cov: ## Run tests with coverage report
	@printf "$(BLUE)▸ Running tests with coverage...$(RESET)\n"
	uv run pytest tests -v --cov=scripts --cov=template/hooks --cov-report=term-missing --cov-report=html
	@printf "$(GREEN)✓ Coverage report at htmlcov/index.html$(RESET)\n"

.PHONY: security
security: ## Run pip-audit for vulnerability scanning
	@printf "$(BLUE)▸ Scanning for vulnerabilities...$(RESET)\n"
	uv run pip-audit
	@printf "$(GREEN)✓ Security scan complete$(RESET)\n"

# ═══════════════════════════════════════════════════════════════════════════════
## Template Generation
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: tui
tui: ## Launch the Textual TUI generator
	@printf "$(BLUE)▸ Launching Riso TUI...$(RESET)\n"
	uv run riso tui --dest $(DEST) $(if $(ANSWERS),--answers $(ANSWERS),)

.PHONY: generate
generate: ## Generate project interactively (DEST=./my-project)
	@printf "$(BLUE)▸ Generating project at $(DEST)...$(RESET)\n"
	uv run copier copy . $(DEST) $(if $(ANSWERS),--answers-file $(ANSWERS),)
	@printf "$(GREEN)✓ Project generated at $(DEST)$(RESET)\n"

.PHONY: generate-default
generate-default: ## Generate with default settings
	@printf "$(BLUE)▸ Generating default project...$(RESET)\n"
	uv run copier copy . $(DEST) --defaults --force
	@printf "$(GREEN)✓ Default project at $(DEST)$(RESET)\n"

.PHONY: samples
samples: ## Render all sample projects
	@printf "$(BLUE)▸ Rendering sample projects...$(RESET)\n"
	./scripts/render-samples.sh
	@printf "$(GREEN)✓ Samples rendered$(RESET)\n"

# ═══════════════════════════════════════════════════════════════════════════════
## Maintenance
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: clean
clean: docs-clean ## Clean all build artifacts
	@printf "$(BLUE)▸ Cleaning build artifacts...$(RESET)\n"
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@printf "$(GREEN)✓ Clean complete$(RESET)\n"

.PHONY: clean-all
clean-all: clean ## Deep clean (includes samples, uv cache)
	@printf "$(BLUE)▸ Deep cleaning...$(RESET)\n"
	rm -rf samples/*/render
	rm -rf /tmp/riso-*
	@printf "$(GREEN)✓ Deep clean complete$(RESET)\n"

.PHONY: update
update: ## Update all dependencies
	@printf "$(BLUE)▸ Updating dependencies...$(RESET)\n"
	uv lock --upgrade
	uv sync --group dev --group docs
	uv run pre-commit autoupdate
	@printf "$(GREEN)✓ Dependencies updated$(RESET)\n"

.PHONY: lock
lock: ## Regenerate uv.lock
	@printf "$(BLUE)▸ Regenerating lockfile...$(RESET)\n"
	uv lock
	@printf "$(GREEN)✓ Lockfile updated$(RESET)\n"

# ═══════════════════════════════════════════════════════════════════════════════
## CI/CD Helpers
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: ci
ci: install quality ## Run CI checks (install + full quality suite)
	@printf "$(GREEN)✓ CI checks passed$(RESET)\n"

.PHONY: ci-docs
ci-docs: docs-build docs-linkcheck ## Build and verify docs
	@printf "$(GREEN)✓ Docs CI passed$(RESET)\n"

# ═══════════════════════════════════════════════════════════════════════════════
## Info & Debugging
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: info
info: ## Show project info and tool versions
	@printf "$(BOLD)$(BLUE)Project Info$(RESET)\n"
	@printf "$(DIM)─────────────────────────────────$(RESET)\n"
	@printf "Python:  %s\n" "$$(python3 --version 2>&1)"
	@printf "uv:      %s\n" "$$(uv --version 2>&1)"
	@printf "ruff:    %s\n" "$$(uv run ruff --version 2>&1 || echo 'not installed')"
	@printf "ty:      %s\n" "$$(uv run ty --version 2>&1 || echo 'not installed')"
	@printf "sphinx:  %s\n" "$$(uv run sphinx-build --version 2>&1 || echo 'not installed')"
	@printf "copier:  %s\n" "$$(uv run copier --version 2>&1 || echo 'not installed')"
