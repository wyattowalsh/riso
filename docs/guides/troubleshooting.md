# Troubleshooting Guide

This guide covers common issues and their solutions when using Riso. Whether you're setting up
a development environment, rendering templates, or using the Riso CLI, you'll find
practical troubleshooting steps here.

## Installation and Setup Issues

### Python Version Incompatibility

**Symptom:** Error about Python version: `Python 3.11+ required` or `RuntimeError: Python 3.11 minimum`

**Solution:**

```bash
# Check your Python version
python3 --version

# If below 3.11, install a newer version
# macOS with Homebrew
brew install python@3.13

# Linux (Ubuntu/Debian)
sudo apt-get install python3.13

# Then set it as default or use explicitly
python3.13 --version
```

**Note:** Riso requires Python 3.11, 3.12, or 3.13 for full compatibility and CI testing.

### uv Not Found or Not in PATH

**Symptom:** `command not found: uv` or `zsh: command not found: uv`

**Solution:**

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to your shell profile (~/.bashrc, ~/.zshrc, ~/.profile, etc.)
export PATH="$HOME/.cargo/bin:$PATH"  # If installed via curl
# OR
export PATH="$HOME/.local/bin:$PATH"  # If installed via pip

# Reload shell configuration
source ~/.zshrc  # for zsh
source ~/.bashrc  # for bash

# Verify installation
uv --version
```

### Copier Version Mismatch

**Symptom:** `Error: Copier version 9.0+ required` or template rendering fails with version warning

**Solution:**

```bash
# Check current Copier version
copier --version

# Update Copier to compatible version
pip install --upgrade copier>=9.1.0

# Or use uv
uv pip install --upgrade copier>=9.1.0

# Verify upgrade
copier --version
```

### Missing System Dependencies

**Symptom:** Various errors during setup (e.g., `command not found: node`, `pnpm: command not found`)

**Solution:**

For Node.js and pnpm (required for docs and full-stack projects):

```bash
# macOS with Homebrew
brew install node@20
npm install -g pnpm

# Linux (Ubuntu/Debian)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
npm install -g pnpm

# Verify installations
node --version    # Should be v20.x or higher
pnpm --version    # Should be v8+
```

For Git and other build tools:

```bash
# macOS
xcode-select --install

# Linux (Ubuntu/Debian)
sudo apt-get install build-essential git curl wget

# Verify
git --version
```

### Docker Not Running

**Symptom:** `Docker daemon is not running` or `cannot connect to Docker daemon`

**Solution:**

```bash
# macOS - Start Docker Desktop
# Click Docker icon in Applications folder

# Linux - Start Docker daemon
sudo systemctl start docker
sudo systemctl enable docker  # Auto-start on boot

# Verify Docker is running
docker ps

# If permission denied, add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

## Template Rendering Issues

### Template Rendering Timeout

**Symptom:** Copier hangs during rendering, takes excessive time, or times out

**Solution:**

```bash
# Try with the --trust flag (disables safety checks)
copier copy --trust gh:wyattowalsh/riso my-project

# Clear Copier cache and retry
rm -rf ~/.cache/copier
copier copy gh:wyattowalsh/riso my-project

# Check network connectivity
ping github.com

# If behind a proxy, configure git
git config --global http.proxy [protocol://]proxyhost[:port]

# Increase Copier verbosity for debugging
copier copy --verbose gh:wyattowalsh/riso my-project
```

### Invalid Answer or Validation Error

**Symptom:** `ValidationError`, `Invalid answer for question`, or errors mentioning `copier-answers.yml`

**Solution:**

```bash
# 1. Check the copier.yml for valid answer values
cat template/copier.yml | grep -A 5 "choices:"

# 2. Review your copier-answers.yml for typos
cat copier-answers.yml

# 3. Valid values commonly used:
#    - project_layout: "single-package" or "monorepo"
#    - quality_profile: "standard" or "strict"
#    - api_languages: "none", "python", "node", or "python+node"
#    - docs_framework: "fumadocs", "sphinx-shibuya", "docusaurus", or "none"
#    - cli_module: "enabled" or "disabled"
#    - mcp_module: "enabled" or "disabled"

# 4. Regenerate from scratch with interactive prompts
rm copier-answers.yml
copier copy gh:wyattowalsh/riso my-project
```

### PyYAML Import Error

**Symptom:** `RuntimeError: PyYAML is required to load Copier configuration`

**Solution:**

```bash
# Install PyYAML
uv pip install PyYAML

# Or with pip
pip install PyYAML

# Verify installation
python3 -c "import yaml; print(yaml.__version__)"
```

### Missing Template Files

