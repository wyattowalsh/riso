#!/usr/bin/env bash
# Riso Setup - Tool Installation Functions
# Cross-platform installation functions for all required tooling
# Pattern based on scripts/install-gh-cli.sh

set -euo pipefail

# Source required libraries (when not already loaded)
# shellcheck disable=SC1091
if [ -z "${COLORS_LOADED:-}" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    # shellcheck source=colors.sh
    . "${SCRIPT_DIR}/colors.sh"
    # shellcheck source=detect-platform.sh
    . "${SCRIPT_DIR}/detect-platform.sh"
    # shellcheck source=logging.sh
    . "${SCRIPT_DIR}/logging.sh"
    # shellcheck source=versions.sh
    . "${SCRIPT_DIR}/versions.sh"
fi

# Utility: Check if command exists
has_cmd() {
    command -v "$1" >/dev/null 2>&1
}

# Utility: Compare version strings (semver-like)
# Returns: 0 if $1 >= $2, 1 otherwise
version_gte() {
    local current="$1"
    local required="$2"

    # Simple string comparison for now (works for X.Y format)
    # For more complex semver, would need awk or external tool
    printf '%s\n%s\n' "$required" "$current" | sort -V -C 2>/dev/null
}

# Utility: Get tool version
# Args: tool_name, version_flag (default: --version)
get_tool_version() {
    local tool_name="$1"
    local version_flag="${2:---version}"

    if ! has_cmd "$tool_name"; then
        echo "unknown"
        return 1
    fi

    local version_output
    version_output=$("$tool_name" "$version_flag" 2>&1 | head -n 1)

    # Extract version number (first occurrence of X.Y.Z pattern)
    local version
    version=$(echo "$version_output" | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -n 1)

    if [ -n "$version" ]; then
        echo "$version"
        return 0
    fi

    echo "unknown"
    return 1
}

#
# Security Utilities
#

# Verify checksum of a downloaded file
# Args: file_path, expected_checksum, algorithm (default: sha256)
# Returns: 0 if checksum matches, 1 otherwise
verify_checksum() {
    local file_path="$1"
    local expected_checksum="$2"
    local algorithm="${3:-sha256}"

    if [ ! -f "$file_path" ]; then
        log_error "Cannot verify checksum: file not found: $file_path"
        return 1
    fi

    local actual_checksum
    case "$algorithm" in
        sha256)
            if has_cmd sha256sum; then
                actual_checksum=$(sha256sum "$file_path" | cut -d' ' -f1)
            elif has_cmd shasum; then
                actual_checksum=$(shasum -a 256 "$file_path" | cut -d' ' -f1)
            else
                log_warn "No checksum tool available (sha256sum or shasum)"
                return 1
            fi
            ;;
        sha512)
            if has_cmd sha512sum; then
                actual_checksum=$(sha512sum "$file_path" | cut -d' ' -f1)
            elif has_cmd shasum; then
                actual_checksum=$(shasum -a 512 "$file_path" | cut -d' ' -f1)
            else
                log_warn "No checksum tool available"
                return 1
            fi
            ;;
        *)
            log_error "Unsupported checksum algorithm: $algorithm"
            return 1
            ;;
    esac

    if [ "$actual_checksum" = "$expected_checksum" ]; then
        log_debug "Checksum verified for $file_path"
        return 0
    else
        log_error "Checksum mismatch for $file_path"
        log_error "  Expected: $expected_checksum"
        log_error "  Actual:   $actual_checksum"
        return 1
    fi
}

# Secure download with retry logic
# Args: url, output_file, [expected_checksum]
# Returns: 0 on success, 1 on failure
secure_download() {
    local url="$1"
    local output_file="$2"
    local expected_checksum="${3:-}"
    local max_retries=3
    local retry_delay=5

    for ((i = 1; i <= max_retries; i++)); do
        log_debug "Download attempt $i/$max_retries: $url"
        if curl -fsSL --retry 3 --retry-delay 2 -o "$output_file" "$url"; then
            # Verify checksum if provided
            if [ -n "$expected_checksum" ]; then
                if verify_checksum "$output_file" "$expected_checksum"; then
                    return 0
                else
                    log_error "Checksum verification failed, removing file"
                    rm -f "$output_file"
                    return 1
                fi
            fi
            return 0
        fi

        if [ $i -lt $max_retries ]; then
            log_warn "Download failed, retrying in ${retry_delay}s..."
            sleep "$retry_delay"
            retry_delay=$((retry_delay * 2))  # Exponential backoff
        fi
    done

    log_error "Download failed after $max_retries attempts: $url"
    return 1
}

