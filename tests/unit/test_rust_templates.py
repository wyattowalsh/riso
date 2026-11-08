"""Rust security contracts and output boundaries in Copier's Jinja environment."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from copier._main import Worker

pytestmark = pytest.mark.unit

TEMPLATE_ROOT = Path(__file__).resolve().parents[2] / "template"


def _render(relative: str, **context: object) -> str:
    """Use Copier's configured environment without copying files or running hooks."""
    with TemporaryDirectory(prefix="riso-rust-jinja-") as destination:
        with Worker(
            src_path=str(TEMPLATE_ROOT), dst_path=Path(destination), defaults=True
        ) as worker:
            template = worker.jinja_env.get_template(f"files/rust/{relative}")
            return template.render(**context)


@pytest.mark.parametrize(
    ("relative", "module"),
    [
        ("tests/api_integration_test.rs.jinja", "api"),
        ("tests/cli_test.rs.jinja", "api"),
        ("cli/main.rs.jinja", "cli"),
        ("cli/commands/hello.rs.jinja", "cli"),
        ("cli/commands/mod.rs.jinja", "cli"),
        ("cli/commands/version.rs.jinja", "cli"),
        ("tests/cli_integration_test.rs.jinja", "cli"),
        ("mcp/tests/integration_test.rs.jinja", "mcp"),
    ],
)
def test_copier_preserves_canonical_rust_file_boundaries(
    relative: str, module: str
) -> None:
    """Copier must emit no leading blank line and exactly one trailing newline."""
    context: dict[str, object] = {
        "project_name": "Rust Contract",
        "project_slug": "rust-contract",
        "package_name": "rust_contract",
        "project_description": "Rust template regression",
        "cli_module": "disabled",
        "cli_languages": [],
        "api_module": "disabled",
        "api_languages": [],
        "mcp_module": "disabled",
        "mcp_languages": [],
    }
    context[f"{module}_module"] = "enabled"
    context[f"{module}_languages"] = ["rust"]
    rendered = _render(relative, **context)
    assert rendered
    assert not rendered.startswith("\n")
    assert rendered.endswith("\n")
    assert not rendered.endswith("\n\n")


def _installed_rust_tool(name: str) -> str:
    """Locate an installed tool without letting a rustup shim install anything."""
    rustup = shutil.which("rustup")
    if rustup is None:
        pytest.skip("An existing rustup-managed Rust toolchain is required")
    # `rustup which` only locates installed binaries; it cannot install a toolchain.
    located = subprocess.run(
        [rustup, "which", name],
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )
    if located.returncode:
        pytest.skip(f"The selected Rust toolchain has no installed {name}")
    return located.stdout.strip()


