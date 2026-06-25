"""Riso CLI application."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated, Optional

import typer

from riso.cli.commands import (
    catalog,
    copy,
    diff,
    doctor,
    export,
    prompts,
    recopy,
    update,
    validate,
    variants,
)
from riso.cli.config import CliConfig
from riso.cli.output import CliContext, emit_success, handle_exception
from riso.core.errors import ExitCode

app = typer.Typer(
    name="riso",
    help="Agent-native CLI for scaffolding from the Riso Copier template.",
    no_args_is_help=True,
    add_completion=False,
)

template_app = typer.Typer(help="Template path utilities.")
variants_app = typer.Typer(help="Sample variant discovery.")
catalog_app = typer.Typer(help="Module catalog introspection.")
prompts_app = typer.Typer(help="Copier prompt introspection.")
export_app = typer.Typer(help="Export copier commands and YAML.")

app.add_typer(template_app, name="template")
app.add_typer(variants_app, name="variants")
app.add_typer(catalog_app, name="catalog")
app.add_typer(prompts_app, name="prompts")
app.add_typer(export_app, name="export")


def _ctx(
    *,
    json_output: bool,
    quiet: bool,
    verbose: bool,
    command: str,
) -> CliContext:
    return CliContext(
        json_mode=json_output,
        quiet=quiet,
        verbose=verbose,
        command_name=command,
    )


def _run(fn, ctx: CliContext, **kwargs) -> None:
    try:
        data = fn(**kwargs)
        payload = data if isinstance(data, dict) else {"result": data}
        warnings = (
            payload.get("warnings")
            if isinstance(payload.get("warnings"), list)
            else None
        )
        emit_success(ctx, data=payload, warnings=warnings)
    except BaseException as exc:
        handle_exception(ctx, exc)


@app.callback()
def global_options(
    ctx: typer.Context,
    template_path: Annotated[
        Optional[Path],
        typer.Option(
            "--template-path", envvar="RISO_TEMPLATE_PATH", help="Template root."
        ),
    ] = None,
    samples_path: Annotated[
        Optional[Path],
        typer.Option(
            "--samples-path", envvar="RISO_SAMPLES_PATH", help="Samples root."
        ),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Emit machine-readable JSON envelope."),
    ] = False,
    quiet: Annotated[
        bool, typer.Option("--quiet", "-q", help="Suppress non-essential output.")
    ] = False,
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Verbose output.")
    ] = False,
    timeout: Annotated[
        Optional[int],
        typer.Option("--timeout", help="Timeout seconds for Copier operations."),
    ] = 300,
) -> None:
    """Global options stored on Typer context."""
    ctx.ensure_object(dict)
    ctx.obj["config"] = CliConfig.from_options(
        template_path=template_path,
        samples_path=samples_path,
        timeout=timeout,
    )
    ctx.obj["cli"] = _ctx(
        json_output=json_output,
        quiet=quiet,
        verbose=verbose,
        command="riso",
    )


def _config(ctx: typer.Context) -> CliConfig:
    return ctx.obj["config"]


def _cli(ctx: typer.Context, command: str) -> CliContext:
    cli = ctx.obj["cli"]
    cli.command_name = command
    return cli


@app.command("doctor")
def doctor_cmd(ctx: typer.Context) -> None:
    """Verify tooling, template path, and environment."""
    _run(
        doctor.run_doctor,
        _cli(ctx, "riso doctor"),
        config=_config(ctx),
    )


@template_app.command("path")
def template_path_cmd(ctx: typer.Context) -> None:
    """Show resolved template root."""
    config = _config(ctx)
    emit_success(
        _cli(ctx, "riso template path"),
        data={"template_path": str(config.template_path)},
    )


@app.command("validate")
def validate_cmd(
    ctx: typer.Context,
    answers_file: Annotated[
        Optional[Path],
        typer.Option("--answers-file", "-f", help="Path to copier-answers.yml."),
    ] = None,
    data: Annotated[
        Optional[list[str]],
        typer.Option("--data", "-d", help="Answer key=value pairs."),
    ] = None,
) -> None:
    """Validate template answers."""
    if not answers_file and not data:
        handle_exception(
            _cli(ctx, "riso validate"),
            ValueError("Provide --answers-file and/or --data key=value"),
        )
    _run(
        validate.run_validate,
        _cli(ctx, "riso validate"),
        config=_config(ctx),
        answers_file=answers_file,
        data_pairs=data,
    )


@app.command("copy")
def copy_cmd(
    ctx: typer.Context,
    destination: Annotated[str, typer.Argument(help="Destination directory.")],
    answers_file: Annotated[
        Optional[Path], typer.Option("--answers-file", "-f")
    ] = None,
    data: Annotated[Optional[list[str]], typer.Option("--data", "-d")] = None,
    force: Annotated[
        bool, typer.Option("--force", help="Overwrite existing destination.")
    ] = False,
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Preview diff without writing.")
    ] = False,
    vcs_ref: Annotated[
        Optional[str], typer.Option("--vcs-ref", help="Git ref for template.")
    ] = None,
) -> None:
    """Generate a new project from the template."""
    _run(
        copy.run_copy,
        _cli(ctx, "riso copy"),
        config=_config(ctx),
        destination=destination,
        answers_file=answers_file,
        data_pairs=data,
        force=force,
        dry_run=dry_run,
        vcs_ref=vcs_ref,
    )


@app.command("update")
def update_cmd(
    ctx: typer.Context,
    destination: Annotated[str, typer.Argument(help="Existing project directory.")],
    skip_answered: Annotated[
        bool, typer.Option("--skip-answered/--no-skip-answered")
    ] = True,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
) -> None:
    """Update an existing project with template changes."""
    _run(
        update.run_update,
        _cli(ctx, "riso update"),
        config=_config(ctx),
        destination=destination,
        skip_answered=skip_answered,
        dry_run=dry_run,
    )


@app.command("recopy")
def recopy_cmd(
    ctx: typer.Context,
    destination: Annotated[str, typer.Argument(help="Existing project directory.")],
    answers_file: Annotated[
        Optional[Path], typer.Option("--answers-file", "-f")
    ] = None,
    data: Annotated[Optional[list[str]], typer.Option("--data", "-d")] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
) -> None:
    """Regenerate a project from the template."""
    _run(
        recopy.run_recopy,
        _cli(ctx, "riso recopy"),
        config=_config(ctx),
        destination=destination,
        answers_file=answers_file,
        data_pairs=data,
        dry_run=dry_run,
    )


@app.command("diff")
def diff_cmd(
    ctx: typer.Context,
    destination: Annotated[str, typer.Argument(help="Destination or project path.")],
    answers_file: Annotated[
        Optional[Path], typer.Option("--answers-file", "-f")
    ] = None,
    data: Annotated[Optional[list[str]], typer.Option("--data", "-d")] = None,
    operation: Annotated[
        str, typer.Option("--operation", help="copy, update, or recopy.")
    ] = "copy",
) -> None:
    """Preview changes for a Copier operation."""
    if operation not in {"copy", "update", "recopy"}:
        handle_exception(
            _cli(ctx, "riso diff"),
            ValueError("operation must be copy, update, or recopy"),
        )
    _run(
        diff.run_diff,
        _cli(ctx, "riso diff"),
        config=_config(ctx),
        destination=destination,
        answers_file=answers_file,
        data_pairs=data,
        operation=operation,  # type: ignore[arg-type]
    )


@variants_app.command("list")
def variants_list_cmd(ctx: typer.Context) -> None:
    """List sample variants."""
    _run(
        variants.run_variants_list,
        _cli(ctx, "riso variants list"),
        config=_config(ctx),
    )


@variants_app.command("show")
def variants_show_cmd(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument(help="Variant name.")],
) -> None:
    """Show a sample variant."""
    _run(
        variants.run_variants_show,
        _cli(ctx, f"riso variants show {name}"),
        config=_config(ctx),
        name=name,
    )


@catalog_app.command("modules")
def catalog_modules_cmd(ctx: typer.Context) -> None:
    """Show module catalog."""
    _run(
        catalog.run_catalog_modules,
        _cli(ctx, "riso catalog modules"),
        config=_config(ctx),
    )


@catalog_app.command("dependencies")
def catalog_deps_cmd(ctx: typer.Context) -> None:
    """Summarize dependency lock files."""
    _run(
        catalog.run_catalog_dependencies,
        _cli(ctx, "riso catalog dependencies"),
        config=_config(ctx),
    )


@prompts_app.callback(invoke_without_command=True)
def prompts_root(ctx: typer.Context) -> None:
    """List all prompts when no subcommand given."""
    if ctx.invoked_subcommand is not None:
        return
    _run(
        prompts.run_prompts_list,
        _cli(ctx, "riso prompts"),
        config=_config(ctx),
    )


@prompts_app.command("show")
def prompts_show_cmd(
    ctx: typer.Context,
    key: Annotated[str, typer.Argument(help="Prompt key.")],
) -> None:
    """Show a single prompt definition."""
    _run(
        prompts.run_prompts_show,
        _cli(ctx, f"riso prompts show {key}"),
        config=_config(ctx),
        key=key,
    )


@export_app.command("cli")
def export_cli_cmd(
    ctx: typer.Context,
    answers_file: Annotated[
        Optional[Path], typer.Option("--answers-file", "-f")
    ] = None,
    data: Annotated[Optional[list[str]], typer.Option("--data", "-d")] = None,
    destination: Annotated[
        str, typer.Option("--dest", help="Target destination path.")
    ] = "./my-project",
) -> None:
    """Export shell commands for copier/riso copy."""
    _run(
        export.run_export_cli,
        _cli(ctx, "riso export cli"),
        config=_config(ctx),
        answers_file=answers_file,
        data_pairs=data,
        destination=destination,
    )


@app.command("export-cli")
def export_cli_alias_cmd(
    ctx: typer.Context,
    answers_file: Annotated[
        Optional[Path], typer.Option("--answers-file", "-f")
    ] = None,
    data: Annotated[Optional[list[str]], typer.Option("--data", "-d")] = None,
    destination: Annotated[
        str, typer.Option("--dest", help="Target destination path.")
    ] = "./my-project",
) -> None:
    """Export shell commands for copier/riso copy (alias for export cli)."""
    _run(
        export.run_export_cli,
        _cli(ctx, "riso export-cli"),
        config=_config(ctx),
        answers_file=answers_file,
        data_pairs=data,
        destination=destination,
    )


@app.command("export-yaml")
def export_yaml_alias_cmd(
    ctx: typer.Context,
    answers_file: Annotated[
        Optional[Path], typer.Option("--answers-file", "-f")
    ] = None,
    data: Annotated[Optional[list[str]], typer.Option("--data", "-d")] = None,
) -> None:
    """Export copier-answers.yml to stdout (alias for export yaml)."""
    _run(
        export.run_export_yaml,
        _cli(ctx, "riso export-yaml"),
        config=_config(ctx),
        answers_file=answers_file,
        data_pairs=data,
    )


@export_app.command("yaml")
def export_yaml_cmd(
    ctx: typer.Context,
    answers_file: Annotated[
        Optional[Path], typer.Option("--answers-file", "-f")
    ] = None,
    data: Annotated[Optional[list[str]], typer.Option("--data", "-d")] = None,
) -> None:
    """Export copier-answers.yml to stdout."""
    _run(
        export.run_export_yaml,
        _cli(ctx, "riso export yaml"),
        config=_config(ctx),
        answers_file=answers_file,
        data_pairs=data,
    )


_GLOBAL_FLAGS = {
    "--json",
    "--quiet",
    "-q",
    "--verbose",
    "-v",
    "--template-path",
    "--samples-path",
    "--timeout",
    "--help",
    "-h",
}


def _normalize_argv(argv: list[str]) -> list[str]:
    """Move global flags before subcommands for Typer callback parsing."""
    if not argv:
        return argv

    globals: list[str] = []
    rest: list[str] = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in _GLOBAL_FLAGS or arg.split("=", 1)[0] in _GLOBAL_FLAGS:
            globals.append(arg)
            if "=" not in arg and arg in {
                "--template-path",
                "--samples-path",
                "--timeout",
            }:
                if i + 1 < len(argv):
                    i += 1
                    globals.append(argv[i])
        else:
            rest.append(arg)
        i += 1

    return globals + rest


def main() -> None:
    """Console entry point."""
    try:
        sys.argv[1:] = _normalize_argv(sys.argv[1:])
        app()
    except KeyboardInterrupt:
        raise SystemExit(ExitCode.INTERRUPTED) from None


if __name__ == "__main__":
    main()
