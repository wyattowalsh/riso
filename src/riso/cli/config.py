"""CLI configuration and path resolution."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from riso.core.errors import TemplateNotFoundError
from riso.core.paths import resolve_samples_path, resolve_template_path


@dataclass
class CliConfig:
    """Resolved CLI paths and defaults."""

    template_path_override: Path | None = None
    samples_path_override: Path | None = None
    timeout: int | None = 300
    force_unsafe: bool = False
    skip_post_gen: bool = False

    @classmethod
    def from_options(
        cls,
        *,
        template_path: Path | None = None,
        samples_path: Path | None = None,
        timeout: int | None = None,
        force_unsafe: bool = False,
        skip_post_gen: bool = False,
    ) -> CliConfig:
        """Normalize explicit path options while retaining operation defaults."""
        return cls(
            template_path_override=(
                Path(str(template_path)).expanduser().resolve()
                if template_path
                else None
            ),
            samples_path_override=(
                samples_path.expanduser().resolve() if samples_path else None
            ),
            timeout=timeout,
            force_unsafe=force_unsafe,
            skip_post_gen=skip_post_gen,
        )

    @property
    def template_path(self) -> Path:
        """Resolve template path or raise TemplateNotFoundError."""
        return resolve_template_path(self.template_path_override)

    @property
    def explicit_template_path(self) -> Path | None:
        """Return a flag/env override without treating the bundled default as one."""
        if self.template_path_override is not None or os.environ.get(
            "RISO_TEMPLATE_PATH"
        ):
            return self.template_path
        return None

    @property
    def samples_path(self) -> Path:
        """Resolve samples path."""
        return resolve_samples_path(self.samples_path_override)

    def optional_template_path(self) -> tuple[Path | None, str | None]:
        """Resolve template path without raising (for doctor)."""
        try:
            return resolve_template_path(self.template_path_override), None
        except TemplateNotFoundError as exc:
            return None, exc.message
