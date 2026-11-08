# Feature Specification: OpenTelemetry Tracing + Prometheus Metrics

**Feature Branch**: `019-otel-metrics`\
**Created**: 2026-08-18\
**Status**: Draft\
**Owner**: Platform Team\
**Input**: Wave C — OpenTelemetry tracing and Prometheus `/metrics` for the Python API track.

## Scope

Optional observability for generated **Python FastAPI** apps: OpenTelemetry traces (OTLP export) and a Prometheus scrape endpoint at `/metrics`.

This directory is **spec scaffolding only**. No template or runtime implementation in this draft.

## Out of Scope

- SaaS Node OpenTelemetry (`specs/012-saas-starter` Sentry/Datadog/OTEL JS)
- Full Grafana/ELK/Loki bundles from `specs/ideas.md` idea **012**
- Replacing health/ready/live routes from `006`
- Replacing rate-limit metric names from `011` — compose registries instead
- Hand-editing `samples/*/render/`
- Tagging `v2.0.0`

## User Scenarios & Testing

### User Story 1 - Scrape Prometheus metrics (Priority: P1)

Operators scrape `/metrics` and see HTTP request counters/histograms for the Python API.

**Why this priority**: The cheapest production signal after health checks.

**Independent Test**: Start the API, hit a route, `GET /metrics`, assert metric names and `200`.

**Acceptance Scenarios**:

1. **Given** Python API + metrics enabled, **When** `/metrics` is scraped, **Then** the body is Prometheus text exposition
1. **Given** a request to an application route, **When** `/metrics` is scraped, **Then** request count (and documented latency histogram) increases
1. **Given** metrics disabled, **When** the project is rendered, **Then** `/metrics` is not mounted as an application scrape target

______________________________________________________________________

### User Story 2 - Emit OpenTelemetry traces (Priority: P1)

Each HTTP request creates a span (or uses auto-instrumentation) exportable via OTLP when an endpoint is configured.

**Why this priority**: Metrics without traces stall incident debugging.

**Independent Test**: Run with an OTLP sink (or in-memory exporter in tests) and assert a span per request.

**Acceptance Scenarios**:

1. **Given** tracing enabled and `OTEL_EXPORTER_OTLP_ENDPOINT` set, **When** a request completes, **Then** a span is exported
1. **Given** no exporter endpoint, **When** the API starts, **Then** it still serves traffic (no-op or console exporter per documented default)
1. **Given** GraphQL or WebSocket also enabled, **When** those requests run, **Then** instrumentation is documented (auto vs explicit) without requiring SaaS Node OTEL

______________________________________________________________________

### User Story 3 - Keep health and metrics distinct (Priority: P2)

Load balancers keep using `/health` (and ready/live). Prometheus uses `/metrics`. Auth for `/metrics` is documented (open on private networks vs token later).

**Why this priority**: Mixing health and metrics breaks probes.

**Independent Test**: `/health` remains JSON; `/metrics` remains exposition format.

**Acceptance Scenarios**:

1. **Given** both routes, **When** a probe hits `/health`, **Then** it does not require parsing Prometheus text
1. **Given** 011 rate-limit metrics, **When** both modules are on, **Then** metric names do not collide; one scrape endpoint can include both families

### Edge Cases

- High-cardinality labels (raw URLs, user ids): forbidden on default metrics
- `/metrics` on a public internet bind: document bind/network advice; optional scrape auth is post-MVP
- Missing OTLP collector: API must not crash on export backoff
- Dual OTEL (SaaS Node + Python API) in a monorepo: separate services, separate resource attributes

## Requirements

### Functional Requirements

- **FR-001**: Python API MUST be able to opt into OTEL tracing + Prometheus `/metrics` without `saas_infra_module`
- **FR-002**: `/metrics` MUST use Prometheus exposition and MUST NOT replace `/health`
- **FR-003**: Tracing MUST use OpenTelemetry APIs; default exporter is OTLP when configured
- **FR-004**: Default metric labels MUST be low-cardinality (route template, method, status class)
- **FR-005**: Rate-limit metrics from `011` MUST remain available; share or concatenate the Prometheus registry rather than a second competing `/metrics` mount
- **FR-006**: Resource attributes MUST include service name from project/package settings
- **FR-007**: This spec MUST NOT pull Sentry/Datadog as required Python API dependencies

### Key Entities

- **Meter/Instrument**: counters and histograms
- **Tracer/Span**: per-request server span
- **OTELResource**: service.name, service.version
- **ScrapeEndpoint**: `GET /metrics`

## Success Criteria

- **SC-001**: After one request, `/metrics` shows a non-zero request counter in a render with the option on
- **SC-002**: Tests can capture at least one span without a live collector
- **SC-003**: Health probes stay green if the OTLP exporter is down
- **SC-004**: SaaS Node OTEL templates are unchanged by this spec

## Dependencies

- Requires shipped FastAPI track (`006`)
- Compose with `011` metrics if both enabled
- Parallel with `017`/`018` (no hard dependency)
- Distinct from `specs/ideas.md` idea **012**
