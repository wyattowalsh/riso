#!/usr/bin/env python3
"""
Verification script for Rust templates.

Tests that all Rust templates render correctly and produce valid Rust code.
"""

from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import sys


def test_template_syntax():
    """Test that all templates have valid Jinja syntax."""
    print("Testing template syntax...")
    env = Environment(loader=FileSystemLoader("template/files/rust"))

    rust_files = Path("template/files/rust").rglob("*.jinja")
    errors = []

    for template_path in rust_files:
        relative_path = template_path.relative_to("template/files/rust")
        try:
            env.get_template(str(relative_path))
            print(f"  ✓ {relative_path}")
        except Exception as e:
            print(f"  ✗ {relative_path}: {e}")
            errors.append((relative_path, e))

    return errors


def test_cli_rendering():
    """Test CLI template rendering."""
    print("\nTesting CLI rendering...")
    env = Environment(loader=FileSystemLoader("template/files/rust"))

    context = {
        "cli_module": "enabled",
        "cli_language": "rust",
        "api_module": "disabled",
        "project_name": "Test CLI",
        "project_slug": "test-cli",
        "package_name": "test_cli",
        "project_description": "A test CLI application",
    }

    templates = [
        "cli/main.rs.jinja",
        "cli/commands/mod.rs.jinja",
        "cli/commands/hello.rs.jinja",
        "cli/commands/version.rs.jinja",
    ]

    errors = []
    for template_name in templates:
        try:
            template = env.get_template(template_name)
            rendered = template.render(context)

            # Basic validation
            if not rendered.strip():
                errors.append((template_name, "Empty output"))
            elif (
                template_name.endswith("main.rs.jinja") and "fn main()" not in rendered
            ):
                errors.append((template_name, "Missing main function"))

            print(f"  ✓ {template_name}")
        except Exception as e:
            print(f"  ✗ {template_name}: {e}")
            errors.append((template_name, e))

    return errors


def test_api_rendering():
    """Test API template rendering."""
    print("\nTesting API rendering...")
    env = Environment(loader=FileSystemLoader("template/files/rust"))

    context = {
        "cli_module": "disabled",
        "api_module": "enabled",
        "api_languages": "rust",
        "project_name": "Test API",
        "project_slug": "test-api",
        "package_name": "test_api",
        "project_description": "A test API server",
    }

    templates = [
        "api/main.rs.jinja",
        "api/config.rs.jinja",
        "api/routes.rs.jinja",
        "api/handlers/mod.rs.jinja",
        "api/handlers/health.rs.jinja",
        "api/handlers/hello.rs.jinja",
        "api/models/mod.rs.jinja",
        "api/models/health.rs.jinja",
        "api/models/response.rs.jinja",
    ]

    errors = []
    for template_name in templates:
        try:
            template = env.get_template(template_name)
            rendered = template.render(context)

            # Basic validation
            if not rendered.strip():
                errors.append((template_name, "Empty output"))
            elif (
                template_name.endswith("main.rs.jinja") and "fn main()" not in rendered
            ):
                errors.append((template_name, "Missing main function"))

            print(f"  ✓ {template_name}")
        except Exception as e:
            print(f"  ✗ {template_name}: {e}")
            errors.append((template_name, e))

    return errors


def test_cargo_toml():
    """Test Cargo.toml rendering with various configurations."""
    print("\nTesting Cargo.toml rendering...")
    env = Environment(loader=FileSystemLoader("template/files/rust"))

    configurations = [
        {
            "name": "CLI only",
            "context": {
                "project_language": "rust",
                "cli_module": "enabled",
                "cli_language": "rust",
                "api_module": "disabled",
                "mcp_module": "disabled",
                "project_layout": "single-package",
                "package_name": "test_project",
            },
            "expected": ["clap", "cli/main.rs"],
            "not_expected": ["actix-web", "api/main.rs"],
        },
        {
            "name": "API only",
            "context": {
                "project_language": "rust",
                "cli_module": "disabled",
                "api_module": "enabled",
                "api_languages": "rust",
                "mcp_module": "disabled",
                "project_layout": "single-package",
                "package_name": "test_project",
            },
            "expected": ["actix-web", "api/main.rs"],
            "not_expected": ["clap", "cli/main.rs"],
        },
        {
            "name": "Both CLI and API",
            "context": {
                "project_language": "rust",
                "cli_module": "enabled",
                "cli_language": "rust",
                "api_module": "enabled",
                "api_languages": "rust",
                "mcp_module": "disabled",
                "project_layout": "single-package",
                "package_name": "test_project",
            },
            "expected": ["clap", "actix-web", "cli/main.rs", "api/main.rs"],
            "not_expected": [],
        },
    ]

    errors = []
    for config in configurations:
        try:
            template = env.get_template("Cargo.toml.jinja")
            rendered = template.render(config["context"])

            # Check expected content
            for expected in config["expected"]:
                if expected not in rendered:
                    errors.append((config["name"], f"Missing expected: {expected}"))
                    print(f"  ✗ {config['name']}: Missing {expected}")

            # Check not expected content
            for not_expected in config["not_expected"]:
                if not_expected in rendered:
                    errors.append((config["name"], f"Found unexpected: {not_expected}"))
                    print(f"  ✗ {config['name']}: Found unexpected {not_expected}")

            if not any(err[0] == config["name"] for err in errors):
                print(f"  ✓ {config['name']}")

        except Exception as e:
            print(f"  ✗ {config['name']}: {e}")
            errors.append((config["name"], e))

    return errors


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("Rust Template Verification")
    print("=" * 60)

    all_errors = []

    all_errors.extend(test_template_syntax())
    all_errors.extend(test_cli_rendering())
    all_errors.extend(test_api_rendering())
    all_errors.extend(test_cargo_toml())

    print("\n" + "=" * 60)
    if all_errors:
        print(f"FAILED: {len(all_errors)} error(s) found")
        print("=" * 60)
        for template, error in all_errors:
            print(f"  {template}: {error}")
        return 1
    else:
        print("SUCCESS: All templates verified")
        print("=" * 60)
        return 0


if __name__ == "__main__":
    sys.exit(main())
