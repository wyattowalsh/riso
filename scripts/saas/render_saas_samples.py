#!/usr/bin/env python3
"""
Render SaaS Starter sample projects.

This script creates configuration files for each recommended technology stack
to validate template functionality and provide examples.

Usage:
    uv run python scripts/saas/render_saas_samples.py
    uv run python scripts/saas/render_saas_samples.py --stack vercel-starter
"""

import argparse
import json
import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT))

from scripts.lib.logger import logger, configure_logging

SAMPLES_DIR = WORKSPACE_ROOT / "samples" / "saas-starter"

# Recommended stacks configuration
RECOMMENDED_STACKS = {
    "vercel-starter": {
        "name": "Vercel Starter Stack",
        "description": "Best developer experience with Next.js on Vercel",
        "config": {
            "project_name": "SaaS Vercel Starter",
            "project_slug": "saas-vercel-starter",
            "saas_starter_module": "enabled",
            "saas_runtime": "nextjs-16",
            "saas_hosting": "vercel",
            "saas_database": "neon",
            "saas_orm": "prisma",
            "saas_auth": "clerk",
            "saas_enterprise_bridge": "none",
            "saas_billing": "stripe",
            "saas_jobs": "trigger",
            "saas_email": "resend",
            "saas_analytics": "posthog",
            "saas_ai": "openai",
            "saas_storage": "r2",
            "saas_cicd": "github",
            "saas_observability_structured_logging": True,
            "saas_observability_sentry": True,
            "saas_observability_otel": False,
            "saas_fixtures": "enabled",
            "saas_factories": "enabled",
        },
    },
    "edge-optimized": {
        "name": "Edge-Optimized Stack",
        "description": "Cloudflare Workers + Remix for global edge deployment",
        "config": {
            "project_name": "SaaS Edge Optimized",
            "project_slug": "saas-edge-optimized",
            "saas_starter_module": "enabled",
            "saas_runtime": "remix-2",
            "saas_hosting": "cloudflare",
            "saas_database": "neon",
            "saas_orm": "drizzle",
            "saas_auth": "clerk",
            "saas_enterprise_bridge": "none",
            "saas_billing": "stripe",
            "saas_jobs": "inngest",
            "saas_email": "resend",
            "saas_analytics": "posthog",
            "saas_ai": "anthropic",
            "saas_storage": "r2",
            "saas_cicd": "github",
            "saas_observability_structured_logging": True,
            "saas_observability_sentry": True,
            "saas_observability_otel": True,
            "saas_fixtures": "enabled",
            "saas_factories": "enabled",
        },
    },
    "all-in-one": {
        "name": "All-in-One Platform Stack",
        "description": "Supabase for database, auth, and storage",
        "config": {
            "project_name": "SaaS All-in-One",
            "project_slug": "saas-all-in-one",
            "saas_starter_module": "enabled",
            "saas_runtime": "nextjs-16",
            "saas_hosting": "vercel",
            "saas_database": "supabase",
            "saas_orm": "prisma",
            "saas_auth": "authjs",
            "saas_enterprise_bridge": "none",
            "saas_billing": "paddle",
            "saas_jobs": "trigger",
            "saas_email": "postmark",
            "saas_analytics": "amplitude",
            "saas_ai": "openai",
            "saas_storage": "supabase-storage",
            "saas_cicd": "github",
            "saas_observability_structured_logging": True,
            "saas_observability_sentry": True,
            "saas_observability_otel": False,
            "saas_fixtures": "enabled",
            "saas_factories": "enabled",
        },
    },
    "enterprise-ready": {
        "name": "Enterprise-Ready Stack",
        "description": "Production-grade with advanced observability",
        "config": {
            "project_name": "SaaS Enterprise",
            "project_slug": "saas-enterprise",
            "saas_starter_module": "enabled",
            "saas_runtime": "nextjs-16",
            "saas_hosting": "vercel",
            "saas_database": "neon",
            "saas_orm": "prisma",
            "saas_auth": "clerk",
            "saas_enterprise_bridge": "none",
            "saas_billing": "stripe",
            "saas_jobs": "trigger",
            "saas_email": "resend",
            "saas_analytics": "amplitude",
            "saas_ai": "anthropic",
            "saas_storage": "r2",
            "saas_cicd": "github",
            "saas_observability_structured_logging": True,
            "saas_observability_sentry": True,
            "saas_observability_otel": True,
            "saas_fixtures": "enabled",
            "saas_factories": "enabled",
        },
    },
}


