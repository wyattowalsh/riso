# Residuals — SAAS lane (W2 / W7 addendum)

**Status:** none blocking for official-matrix answers (all 11 saas-starter dests keep auth+billing modules enabled)
**Date:** 2026-08-18

No owned residual blocks W2-SAAS closeout. Mid-matrix source patches landed for upcoming `saas-starter/*` dests.

## Closed this resume (source)

- HIPAA/SOC2 gates retargeted to Copier SSOT `saas_compliance_level` (`1ba5a14`)
- Shared env / CSP / docker / TOTP now AND `saas_auth_module` / `saas_billing_module` with provider (`f6f6c81`)
- Compiled Next imports: `@/lib/auth/helpers` + `@/lib/database/client` (`15d8ca3`)
- Auth.js dest-root barrels for `@/lib/auth` and `@/lib/auth/authjs/auth.config` (`aec29ec`)
- Nested SaaS GHA honesty: pnpm 9 + `typecheck` (`4e9f7a9`)

## Non-blocking leftovers

1. **Remix + Auth.js `next-auth`:** `saas-starter/remix-cloudflare-neon-drizzle` still ships NextAuth packages. Do not implement a Remix Auth.js adapter mid-matrix.
1. **`.env.example.jinja`:** hook-protected; still provider-only. Leave until the hook allows a module+provider AND.
1. **Provider-only inner gates** remain on some Next layout/middleware/health/ORM/e2e surfaces. Official answers do not disable auth/billing while infra is on, so they will not fail this matrix.
1. **Remix + `saas_i18n`:** Next-intl stays Next-only. remix-i18next remains a future refine.