**Symptom:** `TemplateNotFoundError`, `FileNotFoundError`, or specific files not generated

**Solution:**

```bash
# Verify template path
ls -la template/copier.yml
ls -la template/files/

# Check git status - ensure template files are committed
git status template/

# Clone fresh copy of Riso
rm -rf riso
git clone https://github.com/wyattowalsh/riso.git
cd riso

# Try rendering again
copier copy . ../my-project
```

## Permission and Access Issues

### Permission Denied Creating Files

**Symptom:** `PermissionError`, `Access denied`, or `Permission denied` when writing files

**Solution:**

```bash
# Check directory permissions
ls -ld /path/to/destination

# Fix permissions
chmod u+w /path/to/destination

# Or use different destination
copier copy gh:wyattowalsh/riso ~/my-project

# On Windows/WSL, run as administrator
# PowerShell: Start-Process powershell -Verb RunAs
# Then re-run the copier command
```

### macOS Gatekeeper Blocks Script

**Symptom:** Script execution blocked by Gatekeeper security, or `cannot execute binary file`

**Solution:**

```bash
# Remove Gatekeeper quarantine attribute
xattr -d com.apple.quarantine ./scripts/setup/setup.sh

# Alternative: Allow via security settings
# System Settings > Security & Privacy > General > Allow apps downloaded from

# Or make scripts executable
chmod +x ./scripts/setup/setup.sh
chmod +x ./scripts/render-samples.sh
```

### Windows Permission Denied (Scripts/Docker)

**Symptom:** Cannot execute `.sh` scripts or Docker access denied on Windows

**Solution:**

```bash
# Use Windows Terminal (not Command Prompt) as Administrator
# Start-Process powershell -Verb RunAs

# Use .ps1 scripts instead of .sh
.\scripts\setup\setup.ps1 -Install

# For WSL2, ensure integration is enabled
wsl --list -v  # Check WSL version

# Use WSL2 instead of native Windows
copier copy gh:wyattowalsh/riso /mnt/c/Users/YourUsername/my-project
```

## Riso CLI Issues

### Template Not Found

**Symptom:** `Template not found` when running `riso` commands outside a checkout

**Solution:**

```bash
# Clone the repository or pass an explicit template path
git clone https://github.com/wyattowalsh/riso.git && cd riso
uv sync --group cli
uv run riso doctor --json

# Or set RISO_TEMPLATE_PATH
export RISO_TEMPLATE_PATH=/path/to/riso/template
uv run riso template path --json
```

### Validation Failures

**Symptom:** `riso validate` exits with code 2 and lists answer errors

**Solution:**

```bash
# Inspect prompts and defaults
uv run riso prompts --json

# Check for removed legacy keys (api_tracks, docs_site, etc.)
uv run riso validate --answers-file copier-answers.yml --json

# Use a known-good sample
uv run riso validate --answers-file samples/default/copier-answers.yml --json
```

### Copier Operation Failures

**Symptom:** `riso copy`, `update`, or `recopy` fails with Copier errors

**Solution:**

```bash
# Preview changes first
uv run riso copy ./my-app --answers-file answers.yml --dry-run --json

# Increase timeout for large templates
uv run riso copy ./my-app --answers-file answers.yml --timeout 600 --json

# Verify copier is available
uv run riso doctor --json
```

## Build and Quality Issues

### Type Checking Failures

**Symptom:** `ty check` fails with type errors

**Solution:**

```bash
# Run type checker with full output
uv run ty check

# Show all errors at once
uv run ty check --show-error-context

# Type check specific module
uv run ty check src/riso/cli/ src/riso/core/

# Generate type stub files
uv run ty stubgen -p riso

# Check for common type issues
# - Missing type hints on function parameters
# - Incompatible return types
# - Type annotation mismatches
```

### Linting Failures (ruff/pylint)

**Symptom:** Code quality checks fail, linting errors

**Solution:**

```bash
# Run ruff (fast Python linter)
uv run ruff check .
uv run ruff check --fix .  # Auto-fix issues

# Run pylint (detailed analysis)
uv run pylint src/riso/

# Maintainer repo (riso/ root)
make quality

# Rendered project (samples/*/render/)
make quality  # or: QUALITY_PROFILE=standard uv run task quality

# Fix specific issues
uv run ruff check --select=E501 .  # Line length
uv run ruff check --select=F --fix .  # Unused imports
```

### Test Coverage Below Threshold

**Symptom:** `AssertionError` about coverage, `cov-fail-under` error

**Solution:**

