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
            nixos)
                echo "nixos"
                ;;
            void)
                echo "void"
                ;;
            gentoo)
                echo "gentoo"
                ;;
            *)
                # Fallback checks for distros that may not set ID properly
                if [ -f /etc/nixos/configuration.nix ]; then
                    echo "nixos"
                elif command -v xbps-install >/dev/null 2>&1; then
                    echo "void"
                elif [ -f /etc/gentoo-release ]; then
                    echo "gentoo"
                else
                    echo "unknown"
                fi
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
# Returns: mise, brew, apt, dnf, yum, pacman, apk, zypper, xbps, emerge, nix, winget, choco, scoop, none
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
            elif command -v xbps-install >/dev/null 2>&1; then
                # Void Linux
                echo "xbps"
                return 0
            elif command -v emerge >/dev/null 2>&1; then
                # Gentoo
                echo "emerge"
                return 0
            elif command -v nix-env >/dev/null 2>&1; then
                # NixOS or Nix package manager
                echo "nix"
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

# Check if running in WSL (Windows Subsystem for Linux)
# Returns: 0 if WSL (1 or 2), 1 otherwise
is_wsl() {
    if [ ! -f /proc/version ]; then
        return 1
    fi

    # Microsoft's WSL kernel contains "microsoft" or "Microsoft" in /proc/version
    # Example: "Linux version 5.15.153.1-microsoft-standard-WSL2"
    if grep -qi microsoft /proc/version; then
        return 0
    fi

    # Alternative check: WSL_DISTRO_NAME is set in WSL environments
    if [ -n "${WSL_DISTRO_NAME:-}" ]; then
        return 0
    fi

    return 1
}

# Check if running in WSL2 specifically (vs WSL1)
# Returns: 0 if WSL2, 1 otherwise
is_wsl2() {
    if ! is_wsl; then
        return 1
    fi

    # WSL2 kernel version string contains "WSL2" marker
    if grep -qi 'WSL2\|microsoft-standard' /proc/version 2>/dev/null; then
        return 0
    fi

    # Alternative: Check for /run/WSL directory (WSL2 only)
    if [ -d /run/WSL ]; then
        return 0
    fi

    # Fallback: Check kernel version >= 4.19 (WSL2 minimum)
    # Note: This is less reliable since native Linux can also have 4.19+
    local kernel_major kernel_minor
    kernel_major="$(uname -r | cut -d. -f1)"
    kernel_minor="$(uname -r | cut -d. -f2)"
    if [ "$kernel_major" -gt 4 ] || { [ "$kernel_major" -eq 4 ] && [ "$kernel_minor" -ge 19 ]; }; then
        return 0
    fi

    return 1
}

# Check if running inside a container (Docker, Podman, LXC, etc.)
# Returns: 0 if in container, 1 otherwise
is_container() {
    # Docker container marker
    if [ -f /.dockerenv ]; then
        return 0
    fi

    # Podman container marker
    if [ -f /run/.containerenv ]; then
        return 0
    fi

    # Check container environment variable (set by many container runtimes)
    if [ -n "${container:-}" ]; then
        return 0
    fi

    # Check cgroup for container signatures
    if [ -f /proc/1/cgroup ]; then
        if grep -qE 'docker|lxc|kubepods|containerd' /proc/1/cgroup 2>/dev/null; then
            return 0
        fi
    fi

    # systemd-detect-virt (if available)
    if command -v systemd-detect-virt >/dev/null 2>&1; then
        if systemd-detect-virt -c >/dev/null 2>&1; then
            return 0
        fi
    fi

    return 1
}

# Get container runtime name if in container
# Returns: docker, podman, lxc, kubernetes, containerd, unknown, or empty if not in container
get_container_runtime() {
    if ! is_container; then
        echo ""
        return 1
    fi

    if [ -f /.dockerenv ]; then
        echo "docker"
    elif [ -f /run/.containerenv ]; then
        echo "podman"
    elif [ -n "${KUBERNETES_SERVICE_HOST:-}" ]; then
        echo "kubernetes"
    elif [ -f /proc/1/cgroup ] && grep -q 'lxc' /proc/1/cgroup 2>/dev/null; then
        echo "lxc"
    elif [ -f /proc/1/cgroup ] && grep -q 'containerd' /proc/1/cgroup 2>/dev/null; then
        echo "containerd"
    else
        echo "unknown"
    fi
}

# Get platform summary (for debugging)
get_platform_summary() {
    local container_info=""
    if is_container; then
        container_info="yes ($(get_container_runtime))"
    else
        container_info="no"
    fi

    local wsl_info=""
    if is_wsl; then
        if is_wsl2; then
            wsl_info="yes (WSL2)"
        else
            wsl_info="yes (WSL1)"
        fi
    else
        wsl_info="no"
    fi

    cat <<EOF
OS: $(detect_os)
Distro: $(detect_linux_distro)
Package Manager: $(detect_package_manager)
Architecture: $(detect_arch)
Shell: $(detect_shell)
WSL: ${wsl_info}
Container: ${container_info}
EOF
}
