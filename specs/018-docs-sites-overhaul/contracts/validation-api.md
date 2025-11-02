# Documentation Validation API

**Feature**: 018-docs-sites-overhaul  
**Version**: 1.0  
**Date**: 2025-11-02

## Overview

The Documentation Validation API defines interfaces for validating documentation build artifacts, including link checking with exponential backoff retry logic and WCAG 2.1 Level AA accessibility validation.

## Core Interface

### DocumentationValidator

Main validation class for checking documentation quality.

```python
from typing import List, Optional
from pathlib import Path
from dataclasses import dataclass

@dataclass
class RetryConfig:
    """Retry configuration for external link validation."""
    max_attempts: int = 3  # Per clarification Q2
    initial_delay: float = 1.0  # seconds
    backoff_factor: float = 2.0  # Exponential backoff
    timeout: float = 10.0  # seconds per request
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number (0-indexed)."""
        return self.initial_delay * (self.backoff_factor ** attempt)
    
    def should_retry(self, attempt: int) -> bool:
        """True if should retry after given attempt."""
        return attempt < self.max_attempts

DEFAULT_RETRY = RetryConfig()

class DocumentationValidator:
    """Validate documentation build artifacts."""
    
    def validate_links(
        self,
        docs_dir: Path,
        retry_config: RetryConfig = DEFAULT_RETRY
    ) -> "LinkCheckResult":
        """
        Validate internal and external links with exponential backoff retry.
        
        Args:
            docs_dir: Built documentation directory (e.g., _build/html, .next, build)
            retry_config: Retry settings (default: 3 attempts with exponential backoff)
        
        Returns:
            LinkCheckResult with broken links after retries
        
        Examples:
            >>> validator = DocumentationValidator()
            >>> result = validator.validate_links(Path("_build/html"))
            >>> if not result.passed:
            ...     print(f"Found {len(result.broken_external)} broken external links")
        
        Notes:
            - Internal links checked first (no retry needed)
            - External links checked with exponential backoff (per clarification Q2)
            - Retries: 1s delay → 2s → 4s before marking as broken
        """
        pass
    
    def validate_accessibility(
        self,
        docs_dir: Path,
        standard: str = "WCAG21AA"
    ) -> "AccessibilityResult":
        """
        Validate WCAG 2.1 Level AA compliance (per clarification Q3).
        
        Args:
            docs_dir: Built documentation directory
            standard: Accessibility standard (default: WCAG 2.1 Level AA)
        
        Returns:
            AccessibilityResult with warnings (non-blocking per Q3) and critical errors
        
        Examples:
            >>> validator = DocumentationValidator()
            >>> result = validator.validate_accessibility(Path("_build/html"))
            >>> if result.warnings:
            ...     print(f"Accessibility warnings (non-blocking): {len(result.warnings)}")
            >>> if result.errors:
            ...     print(f"Critical accessibility errors: {len(result.errors)}")
        
        Notes:
            - Warnings are non-blocking per clarification Q3
            - Only critical errors halt the build
            - Uses axe-core for validation
        """
        pass
    
    def validate_images(
        self,
        docs_dir: Path
    ) -> "ImageValidationResult":
        """
        Validate image references (check for missing images).
        
        Args:
            docs_dir: Built documentation directory
        
        Returns:
            ImageValidationResult with list of missing images
        """
        pass
    
    def validate_cross_references(
        self,
        docs_dir: Path
    ) -> "CrossReferenceResult":
        """
        Validate internal cross-references (Sphinx :doc:, :ref:, etc.).
        
        Args:
            docs_dir: Built documentation directory
        
        Returns:
            CrossReferenceResult with invalid references
        """
        pass
```

## Link Checking

### LinkCheckResult

Result of link validation with retry details.

