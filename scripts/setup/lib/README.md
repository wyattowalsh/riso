# Riso Setup Library Modules

Cross-platform bash library modules for Riso template setup and tooling installation.

## Modules

### 1. `versions.sh`

Single source of truth for all version requirements.

**Variables:**

- `PYTHON_MIN_VERSION` - Minimum Python version (3.11)
- `UV_MIN_VERSION` - Minimum uv version (0.4)
- `NODE_MIN_VERSION` - Minimum Node.js version (20)
- `PNPM_MIN_VERSION` - Minimum pnpm version (8)
- `RUFF_VERSION` - Ruff linter version (0.14.2)
- `TY_VERSION` - Ty type checker version (0.0.6)
- `PYLINT_VERSION` - Pylint version (4.0.2)
- `COVERAGE_VERSION` - Coverage.py version (7.6.9)
- `PRECOMMIT_VERSION` - Pre-commit version (3.0)
- `ACTIONLINT_VERSION` - Actionlint version (latest)

**Usage:**

```bash
source scripts/setup/lib/versions.sh
echo "Python minimum version: $PYTHON_MIN_VERSION"
```

### 2. `colors.sh`

ANSI colors and logging functions with NO_COLOR support.

**Functions:**

- `log_info(message)` - Info message with ℹ symbol
- `log_success(message)` - Success message with ✓ symbol
- `log_warn(message)` - Warning message with ⚠ symbol
- `log_error(message)` - Error message with ✗ symbol
- `log_debug(message)` - Debug message (only when DEBUG=1 or VERBOSE=1)
- `log_section(message)` - Formatted section header
- `log_progress(message)` - Progress indicator (no newline)
- `log_progress_done()` - Complete progress line with success
- `log_progress_failed()` - Complete progress line with error

**Usage:**

```bash
source scripts/setup/lib/colors.sh
log_info "Starting installation..."
log_success "Installation complete!"
log_warn "Using fallback method"
log_error "Installation failed"
```

### 3. `detect-platform.sh`

Platform detection functions for OS, distro, package manager, architecture, and shell.

**Functions:**

- `detect_os()` - Returns: macos, linux, windows, unknown
- `detect_linux_distro()` - Returns: ubuntu, debian, fedora, arch, alpine, opensuse, rhel, unknown
- `detect_package_manager()` - Returns: mise, brew, apt, dnf, yum, pacman, apk, zypper, winget, choco, scoop, none
- `detect_arch()` - Returns: x64, arm64, arm, unknown
- `detect_shell()` - Returns: bash, zsh, fish, sh
- `is_wsl()` - Returns: 0 if WSL2, 1 otherwise
- `get_platform_summary()` - Returns multi-line platform summary

**Usage:**

```bash
source scripts/setup/lib/detect-platform.sh
os=$(detect_os)
pkg_mgr=$(detect_package_manager)
echo "Detected OS: $os"
echo "Package Manager: $pkg_mgr"
```

### 4. `logging.sh`

File logging with XDG Base Directory specification compliance.

**Functions:**

- `get_xdg_data_home()` - Returns XDG_DATA_HOME or ~/.local/share
- `get_xdg_config_home()` - Returns XDG_CONFIG_HOME or ~/.config
- `get_xdg_state_home()` - Returns XDG_STATE_HOME or ~/.local/state
- `get_xdg_cache_home()` - Returns XDG_CACHE_HOME or ~/.cache
- `get_log_dir()` - Returns $XDG_STATE_HOME/riso
- `get_config_dir()` - Returns $XDG_CONFIG_HOME/riso
- `get_cache_dir()` - Returns $XDG_CACHE_HOME/riso
- `init_log_file([log_name])` - Creates timestamped log file, returns path
- `log_to_file(log_file, level, message)` - Append to log with ISO 8601 timestamp
- `log_provision_result(tool, status, method, version, duration_ms)` - Log in JSONL format
- `get_latest_log([log_name])` - Get most recent log file
- `clean_old_logs([keep_count], [log_name])` - Keep only N most recent logs
- `show_log_summary(log_file)` - Display log statistics