@pytest.mark.parametrize("example_tools", [False, True])
def test_copier_mcp_server_passes_rustfmt(tmp_path: Path, example_tools: bool) -> None:
    """Check the actual server file with rustfmt in both example branches."""
    rustfmt = _installed_rust_tool("rustfmt")
    context = {
        "mcp_module": "enabled",
        "mcp_languages": ["rust"],
        "mcp_example_tools": example_tools,
        "project_name": "Rust Contract",
    }
    rendered = _render("mcp/src/server.rs.jinja", **context)
    source = tmp_path / "server.rs"
    source.write_text(rendered, encoding="utf-8")
    config = tmp_path / "rustfmt.toml"
    config.write_text(_render("mcp/rustfmt.toml.jinja", **context), encoding="utf-8")
    result = subprocess.run(
        [
            rustfmt,
            "--edition=2021",
            "--config-path",
            str(config),
            "--check",
            str(source),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def _run_rendered_rust_tests(tmp_path: Path, rendered: str, count: int) -> None:
    """Compile actual rendered functions and their tests with the installed rustc."""
    rustc = _installed_rust_tool("rustc")
    source = tmp_path / "contract.rs"
    source.write_text(rendered, encoding="utf-8")
    binary = tmp_path / "contract-tests"
    compilation = subprocess.run(
        [
            rustc,
            "--edition=2021",
            "--test",
            str(source),
            "-o",
            str(binary),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert compilation.returncode == 0, compilation.stdout + compilation.stderr
    execution = subprocess.run(
        [str(binary)], check=False, capture_output=True, text=True, timeout=30
    )
    assert execution.returncode == 0, execution.stdout + execution.stderr
    assert f"{count} passed" in execution.stdout


def test_http_body_truncation_runs_actual_rendered_rust_offline(tmp_path: Path) -> None:
    """Compile the real helper and its UTF-8/ASCII tests without Cargo or HTTP."""
    rendered = _render(
        "mcp/src/tools/http_fetch.rs.jinja",
        mcp_module="enabled",
        mcp_languages=["rust"],
        mcp_example_tools=True,
    )
    helper_start = rendered.index("fn truncate_content(")
    helper_end = rendered.index("\npub async fn http_get(", helper_start)
    tests_start = rendered.index("#[cfg(test)]\nmod truncation_tests")
    tests_end = rendered.index("#[cfg(test)]\nmod address_tests", tests_start)
    _run_rendered_rust_tests(
        tmp_path, rendered[helper_start:helper_end] + rendered[tests_start:tests_end], 3
    )


def test_http_public_address_policy_runs_actual_rendered_rust_offline(
    tmp_path: Path,
) -> None:
    """Execute actual public IP and hostname policy cases without DNS or HTTP."""
    rendered = _render(
        "mcp/src/tools/http_fetch.rs.jinja",
        mcp_module="enabled",
        mcp_languages=["rust"],
        mcp_example_tools=True,
    )
    functions_start = rendered.index("fn public_ipv4(")
    functions_end = rendered.index(
        "#[derive(Debug)]\nstruct PublicTarget", functions_start
    )
    tests_start = rendered.index("#[cfg(test)]\nmod address_tests")
    tests_end = rendered.index("#[cfg(test)]\nmod request_tests", tests_start)
    _run_rendered_rust_tests(
        tmp_path,
        "use std::net::{IpAddr, Ipv4Addr};\n"
        + rendered[functions_start:functions_end]
        + rendered[tests_start:tests_end],
        3,
    )


class TestRustApiCors:
    """Production CORS must use CORS_ORIGINS, never allow_any_origin."""

    def test_main_has_no_allow_any_origin(self) -> None:
        """actix-cors must not call allow_any_origin."""
        rendered = _render(
            "api/main.rs.jinja",
            api_module="enabled",
            api_languages=["rust"],
            project_name="Test API",
        )
        assert ".allow_any_origin(" not in rendered
        assert "CORS_ORIGINS" in rendered or "cors_origins" in rendered
        assert "allowed_origin" in rendered
        assert "is_production" in rendered

    def test_config_parses_cors_origins_env(self) -> None:
        """Config reads comma-separated CORS_ORIGINS and rejects *."""
        rendered = _render(
            "api/config.rs.jinja",
            api_module="enabled",
            api_languages=["rust"],
        )
        assert 'env::var("CORS_ORIGINS")' in rendered
        assert "parse_cors_origins" in rendered
        assert '*origin != "*"' in rendered
        assert "cors_origins: Vec<String>" in rendered


class TestRustPayloadHonesty:
    """Dest CI must not go green on empty API tests; uptime 0 is a labeled stub."""

    def test_api_integration_has_no_dummy_pass_or_todo_macro(self) -> None:
        """Integration tests are ignored EXTENSION POINTs, not assert!(true)."""
        rendered = _render(
            "tests/api_integration_test.rs.jinja",
            api_module="enabled",
            api_languages=["rust"],
            package_name="test_api",
        )
        assert "EXTENSION POINT" in rendered
        assert "#[ignore" in rendered
        code_lines = [line.split("//", 1)[0] for line in rendered.splitlines()]
        joined = "\n".join(code_lines)
        assert "assert!(true)" not in joined
        assert "todo!()" not in joined

    def test_health_uptime_stub_is_extension_point(self) -> None:
        """Health uptime stays 0 and is labeled EXTENSION POINT, not todo!()."""
        rendered = _render(
            "api/models/health.rs.jinja",
            api_module="enabled",
            api_languages=["rust"],
        )
        assert "uptime: 0" in rendered
        assert "EXTENSION POINT" in rendered
        assert "TODO:" not in rendered
        code_lines = [line.split("//", 1)[0] for line in rendered.splitlines()]
        assert "todo!()" not in "\n".join(code_lines)
