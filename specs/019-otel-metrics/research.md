# Research: OpenTelemetry Tracing + Prometheus Metrics

**Status**: Draft | **Owner**: Platform Team | **Date**: 2026-08-18

## Scope

Python FastAPI observability only. Numbering: spec directory **019**, not `specs/ideas.md` idea **012**, and not SaaS OTEL in `012-saas-starter`.

## Decisions

### Traces: OpenTelemetry

- **Decision**: OTEL SDK + FastAPI auto-instrumentation; OTLP/HTTP exporter from standard OTEL env vars.
- **Rejected**: Vendor SDK as the only tracer (Datadog/Sentry required).
- **Reason**: Vendor-neutral; SaaS already has JS OTEL; Python API needs its own.

### Metrics: Prometheus `/metrics`

- **Decision**: Expose Prometheus text at `/metrics` (prometheus_client ASGI app or OTEL Prometheus exporter).
- **Rejected**: OTLP-only metrics with no scrape endpoint for MVP.
- **Reason**: Wave C lock; matches existing `fastapi-patterns.md` sketch and 011 scrape expectations.

### Composition with 011

- **Decision**: One scrape endpoint; rate-limit metric families keep their names.
- **Rejected**: A second `/metrics` mount.
- **Reason**: Duplicate paths confuse Prometheus jobs.

### Failure mode

- **Decision**: Exporter/collector downtime must not fail requests; log at debug/warning with backoff.
- **Rejected**: Hard-fail API startup when OTLP is unreachable.

### Cardinality

- **Decision**: Label with route template, method, and status — not raw paths or user ids.
- **Reason**: Unbounded labels blow Prometheus memory.

## External references

- OpenTelemetry Python: <https://opentelemetry.io/docs/languages/python/>
- FastAPI instrumentation: <https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html>
- Prometheus exposition: <https://prometheus.io/docs/instrumenting/exposition_formats/>
- OTEL env vars: <https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/>
