# Riso

> The ultimate modular Copier-based project template for Python and Node.js applications.

[![Code Quality](https://github.com/wyattowalsh/riso/actions/workflows/quality.yml/badge.svg)](https://github.com/wyattowalsh/riso/actions/workflows/quality.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Riso is a batteries-included template system that scaffolds production-ready projects with optional CLI, API, MCP (Model Context Protocol), documentation, and SaaS starter modules.

## Features

- 🐍 **Python Stack**: Python 3.11+ with uv, pytest, ruff, mypy, pylint
- 📦 **Node.js Stack**: Node.js 20 LTS with pnpm, TypeScript, Vitest
- 🔌 **Modular Design**: Mix and match CLI, API, GraphQL, WebSocket, MCP modules
- 📚 **Documentation**: Choose from Fumadocs, Sphinx Shibuya, or Docusaurus
- 🚀 **SaaS Starter**: Complete SaaS boilerplate with 14 technology categories
- ✅ **Quality First**: 90% test coverage requirement, strict linting profiles
- 🔄 **CI/CD Ready**: GitHub Actions workflows with matrix testing

## Prerequisites

- Python ≥3.11 with [uv](https://github.com/astral-sh/uv)
- Node.js 20 LTS with [pnpm](https://pnpm.io/) ≥8 (for docs/Node tracks)
- [Copier](https://copier.readthedocs.io/) ≥9.1.0

## Quick Start

```bash
# Install Copier if you haven't already
pip install copier

# Create a new project from the template
copier copy gh:wyattowalsh/riso my-project

# Follow the interactive prompts to configure your project
```

## Module Reference

| Module | Prompt Key | Options | Description |
|--------|-----------|---------|-------------|
| **Layout** | `project_layout` | single-package, monorepo | Repository structure |
| **Quality** | `quality_profile` | standard, strict | Linting strictness |
| **CLI** | `cli_module` | disabled, enabled | Typer CLI scaffolding |
| **API** | `api_tracks` | none, python, node, python+node | FastAPI/Fastify services |
| **GraphQL** | `graphql_api_module` | disabled, enabled | Strawberry GraphQL |
| **WebSocket** | `websocket_module` | disabled, enabled | Real-time communication |
| **MCP** | `mcp_module` | disabled, enabled | Model Context Protocol |
| **Docs** | `docs_site` | fumadocs, sphinx-shibuya, docusaurus, none | Documentation site |
| **Changelog** | `changelog_module` | disabled, enabled | Semantic release |
| **SaaS** | `saas_starter_module` | disabled, enabled | Full SaaS boilerplate |

## Sample Configurations

Pre-configured samples are available in `samples/`:

- `default` - Minimal baseline with Fumadocs
- `api-python` - Python FastAPI service
- `api-monorepo` - Python + Node APIs in monorepo
- `cli-docs` - CLI with documentation
- `full-stack` - All modules enabled (strict quality)
- `saas-starter/*` - Various SaaS stack configurations

## Documentation

- **[Maintainer Docs](docs/index.md)** - Shibuya-powered documentation
- **[Agent Operations](AGENTS.md)** - Development setup and automation
- **[Feature Specs](specs/)** - Completed feature specifications
- **[Roadmap](docs/guides/roadmap.md)** - Project roadmap

## Completed Features

- **001** - Riso Template Foundation
- **002** - Documentation Template Expansion (Fumadocs, Sphinx, Docusaurus)
- **003** - Code Quality Integrations (Ruff, Mypy, Pylint, pytest)
- **004** - GitHub Actions Workflows
- **005** - Container & Deployment Patterns
- **006** - FastAPI API Scaffold
- **007** - GraphQL API Scaffold
- **008** - WebSocket Scaffold
- **009** - Typer CLI Scaffold
- **010** - API Versioning Strategy
- **011** - API Rate Limiting
- **012** - SaaS Starter
- **013** - MCP Servers
- **014** - Changelog & Release Management
- **015** - Codegen Scaffolding Tools

## Contributing

Contributions are welcome! Please read our contributing guidelines:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run quality checks: `make quality` or `uv run task quality`
5. Commit with conventional commits: `feat: add amazing feature`
6. Push and open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
