# Docker Best Practices

## Topic: Multi-stage Builds

### Dockerfile
```dockerfile
# Build stage
FROM golang:1.21-alpine AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

# Runtime stage
FROM alpine:3.19

RUN apk --no-cache add ca-certificates

WORKDIR /root/

COPY --from=builder /app/main .

EXPOSE 8080

CMD ["./main"]
```

### Explanation
Multi-stage builds allow you to use multiple FROM statements in a single Dockerfile. Each FROM instruction begins a new stage of the build. The key benefits include:

- **Smaller final images**: Only copy necessary artifacts from build stages, excluding build tools, source code, and intermediate files.
- **Better security**: The runtime image contains fewer packages and attack surface.
- **Separation of concerns**: Build dependencies stay in the build stage; runtime gets only what it needs.
- **Use AS keyword**: Name your stages with `AS` for clarity and easier referencing with `--from=<stage>`.
- **Choose minimal base images**: Use `alpine`, `distroless`, or `scratch` for the final stage when possible.
- **Copy only what you need**: Use `COPY --from=builder` to selectively copy built artifacts.

---

## Topic: Layer Caching

### Dockerfile
```dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy dependency files first (rarely change)
COPY package.json package-lock.json ./

# Install dependencies (cached if package files unchanged)
RUN npm ci --only=production

# Copy source code last (changes frequently)
COPY . .

# Build application
RUN npm run build

CMD ["node", "dist/index.js"]
```

### Explanation
Docker builds images in layers, and each instruction creates a layer. Understanding layer caching dramatically speeds up builds:

- **Order matters**: Place frequently changing instructions (COPY . .) at the end and stable instructions (dependency installation) at the beginning.
- **Leverage .dockerignore**: Create a .dockerignore file to exclude unnecessary files that would invalidate cache:
  ```
  node_modules
  .git
  *.log
  .env
  ```
- **Combine related operations**: Each RUN, COPY, and ADD creates a layer. Combine related RUN commands with `&&`:
  ```dockerfile
  RUN apt-get update && apt-get install -y package && rm -rf /var/lib/apt/lists/*
  ```
- **Pin dependency versions**: Use lock files (package-lock.json, Pipfile.lock) for reproducible builds and better cache utilization.
- **Use BuildKit**: Enable BuildKit for advanced caching features:
  ```bash
  DOCKER_BUILDKIT=1 docker build .
  ```

---

## Topic: Security Best Practices

### Dockerfile
```dockerfile
FROM alpine:3.19

# Create non-root user
RUN addgroup -g 1000 -S appgroup && \
    adduser -u 1000 -S appuser -G appgroup

WORKDIR /app

# Copy files with proper ownership
COPY --chown=appuser:appgroup . .

# Install packages and clean up in one layer
RUN apk add --no-cache curl=8.5.0-r0 && \
    rm -rf /var/cache/apk/*

# Switch to non-root user
USER appuser

# Set read-only root filesystem
# (use with docker run --read-only flag)

# Drop all capabilities by default
# (use with docker run --cap-drop=ALL flag)

EXPOSE 8080

CMD ["./app"]
```

### Explanation
Container security requires a defense-in-depth approach with multiple layers of protection:

- **Run as non-root**: Always create and use a dedicated user. Never run containers as root.
- **Use minimal base images**: Prefer Alpine, Distroless, or Chainguard images to reduce attack surface.
- **Pin image versions**: Use specific version tags (`alpine:3.19.0`) instead of `latest` or `alpine:3`.
- **Scan images regularly**: Use tools like Trivy, Snyk, or Docker Scout to detect vulnerabilities:
  ```bash
  docker scout cves myimage:latest
  ```
- **Sign and verify images**: Use Docker Content Trust (DOCKER_CONTENT_TRUST=1) or Sigstore/Cosign.
- **Limit capabilities**: Run with `--cap-drop=ALL` and add only needed capabilities.
- **Use security profiles**: Apply AppArmor or SELinux profiles for additional isolation.
- **Secret management**: Never hardcode secrets in images. Use Docker secrets, environment variables from orchestrators, or external secret managers.
- **Keep images updated**: Regularly rebuild images to get security patches from base images.