# GitHub API request with optional authentication
# Uses GITHUB_TOKEN or GH_TOKEN environment variable if available
# Args: api_endpoint (e.g., "repos/owner/repo/releases/latest")
# Returns: JSON response on stdout, 0 on success, 1 on failure
github_api() {
    local endpoint="$1"
    local url="https://api.github.com/${endpoint}"
    local auth_header=""

    # Use GitHub token if available (avoids rate limiting)
    local token="${GITHUB_TOKEN:-${GH_TOKEN:-}}"
    if [ -n "$token" ]; then
        auth_header="-H \"Authorization: Bearer $token\""
        log_debug "Using authenticated GitHub API request"
    else
        log_debug "Using unauthenticated GitHub API request (rate limits apply)"
    fi

    local response
    if [ -n "$auth_header" ]; then
        response=$(curl -fsSL -H "Accept: application/vnd.github+json" \
            -H "Authorization: Bearer $token" \
            -H "X-GitHub-Api-Version: 2022-11-28" \
            "$url" 2>/dev/null)
    else
        response=$(curl -fsSL -H "Accept: application/vnd.github+json" \
            -H "X-GitHub-Api-Version: 2022-11-28" \
            "$url" 2>/dev/null)
    fi

    if [ $? -eq 0 ] && [ -n "$response" ]; then
        echo "$response"
        return 0
    else
        log_warn "GitHub API request failed: $url"
        return 1
    fi
}

# Securely execute a remote installer script with checksum verification
# Args: url, expected_checksum, [interpreter (default: sh)]
# Returns: 0 on success, 1 on failure
secure_install_script() {
    local url="$1"
    local expected_checksum="${2:-}"
    local interpreter="${3:-sh}"

    local tmp_script
    tmp_script=$(mktemp "${TMPDIR:-/tmp}/riso-install-XXXXXX.sh")

    # Cleanup on exit
    trap 'rm -f "$tmp_script"' EXIT

    log_info "Downloading installer from $url..."
    if ! secure_download "$url" "$tmp_script" "$expected_checksum"; then
        log_error "Failed to download installer script"
        return 1
    fi

    # If no checksum provided, warn but continue (for backwards compatibility)
    if [ -z "$expected_checksum" ]; then
        log_warn "No checksum verification for: $url"
        log_warn "Consider adding checksum verification for security"
    fi

    log_info "Executing installer..."
    if $interpreter "$tmp_script"; then
        rm -f "$tmp_script"
        return 0
    else
        log_error "Installer script failed"
        rm -f "$tmp_script"
        return 1
    fi
}

#
# UV Installation
#

install_uv_with_mise() {
    if ! has_cmd mise; then
        return 1
    fi

    log_info "Installing uv with mise..."
    if mise install uv@latest >/dev/null 2>&1; then
        return 0
    fi

    log_warn "mise failed to install uv"
    return 1
}

install_uv_with_brew() {
    if ! has_cmd brew; then
        return 1
    fi

    log_info "Installing uv with Homebrew..."
    if brew list uv >/dev/null 2>&1; then
        brew upgrade uv >/dev/null 2>&1 || true
    else
        brew install uv
    fi
    return 0
}

install_uv_with_winget() {
    if ! has_cmd winget; then
        return 1
    fi

    log_info "Installing uv with winget..."
    winget install --id astral-sh.uv -e --source winget
    return 0
}

install_uv_with_curl() {
    if ! has_cmd curl; then
        log_warn "curl is required for standalone uv installation"
        return 1
    fi

    log_info "Installing uv with standalone installer..."
    # Note: uv's install script doesn't provide static checksums
    # The script is fetched over HTTPS from Astral's CDN
    # For enhanced security, consider using mise or brew instead
    if secure_install_script "https://astral.sh/uv/install.sh" "" "sh"; then
        return 0
    fi
    return 1
}

