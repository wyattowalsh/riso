# W8 — dest-root SaaS GHA + Auth.js barrel

Nested `node/saas/.github/workflows/{ci,database,e2e}.yml.jinja` deleted. Dest-root now ships:

- `riso-quality.yml.jinja` job `saas-quality` (`working-directory: node/saas`, Node 20, pnpm 9, `typecheck`)
- `riso-saas-database.yml.jinja` with `node/saas/integrations/orm/**` paths

Auth.js:

- `lib/auth/index.ts.jinja` re-exports `@/integrations/auth/authjs/auth.config`
- `integrations/auth/helpers.ts.jinja` imports that path (not flatten `lib/auth/authjs/...`)

Tests: 84 passed (`test_saas_template_clients` + `test_github_workflow_templates` + node/gitlab/circle). Jinja 6 OK.
