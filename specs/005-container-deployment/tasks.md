# Tasks: Container & Deployment Templates

**Input**: Design documents from `/specs/005-container-deployment/`
**Prerequisites**: plan.md (✅), spec.md (✅), research.md (✅), data-model.md (✅), contracts/ (✅)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for container support

- [ ] T001 [P] [Setup] Create container template directory `template/files/shared/.docker/`
- [ ] T002 [P] [Setup] Create hadolint config directory structure
- [ ] T003 [P] [Setup] Add `include_databases` prompt to `template/copier.yml` (conditional on `api_tracks` includes python/node)
- [ ] T004 [P] [Setup] Create validation script directory `scripts/ci/` for Dockerfile validation

**Checkpoint**: Directory structure ready for template files

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 [P] [Foundation] Create `.dockerignore.jinja` template in `template/files/shared/` (exclude `__pycache__`, `.git`, `*.pyc`, `.env`, `node_modules`, `.riso`, `samples`, `.pytest_cache`)
- [ ] T006 [P] [Foundation] Create `.hadolint.yaml.jinja` config in `template/files/shared/` (ignore DL3008, DL3009, failure-threshold=error)
- [ ] T007 [P] [Foundation] Implement health check endpoint for FastAPI in `template/files/python/src/{{ package_name }}/api/health.py.jinja` (GET /health → {"status": "healthy", "service": "api-python"})
- [ ] T008 [P] [Foundation] Implement health check endpoint for Fastify in `template/files/node/apps/api-node/src/health.ts.jinja` (GET /health → {"status": "healthy", "service": "api-node"})
- [ ] T009 [Foundation] Create `scripts/ci/validate_dockerfiles.py` (hadolint validation with exit codes: 0=pass, 1=errors, 2=tool error)
- [ ] T010 [Foundation] Extend `scripts/render-samples.sh` with container build validation (add --validate-containers flag)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Python Production Containers (Priority: P1) 🎯 MVP

**Goal**: Production-ready Dockerfiles with multi-stage builds, non-root execution (UID 1000:1000), HTTP health checks

**Independent Test**: Render project with `api_tracks=python`, build with `docker build -f Dockerfile -t test:latest .`, verify image size <500MB, run with `docker run -p 8000:8000 test:latest`, check /health returns 200 OK, validate non-root with `docker run --rm test:latest id`

### Implementation for User Story 1

- [ ] T011 [P] [US1] Create base Dockerfile template `template/files/shared/.docker/Dockerfile.jinja` with multi-stage structure (builder + runtime stages)
- [ ] T012 [US1] Implement Python builder stage in Dockerfile.jinja (FROM python:3.11-slim-bookworm AS builder-python, uv sync with cache mounts)
- [ ] T013 [US1] Implement Python runtime stage in Dockerfile.jinja (FROM python:3.11-slim-bookworm AS runtime-python, non-root UID 1000:1000, COPY from builder)
- [ ] T014 [US1] Add conditional CLI entrypoint in Dockerfile.jinja (CMD with `uv run python -m {{ package_name }}.cli --help` when cli_module=enabled)
- [ ] T015 [US1] Add conditional API entrypoint in Dockerfile.jinja (CMD with `uvicorn {{ package_name }}.api.main:app --host 0.0.0.0 --port 8000` when api_tracks=python)
- [ ] T016 [US1] Add HEALTHCHECK directive to Dockerfile.jinja for API services (5s timeout, 3 retries, 2s interval)
- [ ] T017 [P] [US1] Create development Dockerfile variant `template/files/shared/.docker/Dockerfile.dev.jinja` with volume mounts and hot reload (optional)
- [ ] T018 [US1] Update `samples/default/copier-answers.yml` with `include_databases: "no"` default
- [ ] T019 [US1] Validate default sample renders Dockerfile with hadolint (zero errors expected)
- [ ] T020 [US1] Test default sample container build completes in <3min with image size <500MB
- [ ] T021 [US1] Test default sample container runs successfully with health check responding 200 OK
- [ ] T022 [US1] Validate CLI-only sample (cli-docs variant) renders Dockerfile with CLI entrypoint

**Checkpoint**: At this point, User Story 1 should be fully functional - Python containers build, run, and pass health checks independently

---

## Phase 4: User Story 2 - docker-compose Orchestration (Priority: P2)

**Goal**: docker-compose configurations for monorepos with multi-service coordination (Python API, Node API, docs, optional databases)

**Independent Test**: Render project with `api_tracks=python+node`, `docs_site=fumadocs`, `include_databases=yes`, run `docker-compose up -d`, verify all services healthy via `docker-compose ps`, test inter-service communication, access docs at http://localhost:3000, validate cleanup with `docker-compose down -v`

