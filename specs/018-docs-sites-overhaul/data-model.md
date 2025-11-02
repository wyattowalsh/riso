# Data Model: Documentation Sites Overhaul

**Feature**: 018-docs-sites-overhaul  
**Date**: 2025-11-02  
**Status**: Phase 1 Design

## Overview

This data model defines the entities, relationships, and state transitions for documentation site configuration, content transformation, build artifacts, and validation results within the Riso template system.

## Core Entities

### 1. DocumentationConfiguration

Represents user-selected documentation framework and configuration options from Copier prompts.

```python
from typing import Literal, List
from dataclasses import dataclass

@dataclass
class DocumentationConfiguration:
    """User-selected documentation configuration from Copier prompts."""
    
    # Core selections
    framework: Literal["fumadocs", "sphinx-shibuya", "docusaurus", "none"]
    theme_mode: Literal["light", "dark", "auto"]
    search_provider: Literal["none", "local", "algolia", "typesense"]
    api_playground: Literal["disabled", "swagger", "redoc", "both"]
    deploy_target: Literal["github-pages", "netlify", "vercel", "cloudflare"]
    versioning_enabled: bool
    interactive_features_enabled: bool
    
    # Derived properties
    @property
    def requires_node(self) -> bool:
        """True if framework requires Node.js tooling."""
        return self.framework in ["fumadocs", "docusaurus"]
    
    @property
    def requires_python(self) -> bool:
        """True if framework requires Python tooling."""
        return self.framework == "sphinx-shibuya"
    
    @property
    def search_config_template(self) -> str:
        """Path to search configuration template for selected provider."""
        if self.search_provider == "none":
            return ""
        return f"template/files/shared/docs/search/{self.search_provider}.config.jinja"
    
    @property
    def deployment_config_files(self) -> List[str]:
        """List of deployment configuration files to generate."""
        mapping = {
            "github-pages": [".github/workflows/deploy-docs.yml"],
            "netlify": ["netlify.toml"],
            "vercel": ["vercel.json"],
            "cloudflare": ["wrangler.toml"],
        }
        return mapping.get(self.deploy_target, [])
    
    def validate(self) -> List[str]:
        """Validate configuration consistency; return error messages."""
        errors = []
        
        if self.framework == "none":
            if self.theme_mode != "auto":
                errors.append("theme_mode must be 'auto' when docs_site is 'none'")
            if self.search_provider != "none":
                errors.append("search_provider must be 'none' when docs_site is 'none'")
        
        if self.api_playground != "disabled" and self.framework == "none":
            errors.append("api_playground requires docs_site != 'none'")
        
        return errors
```

### 2. ContentTransformationRule

Defines rules for transforming documentation content between formats (Markdown ↔ MDX ↔ RST).

```python
from typing import Callable, List
from enum import Enum

class ContentFormat(Enum):
    MARKDOWN = "markdown"
    MDX = "mdx"
    RST = "rst"

class TransformationFailureMode(Enum):
    ERROR = "error"    # Halt build immediately (per clarification Q1)
    WARN = "warn"      # Log warning and continue
    SKIP = "skip"      # Skip transformation, preserve original

@dataclass
class ContentTransformationRule:
    """Rule for transforming content between documentation formats."""
    
    source_format: ContentFormat
    target_format: ContentFormat
    transformation_fn: Callable[[str], str]
    supported_extensions: List[str]  # e.g., ["mermaid", "code-tabs", "admonitions"]
    failure_mode: TransformationFailureMode
    
    def apply(self, content: str, file_path: str) -> "TransformationResult":
        """Apply transformation rule to content."""
        try:
            transformed_content = self.transformation_fn(content)
            return TransformationResult(
                success=True,
                content=transformed_content,
                errors=[],
                warnings=[]
            )
        except Exception as e:
            if self.failure_mode == TransformationFailureMode.ERROR:
                return TransformationResult(
                    success=False,
                    content=None,
                    errors=[TransformationError(
                        file_path=file_path,
                        line_number=self._extract_line_number(e),
                        unsupported_syntax=str(e),
                        suggestion=self._get_manual_override_suggestion(e)
                    )],
                    warnings=[]
                )
            elif self.failure_mode == TransformationFailureMode.WARN:
                return TransformationResult(
                    success=True,
                    content=content,  # Return original
                    errors=[],
                    warnings=[f"Transformation warning in {file_path}: {e}"]
                )
            else:  # SKIP
                return TransformationResult(
                    success=True,
                    content=content,  # Return original
                    errors=[],
                    warnings=[]
                )
    
    def _extract_line_number(self, exception: Exception) -> int:
        """Extract line number from exception if available."""
        # Implementation would parse traceback
        return 0
    
    def _get_manual_override_suggestion(self, exception: Exception) -> str:
        """Provide manual override instructions for common failures."""
        # Implementation would map exception types to suggestions
        return "Please manually convert this syntax for the target framework."
```

