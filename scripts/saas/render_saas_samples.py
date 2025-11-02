#!/usr/bin/env python3
"""
Render SaaS Starter sample projects.

This script renders sample projects for each recommended technology stack
to validate template functionality and provide examples.

Usage:
    uv run python scripts/saas/render_saas_samples.py
    uv run python scripts/saas/render_saas_samples.py --stack vercel-starter
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Recommended stacks configuration
RECOMMENDED_STACKS = {
    "vercel-starter": {
        "name": "Vercel Starter Stack",
        "description": "Best developer experience, fastest setup, Vercel ecosystem",
        "answers_file": "samples/saas-starter/nextjs-vercel-neon-clerk/copier-answers.yml",
    },
    "edge-optimized": {
        "name": "Edge-Optimized Stack",
        "description": "Global edge deployment, low latency, cost-effective",
        "answers_file": "samples/saas-starter/remix-cloudflare-neon-drizzle/copier-answers.yml",
    },
    "all-in-one": {
        "name": "All-in-One Platform Stack",
        "description": "Single vendor (Supabase + Vercel), simplified operations",
        "answers_file": "samples/saas-starter/nextjs-vercel-supabase-clerk/copier-answers.yml",
    },
    "enterprise-ready": {
        "name": "Enterprise-Ready Stack",
        "description": "SSO, SCIM, compliance-focused, mature services",
        "answers_file": "samples/saas-starter/nextjs-vercel-neon-clerk-workos/copier-answers.yml",
    },
}


def render_sample(stack_key: str, stack_config: dict) -> dict:
    """Render a sample project for the given stack."""
    print(f"\n?? Rendering: {stack_config['name']}")
    print(f"   {stack_config['description']}")
    
    answers_file = Path(stack_config["answers_file"])
    if not answers_file.exists():
        return {
            "stack": stack_key,
            "status": "failed",
            "error": f"Answers file not found: {answers_file}",
        }
    
    # TODO: Implement rendering logic
    # render_dir = answers_file.parent / "render"
    # subprocess.run(["copier", "copy", "--answers-file", str(answers_file), ...])
    
    return {
        "stack": stack_key,
        "status": "skipped",
        "message": "Rendering not yet implemented",
    }


def main() -> int:
    """Main render entry point."""
    parser = argparse.ArgumentParser(
        description="Render SaaS Starter sample projects"
    )
    parser.add_argument(
        "--stack",
        choices=list(RECOMMENDED_STACKS.keys()),
        help="Render only the specified stack (default: render all)",
    )
    args = parser.parse_args()
    
    print("?? SaaS Starter Sample Renderer")
    print("=" * 60)
    
    # Determine which stacks to render
    if args.stack:
        stacks_to_render = {args.stack: RECOMMENDED_STACKS[args.stack]}
    else:
        stacks_to_render = RECOMMENDED_STACKS
    
    print(f"\n?? Rendering {len(stacks_to_render)} stack(s)")
    
    # Render each stack
    results = []
    for stack_key, stack_config in stacks_to_render.items():
        result = render_sample(stack_key, stack_config)
        results.append(result)
    
    # Save results
    results_file = Path("samples/saas-starter/render-results.json")
    results_file.parent.mkdir(parents=True, exist_ok=True)
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
        print("\n??  Some renders failed")
        return 1
    
    if skipped == len(results):
        print("\n??  Rendering not yet implemented (all samples skipped)")
        return 0  # Don't fail for not-yet-implemented functionality
    
    print("\n? All samples rendered successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
