# Tasks: OpenTelemetry Tracing + Prometheus Metrics

**Input**: [spec.md](./spec.md), [plan.md](./plan.md), [research.md](./research.md)\
**Status**: Draft | **Owner**: Platform Team | **Date**: 2026-08-18

Scaffolding is done. Do **not** implement template/runtime work until this spec leaves Draft. Python API only — not SaaS Node OTEL.

## Phase 1: Research and design

- [x] R001 [P] Lock OTEL traces + Prometheus `/metrics` for Python API
- [x] R002 [P] Keep `/health` distinct; compose with 011 metric names
- [x] R003 [P] Low-cardinality label policy
- [ ] D001 Write metric name and label contract
- [ ] D002 Write OTEL resource/attribute contract
- [ ] D003 Confirm Copier prompt key — ask before `copier.yml` (do not reuse SaaS OTEL keys)

## Phase 2: Implementation (blocked on leaving Draft)

- [ ] T001 Add tracing bootstrap under `template/files/python/src/{{ package_name }}/api/observability/`
- [ ] T002 Mount `/metrics` from the FastAPI app factory when enabled
- [ ] T003 [P] HTTP counter + latency histogram with route-template labels
- [ ] T004 Merge or register 011 rate-limit metrics on the same registry
- [ ] T005 [P] Module docs vs SaaS `saas_observability_otel`
- [ ] T006 Maintainer include/exclude tests; scrape + span fixtures

## Phase 3: Validation

- [ ] V001 `GET /metrics` returns exposition after one request
- [ ] V002 Span captured with in-memory exporter
- [ ] V003 API serves if OTLP endpoint is down
- [ ] V004 Sample regeneration via `./scripts/render-samples.sh` only

## Dependencies

- After shipped `006`; compose with `011`
- Parallel with `017` and `018`
- Do not edit `template/files/node/saas/integrations/observability/` in this spec