### 3. TransformationResult

Result of content transformation operation.

```python
@dataclass
class TransformationError:
    """Error encountered during content transformation."""
    file_path: str
    line_number: int
    unsupported_syntax: str
    suggestion: str  # Manual override instructions

@dataclass
class TransformationResult:
    """Result of content transformation."""
    success: bool
    content: str | None
    errors: List[TransformationError]
    warnings: List[str]
    
    def log_errors(self) -> None:
        """Log all errors with details."""
        for error in self.errors:
            print(f"ERROR in {error.file_path}:{error.line_number}")
            print(f"  Unsupported syntax: {error.unsupported_syntax}")
            print(f"  Suggestion: {error.suggestion}")
    
    def log_warnings(self) -> None:
        """Log all warnings."""
        for warning in self.warnings:
            print(f"WARNING: {warning}")
```

### 4. DocumentationBuildArtifact

Represents the output of a documentation build process.

```python
from datetime import datetime
from pathlib import Path

@dataclass
class DocumentationBuildArtifact:
    """Output artifact from documentation build."""
    
    framework: str
    build_timestamp: datetime
    build_duration_seconds: float
    output_directory: Path
    artifact_size_bytes: int
    validation_results: "ValidationResults"
    
    @property
    def build_success(self) -> bool:
        """True if build completed without errors."""
        return (
            self.output_directory.exists() and
            self.artifact_size_bytes > 0 and
            self.validation_results.has_no_critical_errors
        )
    
    def to_smoke_test_result(self) -> dict:
        """Convert to smoke test result format for samples/*/smoke-results.json."""
        return {
            "module": "docs_site",
            "framework": self.framework,
            "passed": self.build_success,
            "build_duration": self.build_duration_seconds,
            "artifact_size_mb": round(self.artifact_size_bytes / (1024 * 1024), 2),
            "validation": {
                "link_check_passed": self.validation_results.link_check_passed,
                "broken_links": len(self.validation_results.broken_internal_links) + 
                               len(self.validation_results.broken_external_links),
                "accessibility_warnings": len(self.validation_results.accessibility_warnings),
            },
            "timestamp": self.build_timestamp.isoformat()
        }
```

### 5. ValidationResults

Results from documentation validation (link checking, accessibility, etc.).