```python
@dataclass
class BrokenLink:
    """Details of a broken link after retries."""
    url: str
    source_file: Path
    source_line: int
    status_code: Optional[int]
    error_message: str
    retry_attempts: int  # Number of retry attempts made
    
    def __str__(self) -> str:
        return (
            f"Broken link: {self.url}\n"
            f"  Source: {self.source_file}:{self.source_line}\n"
            f"  Status: HTTP {self.status_code or 'N/A'}\n"
            f"  Error: {self.error_message}\n"
            f"  Retry attempts: {self.retry_attempts}"
        )

@dataclass
class LinkCheckResult:
    """Result of link validation."""
    passed: bool
    broken_internal: List[BrokenLink]
    broken_external: List[BrokenLink]  # After retries per clarification Q2
    total_checked: int
    
    @property
    def pass_rate(self) -> float:
        """Percentage of links that passed (0.0 - 1.0)."""
        total_broken = len(self.broken_internal) + len(self.broken_external)
        if self.total_checked == 0:
            return 1.0
        return 1.0 - (total_broken / self.total_checked)
    
    @property
    def has_broken_links(self) -> bool:
        """True if any links are broken."""
        return len(self.broken_internal) > 0 or len(self.broken_external) > 0
    
    def generate_report(self) -> str:
        """Generate human-readable link check report."""
        lines = ["# Link Check Report\n"]
        lines.append(f"**Status**: {'✅ PASSED' if self.passed else '❌ FAILED'}")
        lines.append(f"**Pass Rate**: {self.pass_rate:.1%} ({self.total_checked - len(self.broken_internal) - len(self.broken_external)}/{self.total_checked})\n")
        
        if self.broken_internal:
            lines.append(f"## Broken Internal Links ({len(self.broken_internal)})\n")
            for link in self.broken_internal[:20]:  # Limit to 20
                lines.append(f"- `{link.url}` in {link.source_file}:{link.source_line}")
            if len(self.broken_internal) > 20:
                lines.append(f"  *(and {len(self.broken_internal) - 20} more...)*")
        
        if self.broken_external:
            lines.append(f"\n## Broken External Links ({len(self.broken_external)})\n")
            lines.append("*After 3 retry attempts with exponential backoff (1s → 2s → 4s)*\n")
            for link in self.broken_external[:20]:  # Limit to 20
                lines.append(f"- `{link.url}` (HTTP {link.status_code or 'N/A'}, {link.retry_attempts} retries)")
            if len(self.broken_external) > 20:
                lines.append(f"  *(and {len(self.broken_external) - 20} more...)*")
        
        return "\n".join(lines)
```

### Exponential Backoff Implementation

```python
import time
import requests
from typing import Optional

def check_link_with_retry(
    url: str,
    retry_config: RetryConfig = DEFAULT_RETRY
) -> tuple[bool, Optional[int], int]:
    """
    Check link with exponential backoff retry logic.
    
    Args:
        url: URL to check
        retry_config: Retry configuration (default: 3 attempts, exponential backoff)
    
    Returns:
        Tuple of (success, status_code, attempts_made)
    
    Examples:
        >>> success, status, attempts = check_link_with_retry("https://example.com")
        >>> if not success:
        ...     print(f"Failed after {attempts} attempts with status {status}")
    
    Retry Schedule (default):
        - Attempt 0: Immediate
        - Attempt 1: After 1 second delay
        - Attempt 2: After 2 second delay
        - Attempt 3: After 4 second delay
        Total: 3 retries, 7 seconds maximum delay
    """
    attempt = 0
    last_status_code = None
    
    while attempt < retry_config.max_attempts:
        try:
            response = requests.head(
                url,
                timeout=retry_config.timeout,
                allow_redirects=True,
                headers={"User-Agent": "Riso-Docs-LinkChecker/1.0"}
            )
            if response.status_code < 400:
                return True, response.status_code, attempt + 1
            last_status_code = response.status_code
        except requests.RequestException as e:
            # Network error, timeout, etc.
            pass
        
        attempt += 1
        if retry_config.should_retry(attempt):
            delay = retry_config.get_delay(attempt)
            time.sleep(delay)
    
    return False, last_status_code, attempt
```

## Accessibility Validation

### AccessibilityResult

Result of WCAG 2.1 Level AA validation (per clarification Q3).

