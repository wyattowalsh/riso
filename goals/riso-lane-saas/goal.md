# Goal — Riso Lane SAAS

## Articulated goal

Own the Riso Copier **SAAS exclusive-write lane**: finish and refine the full SaaS scaffold under `template/files/node/saas/**` and `template/files/saas-starter/**` via a **full module sweep** (runtime → hosting/DB/ORM → auth → billing → remaining integrations → UI/marketing → compliance/observability/tests). Keep layered gates coherent (`saas_infra` before auth before billing), isolate SaaS content from non-SaaS variants, and route every Copier contract / sample-answer gap to **COORD/PLATFORM handoffs** — never by editing foreign trees.

This is a **payload lane package** for multi-agent execution, not a new product-module backlog. Sample answers and renders remain PLATFORM-owned; contracts remain COORD-owned.

## Shared understanding

Accepted facts: [`facts.md`](./facts.md) (metadata: [`facts.meta.json`](./facts.meta.json)).

Interview provenance: [`interview.json`](./interview.json) → [`interview-result.json`](./interview-result.json)  
(facts review: [`facts-review.json`](./facts-review.json) → [`facts-result.json`](./facts-result.json)).

### Interview decisions (locked)

| Topic | Decision |
|-------|----------|
| First `/goal` focus | **Full module sweep** across owned paths |
| Internal sequence | Canonical layers: runtime → hosting/ORM/db → auth → billing → integrations → UI → compliance |
| Verification bar | **Strict matrix**: all 11 `samples/saas-starter/*/copier-answers.yml` + `validate_saas_combinations` + `validate_jinja_templates` |
| Contract gaps | Structured handoffs under `goals/riso-lane-saas/handoffs/*.md` only |

### Exclusive write roots

| Allowed | Forbidden (handoff only) |
|---------|--------------------------|
| `template/files/node/saas/**` | `template/copier.yml`, `template/hooks/**`, `template/macros/**`, `module_catalog.json.jinja`, `template/prompts/**` |
| `template/files/saas-starter/**` | non-SaaS `template/files/node/**` outside `node/saas/` |
| goal package docs/handoffs under `goals/riso-lane-saas/**` | python/go/rust/frontend/electron/tauri, `src/riso/**`, `web/**` |
| | `samples/*/copier-answers.yml`, `samples/*/render/**`, lockfile hand-edits, secrets |

### Layering contract (read-only; COORD owns schema)

```
saas_infra_module
  → runtime / hosting / database / orm / storage / cicd / observability / app flags
  → saas_auth_module → provider / 2fa / enterprise_bridge
    → saas_billing_module → billing provider
      → saas_app_module → jobs / email / analytics / …
```

Path exclusion when infra is off (COORD-owned `_exclude`): whole `node/saas/` and `saas-starter/` trees. SAAS keeps file-level Jinja gates coherent inside owned files.

### Hard collision rule (subagent fan-out)

Only the SAAS lead writes these shared roots (or applies queued root-deps):

- `package.json.jinja`, `tsconfig.json.jinja`, `components.json.jinja`
- `config/env.ts.jinja`, `.env.example.jinja`
- `lib/utils.ts.jinja` and contested `lib/multi-tenant/**` entrypoints

Subagents with exclusive provider/UI trees **must not** edit those files; they file `handoffs/root-dep-<id>.md` for the lead.

## Execution plan

Primary plan: [`plan.md`](./plan.md) — full-sweep hyperfine graph (waves 0–7), exclusive sub-lanes (ROOT / RT-NEXT / RT-REMIX / HOST / ORM / AUTH / BILL / INT-* / UI / APP / COMP / QA / STARTER), Mermaid DAG, verification SSOT, and subagent prompt contract.

**Wave summary (from plan):**

| Wave | Mode | Focus |
|------|------|-------|
| 0 | lead + parallel validate | Baseline inventory + 11-variant / combo / jinja evidence |
| 1 | serial ROOT | Shared `package.json` / tsconfig / env / Docker / README |
| 2 | parallel | Runtime (Next/Remix) + hosting + ORM |
| 3 | ordered | Auth → billing → subscription examples |
| 4 | massively parallel | Remaining integrations (email/jobs/ai/analytics/storage/…) |
| 5 | parallel + serial tenancy | UI, content, i18n, multi-tenant, remaining app routes |
| 6 | parallel + serial starter | Compliance, tests/scripts/workflows, saas-starter config/README |
| 7 | lead closeout | Strict matrix re-run + ownership `git status` + handoff index |

**Technology matrix anchors** (combination script dimensions): nextjs-16/remix-2 × vercel/cloudflare × neon/supabase × prisma/drizzle × clerk/authjs × stripe/paddle × jobs/email/analytics/ai/storage/cicd providers. Rules SAAS templates must respect: **neon + supabase-storage incompatible**; **billing implies auth**.

**11 PLATFORM-owned saas-starter variants** (validate only; never edit answers): all-in-one, b2b-teams-full, b2c-consumer-app, edge-optimized, enterprise-ready, nextjs-vercel-neon-clerk, nextjs-vercel-neon-clerk-workos, nextjs-vercel-supabase-clerk, prelaunch-waitlist, remix-cloudflare-neon-drizzle, vercel-starter.

### Hygiene

- Always `uv run` for Python; `pnpm` only when needed on SaaS package surfaces under owned paths
- Never hand-edit `samples/*/render/`, `uv.lock`, or `pnpm-lock.yaml`
- Never commit/print/persist secrets
- No branches/worktrees/commits/pushes unless the human explicitly asks (standalone lane default; umbrella assurance may authorize atomic conventional commits)

## Done condition

1. Full-module sweep work under owned paths is coherent (no broken Jinja, missing shared roots, or layering contradictions for enabled modules).
2. SaaS-only content stays gated so non-SaaS variants are not broken by leakage (within gates SAAS controls).
3. `template/files/saas-starter/**` stays aligned with the layered scaffold it documents/configures.
4. Verification green **or** residual only non-owned gaps as COORD/PLATFORM handoffs:

```bash
for f in samples/saas-starter/*/copier-answers.yml; do
  echo "=== $f ==="
  uv run riso validate --answers-file "$f" --json
done

uv run python scripts/ci/validate_saas_combinations.py --json
uv run python scripts/ci/validate_jinja_templates.py \
  template/files/node/saas template/files/saas-starter

git status --short   # only owned paths + this goal package
```

5. Any needed `saas_*` prompt / when-condition / hook / catalog change exists only as structured files under [`handoffs/`](./handoffs/) (create on first execution if missing).
6. No writes outside `template/files/node/saas/**`, `template/files/saas-starter/**`, and this goal package.

## Out of scope

- Non-SaaS NODE (Fumadocs / Docusaurus / api-node outside `node/saas`)
- Python / Go / Rust / frontend / desktop lanes
- Maintainer `web/` wizard
- Copier prompt schema, hooks, macros, catalog edits (COORD)
- Sample answers and render regeneration (PLATFORM / integrator)
- Inventing product modules beyond the existing scaffold sweep

## Provenance

| Artifact | Path |
|----------|------|
| Interview | [interview.json](./interview.json) → [interview-result.json](./interview-result.json) |
| Facts | [facts.md](./facts.md), [facts.meta.json](./facts.meta.json) |
| Facts review | [facts-review.json](./facts-review.json) → [facts-result.json](./facts-result.json) |
| Plan | [plan.md](./plan.md) (full-sweep hyperfine graph; formal plan-gate receipt optional until re-gated) |

## Launch

```text
/goal goals/riso-lane-saas/goal.md
```