```python
@dataclass
class BrokenLink:
    """Details of a broken link."""
    url: str
    source_file: Path
    source_line: int
    status_code: int | None
    error_message: str
    retry_attempts: int  # After 3 retries per clarification Q2

@dataclass
class A11yWarning:
    """WCAG 2.1 Level AA accessibility warning (non-blocking per Q3)."""
    rule_id: str
    impact: Literal["minor", "moderate", "serious", "critical"]
    page_url: str
    element_selector: str
    help_text: str
    wcag_criteria: List[str]  # e.g., ["1.4.3", "1.4.6"]

@dataclass
class A11yError:
    """Critical accessibility error (blocking)."""
    rule_id: str
    impact: Literal["critical"]
    page_url: str
    element_selector: str
    help_text: str

@dataclass
class ValidationResults:
    """Comprehensive validation results for documentation build."""
    
    link_check_passed: bool
    broken_internal_links: List[BrokenLink]
    broken_external_links: List[BrokenLink]  # After retries
    accessibility_warnings: List[A11yWarning]  # WCAG 2.1 AA (non-blocking per Q3)
    accessibility_errors: List[A11yError]      # Critical issues only
    missing_images: List[str]
    invalid_cross_refs: List[str]
    
    @property
    def has_no_critical_errors(self) -> bool:
        """True if no critical errors (broken internal links, accessibility errors)."""
        return (
            len(self.broken_internal_links) == 0 and
            len(self.accessibility_errors) == 0
        )
    
    @property
    def total_issues(self) -> int:
        """Total count of all issues (warnings + errors)."""
        return (
            len(self.broken_internal_links) +
            len(self.broken_external_links) +
            len(self.accessibility_warnings) +
            len(self.accessibility_errors) +
            len(self.missing_images) +
            len(self.invalid_cross_refs)
        )
    
    def generate_report(self) -> str:
        """Generate human-readable validation report."""
        lines = ["# Documentation Validation Report\n"]
        
        lines.append(f"**Link Check**: {'✅ PASSED' if self.link_check_passed else '❌ FAILED'}")
        if self.broken_internal_links:
            lines.append(f"\n## Broken Internal Links ({len(self.broken_internal_links)})\n")
            for link in self.broken_internal_links:
                lines.append(f"- `{link.url}` in {link.source_file}:{link.source_line}")
        
        if self.broken_external_links:
            lines.append(f"\n## Broken External Links ({len(self.broken_external_links)})\n")
            lines.append("*After 3 retry attempts with exponential backoff*\n")
            for link in self.broken_external_links:
                lines.append(f"- `{link.url}` (HTTP {link.status_code or 'N/A'})")
        
        if self.accessibility_warnings:
            lines.append(f"\n## Accessibility Warnings ({len(self.accessibility_warnings)})\n")
            lines.append("*WCAG 2.1 Level AA - Non-blocking*\n")
            for warning in self.accessibility_warnings[:10]:  # Limit to 10
                lines.append(f"- [{warning.rule_id}] {warning.help_text} (Impact: {warning.impact})")
            if len(self.accessibility_warnings) > 10:
                lines.append(f"  *(and {len(self.accessibility_warnings) - 10} more...)*")
        
        if self.accessibility_errors:
            lines.append(f"\n## Critical Accessibility Errors ({len(self.accessibility_errors)})\n")
            for error in self.accessibility_errors:
                lines.append(f"- [{error.rule_id}] {error.help_text}")
        
        return "\n".join(lines)
```

### 6. RetryConfig

Configuration for link checking retry logic with exponential backoff.

```python
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
```

## Entity Relationships

### Configuration → Transformation Rules

```text
DocumentationConfiguration --generates--> ContentTransformationRule[]

Example:
  config.framework = "sphinx-shibuya"
  → generates rules: [Markdown→RST, Mermaid→SphinxDirective]
  
  config.framework = "fumadocs"
  → generates rules: [Markdown→MDX (minimal), Mermaid→CodeBlock (preserve)]
```

### Configuration → Build Artifact

```text
DocumentationConfiguration --produces--> DocumentationBuildArtifact
                                         (via template render + docs build)

Example:
  1. User selects config via Copier prompts
  2. Template renders documentation files
  3. Build process executes (make docs, pnpm build, etc.)
  4. Build artifact created with validation results
```

### Build Artifact → Validation Results

```text
DocumentationBuildArtifact --contains--> ValidationResults

Example:
  artifact.output_directory → run link checker → validation_results.broken_links
                            → run axe-core → validation_results.accessibility_warnings
```

### Transformation Rule → Transformation Result

```text
ContentTransformationRule --applies--> TransformationResult

Example:
  rule.source_format = MARKDOWN
  rule.target_format = RST
  rule.transformation_fn(content) → result.content (RST)
                                  → result.errors (if unsupported syntax)
```

## State Transitions

### Configuration State Machine

```text
[Prompt Selection] → [Validation] → [Template Render] → [Docs Build] → [Quality Check]
                        ↓ (invalid)                        ↓ (failure)      ↓ (passed)
                    [Error Report]                    [Build Logs]    [Smoke Test PASS]
                                                           ↓ (fixes)
                                                      [Re-render] --------→ [Docs Build]
```

**States**:

1. **Prompt Selection**: User answers Copier prompts
   - Input: Interactive CLI session
   - Output: `DocumentationConfiguration` instance

2. **Validation**: Check configuration consistency
   - Input: `DocumentationConfiguration`
   - Output: Pass → proceed | Fail → error report + exit

3. **Template Render**: Generate documentation files
   - Input: Valid `DocumentationConfiguration`
   - Output: Rendered Jinja2 templates in `samples/*/render/`

4. **Docs Build**: Execute framework-specific build
   - Input: Rendered files
   - Output: `DocumentationBuildArtifact` with build logs

5. **Quality Check**: Run validation suite
   - Input: Built documentation
   - Output: `ValidationResults` (link check, accessibility, etc.)

6. **Smoke Test Result**: Record success/failure
   - Input: `ValidationResults`
   - Output: `smoke-results.json` entry

### Content Transformation Pipeline

