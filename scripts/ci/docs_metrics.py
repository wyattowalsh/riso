#!/usr/bin/env python3
"""
Documentation metrics collector.
Feature: 018-docs-sites-overhaul

Collect metrics about documentation:
- Page count
- Word count
- Build time
- Artifact size
- Link count
- Image count

Usage:
    python scripts/ci/docs_metrics.py [--output metrics.json]
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List


class MetricsCollector:
    """Collect documentation metrics."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.metrics = {}

    def collect(self, framework: str) -> Dict:
        """
        Collect all metrics.
        
        Args:
            framework: Documentation framework
            
        Returns:
            Metrics dictionary
        """
        print("📊 Collecting documentation metrics...")
        
        self.metrics = {
            "framework": framework,
            "timestamp": time.time(),
            "pages": self._count_pages(framework),
            "words": self._count_words(framework),
            "links": self._count_links(framework),
            "images": self._count_images(framework),
            "size_mb": self._calculate_size(framework),
        }
        
        return self.metrics

    def _count_pages(self, framework: str) -> int:
        """Count documentation pages."""
        if framework == "sphinx-shibuya":
            docs_dir = self.project_root / "docs"
            if not docs_dir.exists():
                return 0
            return len(list(docs_dir.rglob("*.rst")))
        elif framework == "fumadocs":
            content_dir = self.project_root / "apps/docs-fumadocs/content"
            if not content_dir.exists():
                return 0
            return len(list(content_dir.rglob("*.mdx")))
        elif framework == "docusaurus":
            docs_dir = self.project_root / "apps/docs-docusaurus/docs"
            if not docs_dir.exists():
                return 0
            return len(list(docs_dir.rglob("*.md")))
        return 0

    def _count_words(self, framework: str) -> int:
        """Count total words in documentation."""
        total_words = 0
        
        if framework == "sphinx-shibuya":
            docs_dir = self.project_root / "docs"
            if docs_dir.exists():
                for rst_file in docs_dir.rglob("*.rst"):
                    content = rst_file.read_text(errors='ignore')
                    total_words += len(content.split())
        elif framework == "fumadocs":
            content_dir = self.project_root / "apps/docs-fumadocs/content"
            if content_dir.exists():
                for mdx_file in content_dir.rglob("*.mdx"):
                    content = mdx_file.read_text(errors='ignore')
                    total_words += len(content.split())
        elif framework == "docusaurus":
            docs_dir = self.project_root / "apps/docs-docusaurus/docs"
            if docs_dir.exists():
                for md_file in docs_dir.rglob("*.md"):
                    content = md_file.read_text(errors='ignore')
                    total_words += len(content.split())
        
        return total_words

    def _count_links(self, framework: str) -> int:
        """Count links in documentation."""
        import re
        total_links = 0
        
        if framework == "sphinx-shibuya":
            docs_dir = self.project_root / "docs"
            if docs_dir.exists():
                for rst_file in docs_dir.rglob("*.rst"):
                    content = rst_file.read_text(errors='ignore')
                    # Count :doc:, :ref:, and http(s):// links
                    total_links += len(re.findall(r':doc:`[^`]+`', content))
                    total_links += len(re.findall(r':ref:`[^`]+`', content))
                    total_links += len(re.findall(r'https?://\S+', content))
        else:
            # Markdown-based frameworks
            if framework == "fumadocs":
                content_dir = self.project_root / "apps/docs-fumadocs/content"
                pattern = "*.mdx"
            else:
                content_dir = self.project_root / "apps/docs-docusaurus/docs"
                pattern = "*.md"
            
            if content_dir.exists():
                for doc_file in content_dir.rglob(pattern):
                    content = doc_file.read_text(errors='ignore')
                    # Count [text](url) style links
                    total_links += len(re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content))
        
        return total_links

    def _count_images(self, framework: str) -> int:
        """Count images in documentation."""
        import re
        total_images = 0
        
        if framework == "sphinx-shibuya":
            docs_dir = self.project_root / "docs"
            if docs_dir.exists():
                for rst_file in docs_dir.rglob("*.rst"):
                    content = rst_file.read_text(errors='ignore')
                    # Count .. image:: and .. figure::
                    total_images += len(re.findall(r'\.\. (image|figure)::', content))
        else:
            # Markdown-based frameworks
            if framework == "fumadocs":
                content_dir = self.project_root / "apps/docs-fumadocs/content"
                pattern = "*.mdx"
            else:
                content_dir = self.project_root / "apps/docs-docusaurus/docs"
                pattern = "*.md"
            
            if content_dir.exists():
                for doc_file in content_dir.rglob(pattern):
                    content = doc_file.read_text(errors='ignore')
                    # Count ![alt](url) style images
                    total_images += len(re.findall(r'!\[([^\]]*)\]\(([^\)]+)\)', content))
        
        return total_images

    def _calculate_size(self, framework: str) -> float:
        """Calculate documentation source size in MB."""
        total_size = 0
        
        if framework == "sphinx-shibuya":
            docs_dir = self.project_root / "docs"
            if docs_dir.exists():
                for file in docs_dir.rglob("*"):
                    if file.is_file():
                        total_size += file.stat().st_size
        elif framework == "fumadocs":
            content_dir = self.project_root / "apps/docs-fumadocs"
            if content_dir.exists():
                for file in content_dir.rglob("*"):
                    if file.is_file() and not str(file).startswith(str(content_dir / "node_modules")):
                        total_size += file.stat().st_size
        elif framework == "docusaurus":
            docs_dir = self.project_root / "apps/docs-docusaurus"
            if docs_dir.exists():
                for file in docs_dir.rglob("*"):
                    if file.is_file() and not str(file).startswith(str(docs_dir / "node_modules")):
                        total_size += file.stat().st_size
        
        return total_size / (1024 * 1024)  # Convert to MB

    def print_metrics(self):
        """Print formatted metrics."""
        print("\n" + "=" * 60)
        print("Documentation Metrics")
        print("=" * 60)
        print(f"Framework: {self.metrics['framework']}")
        print(f"Pages: {self.metrics['pages']}")
        print(f"Words: {self.metrics['words']:,}")
        print(f"Links: {self.metrics['links']}")
        print(f"Images: {self.metrics['images']}")
        print(f"Source Size: {self.metrics['size_mb']:.2f} MB")
        
        # Calculate derived metrics
        if self.metrics['pages'] > 0:
            avg_words = self.metrics['words'] / self.metrics['pages']
            print(f"Avg Words/Page: {avg_words:.0f}")
        
        print("=" * 60)

    def save_metrics(self, output_file: Path):
        """Save metrics to JSON file."""
        with open(output_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        print(f"\n✅ Metrics saved to {output_file}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Collect documentation metrics")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output JSON file for metrics"
    )
    parser.add_argument(
        "--framework",
        choices=["sphinx-shibuya", "fumadocs", "docusaurus"],
        help="Documentation framework (auto-detected if not specified)"
    )
    
    args = parser.parse_args()
    
    # Auto-detect framework if not specified
    if not args.framework:
        if (args.project_root / "Makefile.docs").exists():
            args.framework = "sphinx-shibuya"
        elif (args.project_root / "apps/docs-fumadocs").exists():
            args.framework = "fumadocs"
        elif (args.project_root / "apps/docs-docusaurus").exists():
            args.framework = "docusaurus"
        else:
            print("Error: Could not auto-detect framework")
            sys.exit(1)
    
    collector = MetricsCollector(args.project_root)
    collector.collect(args.framework)
    collector.print_metrics()
    
    if args.output:
        collector.save_metrics(args.output)


if __name__ == "__main__":
    main()