### Implementation for User Story 2

- [ ] T023 [US2] Create base docker-compose template `template/files/shared/docker-compose.yml.jinja` with version 3.8+ syntax
- [ ] T024 [P] [US2] Implement Python API service definition in docker-compose.yml.jinja (build context, ports 8000:8000, health check, conditional depends_on)
- [ ] T025 [P] [US2] Implement Node.js API service definition in docker-compose.yml.jinja (build context, ports 3000:3000, health check, conditional rendering)
- [ ] T026 [P] [US2] Implement Fumadocs service definition in docker-compose.yml.jinja (build context, ports 3001:3001, conditional rendering when docs_site=fumadocs)
- [ ] T027 [US2] Implement PostgreSQL service definition in docker-compose.yml.jinja (postgres:16-alpine, conditional on include_databases=yes, health check, volume mount)
- [ ] T028 [US2] Implement Redis service definition in docker-compose.yml.jinja (redis:7-alpine, conditional on include_databases=yes, health check, volume mount)
- [ ] T029 [US2] Add service dependencies with health check conditions (API services depend on databases when enabled)
- [ ] T030 [US2] Add volume declarations for database persistence (postgres_data, redis_data)
- [ ] T031 [US2] Add network declarations for service isolation (default network sufficient for P2)
- [ ] T032 [US2] Add environment variable configuration (.env file template with database credentials)
- [ ] T033 [US2] Implement Node.js builder stage in Dockerfile.jinja (FROM node:20-alpine AS builder-node, pnpm install with cache mounts)
- [ ] T034 [US2] Implement Node.js runtime stage in Dockerfile.jinja (FROM node:20-alpine AS runtime-node, non-root UID 1000:1000, COPY from builder)
- [ ] T035 [US2] Add conditional Node.js API entrypoint in Dockerfile.jinja (CMD with `node apps/api-node/dist/main.js` when api_tracks includes node)
- [ ] T036 [US2] Update `samples/api-monorepo/copier-answers.yml` with `api_tracks: python+node`, `include_databases: yes`
- [ ] T037 [US2] Test api-monorepo sample docker-compose up completes with all services healthy in <30s
- [ ] T038 [US2] Test inter-service communication (Python API → shared logic → PostgreSQL connection)
- [ ] T039 [US2] Test volume mounts enable hot reload for local development
- [ ] T040 [US2] Validate docker-compose down -v cleans up all containers and volumes without orphans

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - single containers AND multi-service orchestration

---

## Phase 5: User Story 3 - Container Registry Publishing (Priority: P3)

**Goal**: GitHub Actions workflows for building, scanning, tagging, and publishing containers to ghcr.io/Docker Hub/ECR

**Independent Test**: Push commit to trigger workflow, verify image builds with layer caching, Trivy scan passes with zero HIGH/CRITICAL CVEs, image pushes to ghcr.io with tags `latest` and `v1.2.3`, workflow artifacts include SBOM and scan report, image pull succeeds with `docker pull ghcr.io/owner/project:latest`

### Implementation for User Story 3

- [ ] T041 [P] [US3] Create container build workflow `template/files/shared/.github/workflows/riso-container-build.yml.jinja` (hadolint → build → scan → upload artifacts)
- [ ] T042 [P] [US3] Create container publish workflow `template/files/shared/.github/workflows/riso-container-publish.yml.jinja` (build → scan → tag → push)
- [ ] T043 [US3] Implement hadolint job in container build workflow (uses hadolint/hadolint-action@v3, fails on errors)
- [ ] T044 [US3] Implement Docker build job with BuildKit caching (actions/cache@v4 with uv.lock/pnpm-lock.yaml hash keys)
- [ ] T045 [US3] Implement Trivy scan job (aquasecurity/trivy-action@0.20.0, fail on HIGH/CRITICAL, generate SBOM)
- [ ] T046 [US3] Implement artifact upload job (build logs, scan report, SBOM with 90-day retention)
- [ ] T047 [US3] Implement ghcr.io publishing with OIDC authentication (GITHUB_TOKEN, permissions: packages: write)
- [ ] T048 [US3] Implement semantic version tagging (extract from git tags or conventional commits, tag latest + v1.2.3 + v1.2 + v1)
- [ ] T049 [P] [US3] Add Docker Hub authentication template in publish workflow (optional, via secrets.DOCKERHUB_USERNAME/DOCKERHUB_TOKEN)
- [ ] T050 [P] [US3] Add AWS ECR authentication template in publish workflow (optional, via OIDC or secrets.AWS_ACCESS_KEY_ID)
- [ ] T051 [US3] Test container build workflow in samples/default with artifact uploads
- [ ] T052 [US3] Test container publish workflow pushes to ghcr.io with correct tags
- [ ] T053 [US3] Validate Trivy scan blocks workflow on HIGH/CRITICAL vulnerabilities
- [ ] T054 [US3] Test multi-architecture build (linux/amd64, linux/arm64) with buildx (optional, if time permits)

