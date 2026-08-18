# W10 SAAS — add missing `@/components/theme-toggle`

- Wave: W10 / PAY-P0-saas-theme-toggle
- Date: 2026-08-18
- Repo: `/Users/ww/dev/projects/riso` · branch `main` · HEAD `89882fff946e10692de1e1eb634ad4aa355ed694`
- Exclusive writes: `template/files/node/saas/components/theme-toggle.tsx.jinja`, this file
- `samples/*/render/**` writes: **0**
- Commits / tags / pushes: **0**
- Status: **green** (compiled `@/components/theme-toggle` now has a payload module)

## Confirmed finding

`components/layouts/dashboard.tsx.jinja` (gated `saas_infra_module == "enabled"`) imports `{ ThemeToggle }` from `@/components/theme-toggle` when `saas_ui_framework == 'shadcn-ui'` and mounts `<ThemeToggle />` with no props. Admin users page pulls that layout. No `components/theme-toggle.tsx.jinja` existed, so default Next compile failed.

`next-themes` is already in `package.json.jinja` when `saas_ui_framework == 'shadcn-ui'`. No new deps. Dashboard was **not** edited.

## File created

| File                                                         | Gate                             | Export                                     |
| ------------------------------------------------------------ | -------------------------------- | ------------------------------------------ |
| `template/files/node/saas/components/theme-toggle.tsx.jinja` | `saas_infra_module == "enabled"` | `export function ThemeToggle()` — no props |

Behavior:

- `'use client'` only when `saas_runtime == 'nextjs-16'`
- When `saas_ui_framework == 'shadcn-ui'` (next-themes present): `useTheme()` + `setTheme('light'|'dark')`, and `.dark` on `document.documentElement` so the toggle still applies without a `ThemeProvider` in layout
- Otherwise: classList `.dark` toggle only (no `next-themes` import)
- Accessible name via `aria-label` (`Switch to light theme` / `Switch to dark theme`, or `Toggle theme` without next-themes)
- Inline sun/moon glyphs; no lucide / new packages

## Import contract (unchanged; now resolvable)

| Consumer                                        | Import                                         |
| ----------------------------------------------- | ---------------------------------------------- |
| `components/layouts/dashboard.tsx.jinja`        | `ThemeToggle` from `@/components/theme-toggle` |
| `runtime/nextjs/app/admin/users/page.tsx.jinja` | pulls `DashboardLayout` (same import)          |

## Commands

```text
git rev-parse --show-toplevel   # /Users/ww/dev/projects/riso
git branch --show-current       # main
git rev-parse HEAD              # 89882fff946e10692de1e1eb634ad4aa355ed694
uv run python scripts/ci/validate_jinja_templates.py \
  template/files/node/saas/components/theme-toggle.tsx.jinja
# Validated 1 Jinja template(s): all OK
.venv/bin/python -m pytest \
  tests/unit/test_saas_template_clients.py::TestSaasThemeToggle \
  -q -n 0 --override-ini='addopts='
# 2 passed
# flatten dest-root probes: next.config.js.jinja, db/schema.ts.jinja — ABSENT
git status --short -- template/files/node/saas/components/layouts/dashboard.tsx.jinja
# empty (dashboard not edited)
```

## Remaining residuals (not this PAY)

| Residual                                                                  | Disposition                                                           |
| ------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| Root layout has no `ThemeProvider` from `next-themes`                     | **out of exclusive write** — toggle still applies `.dark` on `<html>` |
| `PAY-P0-saas-lib-analytics-provider` (`@/lib/analytics/posthog-provider`) | **sibling P0** — not this file                                        |
