# Removed Answer Keys

These keys are rejected by `riso validate` and all mutation commands:

| Removed key           | Use instead                                     |
| --------------------- | ----------------------------------------------- |
| `api_tracks`          | `api_module` + `api_languages`                  |
| `api_language`        | `api_languages`                                 |
| `docs_site`           | `docs_module` + `docs_framework`                |
| `mcp_language`        | `mcp_languages`                                 |
| `saas_starter_module` | `saas_infra_module`                             |
| `saas_auth`           | `saas_auth_module` + `saas_auth_provider`       |
| `saas_billing`        | `saas_billing_module` + `saas_billing_provider` |

Synced with `web/src/lib/removedAnswerKeys.ts`.
