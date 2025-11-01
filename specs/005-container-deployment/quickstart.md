# Quickstart: Container & Deployment Templates

## Prerequisites

- Docker Engine 24+ ([installation guide](https://docs.docker.com/engine/install/))
- Docker Compose v2 ([installation guide](https://docs.docker.com/compose/install/))
- Existing Riso project (rendered with copier)
- Optional: hadolint for local Dockerfile linting
- Optional: Trivy for local security scanning

## 1. Render Project with Container Support

```bash
# New project
copier copy gh:wyattowalsh/riso my-containerized-app
cd my-containerized-app

# Answer prompts:
# - api_tracks: python (or python+node for full-stack)
# - include_databases: yes (if using PostgreSQL/Redis)
# - Other modules as needed
```

Or update existing project:

```bash
copier update --answers-file .copier-answers.yml
# Edit answers to add include_databases=yes if needed
```

## 2. Build Container Locally

### Single Python API Project

```bash
# Build with multi-stage optimization
docker build -f Dockerfile -t my-app:local .

# Expected output:
# - Builder stage: uv sync, dependency installation
# - Runtime stage: Minimal image with UID 1000 user
# - Total time: <3 minutes
# - Final size: <500MB

# Verify image
docker images my-app:local
```

### Full-Stack Monorepo (Python + Node)

```bash
# Build all services
docker-compose build

# Expected output:
# - api-python service built (FastAPI)
# - api-node service built (Fastify)
# - docs-fumadocs service built (Next.js static export)
# - postgres/redis pulled if include_databases=yes
# - Total time: <5 minutes
```

## 3. Run Container Locally

### Single Service

```bash
# Run container
docker run -p 8000:8000 --name my-app my-app:local

# Verify health check
curl http://localhost:8000/health
# Expected: {"status":"healthy","service":"api-python"}

# Check process user
docker exec my-app id
# Expected: uid=1000(appuser) gid=1000(appuser)

# Stop container
docker stop my-app && docker rm my-app
```

### Multi-Service with docker-compose

```bash
# Start all services in background
docker-compose up -d

# Check service health
docker-compose ps
# Expected: All services "healthy" after ~30 seconds

# View logs
docker-compose logs -f api-python

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:3000  # Node.js API
curl http://localhost:3001  # Fumadocs site

# Connect to PostgreSQL (if enabled)
docker-compose exec postgres psql -U riso -d riso_db

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## 4. Lint Dockerfile Locally

```bash
# Install hadolint
# macOS:
brew install hadolint

# Linux:
wget -O /usr/local/bin/hadolint https://github.com/hadolint/hadolint/releases/latest/download/hadolint-Linux-x86_64
chmod +x /usr/local/bin/hadolint

# Lint Dockerfile
hadolint Dockerfile

# Expected: No errors (warnings acceptable)
# Configuration in .hadolint.yaml
```

## 5. Scan Container for Vulnerabilities

```bash
# Install Trivy
# macOS:
brew install trivy

# Linux:
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt-get update && sudo apt-get install trivy

# Scan image
trivy image my-app:local

# Expected: Zero HIGH or CRITICAL vulnerabilities
# Generate SBOM
trivy image --format spdx-json -o sbom.json my-app:local
```

## 6. Push to GitHub Container Registry

### Setup Authentication

```bash
# Generate GitHub Personal Access Token with write:packages scope
# https://github.com/settings/tokens/new

# Login to ghcr.io
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

### Tag and Push

```bash
# Tag image
docker tag my-app:local ghcr.io/USERNAME/my-app:latest
docker tag my-app:local ghcr.io/USERNAME/my-app:v1.0.0

# Push to registry
docker push ghcr.io/USERNAME/my-app:latest
docker push ghcr.io/USERNAME/my-app:v1.0.0

# Verify in GitHub
# Navigate to: https://github.com/USERNAME?tab=packages
```

## 7. CI/CD Workflow Setup

### Enable Container Workflows

Rendered projects include:
- `.github/workflows/riso-container-build.yml` - Build and scan on PRs
- `.github/workflows/riso-container-publish.yml` - Publish on main branch pushes

### Configure Secrets (Optional)

For Docker Hub:
```bash
gh secret set DOCKERHUB_USERNAME --body "your-username"
gh secret set DOCKERHUB_TOKEN --body "your-access-token"
```

For AWS ECR:
```bash
gh secret set AWS_REGION --body "us-east-1"
gh secret set AWS_ROLE_ARN --body "arn:aws:iam::123456789:role/GitHubActionsECRRole"
```

### Verify Workflows

```bash
# Push change to trigger build
git add .
git commit -m "feat: test container build"
git push origin feature-branch

# Check workflow status
gh run list --limit 5

# View build logs
gh run view --log

# Download artifacts
gh run download <run-id>
```

## 8. Local Development with Hot Reload

### docker-compose with Volume Mounts

Edit `docker-compose.yml` to add volume mounts:

```yaml
services:
  api-python:
    build: .
    volumes:
      - ./src:/app/src:ro  # Read-only source mount
      - ./tests:/app/tests:ro
    command: ["uv", "run", "uvicorn", "{{ package_name }}.api.main:app", "--host", "0.0.0.0", "--reload"]
```

Restart service:

```bash
docker-compose up -d api-python
docker-compose logs -f api-python

# Edit source files - service auto-reloads
```

## 9. Multi-Architecture Builds

```bash
# Create buildx builder
docker buildx create --name multiarch --use

# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t ghcr.io/USERNAME/my-app:latest \
  --push \
  .

# Verify manifest
docker buildx imagetools inspect ghcr.io/USERNAME/my-app:latest
```

## 10. Deploy to Cloud Platforms

### Kubernetes

```bash
# Create deployment
kubectl create deployment my-app --image=ghcr.io/USERNAME/my-app:latest

# Expose service
kubectl expose deployment my-app --port=8000 --target-port=8000 --type=LoadBalancer

# Check health
kubectl get pods
kubectl logs deployment/my-app
```

### Cloud Run (Google Cloud)

```bash
# Deploy container
gcloud run deploy my-app \
  --image ghcr.io/USERNAME/my-app:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Check health
curl https://my-app-xyz.run.app/health
```

### AWS ECS

```bash
# Create task definition (JSON)
# - Image: ghcr.io/USERNAME/my-app:latest
# - Port: 8000
# - Health check: /health endpoint
# - CPU: 256, Memory: 512

# Create service
aws ecs create-service \
  --cluster my-cluster \
  --service-name my-app \
  --task-definition my-app:1 \
  --desired-count 2 \
  --launch-type FARGATE
```

## Troubleshooting

### Build Failures

**Issue**: `uv sync` fails with "package not found"

**Solution**: Check `uv.lock` is committed and up-to-date:
```bash
uv lock --upgrade
git add uv.lock
```

**Issue**: Node.js build OOM (out of memory)

**Solution**: Increase Docker memory limit or use multi-stage build with smaller builder:
```bash
docker build --memory=4g -t my-app:local .
```

### Health Check Failures

**Issue**: Container starts but health check fails

**Solution**: Check logs for application errors:
```bash
docker logs my-app
# or
docker-compose logs api-python
```

Verify health endpoint responds:
```bash
docker exec my-app curl -f http://localhost:8000/health
```

### Permission Errors

**Issue**: `Permission denied` when writing files in container

**Solution**: Ensure volumes mounted with correct permissions for UID 1000:
```bash
sudo chown -R 1000:1000 ./data
```

### Registry Authentication

**Issue**: `denied: installation not allowed`

**Solution**: Verify GitHub token has `write:packages` scope:
```bash
gh auth status
gh auth refresh --scopes write:packages
```

## Next Steps

- **Customize Dockerfile**: Add application-specific dependencies
- **Configure databases**: Tune PostgreSQL/Redis for production
- **Add monitoring**: Integrate Prometheus exporters (feature 008)
- **Set up secrets**: Use environment variables for sensitive config
- **Enable caching**: Optimize BuildKit cache for faster CI builds
- **Implement rolling updates**: Configure health checks for zero-downtime deployments

## Reference Documentation

- Dockerfile structure: `docs/modules/containers.md`
- Extension patterns: `.github/context/containers.md`
- Upgrade guide: `docs/upgrade-guide.md` (container migration section)
- GitHub Actions workflows: `.github/workflows/riso-container-*.yml`
