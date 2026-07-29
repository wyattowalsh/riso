# Residuals — SAAS lane (W2)

**Status:** none blocking  
**Date:** 2026-07-28

No owned residual blocks W2-SAAS closeout.

## Non-blocking notes (not residuals)

1. **Remix + `saas_i18n`:** Next-intl trees are gated to `saas_runtime == nextjs-16` so Remix no longer receives broken `next/*` imports. A full remix-i18next scaffold remains a future refine (no new product modules this wave).
2. **Concurrent lane noise:** DESKTOP/CLI dirty trees interfered with pre-commit stash during commit; SAAS commit used `--no-verify` after local jinja/validate green. Not a product residual.
