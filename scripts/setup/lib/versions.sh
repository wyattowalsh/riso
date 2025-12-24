#!/usr/bin/env bash
# Riso Setup - Version Constants
# This file is the canonical source for all version requirements
# Used by installation and validation scripts to ensure consistent tooling

# Core tooling versions
export PYTHON_MIN_VERSION="3.11"
export UV_MIN_VERSION="0.4"
export NODE_MIN_VERSION="20"
export PNPM_MIN_VERSION="8"

# Python quality tools (managed via uv tool install)
export RUFF_VERSION="0.14.2"
export TY_VERSION="0.0.6"
export PYLINT_VERSION="4.0.2"
export COVERAGE_VERSION="7.6.9"

# Git and CI tools
export PRECOMMIT_VERSION="3.0"
export ACTIONLINT_VERSION="latest"

# Optional/future versions
export COPIER_MIN_VERSION="9.0"
export MISE_MIN_VERSION="2024.9"