---

## Topic: Health Checks

### Dockerfile
```dockerfile
FROM nginx:1.25-alpine

# Copy application files
COPY html/ /usr/share/nginx/html/

# Define health check
HEALTHCHECK --interval=30s \
            --timeout=5s \
            --start-period=10s \
            --retries=3 \
            CMD curl -f http://localhost/health || exit 1

# Alternative using wget (alpine doesn't have curl by default)
# HEALTHCHECK CMD wget -q --spider http://localhost/health || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Explanation
Health checks allow Docker and orchestrators to monitor container health and automatically restart unhealthy containers:

- **HEALTHCHECK instruction**: Defines the command Docker executes to check container health.
- **Parameters**:
  - `--interval=DURATION`: Time between checks (default: 30s)
  - `--timeout=DURATION`: Maximum time to wait for a response (default: 30s)
  - `--start-period=DURATION`: Grace period for container startup (default: 0s)
  - `--retries=N`: Consecutive failures needed to mark unhealthy (default: 3)
- **Exit codes**:
  - `0`: Container is healthy
  - `1`: Container is unhealthy
- **Implement application endpoints**: Create dedicated `/health` endpoints that verify:
  - Application is responding
  - Database connections are active
  - Critical services are accessible
- **Check container status**:
  ```bash
  docker inspect --format='{{json .State.Health}}' container_name
  ```
- **Orchestrator integration**: Kubernetes uses readiness/liveness probes; Swarm and Compose use HEALTHCHECK.
- **Keep checks simple**: Fast, lightweight checks that verify core functionality without heavy operations.

---

## Topic: Resource Limits

### Dockerfile
```dockerfile
# Resource limits are typically set at runtime, not in Dockerfile
# However, you can document expected resources in labels

FROM python:3.12-slim

LABEL org.opencontainers.image.resource.memory="512Mi"
LABEL org.opencontainers.image.resource.cpu="0.5"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create directory for pid file (useful for monitoring)
RUN mkdir -p /var/run/app && chown 1000:1000 /var/run/app

USER 1000

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Example docker-compose.yml
```yaml
version: '3.8'
services:
  app:
    build: .
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    # Alternative using traditional syntax
    mem_limit: 512m
    memswap_limit: 1g
    cpus: 0.5
    pids_limit: 100
```

### Explanation
Resource limits prevent runaway containers from consuming all host resources and ensure predictable application performance:

- **Memory limits**:
  - `--memory` or `-m`: Hard limit on RAM usage
  - `--memory-swap`: Total memory + swap limit
  - `--memory-reservation`: Soft limit for container memory reservation
  - Always set limits to prevent OOM issues affecting the host

- **CPU limits**:
  - `--cpus`: Number of CPUs (e.g., 1.5 = 1.5 cores)
  - `--cpu-shares`: Relative weight (default: 1024)
  - `--cpuset-cpus`: Bind to specific CPU cores
  - Use reservations for minimum guaranteed resources

- **Process limits**:
  - `--pids-limit`: Maximum number of processes in container
  - Prevents fork bombs and runaway process creation

- **Always set both limits and reservations**:
  - Limits prevent resource exhaustion
  - Reservations guarantee minimum resources for critical workloads

- **Monitor usage**:
  ```bash
  docker stats container_name
  ```

- **Profile before limiting**: Measure actual resource usage under load before setting limits. Set limits 20-30% above observed peak usage.

- **Handle OOM gracefully**: Implement graceful shutdown handlers in your application to handle memory pressure.

---

## Summary

| Practice | Key Benefit |
|----------|-------------|
| Multi-stage Builds | Smaller, more secure images |
| Layer Caching | Faster build times |
| Security Best Practices | Reduced attack surface |
| Health Checks | Improved reliability and orchestration |
| Resource Limits | Predictable performance and stability |

Apply these practices consistently across your Docker workflows for production-ready containerized applications.
