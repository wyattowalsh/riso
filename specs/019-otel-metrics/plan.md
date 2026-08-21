# Plan: OpenTelemetry Tracing + Prometheus Metrics

**Branch**: `019-otel-metrics` | **Date**: 2026-08-18 | **Spec**: [spec.md](./spec.md)\
**Status**: Draft | **Owner**: Platform Team

## Goal

Add optional OpenTelemetry tracing and a Prometheus `/metrics` scrape route to the **Python FastAPI** track, independent of SaaS Node observability.

This document does **not** implement template or runtime code.

## Workstreams (when leaving Draft)

1. **Prompt**: additive Copier flag (key TBD); default off; Python API only
1. **Metrics**: Prometheus client or OTEL Prometheus exporter; single `/metrics` ASGI mount
1. **Tracing**: FastAPI instrumentation + OTLP exporter from env
1. **Composition**: merge or register 011 rate-limit instruments on the same scrape endpoint
1. **Tests**: scrape content-type/body; in-memory span exporter
1. **Docs**: distinguish from SaaS `saas_observability_otel`

## Non-Goals

- No Grafana dashboards or collector Helm charts in MVP
- No required Sentry/Datadog Python SDKs
- No `copier.yml` / hook / sample-render edits in this scaffolding change
- No `v2.0.0` tag

## Technical Context

**Language/Version**: Python 3.11+\
**Primary Dependencies**: `opentelemetry-sdk`, FastAPI instrumentation, OTLP exporter; `prometheus_client` and/or OTEL Prometheus exporter\
**Storage**: N/A (telemetry)\
**Testing**: pytest; `GET /metrics`; span exporter fixture\
**Constraints**: Optional; low-cardinality labels; health routes unchanged; ty not mypy

## Constitution Check

| Principle               | Assessment                                                  |
| ----------------------- | ----------------------------------------------------------- |
| Template quality first  | Observability code must pass the quality suite when enabled |
| Modular composition     | Independent of SaaS OTEL; optional on Python API            |
| Test-driven development | Scrape + span tests required                                |
| Documentation parity    | Document env vars and `/metrics` vs `/health`               |
| Backwards compatibility | Additive; do not reuse spec numbers 010–016                 |

**GATE**: Pass for Draft.

## Project Structure

### Documentation (this feature)

```text
specs/019-otel-metrics/
├── spec.md
├── plan.md
├── tasks.md
├── research.md
└── checklists/requirements.md
```

### Planned source (implementation later)

```text
template/files/python/src/{{ package_name }}/api/observability/
├── tracing.py.jinja
├── metrics.py.jinja
└── middleware.py.jinja   # if not fully auto-instrumented
```

Mount `/metrics` from the FastAPI app factory in `api/main.py.jinja` when the option is on.

## Complexity Tracking

No constitution violations in this Draft. Two exporters (OTLP + Prometheus scrape) are justified: operators scrape Prometheus locally while traces go to a collector.