install_uv() {
    local start_time
    start_time=$(date +%s%3N)

    # Check if already installed with correct version
    if has_cmd uv; then
        local current_version
        current_version=$(get_tool_version uv)
        if version_gte "$current_version" "$UV_MIN_VERSION"; then
            log_success "uv ${current_version} already installed (>= ${UV_MIN_VERSION})"
            log_provision_result "uv" "skipped" "existing" "$current_version" 0
            return 0
        else
            log_warn "uv ${current_version} is below minimum ${UV_MIN_VERSION}, upgrading..."
        fi
    fi

    # Try installation methods in order
    local install_method=""
    if install_uv_with_mise; then
        install_method="mise"
    elif install_uv_with_brew; then
        install_method="brew"
    elif install_uv_with_winget; then
        install_method="winget"
    elif install_uv_with_curl; then
        install_method="curl"
    else
        log_error "Failed to install uv. Install manually: https://docs.astral.sh/uv/getting-started/installation/"
        log_provision_result "uv" "failure" "none" "unknown" 0
        return 1
    fi

    # Verify installation
    if has_cmd uv; then
        local version
        version=$(get_tool_version uv)
        local duration
        duration=$(($(date +%s%3N) - start_time))
        log_success "uv ${version} installed via ${install_method}"
        log_provision_result "uv" "success" "$install_method" "$version" "$duration"
        return 0
    else
        log_error "uv installation failed"
        log_provision_result "uv" "failure" "$install_method" "unknown" 0
        return 1
    fi
}

#
# Python Installation
#

install_python_with_mise() {
    if ! has_cmd mise; then
        return 1
    fi

    log_info "Installing Python ${PYTHON_MIN_VERSION} with mise..."
    if mise install "python@${PYTHON_MIN_VERSION}" >/dev/null 2>&1; then
        return 0
    fi

    log_warn "mise failed to install Python"
    return 1
}

install_python_with_brew() {
    if ! has_cmd brew; then
        return 1
    fi

    log_info "Installing Python with Homebrew..."
    # Homebrew's python@3.11 or python@3.12
    local python_formula="python@${PYTHON_MIN_VERSION}"
    if brew list "$python_formula" >/dev/null 2>&1; then
        brew upgrade "$python_formula" >/dev/null 2>&1 || true
    else
        brew install "$python_formula"
    fi
    return 0
}

install_python_with_apt() {
    if ! has_cmd apt-get; then
        return 1
    fi

    local python_pkg="python${PYTHON_MIN_VERSION}"
    log_info "Installing Python with apt (${python_pkg})..."

    if has_cmd sudo; then
        sudo apt-get update
        sudo apt-get install -y "$python_pkg" "${python_pkg}-venv" "${python_pkg}-dev"
    else
        apt-get update
        apt-get install -y "$python_pkg" "${python_pkg}-venv" "${python_pkg}-dev"
    fi
    return 0
}

install_python_with_dnf() {
    if ! has_cmd dnf; then
        return 1
    fi

    local python_pkg="python${PYTHON_MIN_VERSION}"
    log_info "Installing Python with dnf (${python_pkg})..."

    if has_cmd sudo; then
        sudo dnf install -y "$python_pkg" "${python_pkg}-devel"
    else
        dnf install -y "$python_pkg" "${python_pkg}-devel"
    fi
    return 0
}

install_python_with_pacman() {
    if ! has_cmd pacman; then
        return 1
    fi

    log_info "Installing Python with pacman..."

    if has_cmd sudo; then
        sudo pacman -Sy --noconfirm python
    else
        pacman -Sy --noconfirm python
    fi
    return 0
}

install_python_with_apk() {
    if ! has_cmd apk; then
        return 1
    fi

    log_info "Installing Python with apk..."

    if has_cmd sudo; then
        sudo apk add --no-cache python3 python3-dev
    else
        apk add --no-cache python3 python3-dev
    fi
    return 0
}

install_python_with_winget() {
    if ! has_cmd winget; then
        return 1
    fi

    log_info "Installing Python with winget..."
    winget install --id Python.Python.3.11 -e --source winget
    return 0
}

