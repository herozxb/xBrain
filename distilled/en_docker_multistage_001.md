# Docker Multi-Stage Builds

## Problem

Implement optimized Docker multi-stage builds for different programming languages, minimizing final image size and improving security.

## Implementation

### Go Application Multi-Stage Build

```dockerfile
# ============================================
# STAGE 1: Build
# ============================================
FROM golang:1.21-alpine AS builder

# Install build dependencies
RUN apk add --no-cache git ca-certificates tzdata

WORKDIR /build

# Copy go mod files first for caching
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build the binary with optimizations
RUN CGO_ENABLED=0 GOOS=linux go build \
    -ldflags='-w -s -extldflags "-static"' \
    -a -installsuffix cgo \
    -o /build/server ./cmd/server

# ============================================
# STAGE 2: Final (Minimal)
# ============================================
FROM scratch AS final

# Copy CA certificates for HTTPS
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

# Copy timezone data
COPY --from=builder /usr/share/zoneinfo /usr/share/zoneinfo

# Copy the binary
COPY --from=builder /build/server /server

# Use non-root user (defined in scratch)
USER 65534:65534

EXPOSE 8080

ENTRYPOINT ["/server"]
```

### Node.js Multi-Stage Build

```dockerfile
# ============================================
# STAGE 1: Dependencies
# ============================================
FROM node:20-alpine AS deps

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci --only=production

# ============================================
# STAGE 2: Build
# ============================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependencies
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build the application
RUN npm run build

# Prune dev dependencies
RUN npm prune --production

# ============================================
# STAGE 3: Runner
# ============================================
FROM node:20-alpine AS runner

WORKDIR /app

# Create non-root user
RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nodejs

# Set environment
ENV NODE_ENV=production
ENV NODE_OPTIONS="--max-old-space-size=2048"

# Copy built application
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /app/package.json ./

USER nodejs

EXPOSE 3000

CMD ["node", "dist/index.js"]
```

### Python Multi-Stage Build

```dockerfile
# ============================================
# STAGE 1: Builder
# ============================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir -r requirements.txt

# ============================================
# STAGE 2: Final
# ============================================
FROM python:3.11-slim AS final

WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application
COPY --chown=appuser:appuser . .

# Security: No cache, unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
```

### Rust Multi-Stage Build

```dockerfile
# ============================================
# STAGE 1: Build
# ============================================
FROM rust:1.74 AS builder

WORKDIR /app

# Create dummy project for dependency caching
RUN mkdir src && echo "fn main() {}" > src/main.rs
COPY Cargo.toml Cargo.lock ./
RUN cargo build --release && rm -rf src

# Build actual application
COPY src ./src
RUN touch src/main.rs && cargo build --release

# ============================================
# STAGE 2: Final
# ============================================
FROM debian:bookworm-slim AS final

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -r -s /bin/false appuser

WORKDIR /app

# Copy binary
COPY --from=builder /app/target/release/myapp /usr/local/bin/

USER appuser

EXPOSE 8080

CMD ["myapp"]
```

### React/Vite Multi-Stage Build

```dockerfile
# ============================================
# STAGE 1: Build
# ============================================
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source and build
COPY . .
RUN npm run build

# ============================================
# STAGE 2: Production (Nginx)
# ============================================
FROM nginx:alpine AS final

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=3s \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### nginx.conf (for React build)

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

## Build & Test Commands

```bash
# Build multi-stage image
docker build -t myapp:latest .

# Build specific stage
docker build --target builder -t myapp:builder .

# Check image size
docker images myapp:latest

# Run container
docker run -p 8080:8080 myapp:latest

# Scan for vulnerabilities
docker scout cves myapp:latest

# Test multi-platform build
docker buildx build --platform linux/amd64,linux/arm64 -t myapp:latest .
```

## Size Comparison

| Base Image | Typical Size |
|------------|--------------|
| scratch | 0 MB (binary only) |
| alpine | ~5 MB |
| distroless | ~20 MB |
| debian-slim | ~80 MB |
| ubuntu | ~180 MB |
| full OS | 500+ MB |

## Optimization Techniques

| Technique | Impact |
|-----------|--------|
| Use scratch/alpine | 90%+ reduction |
| Multi-stage build | 60-80% reduction |
| Layer caching | Faster builds |
| .dockerignore | Smaller context |
| Minimize RUN layers | Fewer layers |
| --no-install-recommends | 20-40% reduction |

## .dockerignore Example

```
node_modules
dist
.git
*.md
.env*
Dockerfile*
docker-compose*
coverage
.nyc_output
*.log
```

## Key Benefits

1. **Smaller Images**: Only runtime artifacts in final image
2. **Better Security**: No build tools in production image
3. **Faster Deploys**: Smaller images push/pull faster
4. **Reproducible Builds**: Consistent environments
5. **Layer Caching**: Faster subsequent builds
