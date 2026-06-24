# CI/CD Platform Support

Riso provides comprehensive CI/CD templates for multiple platforms, each optimized for the platform's specific capabilities.

## Supported Platforms

### GitHub Actions (Default)

- **File**: `.github/workflows/riso-quality.yml`, `.github/workflows/riso-matrix.yml`
- **Features**:
  - Matrix builds for Python versions (3.11, 3.12, 3.13)
  - Dependency caching (uv, pnpm, cargo)
  - Artifacts upload (test results, coverage)
  - Retry logic with exponential backoff
  - Concurrency control
- **Best For**: GitHub-hosted projects, open-source, large ecosystem of actions

### GitLab CI

- **File**: `.gitlab/.gitlab-ci.yml`
- **Features**:
  - `parallel.matrix` for multi-version testing
  - Docker-in-Docker for container builds
  - GitLab Pages deployment for docs
  - Component-specific caching (pip, pnpm, cargo)
  - Per-job artifacts with expiration
- **Best For**: GitLab-hosted projects, self-hosted runners, enterprise deployments

### CircleCI

- **File**: `.circleci/config.yml`
- **Features**:
  - Official orbs (python@2.1, node@5.2, rust@1.6, go@1.11)
  - Workspace persistence for build artifacts
  - Parallelism for monorepo testing
  - Test results storage and visualization
  - Advanced caching strategies
- **Best For**: Complex workflows, parallelism, Docker layer caching

## Selection Guide

### Choose GitHub Actions if:
- Your code is hosted on GitHub
- You want the largest ecosystem of community actions
- You need simple matrix builds
- You want tight integration with GitHub features (releases, packages)

### Choose GitLab CI if:
- Your code is hosted on GitLab
- You need self-hosted runners
- You want built-in container registry integration
- You need advanced pipeline features (includes, extends)

### Choose CircleCI if:
- You need maximum parallelism for large test suites
- You want first-class Docker support
- You need workspace persistence across jobs
- You require advanced caching (Docker layers, incremental)

## Configuration

Set `ci_platform` in your Copier answers:

```yaml
ci_platform: github-actions  # or gitlab-ci, circleci, none
```

## Component-First CI

All CI platforms use the same component-first architecture:

### Python Components
- **Lint**: Ruff check + format, mypy (strict), pylint (strict)
- **Test**: pytest with coverage, component-specific tests (CLI, MCP)
- **Cache**: uv cache, pip cache

### Node.js Components
- **Lint**: ESLint, TypeScript type checking
- **Test**: pnpm test with coverage, E2E tests (SaaS)
- **Build**: pnpm build, artifact persistence
- **Cache**: pnpm store, node_modules

### Rust Components
- **Lint**: cargo fmt, cargo clippy
- **Test**: cargo test (unit + doc tests)
- **Build**: cargo build --release
- **Cache**: cargo registry, target directory

### Go Components
- **Lint**: go fmt, go vet
- **Test**: go test with race detector and coverage
- **Build**: go build with optimizations
- **Cache**: go mod cache

## Quality Profiles

### Standard Profile
- Ruff linting and formatting
- pytest with coverage
- Basic type checking

### Strict Profile
- All standard checks plus:
- mypy static type analysis
- pylint static analysis
- Extended timeout for thorough checking

## Matrix Builds

### GitHub Actions
```yaml
strategy:
  matrix:
    python-version: ["3.11", "3.12", "3.13"]
```

### GitLab CI
```yaml
parallel:
  matrix:
    - PYTHON_VERSION: ["3.11", "3.12", "3.13"]
```

### CircleCI
```yaml
parallelism: 3
```

## Caching Strategies

### GitHub Actions
- Cache key: `${{ runner.os }}-py${{ matrix.python-version }}-${{ hashFiles('**/uv.lock') }}`
- Paths: `~/.cache/uv`, `~/.cache/pip`, `.venv`

