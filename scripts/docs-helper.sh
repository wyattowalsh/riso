#!/usr/bin/env bash
# Documentation environment setup helper
# Feature: 018-docs-sites-overhaul

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/../.."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

# Detect documentation framework
detect_framework() {
    if [ -f "Makefile.docs" ]; then
        echo "sphinx-shibuya"
    elif [ -d "apps/docs-fumadocs" ]; then
        echo "fumadocs"
    elif [ -d "apps/docs-docusaurus" ]; then
        echo "docusaurus"
    else
        echo "none"
    fi
}

# Setup Sphinx environment
setup_sphinx() {
    log_info "Setting up Sphinx environment..."
    
    # Check for uv
    if ! command -v uv &> /dev/null; then
        log_error "uv not found. Install with: pip install uv"
        exit 1
    fi
    
    # Install dependencies
    log_info "Installing Sphinx dependencies..."
    uv sync --group docs
    
    log_info "Sphinx environment ready!"
    log_info "Build with: uv run make -f Makefile.docs docs"
}

# Setup Fumadocs environment
setup_fumadocs() {
    log_info "Setting up Fumadocs environment..."
    
    # Check for pnpm
    if ! command -v pnpm &> /dev/null; then
        log_error "pnpm not found. Install with: npm install -g pnpm"
        exit 1
    fi
    
    # Install dependencies
    log_info "Installing Fumadocs dependencies..."
    pnpm install
    
    log_info "Fumadocs environment ready!"
    log_info "Dev server: pnpm --filter docs-fumadocs dev"
    log_info "Build: pnpm --filter docs-fumadocs build"
}

# Setup Docusaurus environment
setup_docusaurus() {
    log_info "Setting up Docusaurus environment..."
    
    # Check for pnpm
    if ! command -v pnpm &> /dev/null; then
        log_error "pnpm not found. Install with: npm install -g pnpm"
        exit 1
    fi
    
    # Install dependencies
    log_info "Installing Docusaurus dependencies..."
    pnpm install
    
    log_info "Docusaurus environment ready!"
    log_info "Dev server: pnpm --filter docs-docusaurus start"
    log_info "Build: pnpm --filter docs-docusaurus build"
}

# Build documentation
build_docs() {
    local framework="$1"
    
    log_info "Building $framework documentation..."
    
    case "$framework" in
        sphinx-shibuya)
            uv run make -f Makefile.docs docs
            log_info "Documentation built at: _build/html/index.html"
            ;;
        fumadocs)
            pnpm --filter docs-fumadocs build
            log_info "Documentation built at: apps/docs-fumadocs/out/index.html"
            ;;
        docusaurus)
            pnpm --filter docs-docusaurus build
            log_info "Documentation built at: apps/docs-docusaurus/build/index.html"
            ;;
        *)
            log_error "Unknown framework: $framework"
            exit 1
            ;;
    esac
}

# Validate documentation
validate_docs() {
    local framework="$1"
    
    log_info "Validating $framework documentation..."
    
    # Run validation script
    if [ -f "${PROJECT_ROOT}/scripts/ci/validate_docs_config.py" ]; then
        python3 "${PROJECT_ROOT}/scripts/ci/validate_docs_config.py" .
    else
        log_warn "Validation script not found"
    fi
    
    # Framework-specific validation
    case "$framework" in
        sphinx-shibuya)
            log_info "Running link check..."
            uv run make -f Makefile.docs linkcheck || log_warn "Link check found issues"
            ;;
        *)
            log_info "No additional validation for $framework"
            ;;
    esac
}

# Clean documentation artifacts
clean_docs() {
    local framework="$1"
    
    log_info "Cleaning $framework artifacts..."
    
    case "$framework" in
        sphinx-shibuya)
            uv run make -f Makefile.docs clean-docs
            ;;
        fumadocs)
            rm -rf apps/docs-fumadocs/out apps/docs-fumadocs/.next
            ;;
        docusaurus)
            rm -rf apps/docs-docusaurus/build apps/docs-docusaurus/.docusaurus
            ;;
        *)
            log_error "Unknown framework: $framework"
            exit 1
            ;;
    esac
    
    log_info "Artifacts cleaned!"
}

# Show usage
show_usage() {
    cat << EOF
Documentation Environment Helper
Feature: 018-docs-sites-overhaul

Usage: $0 <command> [framework]

Commands:
    setup       Setup documentation environment
    build       Build documentation
    validate    Validate documentation
    clean       Clean build artifacts
    detect      Detect documentation framework

Framework (optional):
    sphinx-shibuya    Sphinx with Shibuya theme
    fumadocs          Fumadocs (Next.js)
    docusaurus        Docusaurus (React)
    
    If not specified, framework will be auto-detected.

Examples:
    $0 setup              # Auto-detect and setup
    $0 build sphinx       # Build Sphinx docs
    $0 validate           # Validate current docs
    $0 clean              # Clean artifacts

EOF
}

# Main
main() {
    if [ $# -eq 0 ]; then
        show_usage
        exit 0
    fi
    
    local command="$1"
    local framework="${2:-}"
    
    # Auto-detect framework if not specified
    if [ -z "$framework" ]; then
        framework="$(detect_framework)"
        log_info "Detected framework: $framework"
    fi
    
    if [ "$framework" = "none" ]; then
        log_error "No documentation framework detected"
        log_info "Ensure you're in a rendered Riso project directory"
        exit 1
    fi
    
    case "$command" in
        setup)
            case "$framework" in
                sphinx-shibuya) setup_sphinx ;;
                fumadocs) setup_fumadocs ;;
                docusaurus) setup_docusaurus ;;
            esac
            ;;
        build)
            build_docs "$framework"
            ;;
        validate)
            validate_docs "$framework"
            ;;
        clean)
            clean_docs "$framework"
            ;;
        detect)
            echo "$framework"
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            log_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

main "$@"