install_python() {
    local start_time
    start_time=$(date +%s%3N)

    # Check if already installed with correct version
    if has_cmd python3; then
        local current_version
        current_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -n 1)
        if version_gte "$current_version" "$PYTHON_MIN_VERSION"; then
            log_success "Python ${current_version} already installed (>= ${PYTHON_MIN_VERSION})"
            log_provision_result "python" "skipped" "existing" "$current_version" 0
            return 0
        else
            log_warn "Python ${current_version} is below minimum ${PYTHON_MIN_VERSION}, upgrading..."
        fi
    fi

    # Try installation methods in order
    local install_method=""
    local os
    os="$(detect_os)"

    if install_python_with_mise; then
        install_method="mise"
    elif [ "$os" = "macos" ] && install_python_with_brew; then
        install_method="brew"
    elif [ "$os" = "linux" ]; then
        local distro
        distro="$(detect_linux_distro)"
        case "$distro" in
            ubuntu|debian)
                if install_python_with_apt; then
                    install_method="apt"
                fi
                ;;
            fedora|rhel)
                if install_python_with_dnf; then
                    install_method="dnf"
                fi
                ;;
            arch)
                if install_python_with_pacman; then
                    install_method="pacman"
                fi
                ;;
            alpine)
                if install_python_with_apk; then
                    install_method="apk"
                fi
                ;;
        esac
    elif [ "$os" = "windows" ] && install_python_with_winget; then
        install_method="winget"
    fi

    if [ -z "$install_method" ]; then
        log_error "Failed to install Python. Install manually: https://www.python.org/downloads/"
        log_provision_result "python" "failure" "none" "unknown" 0
        return 1
    fi

    # Verify installation
    if has_cmd python3; then
        local version
        version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n 1)
        local duration
        duration=$(($(date +%s%3N) - start_time))
        log_success "Python ${version} installed via ${install_method}"
        log_provision_result "python" "success" "$install_method" "$version" "$duration"
        return 0
    else
        log_error "Python installation failed"
        log_provision_result "python" "failure" "$install_method" "unknown" 0
        return 1
    fi
}

#
# Node.js Installation
#

install_node_with_mise() {
    if ! has_cmd mise; then
        return 1
    fi

    log_info "Installing Node.js ${NODE_MIN_VERSION} with mise..."
    if mise install "node@${NODE_MIN_VERSION}" >/dev/null 2>&1; then
        return 0
    fi

    log_warn "mise failed to install Node.js"
    return 1
}

install_node_with_brew() {
    if ! has_cmd brew; then
        return 1
    fi

    log_info "Installing Node.js with Homebrew..."
    # Homebrew's node@20
    local node_formula="node@${NODE_MIN_VERSION}"
    if brew list "$node_formula" >/dev/null 2>&1; then
        brew upgrade "$node_formula" >/dev/null 2>&1 || true
    else
        brew install "$node_formula"
    fi
    return 0
}

install_node_with_apt() {
    if ! has_cmd apt-get || ! has_cmd curl; then
        return 1
    fi

    log_info "Installing Node.js with apt (via NodeSource)..."

    # Add NodeSource repository
    if has_cmd sudo; then
        curl -fsSL "https://deb.nodesource.com/setup_${NODE_MIN_VERSION}.x" | sudo bash -
        sudo apt-get install -y nodejs
    else
        curl -fsSL "https://deb.nodesource.com/setup_${NODE_MIN_VERSION}.x" | bash -
        apt-get install -y nodejs
    fi
    return 0
}

install_node_with_dnf() {
    if ! has_cmd dnf; then
        return 1
    fi

    log_info "Installing Node.js with dnf (module nodejs:${NODE_MIN_VERSION})..."

    if has_cmd sudo; then
        sudo dnf module install -y "nodejs:${NODE_MIN_VERSION}"
    else
        dnf module install -y "nodejs:${NODE_MIN_VERSION}"
    fi
    return 0
}

install_node_with_pacman() {
    if ! has_cmd pacman; then
        return 1
    fi

    log_info "Installing Node.js with pacman..."

    if has_cmd sudo; then
        sudo pacman -Sy --noconfirm nodejs npm
    else
        pacman -Sy --noconfirm nodejs npm
    fi
    return 0
}

install_node_with_winget() {
    if ! has_cmd winget; then
        return 1
    fi

    log_info "Installing Node.js with winget..."
    winget install --id OpenJS.NodeJS.LTS -e --source winget
    return 0
}

