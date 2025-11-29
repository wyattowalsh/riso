"""Input validation models for copier hooks using Pydantic.

This module provides type-safe validation for user inputs during template
generation, ensuring data integrity and providing helpful error messages.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class ProjectConfig(BaseModel):
    """Validated project configuration from copier answers."""

    project_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Human-friendly project name"
    )

    project_slug: str = Field(
        ...,
        pattern=r"^[a-z][a-z0-9-]*$",
        description="URL-safe project slug (lowercase, hyphens only)"
    )

    package_name: str = Field(
        ...,
        pattern=r"^[a-z][a-z0-9_]*$",
        description="Python package name (lowercase, underscores only)"
    )

    project_layout: Literal["single-package", "monorepo"] = Field(
        default="single-package",
        description="Repository layout"
    )

    quality_profile: Literal["standard", "strict"] = Field(
        default="standard",
        description="Code quality suite profile"
    )

    python_versions: list[str] = Field(
        default=["3.11", "3.12", "3.13"],
        description="Python versions to support"
    )

    @field_validator("python_versions")
    @classmethod
    def validate_python_versions(cls, v: list[str]) -> list[str]:
        """Validate Python versions are supported."""
        valid_versions = {"3.11", "3.12", "3.13"}
        for version in v:
            if version not in valid_versions:
                raise ValueError(
                    f"Unsupported Python version: {version}. "
                    f"Supported versions: {', '.join(sorted(valid_versions))}"
                )
        return v


class ModuleConfig(BaseModel):
    """Validated module selection configuration."""

    cli_module: Literal["enabled", "disabled"] = Field(
        default="disabled",
        description="Enable Typer CLI scaffolding"
    )

    api_tracks: Literal["none", "python", "node", "python+node"] = Field(
        default="none",
        description="API tracks to scaffold"
    )

    graphql_api_module: Literal["enabled", "disabled"] = Field(
        default="disabled",
        description="Enable GraphQL API (requires Python API)"
    )

    mcp_module: Literal["enabled", "disabled"] = Field(
        default="disabled",
        description="Enable FastMCP tooling module"
    )

    websocket_module: Literal["enabled", "disabled"] = Field(
        default="disabled",
        description="Enable WebSocket module (requires API)"
    )

    codegen_module: Literal["enabled", "disabled"] = Field(
        default="disabled",
        description="Enable code generation tools"
    )

    changelog_module: Literal["enabled", "disabled"] = Field(
        default="disabled",
        description="Enable changelog and release management"
    )

    notebook_module: Literal["enabled", "disabled"] = Field(
        default="disabled",
        description="Enable Jupyter notebook support with full stack"
    )

    docs_site: Literal["fumadocs", "sphinx-shibuya", "docusaurus", "none"] = Field(
        default="fumadocs",
        description="Documentation variant"
    )

    shared_logic: Literal["enabled", "disabled"] = Field(
        default="disabled",
        description="Generate shared logic package"
    )

    ci_platform: Literal["github-actions", "none"] = Field(
        default="github-actions",
        description="CI/CD platform"
    )

    saas_starter_module: Literal["enabled", "disabled"] = Field(
        default="disabled",
        description="Enable SaaS Starter module"
    )

    @model_validator(mode="after")
    def validate_module_dependencies(self):
        """Validate module dependencies are met."""
        errors = []

        # GraphQL requires Python API
        if self.graphql_api_module == "enabled":
            if self.api_tracks not in ["python", "python+node"]:
                errors.append(
                    "GraphQL module requires Python API. "
                    "Set api_tracks to 'python' or 'python+node'."
                )

        # WebSocket requires API
        if self.websocket_module == "enabled":
            if self.api_tracks == "none":
                errors.append(
                    "WebSocket module requires an API. "
                    "Enable at least one API track."
                )

        if errors:
            raise ValueError(
                "Module dependency validation failed:\n" +
                "\n".join(f"  - {e}" for e in errors)
            )

        return self


class SaaSConfig(BaseModel):
    """Validated SaaS Starter configuration."""

    saas_runtime: Literal["nextjs-16", "remix-2"] = "nextjs-16"
    saas_hosting: Literal["vercel", "cloudflare"] = "vercel"
    saas_database: Literal["neon", "supabase"] = "neon"
    saas_orm: Literal["prisma", "drizzle"] = "prisma"
    saas_auth: Literal["clerk", "authjs"] = "clerk"
    saas_enterprise_bridge: Literal["workos", "none"] = "none"
    saas_billing: Literal["stripe", "paddle"] = "stripe"
    saas_jobs: Literal["triggerdev", "inngest"] = "triggerdev"
    saas_email: Literal["resend", "postmark"] = "resend"
    saas_analytics: Literal["posthog", "amplitude"] = "posthog"
    saas_ai: Literal["openai", "anthropic"] = "openai"
    saas_storage: Literal["r2", "supabase-storage"] = "r2"
    saas_cicd: Literal["github-actions", "cloudflare-ci"] = "github-actions"

    saas_observability_sentry: bool = True
    saas_observability_datadog: bool = True
    saas_observability_otel: bool = True
    saas_observability_structured_logging: bool = True

    saas_include_fixtures: bool = True
    saas_include_factories: bool = True
    saas_test_suite_level: Literal["standard", "comprehensive"] = "standard"

    @model_validator(mode="after")
    def validate_saas_compatibility(self):
        """Validate SaaS technology stack compatibility."""
        errors = []
        warnings = []

        # Error: Incompatible combinations
        if self.saas_database == "neon" and self.saas_storage == "supabase-storage":
            errors.append(
                "Cannot use Neon database with Supabase Storage. "
                "Choose either full Supabase or Neon + Cloudflare R2."
            )

        # Warning: Suboptimal combinations
        if self.saas_hosting == "cloudflare" and self.saas_orm == "prisma":
            warnings.append(
                "Prisma requires TCP connections not supported by Cloudflare Workers. "
                "You'll need Prisma Data Proxy (adds latency/cost). "
                "Consider using Drizzle ORM for better edge compatibility."
            )

        if self.saas_hosting == "vercel" and self.saas_storage == "r2":
            warnings.append(
                "Cloudflare R2 works with Vercel but bandwidth egress charges apply."
            )

        # Info: Configuration notes
        if self.saas_database == "supabase" and self.saas_auth == "clerk":
            # This is fine, just informational
            pass

        if errors:
            raise ValueError(
                "SaaS configuration validation failed:\n" +
                "\n".join(f"  ❌ {e}" for e in errors)
            )

        # Warnings don't fail validation but should be logged
        if warnings:
            import sys
            sys.stderr.write("\n⚠️  SaaS Configuration Warnings:\n")
            for warning in warnings:
                sys.stderr.write(f"  - {warning}\n")
            sys.stderr.write("\n")

        return self


class TemplateConfig(BaseModel):
    """Complete validated template configuration."""

    project: ProjectConfig
    modules: ModuleConfig
    saas: Optional[SaaSConfig] = None

    @model_validator(mode="after")
    def validate_saas_module(self):
        """Ensure SaaS config exists if SaaS module enabled."""
        if self.modules.saas_starter_module == "enabled" and self.saas is None:
            raise ValueError(
                "SaaS Starter module is enabled but SaaS configuration is missing"
            )
        return self


def validate_copier_answers(answers: dict) -> TemplateConfig:
    """
    Validate copier answers using Pydantic models.

    Args:
        answers: Dictionary of copier answers

    Returns:
        Validated TemplateConfig instance

    Raises:
        ValueError: If validation fails with detailed error messages

    Example:
        from template.hooks.validation import validate_copier_answers

        try:
            config = validate_copier_answers(answers)
            print(f"✅ Configuration valid: {config.project.project_name}")
        except ValueError as e:
            print(f"❌ Validation failed: {e}")
            sys.exit(1)
    """
    # Extract project config
    project_data = {
        "project_name": answers.get("project_name"),
        "project_slug": answers.get("project_slug"),
        "package_name": answers.get("package_name"),
        "project_layout": answers.get("project_layout", "single-package"),
        "quality_profile": answers.get("quality_profile", "standard"),
        "python_versions": answers.get("python_versions", ["3.11", "3.12", "3.13"]),
    }

    # Extract module config
    module_data = {
        "cli_module": answers.get("cli_module", "disabled"),
        "api_tracks": answers.get("api_tracks", "none"),
        "graphql_api_module": answers.get("graphql_api_module", "disabled"),
        "mcp_module": answers.get("mcp_module", "disabled"),
        "websocket_module": answers.get("websocket_module", "disabled"),
        "codegen_module": answers.get("codegen_module", "disabled"),
        "changelog_module": answers.get("changelog_module", "disabled"),
        "notebook_module": answers.get("notebook_module", "disabled"),
        "docs_site": answers.get("docs_site", "fumadocs"),
        "shared_logic": answers.get("shared_logic", "disabled"),
        "ci_platform": answers.get("ci_platform", "github-actions"),
        "saas_starter_module": answers.get("saas_starter_module", "disabled"),
    }

    # Extract SaaS config if enabled
    saas_data = None
    if answers.get("saas_starter_module") == "enabled":
        saas_data = {
            k.replace("saas_", ""): v
            for k, v in answers.items()
            if k.startswith("saas_") and k != "saas_starter_module"
        }

    # Validate
    project = ProjectConfig(**project_data)
    modules = ModuleConfig(**module_data)
    saas = SaaSConfig(**saas_data) if saas_data else None

    config = TemplateConfig(
        project=project,
        modules=modules,
        saas=saas,
    )

    return config
