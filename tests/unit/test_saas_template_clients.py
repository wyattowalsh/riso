"""Tests for SaaS template clients and nested CI contracts."""

# pylint: disable=redefined-outer-name,import-outside-toplevel,too-few-public-methods

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("jinja2")

pytestmark = pytest.mark.unit


@pytest.fixture
def saas_files_dir() -> Path:
    """Get the nested SaaS template directory."""
    return Path(__file__).parents[2] / "template" / "files" / "node" / "saas"


def _read(path: Path) -> str:
    """Read a template file as UTF-8 text."""
    return path.read_text(encoding="utf-8")


def _render(template_path: Path, **context: object) -> str:
    """Render a jinja template with the given context."""
    from jinja2 import Environment, FileSystemLoader

    env = Environment(loader=FileSystemLoader(str(template_path.parent)))
    return env.get_template(template_path.name).render(**context)


class TestSaasDatabaseClient:
    """lib/database/client.ts.jinja is the import target for health/admin."""

    def test_client_template_exists(self, saas_files_dir: Path) -> None:
        """client.ts.jinja must exist under lib/database."""
        client = saas_files_dir / "lib" / "database" / "client.ts.jinja"
        assert client.is_file()

    def test_source_exports_db_or_prisma(self, saas_files_dir: Path) -> None:
        """Source template exports prisma and/or db."""
        text = _read(saas_files_dir / "lib" / "database" / "client.ts.jinja")
        assert "export { prisma }" in text or "export const prisma" in text
        assert "export const db" in text

    def test_prisma_render_exports_prisma(self, saas_files_dir: Path) -> None:
        """Prisma render exports prisma (db may alias it)."""
        rendered = _render(
            saas_files_dir / "lib" / "database" / "client.ts.jinja",
            saas_infra_module="enabled",
            saas_orm="prisma",
        )
        assert "export { prisma }" in rendered
        assert "PrismaClient" in rendered

    def test_drizzle_render_exports_db(self, saas_files_dir: Path) -> None:
        """Drizzle render exports db against the live schema path."""
        rendered = _render(
            saas_files_dir / "lib" / "database" / "client.ts.jinja",
            saas_infra_module="enabled",
            saas_orm="drizzle",
            saas_database="neon",
        )
        assert "export const db" in rendered
        assert "@/integrations/orm/drizzle/schema" in rendered
        assert "export { prisma }" not in rendered


class TestSaasAuthHelpers:
    """lib/auth/helpers.ts.jinja re-exports integrations/auth/helpers."""

    def test_helpers_template_exists(self, saas_files_dir: Path) -> None:
        """helpers.ts.jinja must exist under lib/auth."""
        helpers = saas_files_dir / "lib" / "auth" / "helpers.ts.jinja"
        assert helpers.is_file()

    def test_reexports_integrations_auth_helpers(self, saas_files_dir: Path) -> None:
        """Source re-exports the integrations auth helper barrel."""
        text = _read(saas_files_dir / "lib" / "auth" / "helpers.ts.jinja")
        assert "export * from '@/integrations/auth/helpers'" in text

    def test_rendered_reexport(self, saas_files_dir: Path) -> None:
        """Rendered helpers file is a barrel re-export."""
        rendered = _render(
            saas_files_dir / "lib" / "auth" / "helpers.ts.jinja",
            saas_infra_module="enabled",
            saas_auth_module="enabled",
        )
        assert "export * from '@/integrations/auth/helpers'" in rendered


class TestSaasNestedCi:
    """Nested SaaS ci.yml.jinja pins pnpm 9 and the typecheck script."""

    def test_pnpm_version_nine_and_typecheck_script(self, saas_files_dir: Path) -> None:
        """PNPM_VERSION is 9; the script name is typecheck, not type-check."""
        text = _read(saas_files_dir / ".github" / "workflows" / "ci.yml.jinja")
        assert "PNPM_VERSION: '9'" in text
        assert "PNPM_VERSION: '8'" not in text
        assert "pnpm run typecheck" in text
        assert "pnpm run type-check" not in text

    def test_rendered_ci_keeps_pnpm_nine_and_typecheck(
        self, saas_files_dir: Path
    ) -> None:
        """Rendered nested CI keeps pnpm 9 and typecheck."""
        rendered = _render(
            saas_files_dir / ".github" / "workflows" / "ci.yml.jinja",
            saas_infra_module="enabled",
            saas_cicd="github-actions",
            saas_orm="prisma",
            saas_runtime="nextjs-16",
            saas_hosting="vercel",
            saas_observability_sentry=False,
            project_slug="test-project",
        )
        assert "PNPM_VERSION: '9'" in rendered
        assert "pnpm run typecheck" in rendered
        assert "pnpm run type-check" not in rendered
