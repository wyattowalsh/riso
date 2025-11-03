#!/usr/bin/env python3
"""
Documentation configuration comparison utility.
Feature: 018-docs-sites-overhaul

Compare documentation configurations between projects or versions.

Usage:
    python scripts/ci/docs_config_compare.py project1/ project2/
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple


class ConfigComparison:
    """Compare documentation configurations."""

    def __init__(self, path1: Path, path2: Path):
        self.path1 = path1
        self.path2 = path2
        self.config1 = self._load_config(path1)
        self.config2 = self._load_config(path2)

    def _load_config(self, path: Path) -> Dict:
        """Load configuration from path."""
        answers_file = path / ".copier-answers.yml"
        if not answers_file.exists():
            return {}
        
        config = {}
        for line in answers_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            key, value = line.split(":", 1)
            if key.strip().startswith("docs_"):
                config[key.strip()] = value.strip()
        return config

    def compare(self) -> Tuple[List, List, List]:
        """
        Compare configurations.
        
        Returns:
            Tuple of (differences, only_in_1, only_in_2)
        """
        differences = []
        only_in_1 = []
        only_in_2 = []
        
        all_keys = set(self.config1.keys()) | set(self.config2.keys())
        
        for key in sorted(all_keys):
            if key in self.config1 and key in self.config2:
                if self.config1[key] != self.config2[key]:
                    differences.append((key, self.config1[key], self.config2[key]))
            elif key in self.config1:
                only_in_1.append((key, self.config1[key]))
            else:
                only_in_2.append((key, self.config2[key]))
        
        return differences, only_in_1, only_in_2

    def print_comparison(self):
        """Print formatted comparison."""
        print("=" * 80)
        print("Documentation Configuration Comparison")
        print("=" * 80)
        print(f"\nProject 1: {self.path1}")
        print(f"Project 2: {self.path2}\n")
        
        differences, only_in_1, only_in_2 = self.compare()
        
        if not differences and not only_in_1 and not only_in_2:
            print("✅ Configurations are identical!")
            return
        
        if differences:
            print("📊 Differences:")
            print("-" * 80)
            for key, val1, val2 in differences:
                print(f"  {key}:")
                print(f"    Project 1: {val1}")
                print(f"    Project 2: {val2}")
            print()
        
        if only_in_1:
            print("📌 Only in Project 1:")
            print("-" * 80)
            for key, value in only_in_1:
                print(f"  {key}: {value}")
            print()
        
        if only_in_2:
            print("📌 Only in Project 2:")
            print("-" * 80)
            for key, value in only_in_2:
                print(f"  {key}: {value}")
            print()
        
        print("=" * 80)
        print(f"Summary: {len(differences)} differences, "
              f"{len(only_in_1)} unique to Project 1, "
              f"{len(only_in_2)} unique to Project 2")
        print("=" * 80)


def main():
    """Main entry point."""
    if len(sys.argv) != 3:
        print("Usage: docs_config_compare.py <project1> <project2>")
        print("\nExample:")
        print("  python scripts/ci/docs_config_compare.py samples/docs-sphinx samples/docs-fumadocs")
        sys.exit(1)
    
    path1 = Path(sys.argv[1])
    path2 = Path(sys.argv[2])
    
    if not path1.exists():
        print(f"Error: {path1} does not exist")
        sys.exit(1)
    
    if not path2.exists():
        print(f"Error: {path2} does not exist")
        sys.exit(1)
    
    comparison = ConfigComparison(path1, path2)
    comparison.print_comparison()


if __name__ == "__main__":
    main()
