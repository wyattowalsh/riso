# Exhaustive Codebase Review Plan for RISO

> **Optimized for Iterative Batches of Massively Parallel Subagents**
>
> **Total Phases**: 8 | **Total Tasks**: 127 | **Parallelism Factor**: Up to 15 concurrent agents per batch

---

## Executive Summary

This plan provides a comprehensive, end-to-end review of the RISO codebase—a modular Copier-based project template system for Python and Node.js applications. The review is structured in 8 phases, each containing multiple parallel task batches designed to maximize throughput while respecting dependency constraints.

### Phase Overview

| Phase | Focus Area | Parallel Tasks | Dependencies |
|-------|-----------|----------------|--------------|
| **1** | Foundation & Structure | 12 | None (Entry Point) |
| **2** | Template System Deep Dive | 15 | Phase 1 |
| **3** | Scripts & Automation | 14 | Phase 1 |
| **4** | Quality & Testing | 13 | Phase 1 |
| **5** | CI/CD & DevOps | 12 | Phases 2-4 |
| **6** | Documentation & Specifications | 11 | Phase 1 |
| **7** | Samples & Integration | 15 | Phases 2-4 |
| **8** | Cross-Cutting Concerns & Synthesis | 35 | All Prior Phases |

---

## Phase 1: Foundation & Structure Analysis

**Objective**: Establish baseline understanding of project architecture, dependencies, and organization.

**Batch Execution**: All 12 tasks can run in parallel (no inter-dependencies)

### Batch 1.A — Core Structure (6 parallel agents)

| Task ID | Agent Type | Description | Target Files/Dirs | Output Expected |
|---------|-----------|-------------|-------------------|-----------------|
| `1.A.1` | Explore | **Repository Layout Analysis** — Map complete directory structure, identify orphaned files, verify organization patterns | `/home/user/riso/` (recursive) | Directory tree report, organizational anomalies |
| `1.A.2` | Explore | **Git History & Contribution Analysis** — Analyze commit patterns, contributor activity, branch strategy, recent changes | `.git/`, `CHANGELOG.md` | Commit frequency, hot spots, velocity metrics |
| `1.A.3` | Explore | **Dependency Audit (Python)** — Analyze pyproject.toml, identify outdated/vulnerable deps, check version constraints | `pyproject.toml`, `*.txt` requirements | Dependency graph, security concerns, version drift |
| `1.A.4` | Explore | **Configuration File Inventory** — Catalog all configuration files, their purposes, and inter-relationships | `*.toml`, `*.yml`, `*.yaml`, `*.json`, `*.ini` | Config map with relationships |
| `1.A.5` | Explore | **Entry Point Mapping** — Identify all execution entry points (scripts, CLI, hooks, CI triggers) | `template/hooks/`, `scripts/`, `.github/workflows/` | Entry point catalog with call graphs |
| `1.A.6` | Explore | **License & Legal Compliance Check** — Verify LICENSE file, check dependency licenses, identify compliance risks | `LICENSE`, dependencies | Compliance report, license compatibility matrix |

### Batch 1.B — Documentation & Standards (6 parallel agents)

| Task ID | Agent Type | Description | Target Files/Dirs | Output Expected |
|---------|-----------|-------------|-------------------|-----------------|
| `1.B.1` | Explore | **README Quality Assessment** — Evaluate README.md completeness, accuracy, alignment with actual codebase | `README.md` | Accuracy score, missing sections, recommendations |
| `1.B.2` | Explore | **AGENTS.md Accuracy Verification** — Cross-reference AGENTS.md claims against actual repository structure | `AGENTS.md` | Discrepancy report, outdated claims |
| `1.B.3` | Explore | **CONTRIBUTING.md Review** — Assess contribution guidelines completeness, verify documented processes work | `CONTRIBUTING.md` | Process verification report |
| `1.B.4` | Explore | **Code Style & Conventions Analysis** — Extract implicit/explicit coding conventions, check consistency | `ruff.toml`, `mypy.ini`, all Python files | Style guide extraction, violation patterns |
| `1.B.5` | Explore | **Naming Convention Audit** — Analyze naming patterns (files, functions, classes, variables) for consistency | All Python files | Naming inconsistencies, anti-patterns |
| `1.B.6` | Explore | **Import Organization Analysis** — Check import structure, circular dependencies, import hygiene | All Python `*.py` files | Import graph, circular dep warnings |

---

## Phase 2: Template System Deep Dive

**Objective**: Comprehensively analyze the Copier template system—the core of RISO.

**Batch Execution**: 15 tasks in 3 sub-batches

### Batch 2.A — Template Core (5 parallel agents)