**Checkpoint**: All user stories should now be independently functional - local builds, orchestration, AND registry publishing

---

## Phase 6: Documentation & Context

**Purpose**: Comprehensive documentation covering container usage, deployment patterns, troubleshooting

- [ ] T055 [P] [Docs] Create container module documentation `docs/modules/containers.md.jinja` (Dockerfile structure, multi-stage builds, security hardening, health checks)
- [ ] T056 [P] [Docs] Update quickstart guide `docs/quickstart.md.jinja` with container section (build, run, docker-compose, registry push)
- [ ] T057 [P] [Docs] Create container context file `.github/context/containers.md` (extension patterns, custom builds, multi-arch, private registries)
- [ ] T058 [P] [Docs] Add container troubleshooting section to containers.md (build failures, health check issues, permission errors, registry auth)
- [ ] T059 [P] [Docs] Update upgrade guide `docs/upgrade-guide.md.jinja` with container feature (migration notes for projects adding containers)
- [ ] T060 [Docs] Create container quickstart `specs/005-container-deployment/quickstart.md` based on existing draft (10-section deployment guide)

---

## Phase 7: Validation & Integration

**Purpose**: Ensure all sample variants work with containers and CI integration is complete

- [ ] T061 [Validation] Extend `scripts/ci/render_matrix.py` to include container validation (build, scan, compose up/down)
- [ ] T062 [Validation] Add container metrics capture to sample metadata (build time, image size, scan results)
- [ ] T063 [P] [Validation] Validate samples/default renders and builds successfully with containers
- [ ] T064 [P] [Validation] Validate samples/cli-docs renders with CLI-only Dockerfile
- [ ] T065 [P] [Validation] Validate samples/api-monorepo renders with docker-compose multi-service
- [ ] T066 [P] [Validation] Validate samples/full-stack renders with all container features (API + docs + databases)
- [ ] T067 [Validation] Update `.github/workflows/template-ci.yml` with container validation job (calls validate_dockerfiles.py)
- [ ] T068 [Validation] Test template CI workflow runs container validation on PR branches

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories, performance optimization, security review

- [ ] T069 [P] [Polish] Add .env.example template for docker-compose environment variables
- [ ] T070 [P] [Polish] Optimize Dockerfile layer caching with targeted COPY commands (lock files before source)
- [ ] T071 [P] [Polish] Add Dockerfile comments explaining security hardening decisions (non-root, minimal packages)
- [ ] T072 [P] [Polish] Pin all base image digests in Dockerfile.jinja (SHA256 hashes)
- [ ] T073 [Polish] Performance test: Validate Python builds complete in <3min, Node builds <5min in CI
- [ ] T074 [Polish] Performance test: Validate image sizes meet targets (Python <500MB, Node <300MB, docs <200MB)
- [ ] T075 [Polish] Security review: Validate Trivy scans pass with zero HIGH/CRITICAL CVEs in all samples
- [ ] T076 [Polish] Security review: Validate hadolint passes with zero errors in all samples
- [ ] T077 [P] [Polish] Update module_catalog.json.jinja with container module metadata
- [ ] T078 [P] [Polish] Update sample metadata.json files with container build evidence
- [ ] T079 [Polish] Run quickstart.md validation for container deployment workflow
- [ ] T080 [Polish] Final code cleanup and comment consistency across all Jinja templates

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Depends on US1 completion (needs Dockerfile.jinja foundation for docker-compose services)
  - User Story 3 (P3): Depends on US1 completion (needs Dockerfile.jinja to build/publish)
- **Documentation (Phase 6)**: Can start after US1, complete after US3
- **Validation (Phase 7)**: Depends on US1-3 completion
- **Polish (Phase 8)**: Depends on all phases completion

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: **DEPENDS ON US1** - Requires Dockerfile.jinja template from T011-T017 for docker-compose build contexts
- **User Story 3 (P3)**: **DEPENDS ON US1** - Requires Dockerfile.jinja template to build images for registry publishing

### Critical Path