install_node() {
    local start_time
    start_time=$(date +%s%3N)

    # Check if already installed with correct version
    if has_cmd node; then
        local current_version
        current_version=$(node --version 2>&1 | grep -oE '[0-9]+' | head -n 1)
        if [ "$current_version" -ge "$NODE_MIN_VERSION" ]; then
            log_success "Node.js v${current_version} already installed (>= v${NODE_MIN_VERSION})"
            log_provision_result "node" "skipped" "existing" "$current_version" 0
            return 0
        else
            log_warn "Node.js v${current_version} is below minimum v${NODE_MIN_VERSION}, upgrading..."
        fi
    fi

    # Try installation methods in order
    local install_method=""
    local os
    os="$(detect_os)"

    if install_node_with_mise; then
        install_method="mise"
    elif [ "$os" = "macos" ] && install_node_with_brew; then
        install_method="brew"
    elif [ "$os" = "linux" ]; then
        local distro
        distro="$(detect_linux_distro)"
        case "$distro" in
            ubuntu|debian)
                if install_node_with_apt; then
                    install_method="apt"
                fi
                ;;
            fedora|rhel)
                if install_node_with_dnf; then
                    install_method="dnf"
                fi
                ;;
            arch)
                if install_node_with_pacman; then
                    install_method="pacman"
                fi
                ;;
        esac
    elif [ "$os" = "windows" ] && install_node_with_winget; then
        install_method="winget"
    fi

    if [ -z "$install_method" ]; then
        log_error "Failed to install Node.js. Install manually: https://nodejs.org/"
        log_provision_result "node" "failure" "none" "unknown" 0
        return 1
    fi

    # Verify installation
    if has_cmd node; then
        local version
        version=$(node --version 2>&1 | sed 's/^v//')
        local duration
        duration=$(($(date +%s%3N) - start_time))
        log_success "Node.js ${version} installed via ${install_method}"
        log_provision_result "node" "success" "$install_method" "$version" "$duration"
        return 0
    else
        log_error "Node.js installation failed"
        log_provision_result "node" "failure" "$install_method" "unknown" 0
        return 1
    fi
}

#
# pnpm Installation
#

install_pnpm_with_mise() {
    if ! has_cmd mise; then
        return 1
    fi

    log_info "Installing pnpm with mise..."
    if mise install pnpm@latest >/dev/null 2>&1; then
        return 0
    fi

    log_warn "mise failed to install pnpm"
    return 1
}

install_pnpm_with_brew() {
    if ! has_cmd brew; then
        return 1
    fi

    log_info "Installing pnpm with Homebrew..."
    if brew list pnpm >/dev/null 2>&1; then
        brew upgrade pnpm >/dev/null 2>&1 || true
    else
        brew install pnpm
    fi
    return 0
}

install_pnpm_with_corepack() {
    if ! has_cmd corepack; then
        return 1
    fi

    log_info "Installing pnpm with corepack..."
    corepack enable
    corepack prepare pnpm@latest --activate
    return 0
}

install_pnpm_with_npm() {
    if ! has_cmd npm; then
        return 1
    fi

    log_info "Installing pnpm with npm..."
    npm install -g pnpm
    return 0
}

install_pnpm() {
    local start_time
    start_time=$(date +%s%3N)

    # Check if already installed with correct version
    if has_cmd pnpm; then
        local current_version
        current_version=$(get_tool_version pnpm)
        if version_gte "$current_version" "$PNPM_MIN_VERSION"; then
            log_success "pnpm ${current_version} already installed (>= ${PNPM_MIN_VERSION})"
            log_provision_result "pnpm" "skipped" "existing" "$current_version" 0
            return 0
        else
            log_warn "pnpm ${current_version} is below minimum ${PNPM_MIN_VERSION}, upgrading..."
        fi
    fi

    # Try installation methods in order
    local install_method=""
    if install_pnpm_with_mise; then
        install_method="mise"
    elif install_pnpm_with_brew; then
        install_method="brew"
    elif install_pnpm_with_corepack; then
        install_method="corepack"
    elif install_pnpm_with_npm; then
        install_method="npm"
    else
        log_error "Failed to install pnpm. Install manually: https://pnpm.io/installation"
        log_provision_result "pnpm" "failure" "none" "unknown" 0
        return 1
    fi

    # Verify installation
    if has_cmd pnpm; then
        local version
        version=$(get_tool_version pnpm)
        local duration
        duration=$(($(date +%s%3N) - start_time))
        log_success "pnpm ${version} installed via ${install_method}"
        log_provision_result "pnpm" "success" "$install_method" "$version" "$duration"
        return 0
    else
        log_error "pnpm installation failed"
        log_provision_result "pnpm" "failure" "$install_method" "unknown" 0
        return 1
    fi
}

#
# Python Quality Tools (via uv tool install)
#

