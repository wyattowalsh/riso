# Migrating from riso-mcp to Riso CLI

The maintainer `riso-mcp` server has been removed in v1.2.0. Use the `riso` CLI and `riso-scaffold` skill instead.

## Remove MCP configuration

Delete `riso-mcp` from your MCP client config (e.g. Claude Desktop `mcp.json`, Cursor MCP settings):

```text
{
  "mcpServers": {
    "riso": { ... }
  }
}
```

Remove the `riso` entry entirely.

## Replacement mapping

| Old MCP tool                | New CLI command                                   |
| --------------------------- | ------------------------------------------------- |
| `copier_copy`               | `riso copy DEST --answers-file ...`               |
| `copier_update`             | `riso update DEST`                                |
| `copier_recopy`             | `riso recopy DEST`                                |
| `copier_diff`               | `riso diff DEST --operation copy`                 |
| `validate_template_answers` | `riso validate --answers-file ...`                |
| `list_template_variants`    | `riso variants list`                              |
| `get_prompts`               | `riso prompts`                                    |
| `riso://catalog/*`          | `riso catalog modules`                            |
| `wizard_*`                  | Skill-guided workflow (see `riso-scaffold` skill) |

## Install skill

Copy or sync `.agents/skills/riso-scaffold/` into your agent harness skills directory.

## Quickstart

```bash
git clone https://github.com/wyattowalsh/riso.git && cd riso
uv sync --group cli
uv run riso doctor --json
uv run riso copy ./my-app --answers-file samples/default/copier-answers.yml
```