```text
Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3 (US1 - Dockerfiles)
                                               ↓
                                        Phase 4 (US2 - docker-compose) ┐
                                               ↓                         │
                                        Phase 5 (US3 - Registry) -------┘
                                               ↓
                                        Phase 6 (Documentation)
                                               ↓
                                        Phase 7 (Validation)
                                               ↓
                                        Phase 8 (Polish)
```

### Within Each User Story

**User Story 1 (T011-T022)**:
- T011-T017 [P] Templates can be created in parallel
- T018-T022 Validation tasks run sequentially after templates complete

**User Story 2 (T023-T040)**:
- T024-T028 [P] Service definitions can be created in parallel
- T033-T035 Node.js stages can be created in parallel with service definitions
- T036-T040 Validation tasks run sequentially after docker-compose complete

**User Story 3 (T041-T054)**:
- T041-T042 [P] Workflow templates can be created in parallel
- T043-T050 [P] Workflow jobs can be created in parallel
- T051-T054 Validation tasks run sequentially after workflows complete

### Parallel Opportunities

- **Phase 1 Setup**: All tasks (T001-T004) [P] can run in parallel
- **Phase 2 Foundational**: Tasks T005-T008 [P] can run in parallel (different files)
- **Phase 3 US1**: Tasks T011, T017 [P] can run in parallel (Dockerfile vs Dockerfile.dev)
- **Phase 4 US2**: Tasks T024-T028, T033-T034 [P] can run in parallel (service definitions + Node stages)
- **Phase 5 US3**: Tasks T041-T042, T043-T050 [P] can run in parallel (workflows + jobs)
- **Phase 6 Documentation**: All tasks (T055-T060) [P] can run in parallel
- **Phase 7 Validation**: Tasks T063-T066 [P] can run in parallel (different sample variants)
- **Phase 8 Polish**: Tasks T069-T072, T077-T078 [P] can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T010) **CRITICAL - blocks all stories**
3. Complete Phase 3: User Story 1 (T011-T022)
4. **STOP and VALIDATE**: Build default sample, test health checks, verify image size
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational (T001-T010) → Foundation ready
2. Add User Story 1 (T011-T022) → Test independently → Deploy/Demo (MVP - production Dockerfiles!)
3. Add User Story 2 (T023-T040) → Test independently → Deploy/Demo (docker-compose orchestration!)
4. Add User Story 3 (T041-T054) → Test independently → Deploy/Demo (container registry publishing!)
5. Complete Documentation (T055-T060) → Documentation ready
6. Complete Validation (T061-T068) → CI integration ready
7. Complete Polish (T069-T080) → Production ready
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T010)
2. Once Foundational is done:
   - Developer A: User Story 1 (T011-T022) - Python Dockerfiles
   - Developer B: Documentation (T055-T060) - can start early with draft docs
   - Developer C: Validation infrastructure (T061-T062) - prepare for integration
3. After US1 complete:
   - Developer A: User Story 2 (T023-T040) - docker-compose
   - Developer B: User Story 3 (T041-T054) - registry workflows
   - Developer C: Validation (T063-T068) - test all samples
4. Final: All developers on Polish (T069-T080)

---

## Task Count Summary

- **Phase 1 (Setup)**: 4 tasks
- **Phase 2 (Foundational)**: 6 tasks
- **Phase 3 (US1 - P1 MVP)**: 12 tasks
- **Phase 4 (US2 - P2)**: 18 tasks
- **Phase 5 (US3 - P3)**: 14 tasks
- **Phase 6 (Documentation)**: 6 tasks
- **Phase 7 (Validation)**: 8 tasks
- **Phase 8 (Polish)**: 12 tasks

**Total**: 80 tasks

**Estimated Effort**:
- Setup + Foundational: 1-2 days
- User Story 1 (MVP): 2-3 days
- User Story 2: 3-4 days
- User Story 3: 2-3 days
- Documentation + Validation + Polish: 2-3 days
- **Total**: 10-15 days (single developer, sequential)
- **Parallel**: 5-7 days (3 developers)

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- User Story 2 DEPENDS ON User Story 1 (docker-compose needs Dockerfile.jinja)
- User Story 3 DEPENDS ON User Story 1 (workflows need Dockerfile.jinja)
- Commit after each task or logical group (e.g., all service definitions in US2)
- Stop at any checkpoint to validate story independently
- Container builds capture metrics (build time, image size) in sample metadata
- All Trivy scans must pass with zero HIGH/CRITICAL vulnerabilities
- All hadolint checks must pass with zero errors
- Health checks must respond within 5s with 200 OK
- Image sizes must meet NFR-002 targets (Python <500MB, Node <300MB, docs <200MB)