```bash
# Run tests with coverage
uv run pytest --cov --cov-report=term-missing --cov-fail-under=90

# See coverage by file
uv run coverage report

# Generate HTML coverage report
uv run coverage html
open htmlcov/index.html  # View in browser

# Run specific test categories
uv run pytest -m unit  # Unit tests only
uv run pytest -m integration  # Integration tests
uv run pytest -m "not slow"  # Skip slow tests

# Identify uncovered code
uv run coverage report --show-missing
```

### Docker Build Fails

**Symptom:** Docker build errors, `Dockerfile not found`, or layer build failures

**Solution:**

```bash
# Verify Docker is running
docker ps

# Check Dockerfile syntax
docker build --check .  # Syntax check

# Build with verbose output
docker build --progress=plain .

# Common issues and fixes:
# 1. Check base image availability
docker pull python:3.13-slim

# 2. Clear Docker cache
docker build --no-cache .

# 3. Fix layer issues
# - Ensure COPY/ADD paths exist
# - Use absolute paths in Dockerfile
# - Check .dockerignore for excluding needed files

# 4. Test locally before CI
docker build -t my-project:test .
docker run --rm my-project:test python --version
```

### GitHub Actions Workflow Failures

**Symptom:** CI workflow fails, matrix tests fail, or actions timeout

**Solution:**

```bash
# Run quality suite locally matching CI
uv run python scripts/ci/run_quality_suite.py --profile strict

# Test across Python versions locally
python3.11 -m venv venv311
source venv311/bin/activate
uv sync && uv run pytest

# Check workflow syntax
actionlint .github/workflows/quality.yml

# Validate Docker in CI
uv run python scripts/ci/validate_dockerfiles.py

# Review workflow logs in GitHub
# Actions tab > Failed workflow > Review logs
```

## Sample and Matrix Issues

### Sample Rendering Fails

**Symptom:** Sample project generation fails, matrix data outdated

**Solution:**

```bash
# Regenerate all samples
./scripts/render-samples.sh

# Regenerate specific sample
copier copy -f --data='{"project_name":"test"}' \
  template samples/default/render

# Check sample variants
uv run python scripts/ci/render_matrix.py

# Validate sample configurations
cat samples/default/copier-answers.yml
cat samples/metadata/matrix-data.json  # Check schema
```

### Matrix Data Out of Sync

**Symptom:** Web UI shows different options than template, missing configurations

**Solution:**

```bash
# Regenerate matrix data
uv run python scripts/ci/render_matrix.py

# Generate full matrix
uv run python scripts/ci/generate_matrix_data.py

# Verify matrix schema
cat samples/metadata/matrix-data.json | python3 -m json.tool

# Check template against matrix
uv run python scripts/ci/verify_context_sync.py
```

## Documentation Issues

### Sphinx Build Fails

**Symptom:** `sphinx-build` fails, doc build errors

**Solution:**

```bash
# Install docs dependencies
uv sync --group docs

# Build documentation
uv run sphinx-build docs docs/_build

# Clean and rebuild
rm -rf docs/_build
uv run sphinx-build docs docs/_build

# View built docs
open docs/_build/index.html  # macOS
xdg-open docs/_build/index.html  # Linux
start docs\_build\index.html  # Windows

# Check for warnings
uv run sphinx-build -W docs docs/_build  # Treat warnings as errors
```

### Missing Dependencies for Docs

**Symptom:** `ModuleNotFoundError` for doc dependencies (sphinx, myst, etc.)

**Solution:**

```bash
# Install all doc dependencies
uv sync --group docs

# Or install specific packages
uv pip install sphinx-shibuya myst-parser sphinx-copybutton

# Verify installation
uv run python -c "import sphinx; print(sphinx.__version__)"
```

## Node.js and JavaScript Issues

### pnpm Command Not Found

**Symptom:** `command not found: pnpm` when building docs or SaaS modules

**Solution:**

```bash
# Install pnpm globally
npm install -g pnpm

# Verify installation
pnpm --version  # Should be v8+

# Set pnpm in Riso config if needed
# Some projects specify pnpm version in package.json engines
cat package.json | grep engines

# Use npm instead temporarily
npm install
npm run dev
```

### Node Version Mismatch

**Symptom:** Node version incompatibility, pnpm peer dependency issues

**Solution:**

```bash
# Check Node version (should be 20 LTS)
node --version  # Should be v20.x

# Update Node via nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 20
nvm use 20

# Or via Homebrew (macOS)
brew upgrade node@20

# Clear node_modules and reinstall
rm -rf node_modules pnpm-lock.yaml
pnpm install

# Check pnpm config
pnpm config list
```

### Vite or TypeScript Build Error

**Symptom:** Build fails in docs or frontend, TypeScript errors

**Solution:**

