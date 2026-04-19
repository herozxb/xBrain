# Kubernetes/Docker: Production-Ready Microservice Deployment

## Problem
Deploy a microservice to Kubernetes with proper configuration, secrets management, health checks, auto-scaling, and monitoring.

## Solution

### 1. Dockerfile - Multi-stage Build

```dockerfile
# Dockerfile
# Build stage
FROM golang:1.21-alpine AS builder

WORKDIR /build

# Install dependencies
RUN apk add --no-cache git

# Copy go mod files first for better caching
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build the binary with optimizations
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
    go build -ldflags="-w -s" -o /app/server ./cmd/server

# Final stage - minimal image
FROM alpine:3.18

# Install ca-certificates for HTTPS
RUN apk --no-cache add ca-certificates tzdata

# Create non-root user
RUN adduser -D -g '' appuser

WORKDIR /app

# Copy binary from builder
COPY --from=builder /app/server .
COPY --from=builder /build/config ./config

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# Run the binary
ENTRYPOINT ["./server"]
```

### 2. Kubernetes ConfigMap and Secret

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: api-server-config
  namespace: production
data:
  APP_NAME: "user-service"
  LOG_LEVEL: "info"
  DB_HOST: "postgres-service"
  DB_PORT: "5432"
  DB_NAME: "users_db"
  REDIS_HOST: "redis-service"
  REDIS_PORT: "6379"
  SERVER_PORT: "8080"
  METRICS_PORT: "9090"
---
# secret.yaml (use sealed-secrets or external-secrets in production)
apiVersion: v1
kind: Secret
metadata:
  name: api-server-secrets
  namespace: production
type: Opaque
stringData:
  DB_USER: "app_user"
  DB_PASSWORD: "CHANGE_ME_USE_SEALED_SECRETS"
  JWT_SECRET: "CHANGE_ME_USE_SEALED_SECRETS"
  API_KEY: "CHANGE_ME_USE_SEALED_SECRETS"
```

### 3. Deployment with Probes and Resources

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
  namespace: production
  labels:
    app: user-service
    version: v1
spec:
  replicas: 3
  revisionHistoryLimit: 10
  selector:
    matchLabels:
      app: user-service
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: user-service
        version: v1
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: user-service
      
      # Security context
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      
      # Pod anti-affinity for HA
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchExpressions:
                    - key: app
                      operator: In
                      values: [user-service]
                topologyKey: kubernetes.io/hostname
      
      # Graceful termination
      terminationGracePeriodSeconds: 30
      
      containers:
        - name: server
          image: your-registry/user-service:v1.0.0
          imagePullPolicy: IfNotPresent
          
          ports:
            - name: http
              containerPort: 8080
              protocol: TCP
            - name: metrics
              containerPort: 9090
              protocol: TCP
          
          # Environment variables
          envFrom:
            - configMapRef:
                name: api-server-config
            - secretRef:
                name: api-server-secrets
          
          # Resource limits and requests
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
          
          # Liveness probe - restart container if failed
          livenessProbe:
            httpGet:
              path: /health/live
              port: http
            initialDelaySeconds: 10
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3
          
          # Readiness probe - remove from service if failed
          readinessProbe:
            httpGet:
              path: /health/ready
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 3
            successThreshold: 1
          
          # Startup probe - for slow-starting containers
          startupProbe:
            httpGet:
              path: /health/startup
              port: http
            initialDelaySeconds: 0
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 30  # 30 * 5 = 150s max startup time
          
          # Container security
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop: [ALL]
          
          # Volume mounts
          volumeMounts:
            - name: tmp
              mountPath: /tmp
            - name: cache
              mountPath: /app/cache
      
      volumes:
        - name: tmp
          emptyDir: {}
        - name: cache
          emptyDir:
            medium: Memory
            sizeLimit: "64Mi"
---
# Service
apiVersion: v1
kind: Service
metadata:
  name: user-service
  namespace: production
  labels:
    app: user-service
spec:
  type: ClusterIP
  ports:
    - port: 80
      targetPort: http
      protocol: TCP
      name: http
  selector:
    app: user-service
```

### 4. Horizontal Pod Autoscaler

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: user-service-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: user-service
  
  minReplicas: 3
  maxReplicas: 20
  
  metrics:
    # Scale on CPU utilization
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    
    # Scale on memory utilization
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
    
    # Scale on custom metric (requests per second)
    - type: Pods
      pods:
        metric:
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: "1000"
  
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
        - type: Pods
          value: 4
          periodSeconds: 15
      selectPolicy: Max
```

### 5. ServiceMonitor for Prometheus

```yaml
# servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: user-service
  namespace: production
  labels:
    release: prometheus
spec:
  selector:
    matchLabels:
      app: user-service
  namespaceSelector:
    matchNames:
      - production
  endpoints:
    - port: metrics
      path: /metrics
      interval: 30s
      scrapeTimeout: 10s
