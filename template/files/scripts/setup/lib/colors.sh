#!/usr/bin/env bash
# Riso Setup - Colors and Logging Functions
# ANSI color codes and formatted logging with NO_COLOR support

# ANSI color codes (respect NO_COLOR environment variable)
# Exported for use by scripts that source this library
# shellcheck disable=SC2034  # Variables are exported for external use
if [ -n "${NO_COLOR:-}" ] || [ "${TERM:-}" = "dumb" ]; then
    export RED=""
    export GREEN=""
    export YELLOW=""
    export BLUE=""
    export CYAN=""
    export MAGENTA=""
    export BOLD=""
    export NC=""
else
    export RED='\033[0;31m'
    export GREEN='\033[0;32m'
    export YELLOW='\033[1;33m'
    export BLUE='\033[0;34m'
    export CYAN='\033[0;36m'
    export MAGENTA='\033[0;35m'
    export BOLD='\033[1m'
    export NC='\033[0m' # No Color
fi

# Status symbols
SYMBOL_SUCCESS="✓"
SYMBOL_ERROR="✗"
SYMBOL_WARN="⚠"
SYMBOL_INFO="ℹ"
SYMBOL_DEBUG="→"

# Logging functions with consistent formatting
log_info() {
    printf "${BLUE}${SYMBOL_INFO}${NC} [INFO] %s\n" "$*" >&2
}

log_success() {
    printf "${GREEN}${SYMBOL_SUCCESS}${NC} [SUCCESS] %s\n" "$*" >&2
}

log_warn() {
    printf "${YELLOW}${SYMBOL_WARN}${NC} [WARN] %s\n" "$*" >&2
}

log_error() {
    printf "${RED}${SYMBOL_ERROR}${NC} [ERROR] %s\n" "$*" >&2
}

log_debug() {
    if [ "${DEBUG:-}" = "1" ] || [ "${VERBOSE:-}" = "1" ]; then
        printf "${CYAN}${SYMBOL_DEBUG}${NC} [DEBUG] %s\n" "$*" >&2
    fi
}

# Formatted section headers
log_section() {
    printf "\n${BOLD}${BLUE}==>${NC}${BOLD} %s${NC}\n" "$*" >&2
}

# Progress indicator (no newline)
log_progress() {
    printf "${CYAN}${SYMBOL_DEBUG}${NC} %s" "$*" >&2
}

# Progress done (completes progress line)
log_progress_done() {
    printf " %b%b%b\n" "${GREEN}${SYMBOL_SUCCESS}" "${NC}" "" >&2
}

# Progress failed (completes progress line)
log_progress_failed() {
    printf " %b%b%b\n" "${RED}${SYMBOL_ERROR}" "${NC}" "" >&2
}
