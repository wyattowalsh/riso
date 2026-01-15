# Riso Setup Scripts

Comprehensive development environment setup automation for the Riso project.

## Overview

The setup scripts provide automated detection, validation, and installation of all required development tools across Windows, macOS, and Linux platforms.

## Files

### Main Entry Points

- **`setup.sh`** (495 lines) - Main Bash setup script for Unix-like systems

  - Compatible with Bash 3.2+ (including macOS default shell)
  - Uses indexed arrays for compatibility with older Bash versions
  - Full-featured with logging, colored output, and progress tracking

- **`setup.ps1`** (713 lines) - Main PowerShell setup script for Windows

  - Requires PowerShell 5.1 or later
  - Self-contained with inline functions (does not require modules)
  - Full-featured with parameter validation and help system

### Library Modules (Bash)

Located in `lib/`:

- **`versions.sh`** - Canonical version requirements for all tools
- **`colors.sh`** - ANSI colors and logging functions with NO_COLOR support
- **`detect-platform.sh`** - Platform detection (OS, distro, package manager, arch, WSL, containers)
- **`logging.sh`** - File logging with XDG Base Directory compliance
- **`install-tools.sh`** - Cross-platform tool installation functions with security utilities:
  - `verify_checksum()` - SHA256/SHA512 checksum verification
  - `secure_download()` - Download with retry and checksum validation
  - `github_api()` - Authenticated GitHub API requests
  - `secure_install_script()` - Safe remote script execution

### Library Modules (PowerShell)

Located in `lib-ps/`:

- **`Colors.psm1`** - Colored output functions
- **`Detect-Platform.psm1`** - Platform detection
- **`Install-Tools.psm1`** - Installation functions
- **`Logging.psm1`** - Logging functions

> **Note**: The main `setup.ps1` script currently uses inline functions for self-containment. The modules are available for other scripts or future refactoring.

## Usage

### Bash (Linux/macOS)

```bash
# Check what tools are missing (dry-run, default mode)
./scripts/setup/setup.sh

# Check and exit with code (CI-friendly)
./scripts/setup/setup.sh --check-only
# Exit 0 if all present, 1 if any missing

# Install missing tools with confirmation prompts
./scripts/setup/setup.sh --install

# Install without prompts (automation-friendly)
./scripts/setup/setup.sh --install --yes

# Show help
./scripts/setup/setup.sh --help
```

### PowerShell (Windows)

```powershell
# Check what tools are missing (dry-run, default mode)
.\scripts\setup\setup.ps1

# Check and exit with code (CI-friendly)
.\scripts\setup\setup.ps1 -CheckOnly
# Exit 0 if all present, 1 if any missing

# Install missing tools with confirmation prompts
.\scripts\setup\setup.ps1 -Install

# Install without prompts (automation-friendly)
.\scripts\setup\setup.ps1 -Install -Yes

# Show help
.\scripts\setup\setup.ps1 -Help
```

## Features

### Both Scripts

1. **Multi-mode operation**:

   - Default: Check and report (dry-run)
   - Check-only: Exit code-based validation for CI
   - Install: Interactive installation with prompts
   - Install --yes: Non-interactive installation

1. **Comprehensive tool detection**:

   - Python 3.11+
   - uv (Python package manager)
   - Node.js 20 LTS+
   - pnpm (Node package manager)
   - pre-commit (Git hooks)
   - actionlint (GitHub Actions linter)

1. **Version validation**:

   - Checks minimum version requirements
   - Reports current versions
   - Marks outdated tools for upgrade

1. **Status reporting**:

   - Colored, formatted table output
   - Clear status indicators (✓ OK, ✗ MISSING, ⚠ OUTDATED)
   - Respects NO_COLOR environment variable

1. **Smart installation**:

   - Tries multiple installation methods (mise, brew, apt, winget, etc.)
   - Falls back gracefully when methods unavailable
   - Tracks success/failure of each installation
   - Provides manual installation instructions for failures

1. **Security features** (Bash):

   - **Checksum verification** for binary downloads (SHA256/SHA512)
   - **Retry logic** with exponential backoff (3 attempts)
   - **GitHub API authentication** via `GITHUB_TOKEN`/`GH_TOKEN` to avoid rate limits
   - **Secure download utility** with checksum validation before installation

1. **Logging** (Bash):

   - XDG Base Directory compliant logs
   - Structured logging with ISO 8601 timestamps
   - JSONL provision tracking for tool metrics
   - Automatic log rotation (keeps last 10)
   - Logs stored in `~/.local/state/riso/`
   - **Log path disclosure** at end of setup for easy troubleshooting

1. **User-friendly output**:

   - Platform information display (in verbose mode)
   - Clear next steps after setup
   - Helpful error messages with links to docs
   - Progress indicators during installation

### Exit Codes

Both scripts use consistent exit codes:

- **0**: Success - All tools present (or successfully installed)
- **1**: Missing tools (check-only mode) or installation failed
- **2**: Invalid arguments or script error

## Environment Variables

### Bash

- `NO_COLOR` - Disable colored output
- `DEBUG` - Enable debug logging
- `VERBOSE` - Enable verbose logging
- `RISO_LOG_DIR` - Override log directory (default: `~/.local/state/riso`)
- `GITHUB_TOKEN` or `GH_TOKEN` - GitHub API authentication (avoids rate limits in CI)

### PowerShell

- `$env:NO_COLOR` - Disable colored output
- `$env:DEBUG` - Enable debug logging
- `$env:VERBOSE` - Enable verbose logging
- `$env:GITHUB_TOKEN` or `$env:GH_TOKEN` - GitHub API authentication

## Installation Methods

### Python

- **mise** (priority 1, all platforms)
- **brew** (macOS)
- **apt** (Debian/Ubuntu)
- **dnf** (Fedora/RHEL)
- **pacman** (Arch)
- **apk** (Alpine)
- **winget** (Windows)
- **chocolatey** (Windows)

### uv

- **mise** (priority 1, all platforms)
- **brew** (macOS)
- **winget** (Windows)
- **curl installer** (fallback, Unix)
- **PowerShell installer** (fallback, Windows)

### Node.js

- **mise** (priority 1, all platforms)
- **brew** (macOS)
- **apt + NodeSource** (Debian/Ubuntu)
- **dnf modules** (Fedora/RHEL)
- **pacman** (Arch)
- **winget** (Windows)
- **chocolatey** (Windows)

### pnpm

- **mise** (priority 1, all platforms)
- **brew** (macOS)
- **corepack** (all platforms with Node.js)
- **npm** (fallback, all platforms)
- **winget** (Windows)

### pre-commit

- **uv tool install** (all platforms, requires uv)

### actionlint

- **mise** (priority 1, all platforms)
- **brew** (macOS)
- **GitHub release download** (all platforms)

## Platform Detection

The scripts detect and adapt to:

### Operating Systems

- macOS (Darwin)
- Linux (various distributions)
- Windows (native and WSL)

### WSL Detection

- **WSL1** and **WSL2** automatically detected
- Uses `/proc/version` parsing for Microsoft kernel signatures
- Falls back to `WSL_DISTRO_NAME` environment variable
- Separate `is_wsl()` and `is_wsl2()` functions for fine-grained control

### Container Detection

Automatically detects when running inside:

- **Docker** (via `/.dockerenv` marker)
- **Podman** (via `/run/.containerenv` marker)
- **Kubernetes** (via `KUBERNETES_SERVICE_HOST` env var)
- **LXC/containerd** (via cgroup inspection)
- Generic container detection via `systemd-detect-virt`

### Linux Distributions

- Ubuntu/Debian
- Fedora/RHEL/CentOS/Rocky/AlmaLinux
- Arch/Manjaro
- Alpine
- openSUSE/SLES
- **NixOS** (detected via `/etc/nixos/configuration.nix`)
- **Void Linux** (detected via `xbps-install`)
- **Gentoo** (detected via `/etc/gentoo-release`)

### Package Managers

- mise (cross-platform, highest priority)
- Homebrew (macOS/Linux)
- apt (Debian/Ubuntu)
- dnf/yum (Fedora/RHEL)
- pacman (Arch)
- apk (Alpine)
- zypper (openSUSE)
- **xbps** (Void Linux)
- **emerge** (Gentoo)
- **nix** (NixOS)
- winget (Windows)
- chocolatey (Windows)
- scoop (Windows)

### Architectures

- x64 (x86_64, amd64)
- arm64 (aarch64, Apple Silicon)
- arm (armv7l, armv6l)

## Examples

### Basic Workflow

```bash
# 1. Check current status
./scripts/setup/setup.sh

# Example output:
# Tool Status
# Tool            Version              Status
# ----            -------              ------
# python3         3.14.2               ✓ OK
# uv              0.8.22               ✓ OK
# node            25.2.1               ✓ OK
# pnpm            9.15.0               ✓ OK
# pre-commit      4.3.0                ✓ OK
# actionlint      1.7.9                ✓ OK

# 2. Install missing tools
./scripts/setup/setup.sh --install

# 3. Verify installation
./scripts/setup/setup.sh --check-only && echo "All tools ready!"
```

### CI Integration

```yaml
# .github/workflows/setup.yml
- name: Setup development environment
  run: |
    chmod +x scripts/setup/setup.sh
    ./scripts/setup/setup.sh --install --yes
```

### Windows PowerShell

```powershell
# Run from PowerShell with admin rights (if needed for installation)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Check and install
.\scripts\setup\setup.ps1 -Install -Yes
```

## Log Files (Bash)

