# Feature Specification: Code Generation and Scaffolding Tools

**Feature Branch**: `015-codegen-scaffolding-tools`  
**Created**: 2025-11-02  
**Status**: Draft  
**Terminology**: This document uses "scaffolding tool" consistently to refer to the code generation CLI
**Input**: User description: "create a new feature/spec branch/spec for `015-codegen-scaffolding-tools`"

## Clarifications

### Session 2025-11-02

- Q: What is the template storage strategy? → A: Local cache with remote sync (fetch once, use cached, manual update)
- Q: What is the conflict resolution strategy for template updates? → A: Three-way merge with conflict markers (like Git merge conflicts)
- Q: When should template variables be validated? → A: Validate all required variables before starting any file generation
- Q: What is the maximum template size limit? → A: 100MB per template (warn at 50MB)
- Q: How should quality validation gates behave? → A: Warn but allow completion (show issues, generate anyway)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate Project Boilerplate from Template (Priority: P1)

A developer wants to quickly create a new project with a consistent structure, pre-configured tooling, and best practices baked in. They run a single command and receive a fully functional project scaffold that's ready for development.

**Why this priority**: This is the core value proposition - reducing time from zero to first commit. Without this, the feature provides no value.

**Independent Test**: Can be fully tested by running the generation command with minimal inputs (project name only) and validating that the output directory contains a runnable project with passing tests.

**Acceptance Scenarios**:

1. **Given** a user has the scaffolding tool installed, **When** they run `scaffold new my-project`, **Then** a new directory is created with project structure, configuration files, and placeholder code
2. **Given** a generated project, **When** the user runs the project's test suite, **Then** all default tests pass successfully
3. **Given** a generated project, **When** the user attempts to build/compile it, **Then** the build completes without errors
4. **Given** a user provides invalid project name (special characters, reserved words), **When** they run the scaffold command, **Then** the tool provides clear error messages and suggests corrections

---

### User Story 2 - Add Feature Modules to Existing Projects (Priority: P2)

A developer working on an existing project wants to add a new feature module (e.g., authentication, API endpoint, database model) following the project's established patterns. They run a command to generate the module with all necessary files, tests, and configuration updates.

**Why this priority**: Extends value beyond initial setup to ongoing development. Ensures consistency as projects grow.

**Independent Test**: Can be tested by creating a minimal project, running the add-module command, and verifying that new files are created with correct imports and the project still builds/tests successfully.

**Acceptance Scenarios**:

1. **Given** an existing project, **When** a user runs `scaffold add api-endpoint UserProfile`, **Then** the tool generates controller, route, model, test files following project conventions
2. **Given** a module generation request, **When** the module already exists, **Then** the tool warns the user and offers options to skip, overwrite, or merge
3. **Given** a newly generated module, **When** the user runs project tests, **Then** the new module includes passing placeholder tests
4. **Given** a module that requires dependencies, **When** generated, **Then** the tool updates package/dependency files automatically

---

### User Story 3 - Customize Templates with Project-Specific Patterns (Priority: P3)

A team lead wants to define organization-specific templates that enforce their coding standards, security policies, and architectural patterns. They configure custom templates that their team can use for consistent project generation.

**Why this priority**: Enables teams to codify best practices and enforce standards. Valuable but not essential for basic functionality.

**Independent Test**: Can be tested by creating a custom template configuration, generating a project from it, and verifying that the output matches the custom patterns rather than defaults.

**Acceptance Scenarios**:

1. **Given** a template configuration file, **When** a user generates a project with `scaffold new my-project --template my-custom-template`, **Then** the output follows the custom template structure
2. **Given** custom template variables (e.g., organization name, license type), **When** generating a project, **Then** the tool prompts for these values and substitutes them throughout generated files
3. **Given** a user wants to preview template output, **When** they run `scaffold preview my-template`, **Then** the tool shows what files and structure would be generated without creating files

---

### User Story 4 - Update Generated Code as Templates Evolve (Priority: P4)

A developer has projects generated from older template versions and wants to update them with improvements from newer templates (bug fixes, security patches, new best practices) without losing their custom changes.

**Why this priority**: Supports long-term maintainability but assumes existing projects are already functional. Lower priority than initial generation.

**Independent Test**: Can be tested by generating a project from an old template version, making custom modifications, updating the template version, running an update command, and verifying that improvements are applied while preserving custom changes.

**Acceptance Scenarios**:

1. **Given** a project generated from template v1.0, **When** template v1.1 is released and user runs `scaffold update`, **Then** the tool identifies updatable files and shows a diff
2. **Given** conflicts between template updates and local changes, **When** update is attempted, **Then** the tool inserts three-way merge conflict markers (<<<<<<, =======, >>>>>>>) showing original, local changes, and template updates
3. **Given** conflicts have been marked, **When** user resolves them and removes conflict markers, **Then** the update completes successfully
4. **Given** a user wants to see what changed between template versions, **When** they run `scaffold diff-templates v1.0 v1.1`, **Then** the tool shows a summary of template changes

---

### User Story 5 - Generate Code from API Specifications (Priority: P3)

A developer has an OpenAPI/GraphQL schema and wants to generate client/server code that matches the API contract. They provide the specification file and receive type-safe code with validation and documentation.

**Why this priority**: High value for API-first development workflows. Ranked P3 because it's a specialized use case that builds on core generation capabilities.

**Independent Test**: Can be tested by providing a sample OpenAPI spec, running the generation command, and verifying that generated code includes correct types, endpoints, and validation logic that can be imported and used.

**Acceptance Scenarios**:

1. **Given** an OpenAPI specification file, **When** a user runs `scaffold generate-api openapi.yaml --language python`, **Then** the tool generates FastAPI server code with routes, models, and validation
2. **Given** a GraphQL schema, **When** a user runs `scaffold generate-api schema.graphql --type client`, **Then** the tool generates client code with typed queries and mutations
3. **Given** generated API code, **When** the specification changes, **Then** the user can re-run generation to update code while preserving custom business logic in designated areas

---

### Edge Cases

- What happens when a user tries to generate a project in a non-empty directory? (Should detect existing files and warn/fail)
- How does the tool handle file system permission errors? (Should provide clear error messages indicating which operations failed and why)
- What happens when template variables have circular dependencies? (Should detect and report configuration errors)
- How does the tool handle extremely large template repositories? (Should warn users when template exceeds 50MB, reject templates over 100MB, and provide progress indicators during download)
- What happens when a user's environment is missing required tools (e.g., Python, Node.js) for the template? (Should validate prerequisites and provide setup guidance)
- How does the tool handle network failures when fetching remote templates? (Should fall back to cached version if available, otherwise provide clear offline error)
- What happens when generating code for file paths that exceed OS limits? (Should detect and suggest shorter alternatives)
- How does the tool handle template files with syntax errors or invalid Jinja/template syntax? (Should validate templates before generation and report errors with line numbers)
- What happens when a user cancels during variable collection prompts? (Should abort cleanly without creating partial output)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support template-based code generation that reads template files and produces output files with variable substitution
- **FR-002**: System MUST validate user inputs (project names, module names) against naming conventions and reserved words before generating code
- **FR-003**: System MUST detect existing files in target directories and provide options to skip, overwrite, or merge
- **FR-004**: System MUST collect and validate all required template variables via interactive prompts or command-line arguments before beginning file generation
- **FR-005**: System MUST preserve file permissions and executable flags when copying template files
- **FR-006**: System MUST generate configuration files (pyproject.toml, package.json, etc.) with correct dependency versions
- **FR-007**: System MUST provide dry-run mode that shows what would be generated without creating files
- **FR-008**: System MUST support template inheritance where templates can extend other templates
- **FR-009**: System MUST validate generated code syntax for supported languages (Python, TypeScript, etc.)
- **FR-010**: System MUST support hooks (pre-generation, post-generation) for custom validation and setup logic
- **FR-011**: System MUST generate comprehensive README files with setup instructions specific to each template
- **FR-012**: System MUST support conditional file generation based on user selections (e.g., include/exclude test files)
- **FR-013**: System MUST maintain a record of generation metadata (template version, variables used, timestamp) in generated projects
- **FR-014**: Users MUST be able to list available templates and see their descriptions
- **FR-015**: Users MUST be able to add custom template directories and remote template sources (local paths, Git URLs, HTTP registries) to the tool's search path
- **FR-016**: System MUST support fetching templates from remote repositories (Git URLs, package registries) and caching them locally for offline use
- **FR-017**: System MUST provide commands to manually update cached templates from remote sources
- **FR-018**: System MUST provide clear error messages with actionable suggestions when generation fails
- **FR-019**: System MUST enforce a maximum template size of 100MB and warn users when templates exceed 50MB
- **FR-020**: System MUST support generating multiple related files atomically (all-or-nothing)
- **FR-021**: System MUST run quality validation (linting, type checking) on generated projects and display warnings without blocking completion
- **FR-022**: Users MUST be able to update generated projects when template versions change while preserving custom modifications
- **FR-023**: System MUST use three-way merge algorithm when updating projects, inserting conflict markers (<<<<<<, =======, >>>>>>>) when automatic merge is not possible
- **FR-024**: System MUST validate that all conflict markers are resolved before considering an update complete

### Key Entities

- **Template**: A collection of files, directories, and configuration that defines the structure and content to be generated. Includes template files (with variable placeholders), metadata (name, description, version), variables (required and optional inputs), and hooks (pre/post generation scripts).

- **Project**: The output of generation - a directory structure with files created from a template. Contains generated files, configuration files, metadata file (.scaffold-metadata.json) tracking template version and variables used, and custom modifications made by the user.

- **Module**: A smaller unit of generation that can be added to existing projects. Represents a feature or component (e.g., API endpoint, database model). Contains related files (code, tests, config), follows project conventions, and may trigger updates to existing files (imports, routes, etc.).

- **Generator**: The engine that processes templates and produces output. Handles variable substitution, file creation, validation, hook execution, and conflict resolution.

- **Template Registry**: Repository or catalog of available templates. Supports local templates (file system), remote templates (Git, HTTP), and custom registries (team/organization-specific).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can generate a new project scaffold in under 30 seconds from command execution to first successful test run
- **SC-002**: Generated projects produce zero critical errors when quality checks run (warnings allowed)
- **SC-003**: 95% of developers successfully generate their first project without consulting documentation beyond the initial command (success = generates project + passes all tests + completes in <5 minutes)
- **SC-004**: Adding a new module to an existing project takes under 60 seconds and produces immediately runnable code
- **SC-005**: Template updates can be applied to existing projects with zero manual conflict resolution for 80% of cases
- **SC-006**: Generated code follows project conventions with 100% consistency (naming, structure, imports)
- **SC-007**: Tool successfully validates and reports errors for invalid inputs (names, paths) before any file creation occurs
- **SC-008**: Developers can customize templates for their team in under 15 minutes (customize = create template.yml + add 3 template files + test generation successfully)
- **SC-009**: Generated API code from OpenAPI specs achieves 100% type coverage with no manual type annotations needed
- **SC-010**: Tool reduces time to first commit for new projects by 75% compared to manual setup