```python
@dataclass
class A11yWarning:
    """
    WCAG 2.1 Level AA accessibility warning.
    
    Per clarification Q3: Warnings are non-blocking (informational only).
    """
    rule_id: str  # e.g., "color-contrast", "heading-order"
    impact: Literal["minor", "moderate", "serious"]
    page_url: str
    element_selector: str
    help_text: str
    wcag_criteria: List[str]  # e.g., ["1.4.3", "1.4.6"]
    
    def __str__(self) -> str:
        return (
            f"[{self.rule_id}] {self.help_text}\n"
            f"  Impact: {self.impact}\n"
            f"  Page: {self.page_url}\n"
            f"  Element: {self.element_selector}\n"
            f"  WCAG: {', '.join(self.wcag_criteria)}"
        )

@dataclass
class A11yError:
    """
    Critical accessibility error (blocking).
    
    Only truly critical issues (e.g., missing alt text on all images,
    no landmarks, etc.) are treated as errors.
    """
    rule_id: str
    impact: Literal["critical"]
    page_url: str
    element_selector: str
    help_text: str
    
    def __str__(self) -> str:
        return (
            f"[{self.rule_id}] CRITICAL: {self.help_text}\n"
            f"  Page: {self.page_url}\n"
            f"  Element: {self.element_selector}"
        )

@dataclass
class AccessibilityResult:
    """Result of WCAG 2.1 Level AA validation."""
    warnings: List[A11yWarning]  # Non-blocking per clarification Q3
    errors: List[A11yError]       # Critical issues only
    pages_checked: int
    
    @property
    def has_critical_errors(self) -> bool:
        """True if any critical accessibility errors found."""
        return len(self.errors) > 0
    
    @property
    def warning_count_by_impact(self) -> dict[str, int]:
        """Count warnings by impact level."""
        from collections import Counter
        return dict(Counter(w.impact for w in self.warnings))
    
    def generate_report(self) -> str:
        """Generate human-readable accessibility report."""
        lines = ["# Accessibility Validation Report (WCAG 2.1 Level AA)\n"]
        lines.append(f"**Pages Checked**: {self.pages_checked}")
        lines.append(f"**Warnings**: {len(self.warnings)} (non-blocking)")
        lines.append(f"**Critical Errors**: {len(self.errors)}\n")
        
        if self.warnings:
            impact_counts = self.warning_count_by_impact
            lines.append("## Warnings by Impact (Non-blocking)")
            for impact in ["serious", "moderate", "minor"]:
                count = impact_counts.get(impact, 0)
                if count > 0:
                    lines.append(f"- **{impact.title()}**: {count}")
            
            lines.append("\n### Sample Warnings (First 10)\n")
            for warning in self.warnings[:10]:
                lines.append(f"- [{warning.rule_id}] {warning.help_text} (Impact: {warning.impact})")
            if len(self.warnings) > 10:
                lines.append(f"  *(and {len(self.warnings) - 10} more...)*")
        
        if self.errors:
            lines.append("\n## Critical Errors (Blocking)\n")
            for error in self.errors:
                lines.append(f"- [{error.rule_id}] {error.help_text}")
                lines.append(f"  Page: {error.page_url}")
                lines.append(f"  Element: {error.element_selector}")
        
        return "\n".join(lines)
```

### Accessibility Validation Implementation

```python
from pytest_axe import Axe
from selenium import webdriver

def validate_page_accessibility(
    page_url: str,
    driver: webdriver.Chrome
) -> tuple[List[A11yWarning], List[A11yError]]:
    """
    Validate single page for WCAG 2.1 Level AA compliance using axe-core.
    
    Args:
        page_url: URL of page to validate
        driver: Selenium WebDriver instance
    
    Returns:
        Tuple of (warnings, errors)
    
    Examples:
        >>> driver = webdriver.Chrome()
        >>> warnings, errors = validate_page_accessibility("http://localhost:8000", driver)
        >>> print(f"Found {len(warnings)} warnings (non-blocking)")
    """
    driver.get(page_url)
    axe = Axe(driver)
    axe.inject()
    results = axe.run()
    
    warnings = []
    errors = []
    
    # Convert axe violations to warnings (non-blocking per Q3)
    for violation in results.get("violations", []):
        if violation.get("impact") == "critical":
            # Only truly critical issues are blocking
            for node in violation.get("nodes", []):
                errors.append(A11yError(
                    rule_id=violation["id"],
                    impact="critical",
                    page_url=page_url,
                    element_selector=node.get("target", ["unknown"])[0],
                    help_text=violation.get("help", "Unknown error")
                ))
        else:
            # All other violations are warnings (non-blocking)
            for node in violation.get("nodes", []):
                warnings.append(A11yWarning(
                    rule_id=violation["id"],
                    impact=violation.get("impact", "moderate"),
                    page_url=page_url,
                    element_selector=node.get("target", ["unknown"])[0],
                    help_text=violation.get("help", "Unknown warning"),
                    wcag_criteria=violation.get("tags", [])
                ))
    
    return warnings, errors
```

## Image Validation

### ImageValidationResult

```python
@dataclass
class ImageValidationResult:
    """Result of image reference validation."""
    missing_images: List[str]  # Paths to missing image files
    total_checked: int
    
    @property
    def passed(self) -> bool:
        """True if no missing images."""
        return len(self.missing_images) == 0
    
    def generate_report(self) -> str:
        """Generate human-readable image validation report."""
        if self.passed:
            return f"✅ All {self.total_checked} image references valid"
        
        lines = [f"❌ Found {len(self.missing_images)} missing images:"]
        for image in self.missing_images[:20]:
            lines.append(f"  - {image}")
        if len(self.missing_images) > 20:
            lines.append(f"  *(and {len(self.missing_images) - 20} more...)*")
        return "\n".join(lines)
```