Logs are stored in XDG-compliant locations:

- **Log directory**: `~/.local/state/riso/`
- **Log format**: `setup_YYYYMMDD_HHMMSS.log`
- **Retention**: Last 10 log files kept automatically

### Log Contents

```log
# Riso Setup Log - setup
# Started: 2025-12-24T20:51:54Z
# Platform: Darwin 25.3.0 arm64
# Shell: /opt/homebrew/bin/zsh

[2025-12-24T20:51:54Z] INFO    === Setup started ===
[2025-12-24T20:51:54Z] INFO    Mode: check_only=0 install=0 yes=0
[2025-12-24T20:51:55Z] INFO    All tools present
```

### JSONL Provision Tracking

Tool installations are logged in JSONL format at `~/.local/state/riso/toolchain_provisioning.jsonl`:

```jsonl
{"timestamp":"2025-12-24T20:51:54Z","tool":"uv","status":"success","method":"brew","version":"0.8.22","duration_ms":1234}
{"timestamp":"2025-12-24T20:51:55Z","tool":"python","status":"skipped","method":"existing","version":"3.14.2","duration_ms":0}
```

## Compatibility

### Bash Script

- **Minimum**: Bash 3.2 (macOS default)
- **Recommended**: Bash 4.0+
- **Tested on**:
  - macOS 14+ (Bash 3.2)
  - Ubuntu 20.04+ (Bash 5.0)
  - Alpine Linux (Bash 5.1)
  - WSL2 Ubuntu (Bash 5.1)

### PowerShell Script

- **Minimum**: PowerShell 5.1 (Windows)
- **Recommended**: PowerShell 7.0+ (cross-platform)
- **Tested on**:
  - Windows 10/11 (PowerShell 5.1)
  - Windows 11 (PowerShell 7.4)

## Troubleshooting

### "Command not found" after installation

Some package managers require shell restart or PATH refresh:

```bash
# Bash/Zsh
source ~/.bashrc  # or ~/.zshrc
hash -r

# Fish
fish_update_completions
```

```powershell
# PowerShell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

### Version detection fails

Some tools may not report versions in expected format. The script will mark them as "version-unknown" but allow them to pass (assuming the tool exists).

### Installation fails

The script tries multiple methods. If all fail:

1. Check log files for detailed error messages
1. Try manual installation (links provided in error messages)
1. Ensure you have network connectivity
1. On Linux, ensure you have sudo access for package managers
1. On Windows, ensure you're running PowerShell with admin rights

### GitHub API rate limit exceeded

When downloading tools from GitHub releases (e.g., actionlint), you may hit rate limits:

```
Failed to fetch actionlint release info from GitHub API
Set GITHUB_TOKEN to avoid rate limits
```

**Solution**: Set a GitHub token:

```bash
# Bash - use personal access token or GitHub CLI token
export GITHUB_TOKEN=$(gh auth token)
./scripts/setup/setup.sh --install

# Or in CI (GitHub Actions)
# The GITHUB_TOKEN is automatically available
```

```powershell
# PowerShell
$env:GITHUB_TOKEN = gh auth token
.\scripts\setup\setup.ps1 -Install
```

### Permission denied

```bash
# Make script executable
chmod +x scripts/setup/setup.sh

# Or run with explicit bash
bash scripts/setup/setup.sh
```

```powershell
# Set execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Development

### Adding a New Tool

1. Add version requirement to `lib/versions.sh`:

   ```bash
   export NEW_TOOL_VERSION="1.0"
   ```

1. Add installation function to `lib/install-tools.sh`:

   ```bash
   install_new_tool() {
       # Implementation
   }
   ```

1. Add tool to `TOOLS` array in `setup.sh`:

   ```bash
   TOOLS=(python3 uv node pnpm pre-commit actionlint new-tool)
   ```

1. Add check in `check_all_tools()`:

   ```bash
   check_tool "new-tool" "$NEW_TOOL_VERSION" "--version" || true
   ```

1. Add case in `install_missing_tools()`:

   ```bash
   new-tool)
       if install_new_tool; then
           ((install_count++))
       else
           ((fail_count++))
           FAILED_INSTALLS+=("new-tool")
       fi
       ;;
   ```

### Testing

```bash
# Test with dry-run (no changes)
./scripts/setup/setup.sh

# Test check-only mode
./scripts/setup/setup.sh --check-only
echo $?  # Should be 0 or 1

# Test with debug output
DEBUG=1 ./scripts/setup/setup.sh

# Test help
./scripts/setup/setup.sh --help
```

## References

- [AGENTS.md](../../AGENTS.md) - Main project documentation
- [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html)
- [NO_COLOR Standard](https://no-color.org/)
- Version requirements in `lib/versions.sh`
- Installation guides: `docs/development/setup.md`

## License

Part of the Riso project. See main project README for license information.