| Task ID | Agent Type | Description | Target Files/Dirs | Output Expected |
|---------|-----------|-------------|-------------------|-----------------|
| `2.A.1` | Explore | **copier.yml Comprehensive Analysis** — Analyze all 29 prompts, validation rules, defaults, conditionals | `template/copier.yml` | Prompt dependency graph, validation coverage |
| `2.A.2` | Explore | **Prompt System Analysis** — Review dynamic prompt definitions, Jinja logic, edge cases | `template/prompts/*.yml.jinja` | Prompt logic review, edge case catalog |
| `2.A.3` | Explore | **Pre-Generation Hook Deep Dive** — Analyze validation logic, tooling checks, error handling | `template/hooks/pre_gen_project.py` | Logic flow, error handling coverage |
| `2.A.4` | Explore | **Post-Generation Hook Analysis** — Review guidance generation, metadata recording, file cleanup | `template/hooks/post_gen_project.py` | Output correctness, edge cases |
| `2.A.5` | Explore | **Hook Utility Functions Audit** — Analyze shared hook utilities, reusability patterns | `scripts/hooks/*.py` | Utility coverage, duplication analysis |

### Batch 2.B — Template Content - Python Track (5 parallel agents)

| Task ID | Agent Type | Description | Target Files/Dirs | Output Expected |
|---------|-----------|-------------|-------------------|-----------------|
| `2.B.1` | Explore | **Python Package Template Analysis** — Review source package structure, __init__.py patterns | `template/files/python/src/` | Package structure quality, anti-patterns |
| `2.B.2` | Explore | **pyproject.toml.jinja Analysis** — Verify template correctness, all conditional branches | `template/files/python/pyproject.toml.jinja` | Jinja logic errors, missing cases |
| `2.B.3` | Explore | **Quality Tool Configs Review** — Analyze ruff.toml, mypy.ini, pylint templates | `template/files/python/*.jinja` (quality tools) | Config consistency, rule coverage |
| `2.B.4` | Explore | **Test Template Analysis** — Review test patterns, fixtures, pytest configuration | `template/files/python/tests/` | Test pattern quality, fixture design |
| `2.B.5` | Explore | **Task/Makefile Template Analysis** — Verify make vs uv task parity in templates | `template/files/python/Makefile.jinja`, `tasks/` | Parity verification, missing tasks |

### Batch 2.C — Template Content - Node & Shared (5 parallel agents)

| Task ID | Agent Type | Description | Target Files/Dirs | Output Expected |
|---------|-----------|-------------|-------------------|-----------------|
| `2.C.1` | Explore | **Node.js Track Analysis** — Review Fastify API scaffold, TypeScript config, package structure | `template/files/node/` | Architecture quality, TypeScript correctness |
| `2.C.2` | Explore | **Shared Files Analysis** — Review language-agnostic templates (Docker, CI, quality) | `template/files/shared/` | Reusability patterns, duplication |
| `2.C.3` | Explore | **Docker Template Analysis** — Analyze Dockerfile templates, multi-stage builds, CI variants | `template/files/shared/.docker/` | Docker best practices compliance |
| `2.C.4` | Explore | **SaaS Starter Templates** — Review all 14 SaaS configuration categories | `template/files/node/saas/`, `template/files/shared/saas-starter/` | Combination validity, configuration completeness |
| `2.C.5` | Explore | **Module Catalog Analysis** — Verify module_catalog.json.jinja accuracy against actual modules | `template/files/shared/module_catalog.json.jinja` | Catalog accuracy report |

---

## Phase 3: Scripts & Automation Analysis

**Objective**: Audit all automation scripts for correctness, security, and maintainability.

**Batch Execution**: 14 tasks in 3 sub-batches

### Batch 3.A — CI Scripts (5 parallel agents)

| Task ID | Agent Type | Description | Target Files/Dirs | Output Expected |
|---------|-----------|-------------|-------------------|-----------------|
| `3.A.1` | Explore | **render_matrix.py Analysis** — Review GitHub matrix generation logic, edge cases | `scripts/ci/render_matrix.py` | Logic correctness, missing matrix combinations |
| `3.A.2` | Explore | **validate_workflows.py Analysis** — Analyze YAML validation logic, schema enforcement | `scripts/ci/validate_workflows.py` | Validation coverage, false positives/negatives |
| `3.A.3` | Explore | **validate_dockerfiles.py Analysis** — Review Dockerfile validation rules | `scripts/ci/validate_dockerfiles.py` | Rule completeness, best practice coverage |
| `3.A.4` | Explore | **validate_release_configs.py Analysis** — Analyze release configuration validation | `scripts/ci/validate_release_configs.py` | Config validation thoroughness |
| `3.A.5` | Explore | **run_quality_suite.py Analysis** — Review quality orchestration logic | `scripts/ci/run_quality_suite.py` | Tool execution order, error handling |

### Batch 3.B — CI Scripts Continued (5 parallel agents)