---
# PrometheusRule for alerts
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: user-service-alerts
  namespace: production
spec:
  groups:
    - name: user-service.rules
      rules:
        - alert: UserServiceHighErrorRate
          expr: |
            sum(rate(http_requests_total{service="user-service",status=~"5.."}[5m])) 
            / sum(rate(http_requests_total{service="user-service"}[5m])) > 0.05
          for: 5m
          labels:
            severity: critical
          annotations:
            summary: "High error rate on user-service"
            description: "Error rate is {{ $value | humanizePercentage }}"
        
        - alert: UserServiceHighLatency
          expr: |
            histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{service="user-service"}[5m])) by (le)) > 1
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "High latency on user-service"
            description: "P99 latency is {{ $value }}s"
        
        - alert: UserServicePodCrashLooping
          expr: |
            rate(kube_pod_container_status_restarts_total{container="server",namespace="production"}[15m]) > 0.1
          for: 10m
          labels:
            severity: critical
          annotations:
            summary: "Pod is crash looping"
            description: "Container has restarted {{ $value }} times in the last 15 minutes"
```

### 6. Ingress with TLS

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: user-service-ingress
  namespace: production
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
spec:
  tls:
    - hosts:
        - api.example.com
      secretName: api-tls
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /users
            pathType: Prefix
            backend:
              service:
                name: user-service
                port:
                  number: 80
```

### 7. Go Application with Health Endpoints

```go
// cmd/server/main.go
package main

import (
    "context"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"

    "github.com/gorilla/mux"
    "github.com/prometheus/client_golang/prometheus/promhttp"
    "github.com/rs/zerolog/log"
)

type Server struct {
    httpServer *http.Server
    isReady    bool
    isLive     bool
}

func main() {
    // Setup graceful shutdown
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()
    
    // Handle shutdown signals
    sigChan := make(chan os.Signal, 1)
    signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
    
    server := &Server{
        isLive:  true,
        isReady: true, // Set to false during initialization
    }
    
    router := mux.NewRouter()
    
    // Health endpoints
    router.HandleFunc("/health/live", server.livenessHandler).Methods("GET")
    router.HandleFunc("/health/ready", server.readinessHandler).Methods("GET")
    router.HandleFunc("/health/startup", server.startupHandler).Methods("GET")
    
    // Metrics endpoint
    router.Handle("/metrics", promhttp.Handler()).Methods("GET")
    
    // API routes
    api := router.PathPrefix("/api/v1").Subrouter()
    api.HandleFunc("/users", server.listUsers).Methods("GET")
    api.HandleFunc("/users/{id}", server.getUser).Methods("GET")
    
    // Configure HTTP server
    port := getEnv("SERVER_PORT", "8080")
    server.httpServer = &http.Server{
        Addr:         ":" + port,
        Handler:      router,
        ReadTimeout:  15 * time.Second,
        WriteTimeout: 15 * time.Second,
        IdleTimeout:  60 * time.Second,
    }
    
    // Start server in goroutine
    go func() {
        log.Info().Str("port", port).Msg("Starting server")
        if err := server.httpServer.ListenAndServe(); err != http.ErrServerClosed {
            log.Fatal().Err(err).Msg("Server failed")
        }
    }()
    
    // Wait for shutdown signal
    <-sigChan
    log.Info().Msg("Shutting down server...")
    
    // Mark as not ready to stop receiving traffic
    server.isReady = false
    
    // Give pending requests time to complete
    shutdownCtx, shutdownCancel := context.WithTimeout(ctx, 30*time.Second)
    defer shutdownCancel()
    
    if err := server.httpServer.Shutdown(shutdownCtx); err != nil {
        log.Error().Err(err).Msg("Server shutdown error")
    }
    
    log.Info().Msg("Server stopped")
}

func (s *Server) livenessHandler(w http.ResponseWriter, r *http.Request) {
    if s.isLive {
        w.WriteHeader(http.StatusOK)
        w.Write([]byte("OK"))
    } else {
        w.WriteHeader(http.StatusServiceUnavailable)
    }
}

func (s *Server) readinessHandler(w http.ResponseWriter, r *http.Request) {
    if s.isReady {
        w.WriteHeader(http.StatusOK)
        w.Write([]byte("Ready"))
    } else {
        w.WriteHeader(http.StatusServiceUnavailable)
    }
}

func (s *Server) startupHandler(w http.ResponseWriter, r *http.Request) {
    // Check if application has completed startup
    w.WriteHeader(http.StatusOK)
    w.Write([]byte("Started"))
}

func getEnv(key, defaultValue string) string {
    if value := os.Getenv(key); value != "" {
        return value
    }
    return defaultValue
}

func (s *Server) listUsers(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    w.Write([]byte(`{"users": []}`))
}

func (s *Server) getUser(w http.ResponseWriter, r *http.Request) {
    vars := mux.Vars(r)
    w.Header().Set("Content-Type", "application/json")
    w.Write([]byte(`{"id": "` + vars["id"] + `"}`))
}
```

