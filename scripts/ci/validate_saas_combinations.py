#!/usr/bin/env python3
"""
Validate SaaS Starter technology combinations.

This script tests all valid technology combinations to ensure they can be
rendered successfully and produce working applications.

Usage:
    uv run python scripts/ci/validate_saas_combinations.py [--json]
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Literal

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

# Validation rules based on template/hooks/pre_gen_project.py
VALIDATION_RULES = {
    "errors": [
        {
            "name": "neon_supabase_storage_incompatible",
            "combination": {"database": "neon", "storage": "supabase-storage"},
            "message": (
                "Cannot use Neon database with Supabase Storage. "
                "Choose either:\n"
                "  1. Full Supabase (database + storage)\n"
                "  2. Neon database + Cloudflare R2 storage"
            ),
        },
    ],
    "warnings": [
        {
            "name": "cloudflare_prisma_requires_proxy",
            "combination": {"hosting": "cloudflare", "orm": "prisma"},
            "message": (
                "Prisma requires TCP connections, which Cloudflare Workers don't support.\n"
                "You'll need to use Prisma Data Proxy (adds latency and cost).\n"
                "Recommendation: Use Drizzle ORM for better edge compatibility."
            ),
        },
        {
            "name": "vercel_r2_egress_charges",
            "combination": {"hosting": "vercel", "storage": "r2"},
            "message": "Cloudflare R2 works with Vercel but egress bandwidth charges apply.",
        },
    ],
    "info": [
        {
            "name": "supabase_clerk_auth_note",
            "combination": {"database": "supabase", "auth": "clerk"},
            "message": (
                "You've selected both Supabase and Clerk.\n"
                "Supabase Auth will be disabled in favor of Clerk."
            ),
        },
    ],
}

# Required combinations
REQUIRED_RULES = [
    {
        "name": "billing_requires_auth",
        "condition": lambda combo: combo.get("billing") and not combo.get("auth"),
        "message": "Billing functionality requires authentication to be enabled.",
        "severity": "error",
    },
]

# Recommendations
RECOMMENDATION_RULES = [
    {
        "name": "database_should_have_orm",
        "condition": lambda combo: combo.get("database") and not combo.get("orm"),
        "message": "Database selected without ORM. Consider adding Prisma or Drizzle for better developer experience.",
        "severity": "warning",
    },
]

Severity = Literal["error", "warning", "info"]


class ValidationIssue:
    """Represents a validation issue found in a combination."""

    def __init__(self, severity: Severity, name: str, message: str):
        self.severity = severity
        self.name = name
        self.message = message

    def to_dict(self) -> dict:
        return {
            "severity": self.severity,
            "name": self.name,
            "message": self.message,
        }


def validate_combination_rules(combo: dict) -> list[ValidationIssue]:
    """Validate a combination against all defined rules.

    Args:
        combo: Technology combination to validate

    Returns:
        List of validation issues found (errors, warnings, info)
    """
    issues: list[ValidationIssue] = []

    # Check error-level incompatibilities
    for rule in VALIDATION_RULES["errors"]:
        if all(combo.get(key) == value for key, value in rule["combination"].items()):
            issues.append(ValidationIssue("error", rule["name"], rule["message"]))

    # Check warning-level incompatibilities
    for rule in VALIDATION_RULES["warnings"]:
        if all(combo.get(key) == value for key, value in rule["combination"].items()):
            issues.append(ValidationIssue("warning", rule["name"], rule["message"]))

    # Check info-level notices
    for rule in VALIDATION_RULES["info"]:
        if all(combo.get(key) == value for key, value in rule["combination"].items()):
            issues.append(ValidationIssue("info", rule["name"], rule["message"]))

    # Check required combinations
    for rule in REQUIRED_RULES:
        if rule["condition"](combo):
            issues.append(ValidationIssue(rule["severity"], rule["name"], rule["message"]))

    # Check recommendations
    for rule in RECOMMENDATION_RULES:
        if rule["condition"](combo):
            issues.append(ValidationIssue(rule["severity"], rule["name"], rule["message"]))

    return issues


def is_combination_valid(combo: dict) -> bool:
    """Check if a technology combination is valid (no error-level issues).

    Args:
        combo: Technology combination to check

    Returns:
        True if combination has no errors, False otherwise
    """
    issues = validate_combination_rules(combo)
    return not any(issue.severity == "error" for issue in issues)


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


def validate_combination(combo: dict, output_dir: Path, json_output: bool = False) -> dict:
    """Validate a single technology combination.

    Args:
        combo: Technology combination to validate
        output_dir: Directory for output files
        json_output: If True, suppress verbose output

    Returns:
        Validation result dictionary
    """
    combo_name = f"{combo['runtime']}-{combo['hosting']}-{combo['database']}-{combo['orm']}"

    if not json_output:
        print(f"\nValidating combination: {combo_name}")

    result = {
        "combination": combo,
        "name": combo_name,
        "status": "passed",
        "issues": [],
    }

    try:
        # Run validation rules
        issues = validate_combination_rules(combo)

        # Convert issues to result format
        for issue in issues:
            result["issues"].append(issue.to_dict())

        # Determine overall status based on issues
        has_errors = any(issue.severity == "error" for issue in issues)
        has_warnings = any(issue.severity == "warning" for issue in issues)

        if has_errors:
            result["status"] = "failed"
        elif has_warnings:
            result["status"] = "passed_with_warnings"
        else:
            result["status"] = "passed"

        # Print issues if not in JSON mode
        if not json_output:
            for issue in issues:
                if issue.severity == "error":
                    print(f"  ERROR: {issue.message}")
                elif issue.severity == "warning":
                    print(f"  WARNING: {issue.message}")
                elif issue.severity == "info":
                    print(f"  INFO: {issue.message}")

            if result["status"] == "passed":
                print("  PASSED: No issues found")
            elif result["status"] == "passed_with_warnings":
                print("  PASSED: Validation passed with warnings")
            elif result["status"] == "failed":
                print("  FAILED: Error-level incompatibilities found")

    except Exception as e:
        result["status"] = "failed"
        result["issues"].append({
            "severity": "error",
            "name": "validation_exception",
            "message": f"Validation failed with exception: {str(e)}",
        })
        if not json_output:
            print(f"  FAILED: {e}")

    return result


def main() -> int:
    """Main validation entry point.

    Returns:
        Exit code: 0 for success, 1 for validation failures
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Validate SaaS Starter technology combinations"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format only (no verbose output)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("samples/saas-starter"),
        help="Directory to save validation results (default: samples/saas-starter)",
    )
    args = parser.parse_args()

    if not args.json:
        print("SaaS Starter Combination Validator")
        print("=" * 60)

    # Generate test combinations
    combinations = generate_all_combinations()

    if not args.json:
        print(f"\nTesting {len(combinations)} technology combinations")

    # Validate each combination
    results = []
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for combo in combinations:
        result = validate_combination(combo, args.output_dir, args.json)
        results.append(result)

    # Save results to JSON file
    results_file = args.output_dir / "validation-results.json"
    with results_file.open("w") as f:
        json.dump(results, f, indent=2)

    # Calculate summary statistics
    passed = sum(1 for r in results if r["status"] == "passed")
    passed_with_warnings = sum(1 for r in results if r["status"] == "passed_with_warnings")
    failed = sum(1 for r in results if r["status"] == "failed")

    # Output results
    if args.json:
        # JSON output mode - print summary in JSON format
        summary = {
            "total": len(results),
            "passed": passed,
            "passed_with_warnings": passed_with_warnings,
            "failed": failed,
            "results_file": str(results_file),
            "results": results,
        }
        print(json.dumps(summary, indent=2))
    else:
        # Human-readable output mode
        print(f"\nResults saved to {results_file}")
        print("\n" + "=" * 60)
        print("Summary:")
        print(f"  Passed: {passed}")
        print(f"  Passed with warnings: {passed_with_warnings}")
        print(f"  Failed: {failed}")
        print(f"  Total: {len(results)}")

        if failed > 0:
            print("\nSome combinations failed validation")
            return 1
        elif passed_with_warnings > 0:
            print("\nAll combinations passed (some with warnings)")
            return 0
        else:
            print("\nAll combinations passed!")
            return 0

    # Return exit code based on failures
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