| Task ID | Agent Type | Description | Target Files/Dirs | Output Expected |
|---------|-----------|-------------|-------------------|-----------------|
| `3.B.1` | Explore | **check_quality_parity.py Analysis** — Verify make/uv task parity checking logic | `scripts/ci/check_quality_parity.py` | Parity detection accuracy |
| `3.B.2` | Explore | **record_module_success.py Analysis** — Review module success tracking | `scripts/ci/record_module_success.py` | Recording accuracy, data integrity |
| `3.B.3` | Explore | **track_doc_publish.py Analysis** — Analyze documentation publishing tracking | `scripts/ci/track_doc_publish.py` | Tracking completeness |
| `3.B.4` | Explore | **verify_context_sync.py Analysis** — Review context synchronization verification | `scripts/ci/verify_context_sync.py` | Sync detection accuracy |
| `3.B.5` | Explore | **validate_saas_combinations.py Analysis** — Analyze SaaS combination validation | `scripts/ci/validate_saas_combinations.py` | Combination matrix coverage |

### Batch 3.C — Library & Automation Scripts (4 parallel agents)

| Task ID | Agent Type | Description | Target Files/Dirs | Output Expected |
|---------|-----------|-------------|-------------------|-----------------|
| `3.C.1` | Explore | **validation.py Library Analysis** — Review shared validation functions | `scripts/lib/validation.py` | Function quality, reuse patterns |
| `3.C.2` | Explore | **render_client.py Analysis** — Analyze template rendering automation | `scripts/automation/render_client.py` | Rendering logic correctness |
| `3.C.3` | Explore | **render_saas_samples.py Analysis** — Review SaaS sample rendering | `scripts/saas/render_saas_samples.py` | Sample generation quality |
| `3.C.4` | Explore | **Shell Scripts Audit** — Review render-samples.sh and any other shell scripts | `scripts/*.sh` | Shell script quality, portability |

---

## Phase 4: Quality & Testing Analysis

**Objective**: Evaluate test coverage, quality tooling, and verification mechanisms.

**Batch Execution**: 13 tasks in 3 sub-batches

### Batch 4.A — Test Suite Analysis (5 parallel agents)

| Task ID | Agent Type | Description | Target Files/Dirs | Output Expected |
|---------|-----------|-------------|-------------------|-----------------|
| `4.A.1` | Explore | **Test Organization Review** — Analyze test structure, fixture design, conftest.py | `tests/conftest.py`, `tests/` structure | Organization quality, fixture patterns |
| `4.A.2` | Explore | **Unit Test Coverage Analysis** — Review CI script unit tests for completeness | `tests/unit/ci/test_*.py` | Coverage gaps, assertion quality |
| `4.A.3` | Explore | **Hook Test Analysis** — Analyze pre/post generation hook tests | `tests/unit/hooks/test_*.py` | Hook coverage, edge case testing |
| `4.A.4` | Explore | **Integration Test Analysis** — Review template rendering E2E tests | `tests/integration/test_template_rendering.py` | E2E coverage, scenario completeness |
| `4.A.5` | Explore | **Automation Test Analysis** — Analyze sync_test.py and automation tests | `tests/automation/sync_test.py` | Interface parity verification |

### Batch 4.B — Quality Tools Analysis (4 parallel agents)

| Task ID | Agent Type | Description | Target Files/Dirs | Output Expected |
|---------|-----------|-------------|-------------------|-----------------|
| `4.B.1` | Explore | **Ruff Configuration Analysis** — Review linting rules, exclusions, custom settings | `ruff.toml`, `template/files/python/ruff.toml.jinja` | Rule coverage, consistency |
| `4.B.2` | Explore | **Mypy Configuration Analysis** — Analyze type checking strictness, plugin usage | `mypy.ini`, template variants | Type safety level, gaps |
| `4.B.3` | Explore | **Pylint Configuration Analysis** — Review static analysis rules | Pylint configs in templates | Rule effectiveness |
| `4.B.4` | Explore | **Coverage Configuration Analysis** — Analyze pytest-cov settings, exclusions | `pyproject.toml` coverage settings | Coverage accuracy |

### Batch 4.C — Test Fixtures & Patterns (4 parallel agents)

| Task ID | Agent Type | Description | Target Files/Dirs | Output Expected |
|---------|-----------|-------------|-------------------|-----------------|
| `4.C.1` | Explore | **JSON Test Fixtures Analysis** — Review JSON sample fixtures for completeness | `tests/fixtures/json_samples/` | Fixture coverage, realism |
| `4.C.2` | Explore | **YAML Test Fixtures Analysis** — Review YAML sample fixtures | `tests/fixtures/yaml_samples/` | Fixture quality, edge cases |
| `4.C.3` | Explore | **Mock & Patch Pattern Analysis** — Analyze mocking strategies across tests | All test files with mocks | Mock quality, over-mocking risks |
| `4.C.4` | Explore | **Test Marker & Categorization Review** — Verify test markers usage (slow, integration, unit) | All test files | Marker consistency, missing categorizations |