install_quality_tool() {
    local tool_name="$1"
    local tool_version="$2"
    local start_time
    start_time=$(date +%s%3N)

    # Verify uv is available
    if ! has_cmd uv; then
        log_error "uv is required to install ${tool_name}"
        log_provision_result "$tool_name" "failure" "uv-missing" "unknown" 0
        return 1
    fi

    # Check if already installed
    if uv tool list 2>/dev/null | grep -q "^${tool_name} "; then
        local current_version
        current_version=$(uv tool list 2>/dev/null | grep "^${tool_name} " | awk '{print $2}' | sed 's/v//')
        if version_gte "$current_version" "$tool_version"; then
            log_success "${tool_name} ${current_version} already installed (>= ${tool_version})"
            log_provision_result "$tool_name" "skipped" "uv-tool" "$current_version" 0
            return 0
        else
            log_warn "${tool_name} ${current_version} is below minimum ${tool_version}, upgrading..."
        fi
    fi

    log_info "Installing ${tool_name} ${tool_version} with uv tool..."
    if uv tool install "${tool_name}==${tool_version}" >/dev/null 2>&1; then
        local duration
        duration=$(($(date +%s%3N) - start_time))
        log_success "${tool_name} ${tool_version} installed via uv tool"
        log_provision_result "$tool_name" "success" "uv-tool" "$tool_version" "$duration"
        return 0
    else
        log_error "${tool_name} installation failed"
        log_provision_result "$tool_name" "failure" "uv-tool" "unknown" 0
        return 1
    fi
}

install_quality_tools() {
    log_section "Installing Python quality tools"

    local all_success=0

    install_quality_tool "ruff" "$RUFF_VERSION" || all_success=1
    install_quality_tool "ty" "$TY_VERSION" || all_success=1
    install_quality_tool "pylint" "$PYLINT_VERSION" || all_success=1
    install_quality_tool "coverage" "$COVERAGE_VERSION" || all_success=1

    return $all_success
}

#
# Pre-commit Installation
#

install_pre_commit() {
    local start_time
    start_time=$(date +%s%3N)

    # Verify uv is available
    if ! has_cmd uv; then
        log_error "uv is required to install pre-commit"
        log_provision_result "pre-commit" "failure" "uv-missing" "unknown" 0
        return 1
    fi

    # Check if already installed
    if has_cmd pre-commit; then
        local current_version
        current_version=$(get_tool_version pre-commit)
        if version_gte "$current_version" "$PRECOMMIT_VERSION"; then
            log_success "pre-commit ${current_version} already installed (>= ${PRECOMMIT_VERSION})"
            log_provision_result "pre-commit" "skipped" "existing" "$current_version" 0
            return 0
        else
            log_warn "pre-commit ${current_version} is below minimum ${PRECOMMIT_VERSION}, upgrading..."
        fi
    fi

    log_info "Installing pre-commit with uv tool..."
    if uv tool install pre-commit >/dev/null 2>&1; then
        local version
        version=$(get_tool_version pre-commit)
        local duration
        duration=$(($(date +%s%3N) - start_time))
        log_success "pre-commit ${version} installed via uv tool"
        log_provision_result "pre-commit" "success" "uv-tool" "$version" "$duration"
        return 0
    else
        log_error "pre-commit installation failed"
        log_provision_result "pre-commit" "failure" "uv-tool" "unknown" 0
        return 1
    fi
}

#
# actionlint Installation
#

install_actionlint_with_mise() {
    if ! has_cmd mise; then
        return 1
    fi

    log_info "Installing actionlint with mise..."
    if mise install actionlint@latest >/dev/null 2>&1; then
        return 0
    fi

    log_warn "mise failed to install actionlint"
    return 1
}

install_actionlint_with_brew() {
    if ! has_cmd brew; then
        return 1
    fi

    log_info "Installing actionlint with Homebrew..."
    if brew list actionlint >/dev/null 2>&1; then
        brew upgrade actionlint >/dev/null 2>&1 || true
    else
        brew install actionlint
    fi
    return 0
}

