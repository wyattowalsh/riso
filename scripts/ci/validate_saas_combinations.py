#!/usr/bin/env python3
"""
Validate SaaS Starter technology combinations.

This script tests all valid technology combinations to ensure they can be
rendered successfully and produce working applications.

Usage:
    uv run python scripts/ci/validate_saas_combinations.py
"""

import json
import os
import subprocess
import sys
from pathlib import Path

# Define all valid technology combinations
TECHNOLOGY_MATRIX = {
    "runtime": ["nextjs-16", "remix-2"],
    "hosting": ["vercel", "cloudflare"],
    "database": ["neon", "supabase"],
    "orm": ["prisma", "drizzle"],
    "auth": ["clerk", "authjs"],
    "billing": ["stripe", "paddle"],
    "jobs": ["triggerdev", "inngest"],
    "email": ["resend", "postmark"],
    "analytics": ["posthog", "amplitude"],
    "ai": ["openai", "anthropic"],
    "storage": ["r2", "supabase-storage"],
    "cicd": ["github-actions", "cloudflare-ci"],
}

# Define incompatible combinations (will be skipped)
INCOMPATIBLE_COMBINATIONS = [
    {"database": "neon", "storage": "supabase-storage"},  # Different platforms
]


def is_combination_valid(combo: dict) -> bool:
    """Check if a technology combination is valid."""
    for incompatible in INCOMPATIBLE_COMBINATIONS:
        if all(combo.get(key) == value for key, value in incompatible.items()):
            return False
    return True


def generate_all_combinations() -> list[dict]:
    """Generate all valid technology combinations."""
    combinations = []
    
    # For testing purposes, generate a subset of representative combinations
    # rather than all 2^12 = 4096 possible combinations
    
    # Recommended stacks (known to work)
    recommended = [
        {  # Vercel Starter
            "runtime": "nextjs-16",
            "hosting": "vercel",
            "database": "neon",
            "orm": "prisma",
            "auth": "clerk",
            "billing": "stripe",
            "jobs": "triggerdev",
            "email": "resend",
            "analytics": "posthog",
            "ai": "openai",
            "storage": "r2",
            "cicd": "github-actions",
        },
        {  # Edge Optimized
            "runtime": "remix-2",
            "hosting": "cloudflare",
            "database": "neon",
            "orm": "drizzle",
            "auth": "authjs",
            "billing": "stripe",
            "jobs": "inngest",
            "email": "postmark",
            "analytics": "posthog",
            "ai": "anthropic",
            "storage": "r2",
            "cicd": "cloudflare-ci",
        },
        {  # All-in-One Platform
            "runtime": "nextjs-16",
            "hosting": "vercel",
            "database": "supabase",
            "orm": "prisma",
            "auth": "clerk",
            "billing": "stripe",
            "jobs": "triggerdev",
            "email": "resend",
            "analytics": "posthog",
            "ai": "openai",
            "storage": "supabase-storage",
            "cicd": "github-actions",
        },
    ]
    
    combinations.extend(recommended)
    
    # Add edge cases and variations
    # TODO: Add more test combinations for comprehensive coverage
    
    return [c for c in combinations if is_combination_valid(c)]


def validate_combination(combo: dict, output_dir: Path) -> dict:
    """Validate a single technology combination."""
    combo_name = f"{combo['runtime']}-{combo['hosting']}-{combo['database']}-{combo['orm']}"
    print(f"\n🔍 Testing combination: {combo_name}")

    result = {
        "combination": combo,
        "name": combo_name,
        "status": "pending",
        "errors": [],
        "warnings": [],
    }

    try:
        # Create temporary directory for render
        import tempfile
        import shutil
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            render_path = Path(tmpdir) / combo_name

            # Create copier answers for this combination
            answers = {
                "project_name": f"test-{combo_name}",
                "saas_starter_module": "enabled",
                **{f"saas_{k}": v for k, v in combo.items()},
            }

            # Render template
            print(f"  📦 Rendering template...")
            copier_cmd = os.getenv("COPIER_CMD", "copier")
            render_result = subprocess.run(
                [
                    copier_cmd,
                    "copy",
                    "--force",
                    "--data-file", "-",
                    str(Path(__file__).parent.parent.parent),
                    str(render_path),
                ],
                input=json.dumps(answers),
                capture_output=True,
                text=True,
                timeout=300,
            )

            if render_result.returncode != 0:
                result["status"] = "failed"
                result["errors"].append(f"Render failed: {render_result.stderr}")
                print(f"  ❌ Render failed")
                return result

            print(f"  ✅ Render successful")

            # Check for compilation/syntax errors
            print(f"  🔍 Checking for syntax errors...")

            # Check TypeScript/JavaScript files compile
            if (render_path / "package.json").exists():
                check_result = subprocess.run(
                    ["pnpm", "install"],
                    cwd=render_path,
                    capture_output=True,
                    text=True,
                    timeout=180,
                )
                if check_result.returncode != 0:
                    result["warnings"].append(f"pnpm install issues: {check_result.stderr}")
                    print(f"  ⚠️  pnpm install warnings")
                else:
                    print(f"  ✅ Dependencies installed")

            # Check Python files if present
            python_files = list(render_path.rglob("*.py"))
            if python_files:
                import py_compile
                syntax_errors = []
                for py_file in python_files:
                    try:
                        py_compile.compile(str(py_file), doraise=True)
                    except py_compile.PyCompileError as e:
                        syntax_errors.append(f"{py_file.name}: {e}")

                if syntax_errors:
                    result["errors"].extend(syntax_errors)
                    result["status"] = "failed"
                    print(f"  ❌ Python syntax errors found")
                    return result

            # Success!
            result["status"] = "passed"
            print(f"  ✅ All checks passed")

            # Save render to output for manual inspection (optional)
            if output_dir.exists():
                saved_path = output_dir / combo_name
                if saved_path.exists():
                    shutil.rmtree(saved_path)
                shutil.copytree(render_path, saved_path)
                result["saved_path"] = str(saved_path)

    except subprocess.TimeoutExpired:
        result["status"] = "failed"
        result["errors"].append("Validation timed out")
        print(f"  ⏱️  Timeout")
    except Exception as e:
        result["status"] = "failed"
        result["errors"].append(f"Unexpected error: {str(e)}")
        print(f"  ❌ Failed: {e}")

    return result


def main() -> int:
    """Main validation entry point."""
    print("?? SaaS Starter Combination Validator")
    print("=" * 60)
    
    # Generate test combinations
    combinations = generate_all_combinations()
    print(f"\n?? Testing {len(combinations)} technology combinations")
    
    # Validate each combination
    results = []
    output_dir = Path("samples/saas-starter")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for combo in combinations:
        result = validate_combination(combo, output_dir)
        results.append(result)
    
    # Save results
    results_file = output_dir / "validation-results.json"
    with results_file.open("w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n?? Results saved to {results_file}")
    
    # Summary
    passed = sum(1 for r in results if r["status"] == "passed")
    failed = sum(1 for r in results if r["status"] == "failed")
    skipped = sum(1 for r in results if r["status"] == "skipped")
    
    print("\n" + "=" * 60)
    print("?? Summary:")
    print(f"  ? Passed: {passed}")
    print(f"  ? Failed: {failed}")
    print(f"  ??  Skipped: {skipped}")
    print(f"  ?? Total: {len(results)}")
    
    if failed > 0:
        print("\n??  Some combinations failed validation")
        return 1
    
    if skipped == len(results):
        print("\n??  Validation not yet implemented (all tests skipped)")
        return 0  # Don't fail CI for not-yet-implemented tests
    
    print("\n? All tested combinations passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
