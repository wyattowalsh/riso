#!/usr/bin/env bash
# Riso Setup - Platform Detection
# Detect operating system, distribution, package manager, architecture, and shell

# Detect operating system
# Returns: macos, linux, windows, unknown
detect_os() {
    case "$(uname -s)" in
        Darwin*)
            echo "macos"
            ;;
        Linux*)
            echo "linux"
            ;;
        MINGW*|MSYS*|CYGWIN*)
            echo "windows"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# Detect Linux distribution
# Returns: ubuntu, debian, fedora, arch, alpine, opensuse, rhel, unknown
detect_linux_distro() {
    if [ "$(detect_os)" != "linux" ]; then
        echo "unknown"
        return 1
    fi

    # Check for /etc/os-release (systemd standard)
    if [ -f /etc/os-release ]; then
        # shellcheck source=/dev/null
        . /etc/os-release
        case "${ID:-}" in
            ubuntu)
                echo "ubuntu"
                ;;
            debian)
                echo "debian"
                ;;
            fedora)
                echo "fedora"
                ;;
            arch|archarm|manjaro)
                echo "arch"
                ;;
            alpine)
                echo "alpine"
                ;;
            opensuse*|sles)
                echo "opensuse"
                ;;
            rhel|centos|rocky|almalinux)
                echo "rhel"
                ;;
            *)
                echo "unknown"
                ;;
        esac
    elif [ -f /etc/lsb-release ]; then
        # Fallback for older systems
        # shellcheck source=/dev/null
        . /etc/lsb-release
        case "${DISTRIB_ID:-}" in
            Ubuntu)
                echo "ubuntu"
                ;;
            Debian)
                echo "debian"
                ;;
            *)
                echo "unknown"
                ;;
        esac
    else
        echo "unknown"
    fi
}

# Detect package manager (in priority order)
# Returns: mise, brew, apt, dnf, yum, pacman, apk, zypper, winget, choco, scoop, none
detect_package_manager() {
    # Priority 1: mise (cross-platform version manager)
    if command -v mise >/dev/null 2>&1; then
        echo "mise"
        return 0
    fi

    # Priority 2: Platform-specific package managers
    local os
    os="$(detect_os)"

    case "$os" in
        macos)
            if command -v brew >/dev/null 2>&1; then
                echo "brew"
                return 0
            fi
            ;;
        linux)
            # Try package managers in order of popularity
            if command -v apt-get >/dev/null 2>&1; then
                echo "apt"
                return 0
            elif command -v dnf >/dev/null 2>&1; then
                echo "dnf"
                return 0
            elif command -v yum >/dev/null 2>&1; then
                echo "yum"
                return 0
            elif command -v pacman >/dev/null 2>&1; then
                echo "pacman"
                return 0
            elif command -v apk >/dev/null 2>&1; then
                echo "apk"
                return 0
            elif command -v zypper >/dev/null 2>&1; then
                echo "zypper"
                return 0
            fi
            ;;
        windows)
            if command -v winget >/dev/null 2>&1; then
                echo "winget"
                return 0
            elif command -v choco >/dev/null 2>&1; then
                echo "choco"
                return 0
            elif command -v scoop >/dev/null 2>&1; then
                echo "scoop"
                return 0
            fi
            ;;
    esac

    echo "none"
    return 1
}

# Detect CPU architecture
# Returns: x64, arm64, arm, unknown
detect_arch() {
    local machine
    machine="$(uname -m)"

    case "$machine" in
        x86_64|amd64)
            echo "x64"
            ;;
        aarch64|arm64)
            echo "arm64"
            ;;
        armv7l|armv6l)
            echo "arm"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# Detect shell
# Returns: bash, zsh, fish, sh
detect_shell() {
    # First check SHELL environment variable
    if [ -n "${SHELL:-}" ]; then
        case "$SHELL" in
            */bash)
                echo "bash"
                return 0
                ;;
            */zsh)
                echo "zsh"
                return 0
                ;;
            */fish)
                echo "fish"
                return 0
                ;;
            */sh)
                echo "sh"
                return 0
                ;;
        esac
    fi

    # Fallback: check current shell process
    local current_shell
    current_shell="$(ps -p $$ -o comm= 2>/dev/null || echo 'sh')"
    case "$current_shell" in
        bash|*/bash)
            echo "bash"
            ;;
        zsh|*/zsh)
            echo "zsh"
            ;;
        fish|*/fish)
            echo "fish"
            ;;
        *)
            echo "sh"
            ;;
    esac
}

# Check if running in WSL2
# Returns: 0 if WSL2, 1 otherwise
is_wsl() {
    if [ ! -f /proc/version ]; then
        return 1
    fi

    if grep -qi microsoft /proc/version; then
        # WSL1 or WSL2
        if grep -qi "WSL2" /proc/version; then
            return 0
        fi
        # Check kernel version for WSL2 (4.19+)
        local kernel_version
        kernel_version="$(uname -r | cut -d. -f1)"
        if [ "$kernel_version" -ge 4 ]; then
            return 0
        fi
    fi

    return 1
}

# Get platform summary (for debugging)
get_platform_summary() {
    cat <<EOF
OS: $(detect_os)
Distro: $(detect_linux_distro)
Package Manager: $(detect_package_manager)
Architecture: $(detect_arch)
Shell: $(detect_shell)
WSL2: $(is_wsl && echo "yes" || echo "no")
EOF
}
