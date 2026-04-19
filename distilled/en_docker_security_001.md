# Docker Security Best Practices

## Problem

Implement secure Docker configurations including user management, resource limits, capability dropping, and security scanning.

## Implementation

### Secure Dockerfile

```dockerfile
# ============================================
# Use specific version tag (not :latest)
# ============================================
FROM node:20.10-alpine AS builder

# ============================================
# SECURITY: Create non-root user
# ============================================
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# Copy and install dependencies
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# ============================================
# FINAL STAGE: Minimal attack surface
# ============================================
FROM gcr.io/distroless/nodejs20-debian12:nonroot

# Copy from builder
COPY --from=builder /app/dist /app/dist
COPY --from=builder /app/node_modules /app/node_modules
COPY --from=builder /app/package.json /app/

WORKDIR /app

# Distroless already uses nonroot user (65532:65532)
USER nonroot:nonroot

EXPOSE 3000

CMD ["dist/index.js"]
```

### Secure Docker Compose

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: secure-app
    
    # ============================================
    # SECURITY: User and permissions
    # ============================================
    user: "1000:1000"
    
    # ============================================
    # SECURITY: Read-only filesystem
    # ============================================
    read_only: true
    
    # Temporary filesystems for write operations
    tmpfs:
      - /tmp:size=100M,mode=1777
      - /var/cache:size=50M,mode=1777
    
    # ============================================
    # SECURITY: Drop all capabilities, add only needed
    # ============================================
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE  # Only if binding to port < 1024
    
    # ============================================
    # SECURITY: Resource limits
    # ============================================
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M
    
    # ============================================
    # SECURITY: Network isolation
    # ============================================
    networks:
      - app-network
    
    # ============================================
    # SECURITY: No privilege escalation
    # ============================================
    privileged: false
    security_opt:
      - no-new-privileges:true
      - seccomp:seccomp-profile.json
    
    # ============================================
    # SECURITY: Environment variables
    # ============================================
    environment:
      - NODE_ENV=production
      - LOG_LEVEL=info
    env_file:
      - .env.prod
    
    # Mount secrets (not environment variables!)
    secrets:
      - db_password
      - api_key
    
    # ============================================
    # SECURITY: Health check
    # ============================================
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    
    # ============================================
    # SECURITY: Logging
    # ============================================
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  database:
    image: postgres:15-alpine
    container_name: secure-db
    
    user: postgres
    
    # ============================================
    # SECURITY: Database-specific security
    # ============================================
    environment:
      POSTGRES_DB: appdb
      POSTGRES_USER_FILE: /run/secrets/db_user
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_user
      - db_password
    
    volumes:
      - db-data:/var/lib/postgresql/data
    
    networks:
      - app-network
    
    # No external access
    expose:
      - "5432"
    # ports: NOT exposed to host

networks:
  app-network:
    driver: bridge
    internal: true  # No external network access

volumes:
  db-data:
    driver: local

secrets:
  db_password:
    file: ./secrets/db_password.txt
  db_user:
    file: ./secrets/db_user.txt
  api_key:
    file: ./secrets/api_key.txt