---

## Phase 5: CI/CD & DevOps Analysis

**Objective**: Comprehensively review CI/CD pipelines, workflows, and DevOps configurations.

**Batch Execution**: 12 tasks in 2 sub-batches

### Batch 5.A — GitHub Actions Workflows (6 parallel agents)

| Task ID | Agent Type | Description | Target Files/Dirs | Output Expected |
|---------|-----------|-------------|-------------------|-----------------|
| `5.A.1` | Explore | **quality.yml Workflow Analysis** — Review main quality workflow for metaproject | `.github/workflows/quality.yml` | Workflow correctness, optimization opportunities |
| `5.A.2` | Explore | **riso-quality.yml.jinja Template Analysis** — Analyze generated project quality workflow | `.github/workflows/riso-quality.yml.jinja` | Template correctness, profile handling |
| `5.A.3` | Explore | **riso-matrix.yml.jinja Analysis** — Review matrix testing workflow template | `.github/workflows/riso-matrix.yml.jinja` | Matrix coverage, version testing |
| `5.A.4` | Explore | **riso-deps-update.yml.jinja Analysis** — Analyze dependency update workflow | `.github/workflows/riso-deps-update.yml.jinja` | Update automation correctness |
| `5.A.5` | Explore | **Workflow Context Files Analysis** — Review shared workflow context snippets | `.github/context/` | DRY compliance, snippet quality |
| `5.A.6` | Explore | **GitHub Prompts Analysis** — Analyze PR/issue templates, workflow prompts | `.github/prompts/`, `.github/*.md` | Template quality, user guidance |

### Batch 5.B — Container & Infrastructure (6 parallel agents)

| Task ID | Agent Type | Description | Target Files/Dirs | Output Expected |
|---------|-----------|-------------|-------------------|-----------------|
| `5.B.1` | Explore | **Docker Compose Templates Analysis** — Review docker-compose.yml.jinja | `template/files/shared/docker-compose.yml.jinja` | Service configuration quality |
| `5.B.2` | Explore | **Dockerfile Best Practices Audit** — Deep dive into Dockerfile templates | All Dockerfile templates | Security, optimization recommendations |
| `5.B.3` | Explore | **Environment Variable Templates** — Analyze .env.example.jinja patterns | `template/files/shared/.env.example.jinja` | Security, completeness |
| `5.B.4` | Explore | **CI Caching Strategy Review** — Analyze dependency caching approaches | All workflow files | Cache efficiency, hit rate optimization |
| `5.B.5` | Explore | **Artifact Management Review** — Analyze artifact upload/retention strategies | All workflow files | Retention policies, storage efficiency |
| `5.B.6` | Explore | **Branch Protection Analysis** — Review required checks, protection rules | Workflow files, AGENTS.md | Protection completeness |

---

## Phase 6: Documentation & Specifications Analysis

**Objective**: Audit all documentation for accuracy, completeness, and maintainability.

**Batch Execution**: 11 tasks in 2 sub-batches

### Batch 6.A — Maintainer Documentation (6 parallel agents)

| Task ID | Agent Type | Description | Target Files/Dirs | Output Expected |
|---------|-----------|-------------|-------------------|-----------------|
| `6.A.1` | Explore | **Docs Index & Structure Analysis** — Review documentation organization | `docs/index.md`, `docs/` structure | Navigation quality, completeness |
| `6.A.2` | Explore | **Quickstart Guide Analysis** — Verify quickstart accuracy against actual setup | `docs/guides/quickstart.md.jinja` | Accuracy verification, step completeness |
| `6.A.3` | Explore | **Implementation Guide Review** — Analyze feature implementation patterns | `docs/guides/implementation-guide.md` | Pattern quality, applicability |
| `6.A.4` | Explore | **Testing Strategy Guide Analysis** — Review testing documentation | `docs/guides/testing-strategy.md` | Strategy completeness, alignment with tests |
| `6.A.5` | Explore | **API Documentation Review** — Analyze script/API reference docs | `docs/api/` | Reference accuracy, completeness |
| `6.A.6` | Explore | **Sphinx Configuration Analysis** — Review docs build configuration | `docs/conf.py` | Config correctness, theme settings |

### Batch 6.B — Specifications & Roadmap (5 parallel agents)