install_actionlint_with_download() {
    if ! has_cmd curl; then
        log_warn "curl is required to download actionlint"
        return 1
    fi

    local os
    os="$(detect_os)"
    local arch
    arch="$(detect_arch)"

    # Check if in container - may need different install approach
    if is_container; then
        log_debug "Running in container environment"
    fi

    # Map to actionlint naming
    local os_name
    case "$os" in
        macos) os_name="darwin" ;;
        linux) os_name="linux" ;;
        windows) os_name="windows" ;;
        *) return 1 ;;
    esac

    local arch_name
    case "$arch" in
        x64) arch_name="amd64" ;;
        arm64) arch_name="arm64" ;;
        *) return 1 ;;
    esac

    log_info "Downloading actionlint from GitHub releases..."

    # Get latest release version using authenticated API if token available
    local release_info
    release_info=$(github_api "repos/rhysd/actionlint/releases/latest")

    if [ -z "$release_info" ]; then
        log_warn "Failed to fetch actionlint release info from GitHub API"
        log_warn "Set GITHUB_TOKEN to avoid rate limits"
        return 1
    fi

    local latest_version
    latest_version=$(echo "$release_info" | grep '"tag_name"' | sed -E 's/.*"v([^"]+)".*/\1/')

    if [ -z "$latest_version" ]; then
        log_warn "Failed to determine latest actionlint version"
        return 1
    fi

    local download_url="https://github.com/rhysd/actionlint/releases/download/v${latest_version}/actionlint_${latest_version}_${os_name}_${arch_name}.tar.gz"
    local checksum_url="https://github.com/rhysd/actionlint/releases/download/v${latest_version}/actionlint_${latest_version}_checksums.txt"
    local install_dir="${HOME}/.local/bin"
    local tmp_dir
    tmp_dir=$(mktemp -d "${TMPDIR:-/tmp}/actionlint-XXXXXX")
    local tarball="${tmp_dir}/actionlint.tar.gz"

    mkdir -p "$install_dir"

    # Download tarball with retry
    if ! secure_download "$download_url" "$tarball"; then
        log_warn "Failed to download actionlint"
        rm -rf "$tmp_dir"
        return 1
    fi

    # Try to verify checksum (actionlint publishes checksums)
    local checksums_file="${tmp_dir}/checksums.txt"
    if secure_download "$checksum_url" "$checksums_file"; then
        local expected_checksum
        expected_checksum=$(grep "actionlint_${latest_version}_${os_name}_${arch_name}.tar.gz" "$checksums_file" | cut -d' ' -f1)
        if [ -n "$expected_checksum" ]; then
            if ! verify_checksum "$tarball" "$expected_checksum"; then
                log_error "Checksum verification failed for actionlint"
                rm -rf "$tmp_dir"
                return 1
            fi
            log_success "Checksum verified for actionlint v${latest_version}"
        fi
    else
        log_warn "Could not fetch checksums for actionlint (continuing without verification)"
    fi

    # Extract and install
    if tar -xzf "$tarball" -C "$tmp_dir" actionlint; then
        mv "${tmp_dir}/actionlint" "${install_dir}/actionlint"
        chmod +x "${install_dir}/actionlint"
        rm -rf "$tmp_dir"
        return 0
    else
        log_warn "Failed to extract actionlint"
        rm -rf "$tmp_dir"
        return 1
    fi
}

install_actionlint() {
    local start_time
    start_time=$(date +%s%3N)

    # Check if already installed
    if has_cmd actionlint; then
        local current_version
        current_version=$(get_tool_version actionlint "-version")
        log_success "actionlint ${current_version} already installed"
        log_provision_result "actionlint" "skipped" "existing" "$current_version" 0
        return 0
    fi

    # Try installation methods in order
    local install_method=""
    if install_actionlint_with_mise; then
        install_method="mise"
    elif install_actionlint_with_brew; then
        install_method="brew"
    elif install_actionlint_with_download; then
        install_method="github-release"
    else
        log_error "Failed to install actionlint. Install manually: https://github.com/rhysd/actionlint"
        log_provision_result "actionlint" "failure" "none" "unknown" 0
        return 1
    fi

    # Verify installation
    if has_cmd actionlint; then
        local version
        version=$(get_tool_version actionlint "-version")
        local duration
        duration=$(($(date +%s%3N) - start_time))
        log_success "actionlint ${version} installed via ${install_method}"
        log_provision_result "actionlint" "success" "$install_method" "$version" "$duration"
        return 0
    else
        log_error "actionlint installation failed"
        log_provision_result "actionlint" "failure" "$install_method" "unknown" 0
        return 1
    fi
}

# Export all functions
# Export utility functions
export -f has_cmd version_gte get_tool_version

# Export security functions
export -f verify_checksum secure_download github_api secure_install_script

# Export installation functions
export -f install_uv install_python install_node install_pnpm
export -f install_quality_tools install_quality_tool
export -f install_pre_commit install_actionlint
