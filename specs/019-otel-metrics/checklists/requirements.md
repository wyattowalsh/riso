# Specification Quality Checklist: OpenTelemetry + Prometheus Metrics

**Purpose**: Validate this Draft before implementation\
**Created**: 2026-08-18\
**Owner**: Platform Team\
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation shipped in this change
- [x] Python API only; SaaS Node OTEL excluded
- [x] Distinct from ideas.md 012 numbering
- [x] `/health` vs `/metrics` separated

## Requirement Completeness

- [x] Tracing (OTEL) and scrape (`/metrics`) both specified
- [x] Cardinality policy stated
- [x] 011 composition stated
- [ ] Metric name contract written (D001)
- [ ] Copier prompt key named (ask before `copier.yml`; not SaaS keys)

## Feature Readiness

- [ ] Exporter failure mode tested in an implementation PR
- [ ] Registry merge with 011 designed in D001
- [x] No `v2.0.0` tag in this spec

## Notes

Draft is ready for design follow-up, not for template edits.