```

### Seccomp Profile (seccomp-profile.json)

```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": ["SCMP_ARCH_X86_64", "SCMP_ARCH_X86"],
  "syscalls": [
    {
      "names": [
        "accept",
        "accept4",
        "access",
        "arch_prctl",
        "bind",
        "brk",
        "capget",
        "capset",
        "chdir",
        "clock_getres",
        "clock_gettime",
        "clock_nanosleep",
        "close",
        "connect",
        "dup",
        "dup2",
        "dup3",
        "epoll_create",
        "epoll_create1",
        "epoll_ctl",
        "epoll_wait",
        "eventfd",
        "eventfd2",
        "execve",
        "exit",
        "exit_group",
        "fcntl",
        "fstat",
        "futex",
        "getcwd",
        "getdents",
        "getdents64",
        "getegid",
        "geteuid",
        "getgid",
        "getpid",
        "getppid",
        "getrlimit",
        "getsockname",
        "getsockopt",
        "gettid",
        "getuid",
        "ioctl",
        "listen",
        "lseek",
        "madvise",
        "mmap",
        "mprotect",
        "munmap",
        "nanosleep",
        "open",
        "openat",
        "pipe",
        "pipe2",
        "poll",
        "read",
        "readv",
        "recvfrom",
        "recvmsg",
        "rt_sigaction",
        "rt_sigprocmask",
        "rt_sigreturn",
        "sched_getaffinity",
        "sched_yield",
        "sendmsg",
        "sendto",
        "set_robust_list",
        "set_tid_address",
        "setitimer",
        "setsockopt",
        "shutdown",
        "sigaltstack",
        "socket",
        "stat",
        "statfs",
        "sysinfo",
        "uname",
        "wait4",
        "write",
        "writev"
      ],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
```

### Security Scan Script

```bash
#!/bin/bash
# security-scan.sh - Comprehensive security scanning

IMAGE=$1
REPORT_DIR="./security-reports"
mkdir -p $REPORT_DIR

echo "=== Docker Security Scan for $IMAGE ==="

# 1. Trivy vulnerability scan
echo "Running Trivy vulnerability scan..."
trivy image --severity HIGH,CRITICAL \
    --output $REPORT_DIR/trivy-report.json \
    --format json \
    $IMAGE

# 2. Docker Scout (built-in)
echo "Running Docker Scout..."
docker scout cves $IMAGE > $REPORT_DIR/scout-report.txt

# 3. Check image configuration
echo "Checking image configuration..."
docker inspect $IMAGE | jq '.[0]' > $REPORT_DIR/image-config.json

# 4. Security recommendations
echo "Checking security recommendations..."
docker scout recommendations $IMAGE > $REPORT_DIR/recommendations.txt

# 5. Container runtime check
echo "Running container security check..."
docker run --rm \
    -v /var/run/docker.sock:/var/run/docker.sock \
    aquasec/trivy image $IMAGE

# 6. Benchmark check (CIS Docker Benchmark)
echo "Running CIS Docker Benchmark..."
docker run --rm \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --net host \
    --pid host \
    --cap-add audit_control \
    docker/docker-bench-security > $REPORT_DIR/cis-benchmark.txt

echo "=== Security scan complete. Reports in $REPORT_DIR ==="
```

### Runtime Security with Falco Rules

```yaml
# falco-rules.yaml - Detect suspicious container activity
- rule: Container Drift Detected
  desc: Detect when a container binary is modified at runtime
  condition: >
    spawned_process and container and
    proc.name in (apt, apt-get, yum, dnf, apk, pip, npm, gem)
  output: >
    Container drift detected (user=%user.name container=%container.id
    process=%proc.name parent=%proc.pname)
  priority: WARNING

- rule: Shell Spawned in Container
  desc: Detect shell spawned in container
  condition: >
    spawned_process and container and
    proc.name in (bash, sh, zsh, ash)
  output: >
    Shell spawned in container (user=%user.name container=%container.id
    shell=%proc.name parent=%proc.pname)
  priority: NOTICE

- rule: Network Connection Outside Allowed
  desc: Detect outbound connections to disallowed IPs
  condition: >
    outbound and container and
    not fd.sip in (allowed_outbound_ips)
  output: >
    Disallowed outbound connection (container=%container.id
    connection=%fd.name)
  priority: WARNING
```

### Tests

```bash
#!/bin/bash
# test-security.sh

set -e

echo "Running security tests..."

# Test 1: No root user
echo "Test 1: Checking for non-root user..."
docker run --rm $IMAGE whoami | grep -v root

# Test 2: Read-only filesystem
echo "Test 2: Checking read-only filesystem..."
docker run --rm --read-only $IMAGE ls /app

# Test 3: No sensitive mounts
echo "Test 3: Checking for sensitive volume mounts..."
docker inspect $IMAGE | jq '.[0].Mounts' | grep -v "/var/run/docker.sock"

# Test 4: Capability check
echo "Test 4: Checking dropped capabilities..."
docker inspect $IMAGE | jq '.[0].HostConfig.CapDrop' | grep "ALL"

# Test 5: Resource limits
echo "Test 5: Checking resource limits..."
docker inspect $IMAGE | jq '.[0].HostConfig.Memory' | grep -v "0"

echo "All security tests passed!"
```

## Security Checklist

| Category | Check | Priority |
|----------|-------|----------|
| Base Image | Use minimal/specific tag | High |
| User | Run as non-root | Critical |
| Capabilities | Drop ALL, add minimal | High |
| Filesystem | Read-only root | High |
| Network | Internal networks | Medium |
| Secrets | Use Docker secrets | Critical |
| Resources | Set CPU/memory limits | Medium |
| Logging | Centralized logs | Medium |
| Scanning | Regular CVE scans | High |

## Security Tools

| Tool | Purpose |
|------|---------|
| Trivy | Vulnerability scanning |
| Docker Scout | Image analysis |
| Falco | Runtime monitoring |
| CIS Benchmark | Configuration audit |
| Anchore | Policy enforcement |
| Snyk | Dependency scanning |

## Key Principles

1. **Least Privilege**: Run with minimum permissions
2. **Defense in Depth**: Multiple security layers
3. **Immutable Infrastructure**: Read-only containers
4. **Secrets Management**: Never in environment variables
5. **Regular Updates**: Keep base images updated
6. **Monitoring**: Detect anomalies at runtime