def create_copier_answers_file(stack_key: str, config: dict) -> Path:
    """Create a copier-answers.yml file for the stack."""
    answers_dir = SAMPLES_DIR / stack_key
    answers_dir.mkdir(parents=True, exist_ok=True)
    answers_file = answers_dir / "copier-answers.yml"
    
    # Convert config to YAML format
    with open(answers_file, "w") as f:
        f.write(f"# Copier Answers: {RECOMMENDED_STACKS[stack_key]['name']}\n")
        f.write(f"# {RECOMMENDED_STACKS[stack_key]['description']}\n\n")
        for key, value in config.items():
            if isinstance(value, bool):
                f.write(f"{key}: {str(value).lower()}\n")
            else:
                f.write(f"{key}: {value}\n")
    
    return answers_file


def render_sample(stack_key: str, stack_config: dict) -> dict:
    """Configure a sample project for the given stack."""
    logger.info(f"Configuring: {stack_config['name']}")
    logger.info(f"   {stack_config['description']}")
    
    try:
        # Create copier-answers.yml
        answers_file = create_copier_answers_file(stack_key, stack_config["config"])
        logger.info(f"   Created: {answers_file.relative_to(WORKSPACE_ROOT)}")
        
        # Create metadata file
        metadata = {
            "stack": stack_key,
            "name": stack_config["name"],
            "description": stack_config["description"],
            "status": "configured",
            "config": stack_config["config"],
        }
        
        metadata_file = SAMPLES_DIR / stack_key / "metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"   Created: {metadata_file.relative_to(WORKSPACE_ROOT)}")
        
        return {
            "stack": stack_key,
            "status": "configured",
            "message": "Configuration files created",
            "answers_file": str(answers_file.relative_to(WORKSPACE_ROOT)),
            "metadata_file": str(metadata_file.relative_to(WORKSPACE_ROOT)),
        }
        
    except Exception as e:
        logger.error(f"   Error: {e}")
        return {
            "stack": stack_key,
            "status": "failed",
            "error": str(e),
        }


def main() -> int:
    """Main render entry point."""
    configure_logging()

    parser = argparse.ArgumentParser(
        description="Configure SaaS Starter sample projects"
    )
    parser.add_argument(
        "--stack",
        choices=list(RECOMMENDED_STACKS.keys()),
        help="Configure only the specified stack (default: configure all)",
    )
    args = parser.parse_args()

    logger.info("SaaS Starter Sample Configuration")
    logger.info("=" * 60)
    
    # Determine which stacks to configure
    if args.stack:
        stacks_to_configure = {args.stack: RECOMMENDED_STACKS[args.stack]}
    else:
        stacks_to_configure = RECOMMENDED_STACKS

    logger.info(f"Configuring {len(stacks_to_configure)} stack(s)")
    
    # Configure each stack
    results = []
    for stack_key, stack_config in stacks_to_configure.items():
        result = render_sample(stack_key, stack_config)
        results.append(result)
    
    # Save results
    results_file = SAMPLES_DIR / "configuration-results.json"
    results_file.parent.mkdir(parents=True, exist_ok=True)
    with results_file.open("w") as f:
        json.dump(results, f, indent=2)

    logger.info(f"Results saved to {results_file.relative_to(WORKSPACE_ROOT)}")
    
    # Summary
    configured = sum(1 for r in results if r["status"] == "configured")
    failed = sum(1 for r in results if r["status"] == "failed")

    logger.info("=" * 60)
    logger.info("Summary:")
    logger.info(f"  Configured: {configured}")
    logger.info(f"  Failed: {failed}")
    logger.info(f"  Total: {len(results)}")
    
    if failed > 0:
        logger.warning("Some configurations failed")
        return 1

    logger.info("All stacks configured successfully!")
    logger.info("Next steps:")
    logger.info("  1. Render a sample: copier copy . samples/saas-starter/<stack>/render -f samples/saas-starter/<stack>/copier-answers.yml")
    logger.info("  2. Install deps: cd samples/saas-starter/<stack>/render && pnpm install")
    logger.info("  3. Run tests: pnpm run test")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
