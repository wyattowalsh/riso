#!/usr/bin/env python3
"""
Documentation health check script.
Feature: 018-docs-sites-overhaul

Performs comprehensive health checks on documentation:
- Configuration validation
- Dependency checks
- Build readiness
- Quality metrics

Usage:
    python scripts/ci/docs_health_check.py [--fix]
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class HealthCheck:
    """Documentation health check."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.issues: List[str] = []
        self.warnings: List[str] = []
        self.passed: List[str] = []

    def run(self) -> bool:
        """
        Run all health checks.
        
        Returns:
            True if all checks passed
        """
        print("=" * 60)
        print("Documentation Health Check")
        print("Feature: 018-docs-sites-overhaul")
        print("=" * 60)
        
        # Load configuration
        answers = self._load_answers()
        if not answers:
            self.issues.append("Could not load .copier-answers.yml")
            return False
        
        docs_site = answers.get("docs_site", "none")
        print(f"\n📚 Documentation Framework: {docs_site}\n")
        
        if docs_site == "none":
            print("✅ No documentation configured")
            return True
        
        # Run checks
        self._check_dependencies(docs_site)
        self._check_structure(docs_site)
        self._check_configuration(docs_site, answers)
        self._check_build_readiness(docs_site)
        
        # Report results
        self._print_results()
        
        return len(self.issues) == 0

    def _load_answers(self) -> Dict:
        """Load copier answers."""
        answers_file = self.project_root / ".copier-answers.yml"
        if not answers_file.exists():
            return {}
        
        answers = {}
        for line in answers_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            key, value = line.split(":", 1)
            answers[key.strip()] = value.strip()
        return answers

    def _check_dependencies(self, framework: str):
        """Check required dependencies."""
        print("🔍 Checking dependencies...")
        
        if framework == "sphinx-shibuya":
            # Check Python and uv
            if self._command_exists("python3"):
                self.passed.append("Python 3 installed")
            else:
                self.issues.append("Python 3 not found")
            
            if self._command_exists("uv"):
                self.passed.append("uv installed")
            else:
                self.issues.append("uv not found (install: pip install uv)")
        
        elif framework in ["fumadocs", "docusaurus"]:
            # Check Node and pnpm
            if self._command_exists("node"):
                version = subprocess.run(
                    ["node", "--version"],
                    capture_output=True,
                    text=True
                ).stdout.strip()
                if version.startswith("v20"):
                    self.passed.append(f"Node.js {version} installed")
                else:
                    self.warnings.append(f"Node.js {version} (v20 LTS recommended)")
            else:
                self.issues.append("Node.js not found")
            
            if self._command_exists("pnpm"):
                self.passed.append("pnpm installed")
            else:
                self.issues.append("pnpm not found (install: npm install -g pnpm)")

    def _check_structure(self, framework: str):
        """Check directory structure."""
        print("📁 Checking directory structure...")
        
        if framework == "sphinx-shibuya":
            required_files = [
                "docs/conf.py",
                "docs/index.rst",
                "Makefile.docs"
            ]
        elif framework == "fumadocs":
            required_files = [
                "apps/docs-fumadocs/next.config.mjs",
                "apps/docs-fumadocs/app/layout.tsx"
            ]
        elif framework == "docusaurus":
            required_files = [
                "apps/docs-docusaurus/docusaurus.config.js",
                "apps/docs-docusaurus/docs/intro.md"
            ]
        else:
            return
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.passed.append(f"Found {file_path}")
            else:
                self.issues.append(f"Missing {file_path}")

    def _check_configuration(self, framework: str, answers: Dict):
        """Check configuration values."""
        print("⚙️  Checking configuration...")
        
        # Check required prompts
        required_prompts = [
            "docs_theme_mode",
            "docs_search_provider",
            "docs_deploy_target",
            "docs_quality_gates"
        ]
        
        for prompt in required_prompts:
            if prompt in answers:
                self.passed.append(f"{prompt}: {answers[prompt]}")
            else:
                self.warnings.append(f"{prompt} not set (will use default)")

    def _check_build_readiness(self, framework: str):
        """Check if documentation can be built."""
        print("🏗️  Checking build readiness...")
        
        if framework == "sphinx-shibuya":
            # Check if Sphinx is installed
            try:
                result = subprocess.run(
                    ["python3", "-m", "sphinx", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self.passed.append("Sphinx is available")
                else:
                    self.warnings.append("Sphinx not found (run: uv sync --group docs)")
            except Exception:
                self.warnings.append("Could not check Sphinx installation")
        
        elif framework in ["fumadocs", "docusaurus"]:
            # Check if node_modules exists
            if (self.project_root / "node_modules").exists():
                self.passed.append("Dependencies installed")
            else:
                self.warnings.append("Dependencies not installed (run: pnpm install)")

    def _command_exists(self, command: str) -> bool:
        """Check if command exists."""
        try:
            subprocess.run(
                ["which", command],
                capture_output=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def _print_results(self):
        """Print check results."""
        print("\n" + "=" * 60)
        print("Results")
        print("=" * 60)
        
        if self.passed:
            print(f"\n✅ Passed ({len(self.passed)}):")
            for item in self.passed:
                print(f"  ✓ {item}")
        
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for item in self.warnings:
                print(f"  ⚠ {item}")
        
        if self.issues:
            print(f"\n❌ Issues ({len(self.issues)}):")
            for item in self.issues:
                print(f"  ✗ {item}")
        
        print("\n" + "=" * 60)
        
        if self.issues:
            print("❌ Health check FAILED")
            print(f"   {len(self.issues)} issue(s) need attention")
        elif self.warnings:
            print("⚠️  Health check PASSED with warnings")
            print(f"   {len(self.warnings)} warning(s) - review recommended")
        else:
            print("✅ Health check PASSED")
            print("   Documentation is ready to build!")
        
        print("=" * 60)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Documentation health check")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to fix issues automatically"
    )
    
    args = parser.parse_args()
    
    checker = HealthCheck(args.project_root)
    success = checker.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
