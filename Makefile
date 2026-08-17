# Maintainer compatibility shim — use `just` as the command SSOT.
# Rendered template projects still ship Makefile and justfile tracks via Copier.
.DEFAULT_GOAL := help
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

.PHONY: help
help:
	@command -v just >/dev/null 2>&1 || { \
		printf 'error: install just (https://github.com/casey/just)\n' >&2; \
		exit 1; \
	}
	@just --list

.PHONY: %
%:
	@command -v just >/dev/null 2>&1 || { \
		printf 'error: install just (https://github.com/casey/just)\n' >&2; \
		exit 1; \
	}
	@just $@