| Task ID | Agent Type | Description | Target Files/Dirs | Output Expected |
|---------|-----------|-------------|-------------------|-----------------|
| `6.B.1` | Explore | **Feature Specs Overview** — Catalog all 15 feature specifications | `specs/` directory | Spec inventory, completion status |
| `6.B.2` | Explore | **Contract Quality Analysis** — Review spec contract quality across features | `specs/*/contracts/*.md` | Contract clarity, implementation alignment |
| `6.B.3` | Explore | **TASKS.md Analysis** — Review active task tracking accuracy | `TASKS.md` | Task relevance, completion accuracy |
| `6.B.4` | Explore | **AUDIT_REPORT.md Review** — Analyze previous audit findings and resolutions | `AUDIT_REPORT.md` | Resolution verification, recurring issues |
| `6.B.5` | Explore | **Roadmap & Ideas Analysis** — Review future plans, prioritization | `docs/guides/roadmap.md`, `specs/ideas.md` | Roadmap coherence, feasibility |

---

## Phase 7: Samples & Integration Analysis

**Objective**: Verify all sample configurations render correctly and follow best practices.

**Batch Execution**: 15 tasks in 3 sub-batches

### Batch 7.A — Core Samples (5 parallel agents)

| Task ID | Agent Type | Description | Target Files/Dirs | Output Expected |
|---------|-----------|-------------|-------------------|-----------------|
| `7.A.1` | Explore | **Default Sample Analysis** — Review minimal Python + Fumadocs sample | `samples/default/` | Configuration validity, minimal viable setup |
| `7.A.2` | Explore | **API Python Sample Analysis** — Analyze FastAPI sample configuration | `samples/api-python/` | API scaffold quality, best practices |
| `7.A.3` | Explore | **API Monorepo Sample Analysis** — Review Python + Node monorepo sample | `samples/api-monorepo/` | Monorepo structure quality |
| `7.A.4` | Explore | **CLI-Docs Sample Analysis** — Analyze Typer CLI with documentation | `samples/cli-docs/` | CLI scaffold quality, docs integration |
| `7.A.5` | Explore | **Full-Stack Sample Analysis** — Review all-modules-enabled strict profile | `samples/full-stack/` | Complete integration, strict compliance |

### Batch 7.B — Changelog & Docs Samples (5 parallel agents)

| Task ID | Agent Type | Description | Target Files/Dirs | Output Expected |
|---------|-----------|-------------|-------------------|-----------------|
| `7.B.1` | Explore | **Changelog Python Sample Analysis** — Review changelog + release sample | `samples/changelog-python/` | Changelog integration quality |
| `7.B.2` | Explore | **Changelog Monorepo Sample Analysis** — Analyze monorepo + changelog | `samples/changelog-monorepo/` | Multi-package changelog handling |
| `7.B.3` | Explore | **Changelog Full-Stack Sample Analysis** — Review full stack + changelog | `samples/changelog-full-stack/` | Complete release automation |
| `7.B.4` | Explore | **Docs Samples Cross-Analysis** — Compare Fumadocs/Sphinx/Docusaurus samples | `samples/docs-fumadocs/`, `samples/docs-sphinx/`, `samples/docs-docusaurus/` | Doc framework parity, quality comparison |
| `7.B.5` | Explore | **Copier Answers Consistency Check** — Verify all .copier-answers.yml files | All `samples/*/.copier-answers.yml` | Answer consistency, reproducibility |

### Batch 7.C — SaaS Samples (5 parallel agents)

| Task ID | Agent Type | Description | Target Files/Dirs | Output Expected |
|---------|-----------|-------------|-------------------|-----------------|
| `7.C.1` | Explore | **SaaS All-in-One Analysis** — Review comprehensive SaaS starter | `samples/saas-starter/all-in-one/` | Feature completeness |
| `7.C.2` | Explore | **SaaS Edge-Optimized Analysis** — Analyze Cloudflare/edge-focused variant | `samples/saas-starter/edge-optimized/` | Edge deployment quality |
| `7.C.3` | Explore | **SaaS Enterprise-Ready Analysis** — Review enterprise (WorkOS) variant | `samples/saas-starter/enterprise-ready/` | Enterprise feature completeness |
| `7.C.4` | Explore | **SaaS Next.js Variants Analysis** — Compare Next.js-based SaaS samples | `samples/saas-starter/nextjs-*` | Next.js scaffold quality, variant differences |
| `7.C.5` | Explore | **SaaS Remix Variant Analysis** — Analyze Remix + Cloudflare variant | `samples/saas-starter/remix-cloudflare-*` | Remix scaffold quality, Cloudflare integration |

---

## Phase 8: Cross-Cutting Concerns & Synthesis

**Objective**: Perform holistic analysis across the entire codebase, synthesize findings, and produce actionable recommendations.

**Batch Execution**: 35 tasks in 7 sub-batches (this is the largest phase)

### Batch 8.A — Security Analysis (5 parallel agents)

