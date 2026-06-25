# Riso CLI Workflows

## New project from sample variant

```bash
uv run riso variants show default --json
uv run riso validate --answers-file samples/default/copier-answers.yml --json
uv run riso copy ./my-app --answers-file samples/default/copier-answers.yml --json
```

## New project from scratch

```bash
uv run riso prompts --json
uv run riso export yaml --data project_name=MyApp --data cli_module=enabled
# Save YAML, then:
uv run riso validate --answers-file copier-answers.yml --json
uv run riso copy ./my-app --answers-file copier-answers.yml --json
```

## Update existing project

```bash
uv run riso diff ./my-app --operation update --json
uv run riso update ./my-app --dry-run --json
uv run riso update ./my-app --json
```

## Recopy (regenerate)

```bash
uv run riso recopy ./my-app --dry-run --json
uv run riso recopy ./my-app --json
```

## Module catalog

```bash
uv run riso catalog modules --json
```