**Usage:**

```bash
source scripts/setup/lib/logging.sh
LOG_FILE=$(init_log_file "setup")
log_to_file "$LOG_FILE" "INFO" "Starting installation"
log_provision_result "uv" "success" "brew" "0.4.1" 1234
```

### 5. `install-tools.sh`

Cross-platform installation functions for all required tooling.

**Functions:**

- `has_cmd(command)` - Check if command exists
- `version_gte(current, required)` - Compare versions (returns 0 if current >= required)
- `get_tool_version(tool, [version_flag])` - Extract version from tool output
- `install_uv()` - Install uv (brew, winget, or curl installer)
- `install_python()` - Install Python (mise, brew, apt, dnf, pacman, apk, winget)
- `install_node()` - Install Node.js (mise, brew, NodeSource, dnf, pacman, winget)
- `install_pnpm()` - Install pnpm (mise, brew, corepack, npm)
- `install_quality_tools()` - Install ruff, ty, pylint, coverage via uv tool
- `install_pre_commit()` - Install pre-commit via uv tool
- `install_actionlint()` - Install actionlint (mise, brew, GitHub releases)

Each installation function:

1. Checks if tool is already present with correct version
1. Tries mise first if available
1. Falls back to platform-specific package manager
1. Falls back to curl installer or manual instructions
1. Logs results using `log_provision_result()`
1. Returns 0 on success, 1 on failure

**Usage:**

```bash
source scripts/setup/lib/install-tools.sh

# Install core tools
install_uv || log_error "Failed to install uv"
install_python || log_error "Failed to install Python"
install_node || log_error "Failed to install Node.js"
install_pnpm || log_error "Failed to install pnpm"

# Install quality tools
install_quality_tools || log_error "Failed to install quality tools"
install_pre_commit || log_error "Failed to install pre-commit"
```

## Complete Example

```bash
#!/usr/bin/env bash
set -euo pipefail

# Load all libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/versions.sh"
source "${SCRIPT_DIR}/lib/colors.sh"
source "${SCRIPT_DIR}/lib/detect-platform.sh"
source "${SCRIPT_DIR}/lib/logging.sh"
source "${SCRIPT_DIR}/lib/install-tools.sh"

# Initialize logging
LOG_FILE=$(init_log_file "my-setup")
export LOG_FILE

# Show platform info
log_section "Platform Detection"
get_platform_summary

# Install tools
log_section "Installing Core Tools"
install_uv || exit 1
install_python || exit 1
install_node || exit 1
install_pnpm || exit 1

log_section "Installing Quality Tools"
install_quality_tools || exit 1
install_pre_commit || exit 1

log_success "Setup complete! Log: $LOG_FILE"
```

## Features

- **Cross-platform**: macOS, Linux (Ubuntu, Debian, Fedora, Arch, Alpine, RHEL), Windows (WSL, native)
- **Multiple package managers**: mise, brew, apt, dnf, yum, pacman, apk, zypper, winget, choco, scoop
- **Smart fallbacks**: Tries preferred methods first, gracefully falls back
- **Version checking**: Skips installation if correct version already present
- **Structured logging**: XDG-compliant file logging with JSONL provision tracking
- **NO_COLOR support**: Respects NO_COLOR environment variable
- **Error handling**: set -euo pipefail with graceful error handling
- **ShellCheck validated**: No warnings (except intentional unused variables)

## Validation

All modules pass shellcheck validation:

```bash
shellcheck scripts/setup/lib/*.sh
```

## Testing

Test that all modules load correctly:

```bash
bash -c '
source scripts/setup/lib/versions.sh
source scripts/setup/lib/colors.sh
source scripts/setup/lib/detect-platform.sh
source scripts/setup/lib/logging.sh
source scripts/setup/lib/install-tools.sh
echo "✓ All modules loaded successfully"
'
```