```bash
# Clear build artifacts
rm -rf dist .next build

# Reinstall dependencies
pnpm install --force

# Run type check
pnpm type-check

# Build with verbose output
pnpm build --debug

# Check TypeScript configuration
cat tsconfig.json
cat vite.config.ts

# Compile TypeScript directly
pnpm exec tsc --noEmit
```

## Debugging and Getting Help

### Enable Debug Logging

**Symptom:** Need more details about what's failing

**Solution:**

```bash
# Enable debug output globally
DEBUG=1 copier copy gh:wyattowalsh/riso my-project

# Enable for specific modules
DEBUG=riso:* copier copy gh:wyattowalsh/riso my-project

# Python debugging
uv run riso --verbose doctor --json

# Verbose mode for various tools
copier copy --verbose gh:wyattowalsh/riso my-project
uv --verbose sync
pnpm --verbose install
```

### Collect Diagnostic Information

Before opening an issue, gather:

```bash
# System information
uname -a  # OS info
python3 --version  # Python version
copier --version  # Copier version
uv --version  # uv version
git --version  # Git version

# Riso-specific info
cd /path/to/riso
git log -1 --oneline  # Last commit
git remote -v  # Remote URLs

# Project-specific info (in generated project)
cat pyproject.toml  # Dependencies
cat copier-answers.yml  # Configuration
ls -la .github/workflows/  # CI workflows
```

### Check GitHub Issues and Discussions

1. **Search existing issues**: https://github.com/wyattowalsh/riso/issues
1. **Check discussions**: https://github.com/wyattowalsh/riso/discussions
1. **Review documentation**: https://github.com/wyattowalsh/riso/tree/main/docs

### Opening a New Issue

Include:

1. **Title**: Clear, specific description of the issue
1. **Environment**:
   - OS and version
   - Python version
   - Riso version or commit hash
   - Node.js version (if applicable)
1. **Steps to reproduce**: Exact commands that trigger the issue
1. **Expected behavior**: What should happen
1. **Actual behavior**: What actually happened
1. **Error message**: Full error output with stack trace
1. **Logs**: Debug output from `DEBUG=1` runs

Example:

```
**Title**: Template rendering times out with Python 3.13 on macOS

**Environment**:
- OS: macOS 14.2
- Python: 3.13.0
- Copier: 9.1.0
- Riso: commit abc123

**Steps to reproduce**:
1. Run: `copier copy gh:wyattowalsh/riso my-project`
2. Select all default options
3. Hangs after ~30 seconds

**Error message**:
[full error text]

**Debug output**:
DEBUG=1 copier copy gh:wyattowalsh/riso my-project
[debug output]
```

## Common Environment Variables

Use these to configure Riso behavior:

```bash
# Debugging
DEBUG=1  # Enable debug logging
DEBUG=riso:*  # Debug specific modules
VERBOSE=1  # Verbose output

# Colors and output
NO_COLOR=1  # Disable colored output

# Setup scripts
RISO_LOG_DIR=/custom/log/dir  # Override log directory
GITHUB_TOKEN=<token>  # Avoid GitHub API rate limits during CI

# Python
PYTHONPATH=/path/to/riso  # Add Riso to Python path
PYTHONDONTWRITEBYTECODE=1  # Don't create __pycache__

# Git (if behind proxy)
GIT_TRACE=1  # Debug git operations
GIT_SSH_COMMAND="ssh -vvv"  # Verbose SSH

# Node.js
NODE_OPTIONS=--max-old-space-size=4096  # Increase memory limit
```

## Quick Reference: Common Solutions

| Issue               | Quick Fix                                          |
| ------------------- | -------------------------------------------------- |
| Python 3.11+ needed | `brew install python@3.13`                         |
| uv not found        | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Copier outdated     | `uv pip install --upgrade copier>=9.1.0`           |
| Port 3141 in use    | `lsof -i :3141` then `kill -9 <PID>`               |
| Template timeout    | `copier copy --trust gh:wyattowalsh/riso ...`      |
| Permission denied   | `chmod +x scripts/setup/setup.sh`                  |
| Type check fails    | `uv run ty check` then fix errors                  |
| Coverage too low    | `uv run pytest --cov --cov-fail-under=90`          |
| Docker not running  | `open /Applications/Docker.app` (macOS)            |
| Clear Copier cache  | `rm -rf ~/.cache/copier`                           |

## Additional Resources

- **[Riso GitHub Repository](https://github.com/wyattowalsh/riso)**
- **[Copier Documentation](https://copier.readthedocs.io/)**
- **[Python uv Documentation](https://docs.astral.sh/uv/)**
- **[Riso CLI Reference](../tools/riso-cli.md)**
- **[Sphinx Documentation](https://www.sphinx-doc.org/)**