| Task ID | Agent Type | Description | Target Files/Dirs | Output Expected |
|---------|-----------|-------------|-------------------|-----------------|
| `8.A.1` | Explore | **Secrets & Credential Exposure Audit** — Scan for hardcoded secrets, credential patterns | Entire codebase | Security findings, exposure risks |
| `8.A.2` | Explore | **Input Validation Analysis** — Review user input handling in hooks and scripts | `template/hooks/`, `scripts/` | Injection vulnerabilities |
| `8.A.3` | Explore | **Path Traversal Risk Assessment** — Check file path handling for traversal risks | All file-handling code | Path security issues |
| `8.A.4` | Explore | **Subprocess Security Review** — Analyze shell command execution patterns | All subprocess calls | Command injection risks |
| `8.A.5` | Explore | **Dependency Vulnerability Deep Scan** — Cross-reference deps with CVE databases | All dependency files | Known vulnerability report |

### Batch 8.B — Performance & Efficiency (5 parallel agents)

| Task ID | Agent Type | Description | Target Files/Dirs | Output Expected |
|---------|-----------|-------------|-------------------|-----------------|
| `8.B.1` | Explore | **Template Rendering Performance** — Analyze Jinja rendering complexity | All `.jinja` files | Complexity hotspots, optimization opportunities |
| `8.B.2` | Explore | **CI Pipeline Efficiency Analysis** — Review workflow execution efficiency | All workflow files | Runtime optimization recommendations |
| `8.B.3` | Explore | **File I/O Pattern Analysis** — Review file reading/writing efficiency | Scripts and hooks | I/O optimization opportunities |
| `8.B.4` | Explore | **Memory Usage Pattern Analysis** — Check for memory-inefficient patterns | All Python files | Memory optimization recommendations |
| `8.B.5` | Explore | **Parallelization Opportunities** — Identify serial operations that could parallelize | All scripts | Parallelization recommendations |

### Batch 8.C — Code Quality Deep Dive (5 parallel agents)

| Task ID | Agent Type | Description | Target Files/Dirs | Output Expected |
|---------|-----------|-------------|-------------------|-----------------|
| `8.C.1` | Explore | **Cyclomatic Complexity Analysis** — Identify high-complexity functions | All Python files | Complexity report, refactoring candidates |
| `8.C.2` | Explore | **Code Duplication Detection** — Find duplicated code patterns | Entire codebase | Duplication report, DRY violations |
| `8.C.3` | Explore | **Dead Code Detection** — Identify unused functions, imports, variables | All Python files | Dead code inventory |
| `8.C.4` | Explore | **Error Handling Pattern Analysis** — Review exception handling consistency | All Python files | Exception handling quality report |
| `8.C.5` | Explore | **Type Annotation Completeness** — Audit type hint coverage | All Python files | Type coverage metrics, gaps |

### Batch 8.D — Consistency & Standards (5 parallel agents)

| Task ID | Agent Type | Description | Target Files/Dirs | Output Expected |
|---------|-----------|-------------|-------------------|-----------------|
| `8.D.1` | Explore | **Cross-Module API Consistency** — Verify function signatures follow patterns | All scripts | API consistency report |
| `8.D.2` | Explore | **Configuration Schema Consistency** — Check config file schema patterns | All YAML/JSON configs | Schema consistency report |
| `8.D.3` | Explore | **Logging Pattern Consistency** — Review logging usage and formats | All Python files | Logging standardization recommendations |
| `8.D.4` | Explore | **Comment & Docstring Quality** — Analyze documentation in code | All Python files | Documentation quality metrics |
| `8.D.5` | Explore | **Magic Numbers & Constants Audit** — Find hardcoded values needing extraction | All code files | Constants extraction recommendations |

### Batch 8.E — Maintainability Assessment (5 parallel agents)

| Task ID | Agent Type | Description | Target Files/Dirs | Output Expected |
|---------|-----------|-------------|-------------------|-----------------|
| `8.E.1` | Explore | **Module Coupling Analysis** — Measure inter-module dependencies | All Python files | Coupling metrics, dependency graph |
| `8.E.2` | Explore | **Test Maintainability Review** — Assess test code quality and clarity | All test files | Test maintainability score |
| `8.E.3` | Explore | **Configuration Sprawl Assessment** — Identify config file proliferation | All config files | Config consolidation recommendations |
| `8.E.4` | Explore | **Versioning & Compatibility Analysis** — Review version handling patterns | `pyproject.toml`, copier.yml | Versioning strategy assessment |
| `8.E.5` | Explore | **Deprecation Pattern Review** — Check for deprecated pattern usage | All code files | Deprecation warnings, migration needs |

### Batch 8.F — Feature Completeness (5 parallel agents)