## Cross-Reference Validation

### CrossReferenceResult

```python
@dataclass
class InvalidCrossRef:
    """Details of an invalid cross-reference."""
    ref_type: str  # e.g., "doc", "ref", "numref"
    target: str
    source_file: Path
    source_line: int
    
    def __str__(self) -> str:
        return f":{self.ref_type}:`{self.target}` in {self.source_file}:{self.source_line}"

@dataclass
class CrossReferenceResult:
    """Result of cross-reference validation."""
    invalid_refs: List[InvalidCrossRef]
    total_checked: int
    
    @property
    def passed(self) -> bool:
        """True if no invalid cross-references."""
        return len(self.invalid_refs) == 0
    
    def generate_report(self) -> str:
        """Generate human-readable cross-reference validation report."""
        if self.passed:
            return f"✅ All {self.total_checked} cross-references valid"
        
        lines = [f"❌ Found {len(self.invalid_refs)} invalid cross-references:"]
        for ref in self.invalid_refs[:20]:
            lines.append(f"  - {ref}")
        if len(self.invalid_refs) > 20:
            lines.append(f"  *(and {len(self.invalid_refs) - 20} more...)*")
        return "\n".join(lines)
```

## Usage Examples

### Example 1: Complete Documentation Validation

```python
from pathlib import Path
from riso.docs.validation import DocumentationValidator, DEFAULT_RETRY

validator = DocumentationValidator()
docs_dir = Path("_build/html")

# Validate links with retry
print("Validating links...")
link_result = validator.validate_links(docs_dir, retry_config=DEFAULT_RETRY)
print(link_result.generate_report())

if not link_result.passed:
    print("\n❌ Link check failed")
    sys.exit(1)

# Validate accessibility (non-blocking warnings)
print("\nValidating accessibility...")
a11y_result = validator.validate_accessibility(docs_dir)
print(a11y_result.generate_report())

if a11y_result.has_critical_errors:
    print("\n❌ Critical accessibility errors found")
    sys.exit(1)

if a11y_result.warnings:
    print(f"\n⚠️  {len(a11y_result.warnings)} accessibility warnings (non-blocking)")

# Validate images
print("\nValidating images...")
image_result = validator.validate_images(docs_dir)
print(image_result.generate_report())

if not image_result.passed:
    print("\n❌ Image validation failed")
    sys.exit(1)

print("\n✅ All validation checks passed")
```

### Example 2: Custom Retry Configuration

```python
from riso.docs.validation import RetryConfig

# More aggressive retry for flaky external services
aggressive_retry = RetryConfig(
    max_attempts=5,  # 5 attempts instead of 3
    initial_delay=2.0,  # Start with 2s delay
    backoff_factor=2.0,  # Exponential backoff (2s → 4s → 8s → 16s → 32s)
    timeout=15.0  # 15s timeout per request
)

link_result = validator.validate_links(docs_dir, retry_config=aggressive_retry)
```

### Example 3: CI Integration

```python
# In GitHub Actions workflow validation script
import sys
from pathlib import Path
from riso.docs.validation import DocumentationValidator

def main():
    """CI validation entrypoint."""
    validator = DocumentationValidator()
    docs_dir = Path(os.getenv("DOCS_DIR", "_build/html"))
    
    # Run all validations
    link_result = validator.validate_links(docs_dir)
    a11y_result = validator.validate_accessibility(docs_dir)
    image_result = validator.validate_images(docs_dir)
    
    # Write reports to artifacts
    Path("validation-report.md").write_text(
        link_result.generate_report() + "\n\n" +
        a11y_result.generate_report() + "\n\n" +
        image_result.generate_report()
    )
    
    # Exit with failure if critical errors
    if not link_result.passed or a11y_result.has_critical_errors or not image_result.passed:
        print("❌ Validation failed")
        sys.exit(1)
    
    # Log warnings but don't fail
    if a11y_result.warnings:
        print(f"⚠️  {len(a11y_result.warnings)} accessibility warnings (non-blocking)")
    
    print("✅ Validation passed")
    sys.exit(0)

if __name__ == "__main__":
    main()
```

---

**API Version**: 1.0  
**Status**: Ready for Implementation  
**Related**: See `transformation-api.md` for content transformation interfaces