### GitLab CI
- Cache key: `python-${CI_COMMIT_REF_SLUG}`
- Paths: `.cache/pip/`, `.cache/uv/`, `.venv/`

### CircleCI
- Restore/save cache with checksum: `uv-cache-{{ checksum "uv.lock" }}`
- Paths: `~/.cache/uv`, `.venv`

## Documentation Deployment

### GitHub Actions
- Deploys to GitHub Pages via `gh-pages` branch
- Sphinx: `sphinx-build docs/ _build/`
- Fumadocs: `pnpm run docs:build`

### GitLab CI
- Deploys to GitLab Pages via `public/` artifact
- Sphinx: `sphinx-build docs/ public/`
- Fumadocs: `pnpm run docs:build && mv docs/out public/`

### CircleCI
- Stores docs as artifacts
- Manual deployment step required

## Container Builds

### GitHub Actions
- Uses `docker/build-push-action@v5`
- Multi-platform builds (linux/amd64, linux/arm64)
- Automatic tagging (latest, SHA, semantic version)

### GitLab CI
- Uses Docker-in-Docker service
- Pushes to GitLab Container Registry
- Tags: `$CI_COMMIT_SHORT_SHA`, `latest`

### CircleCI
- Remote Docker executor
- Manual registry configuration
- Requires Docker Hub credentials

## Migration Between Platforms

To migrate from one CI platform to another:

1. Update `ci_platform` in `.copier-answers.yml`
2. Run `copier update` to regenerate CI files
3. Remove old CI configuration manually
4. Commit the new configuration

Example:
```bash
# Update from GitHub Actions to GitLab CI
copier update --data ci_platform=gitlab-ci

# Remove old GitHub Actions files
rm -rf .github/workflows/riso-*.yml

# Commit new GitLab CI config
git add .gitlab/.gitlab-ci.yml
git commit -m "chore: migrate to GitLab CI"
```

## Troubleshooting

### GitHub Actions
- **Issue**: Cache misses
- **Fix**: Check `uv.lock` is committed and hashFiles works

### GitLab CI
- **Issue**: Parallel jobs failing
- **Fix**: Ensure matrix variables are properly templated

### CircleCI
- **Issue**: Workspace not persisting
- **Fix**: Verify `persist_to_workspace` and `attach_workspace` paths match

## Performance Optimization

### Reduce CI Time
1. **Caching**: Enable all relevant caches (uv, pnpm, cargo)
2. **Parallelism**: Use matrix builds for independent jobs
3. **Conditional Jobs**: Skip unchanged components
4. **Fail-Fast**: Enable for development branches, disable for release

### Reduce CI Cost
1. **Self-Hosted Runners**: GitLab CI supports self-hosted (free)
2. **Smaller Executors**: Use Alpine images where possible
3. **Cache Effectively**: Reduce dependency download time
4. **Optimize Docker Layers**: Order Dockerfile for cache reuse

## Best Practices

1. **Commit Lock Files**: Always commit `uv.lock`, `pnpm-lock.yaml`, `Cargo.lock`
2. **Pin Versions**: Use specific action/orb versions (not `@latest`)
3. **Separate Concerns**: Lint, test, build as separate jobs
4. **Artifacts Retention**: Set appropriate retention periods (7-90 days)
5. **Secrets Management**: Use platform-specific secret stores
6. **Branch Protection**: Require CI pass before merge

## Platform-Specific Features

### GitHub Actions Only
- Dependabot integration
- GitHub Packages publishing
- GitHub Releases automation
- CodeQL security scanning

### GitLab CI Only
- Auto DevOps
- Review Apps
- Built-in container registry
- Kubernetes integration

### CircleCI Only
- Advanced parallelism (split tests)
- Docker layer caching
- Remote Docker
- Insights dashboard

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitLab CI Documentation](https://docs.gitlab.com/ee/ci/)
- [CircleCI Documentation](https://circleci.com/docs/)
