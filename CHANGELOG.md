# Changelog

All notable changes to the Riso project template will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## <small>1.1.2 (2026-01-15)</small>

* fix(web): fix trailing whitespace in lib files ([59950a3](https://github.com/wyattowalsh/riso/commit/59950a3))

## <small>1.1.1 (2026-01-15)</small>

* fix(pre-commit): exclude web/public/docs/ from formatting hooks ([e22bd2f](https://github.com/wyattowalsh/riso/commit/e22bd2f))

## 1.1.0 (2026-01-15)

* feat(web): include pre-built Sphinx docs for Vercel deployment ([1695b51](https://github.com/wyattowalsh/riso/commit/1695b51))

## <small>1.0.3 (2026-01-15)</small>

* fix(web/api): switch MCP endpoint to Node.js runtime ([e9fa9d5](https://github.com/wyattowalsh/riso/commit/e9fa9d5))
* fix(web): add web/src/lib directory to git for Vercel deployment ([bf9930c](https://github.com/wyattowalsh/riso/commit/bf9930c))

## <small>1.0.2 (2026-01-15)</small>

* fix(web): add matrix-data.json for Vercel deployment ([2912eae](https://github.com/wyattowalsh/riso/commit/2912eae))

## <small>1.0.1 (2026-01-15)</small>

* fix(web): correct matrix data import path in MCP API endpoint ([7d8195e](https://github.com/wyattowalsh/riso/commit/7d8195e))

## 1.0.0 (2026-01-15)

* fix(ci): add missing newlines and make ty check non-blocking ([6ab52a9](https://github.com/wyattowalsh/riso/commit/6ab52a9))
* fix(ci): exclude conflicting file types from jinja validation and make scripts executable ([87ec9fe](https://github.com/wyattowalsh/riso/commit/87ec9fe))
* fix(ci): fix jinja template validator undefined parameter ([a6d6399](https://github.com/wyattowalsh/riso/commit/a6d6399))
* fix(ci): make all scripts with shebangs executable ([8e3b86c](https://github.com/wyattowalsh/riso/commit/8e3b86c))
* fix(ci): resolve pre-commit and release workflow failures ([48e59f0](https://github.com/wyattowalsh/riso/commit/48e59f0))
* fix(ci): resolve pre-commit and release workflow failures ([5149f5b](https://github.com/wyattowalsh/riso/commit/5149f5b))
* fix(ci): resolve pre-commit and test failures ([001cb71](https://github.com/wyattowalsh/riso/commit/001cb71))
* fix(ci): resolve workflow failures ([108e1f3](https://github.com/wyattowalsh/riso/commit/108e1f3))
* fix(ci): upgrade Node.js to 22 for semantic-release v25 compatibility ([57de4f8](https://github.com/wyattowalsh/riso/commit/57de4f8))
* fix(mcp): update test path and add missing runtime deps ([dbcd5dd](https://github.com/wyattowalsh/riso/commit/dbcd5dd))
* fix: resolve 7 critical issues from codebase audit ([238d358](https://github.com/wyattowalsh/riso/commit/238d358))
* fix(security): add concurrency controls to prevent overlapping runs [SEC-004] ([0ee7a1b](https://github.com/wyattowalsh/riso/commit/0ee7a1b))
* fix(security): add URL validation for variant names [SEC-008] ([c45a765](https://github.com/wyattowalsh/riso/commit/c45a765))
* fix(security): add validation for environment-loaded config values [SEC-005] ([9f421fd](https://github.com/wyattowalsh/riso/commit/9f421fd))
* fix(security): fix file handle resource leak in hadolint execution [SEC-007] ([b06edd3](https://github.com/wyattowalsh/riso/commit/b06edd3))
* fix(security): pin trivy-action to stable version [SEC-002] ([4c8cc5e](https://github.com/wyattowalsh/riso/commit/4c8cc5e))
* fix(security): replace curl|sh with official uv action [SEC-003] ([7989121](https://github.com/wyattowalsh/riso/commit/7989121))
* fix(security): use yaml.safe_load instead of manual parsing [SEC-006] ([3af4363](https://github.com/wyattowalsh/riso/commit/3af4363))
* fix(security): validate COPIER_CMD to prevent command injection [SEC-001] ([5c6761a](https://github.com/wyattowalsh/riso/commit/5c6761a))
* style: apply ruff format to Python files ([f9832f6](https://github.com/wyattowalsh/riso/commit/f9832f6))
* feat(005): Add container & deployment feature specification ([b711991](https://github.com/wyattowalsh/riso/commit/b711991))
* feat(005): Complete container deployment implementation ([6c7ddae](https://github.com/wyattowalsh/riso/commit/6c7ddae))
* feat: Add automated changelog and release management ([d3ec078](https://github.com/wyattowalsh/riso/commit/d3ec078))
* feat: add comprehensive API versioning strategy specification ([5611ba1](https://github.com/wyattowalsh/riso/commit/5611ba1))
* feat: add comprehensive pre-commit stack with security and quality hooks ([7a7084d](https://github.com/wyattowalsh/riso/commit/7a7084d))
* feat: add comprehensive production readiness requirements checklist ([69bfce7](https://github.com/wyattowalsh/riso/commit/69bfce7))
* feat: Add comprehensive SaaS starter template enhancements ([ae36ac6](https://github.com/wyattowalsh/riso/commit/ae36ac6))
* feat: add FastAPI API scaffold specification ([cc3a7c9](https://github.com/wyattowalsh/riso/commit/cc3a7c9))
* feat: add FastAPI scaffold implementation plan (Phase 0 & 1) ([865d037](https://github.com/wyattowalsh/riso/commit/865d037))
* feat: add FastAPI scaffold task breakdown (Phase 2) ([2795e65](https://github.com/wyattowalsh/riso/commit/2795e65))
* feat: add GitHub Actions CI/CD workflows specification ([3a38921](https://github.com/wyattowalsh/riso/commit/3a38921))
* feat: add GitHub Actions CI/CD workflows specification ([a277c91](https://github.com/wyattowalsh/riso/commit/a277c91))
* feat: Add GraphQL API module with Strawberry ([2fe9942](https://github.com/wyattowalsh/riso/commit/2fe9942))
* feat: Add Next.js 16 and Remix 2.x base templates ([8fb808e](https://github.com/wyattowalsh/riso/commit/8fb808e))
* feat: Add SaaS starter module and configurations ([ccaf1dc](https://github.com/wyattowalsh/riso/commit/ccaf1dc))
* feat: Add SaaS starter template and CI/CD configurations ([77abe54](https://github.com/wyattowalsh/riso/commit/77abe54))
* feat: Add WebSocket real-time communication module ([2435e0c](https://github.com/wyattowalsh/riso/commit/2435e0c))
* feat: complete code quality integration suite (003) ([69644b8](https://github.com/wyattowalsh/riso/commit/69644b8))
* feat: complete code quality integration suite with uv run enforcement ([228b112](https://github.com/wyattowalsh/riso/commit/228b112))
* feat: complete GitHub Actions CI/CD workflows (004) ([64eaf18](https://github.com/wyattowalsh/riso/commit/64eaf18))
* feat: Configure SaaS starter samples and generate config files ([06e5dab](https://github.com/wyattowalsh/riso/commit/06e5dab))
* feat: ensure smoke-results.json generation for samples [FEAT-001] ([76f125d](https://github.com/wyattowalsh/riso/commit/76f125d))
* feat: Implement core SaaS integrations ([bfc0799](https://github.com/wyattowalsh/riso/commit/bfc0799))
* feat: Introduce expanded documentation template options with Fumadocs, Sphinx Shibuya, and Docusauru ([e50d462](https://github.com/wyattowalsh/riso/commit/e50d462))
* feat(mcp): add comprehensive MCP integration for project and templates ([edd1b26](https://github.com/wyattowalsh/riso/commit/edd1b26))
* feat(release): add comprehensive SDLC tooling stack ([68e3832](https://github.com/wyattowalsh/riso/commit/68e3832))
* feat: replace mypy with ty as default Python type checker ([5f44fb0](https://github.com/wyattowalsh/riso/commit/5f44fb0))
* feat(setup): add comprehensive cross-platform setup scripts ([452a18e](https://github.com/wyattowalsh/riso/commit/452a18e))
* feat(spec): create 015-codegen-scaffolding-tools specification ([98158dc](https://github.com/wyattowalsh/riso/commit/98158dc))
* feat: Update WebSocket scaffold specification and add task breakdown ([c0e305d](https://github.com/wyattowalsh/riso/commit/c0e305d))
* feat: upgrade tooling versions and add strict commit-msg policy ([4f1c8b4](https://github.com/wyattowalsh/riso/commit/4f1c8b4))
* feat(web): add MCP server endpoint and UI polish ([6757e5d](https://github.com/wyattowalsh/riso/commit/6757e5d))
* chore: add development dependency groups [CFG-003] ([42dbf53](https://github.com/wyattowalsh/riso/commit/42dbf53))
* chore: add missing quality scaffolding files after merge ([902d763](https://github.com/wyattowalsh/riso/commit/902d763))
* chore(ci): add actionlint workflow validation [CI-004] ([2b21b57](https://github.com/wyattowalsh/riso/commit/2b21b57))
* chore(ci): add Dependabot configuration for dependency updates [CI-005] ([39cf554](https://github.com/wyattowalsh/riso/commit/39cf554))
* chore(ci): add if-no-files-found to artifact uploads [CI-002] ([7811f83](https://github.com/wyattowalsh/riso/commit/7811f83))
* chore(ci): add pip-audit security scanning [CI-006] ([6a39200](https://github.com/wyattowalsh/riso/commit/6a39200))
* chore(ci): update GitHub Actions to latest versions [CI-001] ([4de844d](https://github.com/wyattowalsh/riso/commit/4de844d))
* chore: finalize matrix integration updates ([c9dc87e](https://github.com/wyattowalsh/riso/commit/c9dc87e))
* chore: sync matrix data and template updates ([aa1c46d](https://github.com/wyattowalsh/riso/commit/aa1c46d))
* chore: update pyproject.toml with proper metadata [CFG-001] ([fc67af2](https://github.com/wyattowalsh/riso/commit/fc67af2))
* chore: update workflow and saas templates ([3fec16d](https://github.com/wyattowalsh/riso/commit/3fec16d))
* docs(005): Add clarification session with 3 critical decisions ([af5dc3b](https://github.com/wyattowalsh/riso/commit/af5dc3b))
* docs(005): Complete implementation plan with research and data model ([3f52a14](https://github.com/wyattowalsh/riso/commit/3f52a14))
* docs(005): Complete Phase 2 with task breakdown ([f940219](https://github.com/wyattowalsh/riso/commit/f940219))
* docs: add API documentation for scripts [DOC-004] ([d5481be](https://github.com/wyattowalsh/riso/commit/d5481be))
* docs: add comprehensive edge cases, testing strategy, and tooling compatibility specifications ([fc26484](https://github.com/wyattowalsh/riso/commit/fc26484))
* docs: add comprehensive gap resolution summary - 270/270 gaps addressed (100%) ([72fa2f3](https://github.com/wyattowalsh/riso/commit/72fa2f3))
* docs: add contributing guidelines [DOC-005] ([bd631b1](https://github.com/wyattowalsh/riso/commit/bd631b1))
* docs: add exhaustive codebase review plan for parallel subagent execution ([9ba701e](https://github.com/wyattowalsh/riso/commit/9ba701e))
* docs: add WebSocket scaffold specification (008-websockets-scaffold) ([15fe6d5](https://github.com/wyattowalsh/riso/commit/15fe6d5))
* docs: complete project constitution with governance principles [DOC-002] ([acd57bb](https://github.com/wyattowalsh/riso/commit/acd57bb))
* docs: expand README with comprehensive documentation [DOC-001] ([0eee01f](https://github.com/wyattowalsh/riso/commit/0eee01f))
* docs(matrix): add SSOT documentation and workflow permissions ([c470589](https://github.com/wyattowalsh/riso/commit/c470589))
* Add comprehensive E2E audit report ([484e080](https://github.com/wyattowalsh/riso/commit/484e080))
* Add comprehensive features and specifications roadmap for Riso v2.0 ([4df5785](https://github.com/wyattowalsh/riso/commit/4df5785))
* Add comprehensive next features roadmap and implementation guide ([8990d83](https://github.com/wyattowalsh/riso/commit/8990d83))
* Add comprehensive security requirements to 015-codegen-scaffolding-tools ([7b69e06](https://github.com/wyattowalsh/riso/commit/7b69e06))
* Add comprehensive task list optimized for Claude Code subagents ([8054b84](https://github.com/wyattowalsh/riso/commit/8054b84))
* Add comprehensive tests and documentation ([f244c00](https://github.com/wyattowalsh/riso/commit/f244c00))
* Add documentation variant expansion spec ([7ffaf88](https://github.com/wyattowalsh/riso/commit/7ffaf88))
* Add quality validation and test fixtures ([5d401a1](https://github.com/wyattowalsh/riso/commit/5d401a1))
* Add quick reference guide and update README with roadmap links ([be1757d](https://github.com/wyattowalsh/riso/commit/be1757d))
* Changes before error encountered ([1a93dda](https://github.com/wyattowalsh/riso/commit/1a93dda))
* Complete Phase 1 planning for 015-codegen-scaffolding-tools ([dc38cb4](https://github.com/wyattowalsh/riso/commit/dc38cb4))
* Complete refactoring and feature tasks from audit ([6c8e5b3](https://github.com/wyattowalsh/riso/commit/6c8e5b3))
* cursor speckit command scaffolds ([57bd49f](https://github.com/wyattowalsh/riso/commit/57bd49f))
* deps(actions)(deps): bump the actions group with 3 updates ([f906183](https://github.com/wyattowalsh/riso/commit/f906183))
* Document Phase 1 completion in plan.md ([671034b](https://github.com/wyattowalsh/riso/commit/671034b))
* Elite enhancements: Add performance, validation, plugins, and recovery utilities ([c3c9460](https://github.com/wyattowalsh/riso/commit/c3c9460))
* fax dat ([9e51f63](https://github.com/wyattowalsh/riso/commit/9e51f63))
* Final enhancements: Implement scaffold info, add CLI entry point, improve exports ([87aa293](https://github.com/wyattowalsh/riso/commit/87aa293))
* Final excellence pass: Add async support, example template, and comprehensive guides ([6322ca2](https://github.com/wyattowalsh/riso/commit/6322ca2))
* Fix analysis issues in 015-codegen-scaffolding-tools ([b262d8f](https://github.com/wyattowalsh/riso/commit/b262d8f))
* Generate task breakdown for 015-codegen-scaffolding-tools ([f300f1d](https://github.com/wyattowalsh/riso/commit/f300f1d))
* Implement Riso template foundation ([7a47f58](https://github.com/wyattowalsh/riso/commit/7a47f58))
* Initial commit ([6f5a98b](https://github.com/wyattowalsh/riso/commit/6f5a98b))
* Initial plan ([7b9b1c8](https://github.com/wyattowalsh/riso/commit/7b9b1c8))
* Initial plan ([103b1d8](https://github.com/wyattowalsh/riso/commit/103b1d8))
* ketchup ([53942b4](https://github.com/wyattowalsh/riso/commit/53942b4))
* ketchup ([00f09de](https://github.com/wyattowalsh/riso/commit/00f09de))
* Merge branch '003-code-quality-integrations' ([dd24f84](https://github.com/wyattowalsh/riso/commit/dd24f84))
* Merge branch '010-api-versioning-strategy' ([8674f63](https://github.com/wyattowalsh/riso/commit/8674f63))
* Merge branch '015-codegen-scaffolding-tools' ([b448857](https://github.com/wyattowalsh/riso/commit/b448857))
* Merge branch 'claude/codebase-review-plan-nWkZs' into main ([af0c424](https://github.com/wyattowalsh/riso/commit/af0c424))
* Merge branch 'main' into 008-websockets-scaffold ([8aef0b1](https://github.com/wyattowalsh/riso/commit/8aef0b1))
* Merge branch 'main' into 012-saas-starter ([015867a](https://github.com/wyattowalsh/riso/commit/015867a))
* Merge branch 'main' into 014-changelog-release-management ([d96ca58](https://github.com/wyattowalsh/riso/commit/d96ca58))
* Merge branch 'main' into 015-codegen-scaffolding-tools ([1efc4e1](https://github.com/wyattowalsh/riso/commit/1efc4e1))
* Merge branch 'main' of https://github.com/wyattowalsh/riso ([91aee6d](https://github.com/wyattowalsh/riso/commit/91aee6d))
* Merge branch 'main' of https://github.com/wyattowalsh/riso ([4408fd1](https://github.com/wyattowalsh/riso/commit/4408fd1))
* Merge feature 004: GitHub Actions CI/CD workflows ([b5ce645](https://github.com/wyattowalsh/riso/commit/b5ce645))
* Merge feature 005: Container & Deployment Support ([91bc3ec](https://github.com/wyattowalsh/riso/commit/91bc3ec))
* Merge feature 009-typer-cli-scaffold into main ([630465d](https://github.com/wyattowalsh/riso/commit/630465d))
* Merge feature: Code Quality Integration Suite ([7d4c984](https://github.com/wyattowalsh/riso/commit/7d4c984))
* Merge pull request #15 from wyattowalsh/cursor/implement-saas-starter-project-with-advanced-techniqu ([e3f5a78](https://github.com/wyattowalsh/riso/commit/e3f5a78)), closes [#15](https://github.com/wyattowalsh/riso/issues/15)
* Merge pull request #16 from wyattowalsh/012-saas-starter ([2434239](https://github.com/wyattowalsh/riso/commit/2434239)), closes [#16](https://github.com/wyattowalsh/riso/issues/16)
* Merge pull request #17 from wyattowalsh/cursor/implement-changelog-and-release-management-08e3 ([ffafe13](https://github.com/wyattowalsh/riso/commit/ffafe13)), closes [#17](https://github.com/wyattowalsh/riso/issues/17)
* Merge pull request #18 from wyattowalsh/014-changelog-release-management ([47345e8](https://github.com/wyattowalsh/riso/commit/47345e8)), closes [#18](https://github.com/wyattowalsh/riso/issues/18)
* Merge pull request #19 from wyattowalsh/copilot/implement-codegen-scaffolding-tools ([6be5415](https://github.com/wyattowalsh/riso/commit/6be5415)), closes [#19](https://github.com/wyattowalsh/riso/issues/19)
* Merge pull request #2 from wyattowalsh/copilot/add-next-features-specs ([744b17c](https://github.com/wyattowalsh/riso/commit/744b17c)), closes [#2](https://github.com/wyattowalsh/riso/issues/2)
* Merge pull request #21 from wyattowalsh/015-codegen-scaffolding-tools ([3844a4a](https://github.com/wyattowalsh/riso/commit/3844a4a)), closes [#21](https://github.com/wyattowalsh/riso/issues/21)
* Merge pull request #23 from wyattowalsh/codex/refactor-and-update-root-dev-docs-site ([47d76b7](https://github.com/wyattowalsh/riso/commit/47d76b7)), closes [#23](https://github.com/wyattowalsh/riso/issues/23)
* Merge pull request #24 from wyattowalsh/claude/audit-riso-e2e-vrTcc ([103b651](https://github.com/wyattowalsh/riso/commit/103b651)), closes [#24](https://github.com/wyattowalsh/riso/issues/24)
* Merge pull request #25 from wyattowalsh/dependabot/github_actions/actions-b5b051dfbe ([2dc26c2](https://github.com/wyattowalsh/riso/commit/2dc26c2)), closes [#25](https://github.com/wyattowalsh/riso/issues/25)
* Merge pull request #26 from wyattowalsh/claude/codebase-review-plan-nWkZs ([4dbc1ef](https://github.com/wyattowalsh/riso/commit/4dbc1ef)), closes [#26](https://github.com/wyattowalsh/riso/issues/26)
* Merge pull request #27 from wyattowalsh/claude/codebase-review-plan-nWkZs ([ad71183](https://github.com/wyattowalsh/riso/commit/ad71183)), closes [#27](https://github.com/wyattowalsh/riso/issues/27)
* Merge pull request #4 from wyattowalsh/cursor/implement-fastapi-api-scaffold-tasks-b1a6 ([b80a07f](https://github.com/wyattowalsh/riso/commit/b80a07f)), closes [#4](https://github.com/wyattowalsh/riso/issues/4)
* Merge pull request #5 from wyattowalsh/006-fastapi-api-scaffold ([767e799](https://github.com/wyattowalsh/riso/commit/767e799)), closes [#5](https://github.com/wyattowalsh/riso/issues/5)
* Merge pull request #6 from wyattowalsh/cursor/implement-graphql-api-scaffold-from-specs-4f1c ([1032d69](https://github.com/wyattowalsh/riso/commit/1032d69)), closes [#6](https://github.com/wyattowalsh/riso/issues/6)
* Merge pull request #7 from wyattowalsh/007-graphql-api-scaffold ([0a80ace](https://github.com/wyattowalsh/riso/commit/0a80ace)), closes [#7](https://github.com/wyattowalsh/riso/issues/7)
* Merge pull request #8 from wyattowalsh/cursor/implement-websocket-scaffold-and-tasks-cc6e ([8018c67](https://github.com/wyattowalsh/riso/commit/8018c67)), closes [#8](https://github.com/wyattowalsh/riso/issues/8)
* Merge pull request #9 from wyattowalsh/008-websockets-scaffold ([bb2096b](https://github.com/wyattowalsh/riso/commit/bb2096b)), closes [#9](https://github.com/wyattowalsh/riso/issues/9)
* mr potatoe ([a2008fa](https://github.com/wyattowalsh/riso/commit/a2008fa))
* Phase 1 & 2: Setup directory structure and core data models ([bf106ff](https://github.com/wyattowalsh/riso/commit/bf106ff))
* Phase 2 infrastructure: Engine, loaders, cache, validator, and CLI skeleton ([5e2c2a1](https://github.com/wyattowalsh/riso/commit/5e2c2a1))
* Phase 3: Core generation implementation (US1 MVP) ([5bf61cc](https://github.com/wyattowalsh/riso/commit/5bf61cc))
* Phase 4 (US2): Implement module addition functionality ([25cabc1](https://github.com/wyattowalsh/riso/commit/25cabc1))
* Phase 6 (US4): Implement template updates with three-way merge ([bdf6dfd](https://github.com/wyattowalsh/riso/commit/bdf6dfd))
* Phase 8: Implement cache and config commands ([151edd4](https://github.com/wyattowalsh/riso/commit/151edd4))
* Phase 9: Final polish - documentation and README ([0cc3527](https://github.com/wyattowalsh/riso/commit/0cc3527))
* Reinforce coverage enforcement in Shibuya docs ([0757c5e](https://github.com/wyattowalsh/riso/commit/0757c5e))
* relishhh 🥒 ([340ea9f](https://github.com/wyattowalsh/riso/commit/340ea9f))
* Scaffold documentation variants and automation hooks ([db5b910](https://github.com/wyattowalsh/riso/commit/db5b910))
* Update GitHub Sponsors username in FUNDING.yml ([66b76b5](https://github.com/wyattowalsh/riso/commit/66b76b5))
* Update ideas.md with spec 015 as highest priority (4.9) ([6d723e8](https://github.com/wyattowalsh/riso/commit/6d723e8))
* yeet ([57cee4c](https://github.com/wyattowalsh/riso/commit/57cee4c))
* test: add integration tests for template rendering [TEST-010] ([db24545](https://github.com/wyattowalsh/riso/commit/db24545))
* test: add pytest and coverage configuration [TEST-001] ([c86e9ff](https://github.com/wyattowalsh/riso/commit/c86e9ff))
* test: add unit tests for pre_gen_project hook [TEST-004] ([fe08a21](https://github.com/wyattowalsh/riso/commit/fe08a21))
* test: add unit tests for quality_tool_check [TEST-009] ([40a524d](https://github.com/wyattowalsh/riso/commit/40a524d))
* test: add unit tests for record_module_success [TEST-005] ([d448eec](https://github.com/wyattowalsh/riso/commit/d448eec))
* test: add unit tests for render_matrix [TEST-008] ([9b5d568](https://github.com/wyattowalsh/riso/commit/9b5d568))
* test: add unit tests for validate_dockerfiles [TEST-006] ([27f6698](https://github.com/wyattowalsh/riso/commit/27f6698))
* test: add unit tests for validate_release_configs [TEST-003] ([1667186](https://github.com/wyattowalsh/riso/commit/1667186))
* test: add unit tests for validate_workflows [TEST-007] ([948ee45](https://github.com/wyattowalsh/riso/commit/948ee45))
* test: create test directory structure and fixtures [TEST-002] ([39db422](https://github.com/wyattowalsh/riso/commit/39db422))
* test: expand automation and hook coverage ([99a2503](https://github.com/wyattowalsh/riso/commit/99a2503))
* refactor: extract common environment loading logic [REF-001] ([8b407f3](https://github.com/wyattowalsh/riso/commit/8b407f3))
* refactor: normalize type hints to modern Python style [REF-003] ([adc5291](https://github.com/wyattowalsh/riso/commit/adc5291))
* refactor: renumber FastAPI scaffold to 006 and remove monitoring spec ([cd3e05c](https://github.com/wyattowalsh/riso/commit/cd3e05c))
* refactor: use specific exception types instead of broad Exception [REF-002] ([946c778](https://github.com/wyattowalsh/riso/commit/946c778))
* Final: Complete implementation summary and wrap-up ([c0560ea](https://github.com/wyattowalsh/riso/commit/c0560ea))
* clarify: answer 5 key questions for codegen scaffolding tools ([cb948b7](https://github.com/wyattowalsh/riso/commit/cb948b7))
* clarify: resolve 5 critical ambiguities in API versioning spec ([7ab5156](https://github.com/wyattowalsh/riso/commit/7ab5156))
* contracts: complete OpenAPI spec - address all 58 API contract gaps ([61998a4](https://github.com/wyattowalsh/riso/commit/61998a4))
* contracts: enhance OpenAPI spec with security, validation, and comprehensive error handling ([0ff4762](https://github.com/wyattowalsh/riso/commit/0ff4762))
* spec: address critical gaps - add security, performance, and observability requirements ([8104208](https://github.com/wyattowalsh/riso/commit/8104208))
* checklists: add consolidated gap analysis summary ([dd8678c](https://github.com/wyattowalsh/riso/commit/dd8678c))
* checklists: add focused security, performance, and API contract checklists ([19acc1e](https://github.com/wyattowalsh/riso/commit/19acc1e)), closes [hi#level](https://github.com/hi/issues/level)
* checklist: generate comprehensive QA requirements quality checklist ([7435918](https://github.com/wyattowalsh/riso/commit/7435918))
* analysis: implement all recommended fixes from /speckit.analyze ([9fcb56d](https://github.com/wyattowalsh/riso/commit/9fcb56d))
* tasks: generate 98-task breakdown for API versioning ([b2b71e9](https://github.com/wyattowalsh/riso/commit/b2b71e9))
* plan: complete Phase 0-1 for API versioning strategy ([41e0535](https://github.com/wyattowalsh/riso/commit/41e0535))
* Refactor: Add FastAPI API module and tests ([4557ffb](https://github.com/wyattowalsh/riso/commit/4557ffb))


### BREAKING CHANGE

* Spec directory structure updated

Changes:
- Renamed specs/001-fastapi-api-scaffold/ → specs/006-fastapi-api-scaffold/
- Removed specs/008-monitoring-observability/ (out of scope)
- Created branch 006-fastapi-api-scaffold to match spec numbering
- Updated all internal references from 001 to 006:
  - spec.md: Feature Branch updated
  - plan.md: Branch and input paths updated
  - data-model.md: Feature number updated
  - quickstart.md: Feature number updated
  - research.md: Feature number updated
  - tasks.md: Feature and input paths updated
  - gap-resolution-report.md: Feature number updated

Rationale:
- Proper chronological ordering (006 follows 005-container-deployment)
- Removes duplicate 001 prefix (001-build-riso-template already exists)
- Eliminates monitoring-observability spec (deferred to future work)

Current spec structure:
001-build-riso-template
002-docs-template-expansion
003-code-quality-integrations
004-github-actions-workflows
005-container-deployment
006-fastapi-api-scaffold (renamed from 001)

Status: Ready for implementation with correct numbering

## [Unreleased]

### Added

- Comprehensive pre-commit stack with security and quality hooks
  - Python: ruff, ty, pylint, vulture
  - Security: gitleaks, pip-audit
  - Shell: shellcheck
  - Docs: codespell, mdformat
  - CI: actionlint, check-jsonschema
- SDLC tooling integration
  - commitlint for commit message validation
  - commitizen for interactive commits
  - semantic-release for automated versioning
  - Release drafter for PR descriptions
  - Auto-labeler for PR categorization
- Profile-aware pre-commit configuration in template
  - Standard profile: Fast, essential hooks
  - Strict profile: Comprehensive validation
- Post-generation hook auto-installs pre-commit hooks
- Makefile targets: hooks, hooks-run, hooks-update, release

### Changed

- Fixed .gitignore CMake section incorrectly ignoring project Makefile

### Documentation

- Added comprehensive pre-commit test suite (30 tests)

---

*This changelog is automatically updated by [semantic-release](https://github.com/semantic-release/semantic-release).*