| Task ID | Agent Type | Description | Target Files/Dirs | Output Expected |
|---------|-----------|-------------|-------------------|-----------------|
| `8.F.1` | Explore | **Module Feature Parity Check** — Verify all 13 modules implement features consistently | Template files for all modules | Feature parity matrix |
| `8.F.2` | Explore | **Quality Profile Feature Parity** — Confirm standard/strict profiles complete | All profile-conditional code | Profile completeness report |
| `8.F.3` | Explore | **Language Track Feature Parity** — Compare Python vs Node.js feature coverage | `template/files/python/`, `template/files/node/` | Language parity report |
| `8.F.4` | Explore | **Documentation Framework Parity** — Compare Fumadocs/Sphinx/Docusaurus features | All docs templates | Docs framework comparison |
| `8.F.5` | Explore | **CI/CD Feature Completeness** — Verify all workflows cover all scenarios | All workflow templates | CI/CD coverage matrix |

### Batch 8.G — Synthesis & Recommendations (5 parallel agents)

| Task ID | Agent Type | Description | Target Files/Dirs | Output Expected |
|---------|-----------|-------------|-------------------|-----------------|
| `8.G.1` | Plan | **Architecture Recommendations Synthesis** — Compile architectural improvements | Phase 1-7 outputs | Architecture recommendations document |
| `8.G.2` | Plan | **Security Recommendations Synthesis** — Compile security improvements | Phase 8.A outputs | Security hardening plan |
| `8.G.3` | Plan | **Performance Recommendations Synthesis** — Compile performance improvements | Phase 8.B outputs | Performance optimization roadmap |
| `8.G.4` | Plan | **Quality Recommendations Synthesis** — Compile quality improvements | Phase 8.C-8.E outputs | Quality improvement plan |
| `8.G.5` | Plan | **Prioritized Action Plan Generation** — Create prioritized fix/enhancement list | All phase outputs | Master action plan with priorities |

---

## Execution Strategy

### Parallel Batch Scheduling

```
Timeline (conceptual batches):

┌─────────────────────────────────────────────────────────────────────────┐
│ BATCH 0: Foundation (Phase 1)                                           │
│ 12 parallel agents → Baseline understanding                             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────┐
    │                               │                               │
    ▼                               ▼                               ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│ BATCH 1A:       │       │ BATCH 1B:       │       │ BATCH 1C:       │
│ Template Core   │       │ Scripts CI      │       │ Testing         │
│ (Phase 2A)      │       │ (Phase 3A)      │       │ (Phase 4A)      │
│ 5 agents        │       │ 5 agents        │       │ 5 agents        │
└────────┬────────┘       └────────┬────────┘       └────────┬────────┘
         │                         │                         │
    ┌────┴────┐               ┌────┴────┐               ┌────┴────┐
    ▼         ▼               ▼         ▼               ▼         ▼
┌──────┐ ┌──────┐       ┌──────┐ ┌──────┐       ┌──────┐ ┌──────┐
│2B    │ │2C    │       │3B    │ │3C    │       │4B    │ │4C    │
│Python│ │Node  │       │CI+   │ │Lib   │       │Tools │ │Fix   │
│5 agt │ │5 agt │       │5 agt │ │4 agt │       │4 agt │ │4 agt │
└──┬───┘ └──┬───┘       └──┬───┘ └──┬───┘       └──┬───┘ └──┬───┘
   │        │              │        │              │        │
   └────────┴──────┬───────┴────────┴──────────────┴────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ▼              ▼              ▼
┌─────────┐  ┌─────────┐  ┌─────────┐
│ BATCH 2:│  │ BATCH 3:│  │ BATCH 4:│
│ CI/CD   │  │ Docs    │  │ Samples │
│ (Ph 5)  │  │ (Ph 6)  │  │ (Ph 7)  │
│ 12 agt  │  │ 11 agt  │  │ 15 agt  │
└────┬────┘  └────┬────┘  └────┬────┘
     │            │            │
     └────────────┼────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ BATCH 3: Cross-Cutting & Synthesis (Phase 8)                            │
│ 35 agents in 7 sub-batches → Final analysis & recommendations           │
└─────────────────────────────────────────────────────────────────────────┘
```

### Agent Configuration Recommendations

```yaml
# Explore agents (research/analysis)
explore_agent:
  subagent_type: "Explore"
  thoroughness: "very thorough"  # For comprehensive analysis
  output: "detailed findings with file:line references"

# Plan agents (synthesis/recommendations)
plan_agent:
  subagent_type: "Plan"
  focus: "actionable recommendations"
  output: "prioritized improvement list"
```

### Execution Commands

For each batch, execute with parallel Task tool calls:

```
# Example: Execute Batch 1.A (6 parallel agents)
Task(subagent_type="Explore", description="Repository Layout Analysis", prompt="...")
Task(subagent_type="Explore", description="Git History Analysis", prompt="...")
Task(subagent_type="Explore", description="Dependency Audit", prompt="...")
Task(subagent_type="Explore", description="Config File Inventory", prompt="...")
Task(subagent_type="Explore", description="Entry Point Mapping", prompt="...")
Task(subagent_type="Explore", description="License Compliance", prompt="...")
```

---

## Output Artifacts

### Per-Phase Deliverables

| Phase | Primary Output | Format |
|-------|----------------|--------|
| 1 | Foundation Assessment Report | Markdown |
| 2 | Template System Analysis | Markdown + Diagrams |
| 3 | Scripts Audit Report | Markdown + Code Refs |
| 4 | Test Coverage & Quality Report | Markdown + Metrics |
| 5 | CI/CD Analysis Report | Markdown + Workflow Diagrams |
| 6 | Documentation Accuracy Report | Markdown + Checklist |
| 7 | Sample Validation Report | Markdown + Matrix |
| 8 | Comprehensive Findings & Action Plan | Markdown + Priority List |

### Final Synthesis Document

```markdown
# RISO Codebase Audit - Final Report

## Executive Summary
- Overall health score
- Critical findings count
- High-priority recommendations

## Section 1: Architecture Assessment
## Section 2: Security Findings
## Section 3: Performance Analysis
## Section 4: Code Quality Metrics
## Section 5: Test Coverage Analysis
## Section 6: Documentation Status
## Section 7: CI/CD Evaluation
## Section 8: Recommendations Matrix
## Section 9: Prioritized Action Items
## Appendix: Detailed Findings by Phase
```

---

## Quality Gates

### Phase Completion Criteria

Each phase must produce:
1. ✅ Complete findings for all assigned tasks
2. ✅ File:line references for all issues found
3. ✅ Severity classification (Critical/High/Medium/Low/Info)
4. ✅ Actionable recommendations where applicable
5. ✅ No blocking dependencies on incomplete prior phases

### Review Checkpoints

| Checkpoint | Trigger | Action |
|------------|---------|--------|
| Post-Phase 1 | Foundation complete | Validate baseline understanding before deep dives |
| Post-Phases 2-4 | Core analysis complete | Cross-check findings, identify patterns |
| Post-Phase 7 | All analysis complete | Prepare for synthesis |
| Post-Phase 8 | Synthesis complete | Final review and prioritization |

---

## Risk Mitigation

### Potential Issues & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Agent overlap/duplication | Medium | Low | Clear task boundaries, deduplication in synthesis |
| Missing context between agents | Medium | Medium | Comprehensive prompts with full context |
| False positives | Medium | Low | Human review of critical findings |
| Incomplete coverage | Low | High | Systematic task assignment with coverage tracking |
| Agent timeout | Low | Medium | Reasonable scope per agent, timeout handling |

---

## Appendix A: Task ID Quick Reference

```
Phase 1: 1.A.1-1.A.6, 1.B.1-1.B.6  (12 tasks)
Phase 2: 2.A.1-2.A.5, 2.B.1-2.B.5, 2.C.1-2.C.5  (15 tasks)
Phase 3: 3.A.1-3.A.5, 3.B.1-3.B.5, 3.C.1-3.C.4  (14 tasks)
Phase 4: 4.A.1-4.A.5, 4.B.1-4.B.4, 4.C.1-4.C.4  (13 tasks)
Phase 5: 5.A.1-5.A.6, 5.B.1-5.B.6  (12 tasks)
Phase 6: 6.A.1-6.A.6, 6.B.1-6.B.5  (11 tasks)
Phase 7: 7.A.1-7.A.5, 7.B.1-7.B.5, 7.C.1-7.C.5  (15 tasks)
Phase 8: 8.A.1-8.A.5, 8.B.1-8.B.5, 8.C.1-8.C.5, 8.D.1-8.D.5, 8.E.1-8.E.5, 8.F.1-8.F.5, 8.G.1-8.G.5  (35 tasks)

Total: 127 tasks
```

---

## Appendix B: Detailed Agent Prompts

For each task, use prompts following this template:

```
You are analyzing the RISO codebase - a Copier-based project template system.

**Task**: [Task Description]
**Scope**: [Target Files/Directories]
**Thoroughness**: very thorough

**Analysis Requirements**:
1. [Specific analysis point 1]
2. [Specific analysis point 2]
3. [Specific analysis point 3]

**Output Format**:
- Provide findings with file:line references
- Classify severity: Critical/High/Medium/Low/Info
- Include actionable recommendations
- Note any blockers or dependencies

**Context**: This is part of a comprehensive codebase audit (Task [ID] of 127).
```

---

*Plan Version: 1.0*
*Generated: 2026-01-06*
*Target Codebase: RISO v0.1.0-alpha*