## Tests

```yaml
# test/k8s-test.yaml
apiVersion: v1
kind: Pod
metadata:
  name: k8s-test
  namespace: production
  annotations:
    "helm.sh/hook": test-success
spec:
  containers:
    - name: test
      image: curlimages/curl:latest
      command: ["/bin/sh", "-c"]
      args:
        - |
          echo "Testing health endpoints..."
          
          # Test liveness
          HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://user-service/health/live)
          if [ "$HTTP_CODE" != "200" ]; then
            echo "Liveness check failed: $HTTP_CODE"
            exit 1
          fi
          echo "Liveness: OK"
          
          # Test readiness
          HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://user-service/health/ready)
          if [ "$HTTP_CODE" != "200" ]; then
            echo "Readiness check failed: $HTTP_CODE"
            exit 1
          fi
          echo "Readiness: OK"
          
          # Test API endpoint
          HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://user-service/api/v1/users)
          if [ "$HTTP_CODE" != "200" ]; then
            echo "API check failed: $HTTP_CODE"
            exit 1
          fi
          echo "API: OK"
          
          echo "All tests passed!"
  restartPolicy: Never
```

```bash
# test/integration-test.sh
#!/bin/bash
set -euo pipefail

echo "=== Kubernetes Deployment Tests ==="

# Test 1: Deployment is available
echo "Test 1: Checking deployment availability..."
kubectl wait --for=condition=available --timeout=60s deployment/user-service -n production
echo "✓ Deployment is available"

# Test 2: Pods are running
echo "Test 2: Checking pod status..."
READY_PODS=$(kubectl get pods -n production -l app=user-service -o json | \
  jq -r '.items[] | select(.status.phase=="Running") | .status.containerStatuses[0].ready' | \
  grep -c true || echo "0")
if [ "$READY_PODS" -lt 3 ]; then
  echo "✗ Not enough ready pods: $READY_PODS"
  exit 1
fi
echo "✓ $READY_PODS pods are ready"

# Test 3: Service is accessible
echo "Test 3: Testing service endpoint..."
kubectl run curl-test --rm -it --restart=Never --image=curlimages/curl -- \
  curl -sf http://user-service/health/ready
echo "✓ Service is accessible"

# Test 4: HPA is configured
echo "Test 4: Checking HPA..."
HPA_STATUS=$(kubectl get hpa user-service-hpa -n production -o jsonpath='{.status.conditions[?(@.type=="AbleToScale")].status}')
if [ "$HPA_STATUS" != "True" ]; then
  echo "✗ HPA not able to scale"
  exit 1
fi
echo "✓ HPA is configured"

# Test 5: Resource limits are set
echo "Test 5: Checking resource limits..."
LIMITS=$(kubectl get deployment user-service -n production -o json | \
  jq -r '.spec.template.spec.containers[0].resources.limits')
if [ -z "$LIMITS" ] || [ "$LIMITS" == "null" ]; then
  echo "✗ Resource limits not set"
  exit 1
fi
echo "✓ Resource limits are set"

# Test 6: Security context is configured
echo "Test 6: Checking security context..."
RUN_AS_NON_ROOT=$(kubectl get deployment user-service -n production -o json | \
  jq -r '.spec.template.spec.securityContext.runAsNonRoot')
if [ "$RUN_AS_NON_ROOT" != "true" ]; then
  echo "✗ Security context not properly configured"
  exit 1
fi
echo "✓ Security context is configured"

# Test 7: Rolling update strategy
echo "Test 7: Checking deployment strategy..."
STRATEGY=$(kubectl get deployment user-service -n production -o jsonpath='{.spec.strategy.type}')
if [ "$STRATEGY" != "RollingUpdate" ]; then
  echo "✗ Deployment strategy is not RollingUpdate"
  exit 1
fi
echo "✓ Rolling update strategy configured"

echo ""
echo "=== All tests passed! ==="
```

## Key Features

1. **Multi-stage Docker Build** - Minimal final image size
2. **Health Checks** - Liveness, readiness, and startup probes
3. **Security Hardening** - Non-root user, read-only filesystem
4. **Resource Management** - Requests, limits, and QoS
5. **Auto-scaling** - HPA with custom metrics
6. **Monitoring** - Prometheus integration with ServiceMonitor
7. **Alerting** - Custom alert rules for error rate, latency, crashes
8. **TLS/SSL** - Cert-manager integration for automatic certificates
9. **Graceful Shutdown** - Proper signal handling in application
10. **Integration Tests** - Automated Kubernetes test suite