```text
[Source Markdown] → [AST Parsing] → [Transformation] → [Target Format] → [Write File]
                                         ↓ (error)
                                    [Halt Build] + [Error Log] + [Manual Override Instructions]
```

**States**:

1. **Source Markdown**: Original documentation content
2. **AST Parsing**: Parse Markdown into abstract syntax tree
3. **Transformation**: Apply `ContentTransformationRule`
4. **Target Format**: Output as MDX/RST/Markdown
5. **Write File**: Save transformed content
6. **Error Handling** (if transformation fails):
   - Halt build immediately (per clarification Q1)
   - Log error with file path, line number
   - Show unsupported syntax excerpt
   - Provide manual override instructions

## Usage Examples

### Example 1: Rendering Sphinx Documentation

```python
# User selects Sphinx via Copier prompts
config = DocumentationConfiguration(
    framework="sphinx-shibuya",
    theme_mode="dark",
    search_provider="local",
    api_playground="swagger",
    deploy_target="github-pages",
    versioning_enabled=False,
    interactive_features_enabled=True
)

# Validate configuration
errors = config.validate()
if errors:
    raise ValueError(f"Invalid configuration: {errors}")

# Generate transformation rules
rules = [
    ContentTransformationRule(
        source_format=ContentFormat.MARKDOWN,
        target_format=ContentFormat.RST,
        transformation_fn=markdown_to_rst,
        supported_extensions=["mermaid", "admonitions"],
        failure_mode=TransformationFailureMode.ERROR
    )
]

# Apply transformations
for doc_file in doc_files:
    content = doc_file.read_text()
    result = rules[0].apply(content, doc_file.name)
    if not result.success:
        result.log_errors()
        sys.exit(1)
    doc_file.write_text(result.content)

# Build documentation
build_artifact = build_sphinx_docs(config)

# Validate
validation_results = validate_docs(
    build_artifact.output_directory,
    retry_config=RetryConfig(max_attempts=3)
)

# Record smoke test
smoke_result = build_artifact.to_smoke_test_result()
save_smoke_test("samples/docs-sphinx/smoke-results.json", smoke_result)
```

### Example 2: Link Checking with Retry Logic

```python
retry_config = RetryConfig(
    max_attempts=3,
    initial_delay=1.0,
    backoff_factor=2.0,
    timeout=10.0
)

broken_links = []
for link in external_links:
    attempt = 0
    while retry_config.should_retry(attempt):
        try:
            response = requests.head(link.url, timeout=retry_config.timeout)
            if response.status_code < 400:
                break  # Success
        except requests.RequestException as e:
            attempt += 1
            if retry_config.should_retry(attempt):
                delay = retry_config.get_delay(attempt)
                time.sleep(delay)
            else:
                broken_links.append(BrokenLink(
                    url=link.url,
                    source_file=link.source_file,
                    source_line=link.source_line,
                    status_code=None,
                    error_message=str(e),
                    retry_attempts=attempt
                ))

validation_results = ValidationResults(
    link_check_passed=len(broken_links) == 0,
    broken_external_links=broken_links,
    # ... other fields
)
```

## Data Persistence

### Files Written

1. **`samples/*/smoke-results.json`**: Smoke test results per variant
   ```json
   {
     "module": "docs_site",
     "framework": "sphinx-shibuya",
     "passed": true,
     "build_duration": 12.5,
     "artifact_size_mb": 8.2,
     "validation": {
       "link_check_passed": true,
       "broken_links": 0,
       "accessibility_warnings": 3
     },
     "timestamp": "2025-11-02T10:30:00"
   }
   ```

2. **`samples/metadata/module_success.json`**: Aggregated success rates
   ```json
   {
     "docs_site": {
       "fumadocs": {"success_rate": 1.0, "total_runs": 10},
       "sphinx-shibuya": {"success_rate": 1.0, "total_runs": 10},
       "docusaurus": {"success_rate": 1.0, "total_runs": 10}
     }
   }
   ```

3. **`.riso/post_gen_metadata.json`**: Rendered project metadata
   ```json
   {
     "rendered_at": "2025-11-02T10:00:00",
     "riso_version": "1.0.0",
     "modules": {
       "docs_site": {
         "framework": "sphinx-shibuya",
         "search_provider": "local",
         "deployment": "github-pages"
       }
     }
   }
   ```

---

**Data Model Version**: 1.0  
**Created**: 2025-11-02  
**Status**: Ready for Implementation
