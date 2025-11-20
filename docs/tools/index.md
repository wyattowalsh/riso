# Tools

Riso ships automation to keep rendered projects deterministic and governed.

- **Render scripts**: `scripts/render-samples.sh` renders canonical variants and
  records smoke-test results.
- **CI sync**: `scripts/ci/verify_context_sync.py` enforces that shared GitHub
  context files match the template payload.
- **Docs publishing**: `scripts/ci/track_doc_publish.py` records doc build
  outcomes (Shibuya, Fumadocs, or Docusaurus) for governance reporting.
- **Quality parity**: `scripts/ci/run_quality_suite.py` mirrors the Makefile and
  Taskipy lanes, enforcing coverage and matrix parity across Python 3.11–3.13.

When documenting new automation, add frontmatter-driven entries in this folder
so the Shibuya theme can surface tool metadata in navigation and search.
