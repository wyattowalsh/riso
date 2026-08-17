# W2 SAAS-T04 — token / a11y polish only (no new vendors)

- Task: `SAAS-T04`
- Wave: W2 / lane SAAS
- Deps: SAAS-T03
- Exclusive write roots: `template/files/node/saas/**`, `template/files/saas-starter/**`
- Verify: no new runtime / host / vendor
- Status: **green**
- Date: 2026-08-13
- Repo: `/Users/ww/dev/projects/riso` · branch `main` · HEAD `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b`
- `samples/*/render/**` writes: **0**

## Scope

Keep matching dirty-tree polish. Apply DESIGN.md tokens + a11y on runtime shells and leftover UI remaps. Do **not** add languages, runtimes, hosts, or new package vendors.

## Token SSOT

`runtime/nextjs/app/globals.css.jinja` and new `runtime/remix/app/styles/globals.css.jinja` share the DESIGN bag:

- `--primary` / `--accent` = teal `173 80% 40%` (`#14b8a6`), not zinc/infima blue
- sidebar tokens for dashboard chrome (`--sidebar*`)
- `color-scheme` on `:root` / `.dark`
- `--focus-ring` + `:focus-visible` 2px / 2px offset
- `.skip-link` + `prefers-reduced-motion: reduce`

Remix `root.tsx` already imported `~/styles/globals.css`; the styles file now exists (runtime-isolated). Remix shadcn postcss reuses existing `@tailwindcss/postcss` (same as Next).

## a11y

- Skip-to-content on Next `layout.tsx` and Remix `root.tsx` (`#main-content`)
- Home + comparison CTAs: `focus-visible:ring-ring`; comparison table `aria-label` + `scope="col"`; boolean cells `aria-label` Yes/No
- Search fallback dialog: `role="dialog"` `aria-modal` `aria-label`; search input `type="search"` + `aria-label`
- Language switcher / settings fallbacks: token classes + `focus-visible` rings
- Landing CTA leftover raw `text-white` remapped to `sidebar-foreground`

## KEEP dirty polish (not rewritten)

39 W0-owned `M` files stay. T04 only remapped remaining raw gray/indigo/blue on already-dirty UI (`SearchDialog`, `LanguageSwitcher`, `settings`, landing). Integration/package/Dockerfile/README polish left as KEEP.

`package.json.jinja` **not edited** this task. Dirty KEEP already listed `@fontsource/inter` + `@fontsource/jetbrains-mono` for remix+shadcn; Remix root now imports those existing deps. Next still uses `next/font/google` (already present). No new vendor names added.

## No new runtime / host

- Runtimes remain `nextjs-16` and `remix-2` only.
- Hosting trees unchanged (`vercel`, `cloudflare`).
- Flatten copies not restored.

## Jinja

```text
find template/files/node/saas template/files/saas-starter -type f -name '*.jinja' -print0 \
  | xargs -0 uv run python scripts/ci/validate_jinja_templates.py
# Validated 197 Jinja template(s): all OK
```
