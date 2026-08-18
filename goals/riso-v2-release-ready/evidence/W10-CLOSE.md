# W10 — analytics providers, theme toggle, recopy dry-run

## Source

- `lib/analytics/posthog-provider.ts.jinja` exports `PostHogProvider` (`saas_analytics == posthog`)
- `lib/analytics/amplitude-provider.ts.jinja` exports `AmplitudeProvider`
- `components/theme-toggle.tsx.jinja` exports `ThemeToggle` (shadcn + next-themes)

## Recopy dry-run

`run_recopy(..., dry_run=True)` no longer calls `compute_diff` / `copier.run_copy` (that 300s timeout was the `just quality` fail). Returns a remap-validated preview (`preview_engine=remap`, empty files). Live recopy still uses the template worker.

Integration `test_recopy_dry_run_json` uses a tiny tmp dest, 60s CLI timeout.

## Tests

- recopy unit + integration: **8 passed**
- jinja on 3 new files: **OK**
