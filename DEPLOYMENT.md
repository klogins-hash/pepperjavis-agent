# PepperJarvis Agent - Docker Deployment Guide

Complete guide to deploy PepperJarvis Agent with PostgreSQL, Redis, MinIO, and observability stack locally.

## 📋 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   Docker Compose Stack                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────┐  ┌───────────────────┐   │
│  │   PepperJarvis Agent         │  │   PostgreSQL      │   │
│  │   (FastAPI Server)           │  │   + pgvector      │   │
│  │   │                          │  │                   │   │
│  │   ├─ /health                │  │ - Sessions        │   │
│  │   ├─ /metrics               │  │ - Messages        │   │
│  │   ├─ /v1/messages           │  │ - Embeddings      │   │
│  │   └─ /v1/capabilities       │  │ - Tasks           │   │
│  └──────────────────────────────┘  └───────────────────┘   │
│           │                                  │               │
│           └──────────────────┬───────────────┘               │
│                              │                               │
│  ┌──────────────────────────────┐  ┌───────────────────┐   │
│  │   Redis Cache                │  │   MinIO Storage   │   │
│  │                              │  │                   │   │
│  │ - Sessions                   │  │ - Documents       │   │
│  │ - Message cache              │  │ - Files           │   │
│  │ - Rate limiting              │  │ - Backups         │   │
│  └──────────────────────────────┘  └───────────────────┘   │
│           │                                                  │
└───────────┼──────────────────────────────────────────────────┘
            │
      ┌─────┴──────────────────────────────────┐
      │     Observability Stack                │
      │                                        │
      │  ┌──────────────────┐                 │
      │  │ Prometheus       │ ← Metrics       │
      │  │ :9090            │                 │
      │  └──────────────────┘                 │
      │           │                           │
      │  ┌────────┴──────────┐                │
      │  │ Grafana           │                │
      │  │ :3000             │                │
      │  └────────┬──────────┘                │
      │           │                           │
      │  ┌────────┴──────────┐                │
      │  │ Jaeger            │                │
      │  │ :16686            │                │
      │  └───────────────────┘                │
      │                                        │
      └────────────────────────────────────────┘
```

## 🚀 Quick Start - Deploy Everything

### Prerequisites

- Docker & Docker Compose installed
- 4GB+ available RAM
- Ports 8000, 5432, 6379, 9000, 9001, 9090, 3000, 16686 available

### 1. Clone the Repository

```bash
git clone https://github.com/klogins-hash/pepperjavis-agent.git
cd pepperjavis-agent
```

### 2. Initialize Submodules (if cloned from GitHub)

```bash
git submodule update --init --recursive
```

### 3. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` if needed to customize passwords and settings.

### 4. Start All Services

```bash
# Start in detached mode (background)
docker-compose up -d

# Or start in foreground (see logs)
docker-compose up
```

### 5. Verify Services are Running

```bash
# Check container status
docker-compose ps

# Expected output:
# NAME                   STATUS              PORTS
# pepperjavis-agent      Up 2 minutes        0.0.0.0:8000->8000/tcp
# pepperjavis-postgres   Up 2 minutes        0.0.0.0:5432->5432/tcp
# pepperjavis-redis      Up 2 minutes        0.0.0.0:6379->6379/tcp
# pepperjavis-minio      Up 2 minutes        0.0.0.0:9000->9000/tcp, 0.0.0.0:9001->9001/tcp
# pepperjavis-prometheus Up 2 minutes        0.0.0.0:9090->9090/tcp
# pepperjavis-grafana    Up 2 minutes        0.0.0.0:3000->3000/tcp
# pepperjavis-jaeger     Up 2 minutes        0.0.0.0:16686->16686/tcp
```

## 🔗 Access Services

Once deployed, access services at:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Agent API** | http://localhost:8000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **Health Check** | http://localhost:8000/health | - |
| **Metrics** | http://localhost:8000/metrics | - |
| **Grafana** | http://localhost:3000 | admin / admin |
| **Jaeger UI** | http://localhost:16686 | - |
| **MinIO Console** | http://localhost:9001 | minioadmin / minio_secure_pass |
| **PostgreSQL** | localhost:5432 | pepperjavis / pepperjavis_secure_pass |
| **Redis** | localhost:6379 | (password: redis_secure_pass) |
| **Prometheus** | http://localhost:9090 | - |

## 📝 API Usage Examples

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "service": "pepperjavis-agent",
  "agent_ready": true,
  "database_ready": true,
  "cache_ready": true
}
```

### Send Message to Agent

```bash
curl -X POST http://localhost:8000/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user-123-session",
    "message": "What time should we schedule the meeting?",
    "temperature": 0.7
  }'
```

### Get Agent Capabilities

```bash
curl http://localhost:8000/v1/capabilities
```

### Get Metrics

```bash
curl http://localhost:8000/metrics
```

## 📊 Monitoring Setup

### Prometheus

Prometheus automatically scrapes metrics from:
- PepperJarvis Agent (:8000/metrics)
- PostgreSQL
- Redis
- MinIO
- Jaeger

View at: http://localhost:9090

### Grafana

Grafana connects to Prometheus and displays metrics dashboards.

**Login:**
- URL: http://localhost:3000
- Username: admin
- Password: admin (from docker-compose.yml)

**Add Dashboard:**
1. Go to Dashboards → New Dashboard
2. Add Prometheus queries for:
   - `pepperjavis_requests_total`
   - `pepperjavis_request_duration_seconds`
   - `pepperjavis_agent_requests_total`
   - `pepperjavis_agent_errors_total`

### Jaeger

Jaeger collects distributed tracing data from the application.

View traces at: http://localhost:16686

**Features:**
- Trace agent requests through the entire stack
- View latency between services
- Identify bottlenecks

## 🗄️ Database Management

### Connect to PostgreSQL

```bash
# From your local machine
psql -h localhost -p 5432 -U pepperjavis -d pepperjavis

# From within Docker
docker-compose exec postgres psql -U pepperjavis -d pepperjavis
```

### Useful PostgreSQL Commands

```sql
-- List tables
\dt

-- View sessions table
SELECT * FROM agent_sessions;

-- View message history
SELECT * FROM messages WHERE session_id = 'user-123-session';

-- View embeddings
SELECT content, created_at FROM embeddings LIMIT 10;

-- View tasks
SELECT * FROM tasks WHERE status = 'pending';
```

### Backup Database

```bash
# Backup to file
docker-compose exec postgres pg_dump -U pepperjavis pepperjavis > backup.sql

# Restore from file
docker-compose exec -T postgres psql -U pepperjavis pepperjavis < backup.sql
```

## 🔴 Redis Management

### Connect to Redis

```bash
# From Docker
docker-compose exec redis redis-cli -a redis_secure_pass

# Commands:
redis-cli -h localhost -p 6379 -a redis_secure_pass
```

### Redis Commands

```bash
# Get keys
KEYS *

# Get value
GET session:user-123-session:last_message

# Monitor cache
MONITOR

# View stats
INFO stats
```

## 📦 MinIO Management

### Access MinIO Console

- URL: http://localhost:9001
- Username: minioadmin
- Password: minio_secure_pass

### Create Bucket

```bash
docker-compose exec minio mc mb minio/pepperjavis
```

### Upload File

```bash
docker-compose exec minio mc cp /path/to/file minio/pepperjavis/
```

## 🛠️ Management Commands

### View Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs pepperjavis

# Follow logs in real-time
docker-compose logs -f pepperjavis
```

### Stop Services

```bash
# Stop but keep containers
docker-compose stop

# Stop and remove
docker-compose down

# Stop and remove volumes (cleans database)
docker-compose down -v
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart pepperjavis
```

### Rebuild Images

```bash
# Rebuild agent image
docker-compose build pepperjavis

# Rebuild and restart
docker-compose up -d --build pepperjavis
```

## 🔍 Troubleshooting

### Agent Container Won't Start

```bash
# Check logs
docker-compose logs pepperjavis

# Verify dependencies are running
docker-compose ps

# Ensure ports are free
lsof -i :8000
```

### Database Connection Error

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Try manual connection
docker-compose exec postgres psql -U pepperjavis -d pepperjavis

# Check logs
docker-compose logs postgres
```

### Redis Connection Issues

```bash
# Check Redis is running
docker-compose exec redis redis-cli ping

# Check Redis logs
docker-compose logs redis
```

### Out of Memory

```bash
# Check Docker resource usage
docker stats

# Increase Docker memory limit in Docker Desktop settings
# Or reduce configured memory limits
```

### Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

## 📈 Performance Tuning

### PostgreSQL

Edit `docker-compose.yml`:

```yaml
environment:
  POSTGRES_INIT_ARGS: |
    -c shared_buffers=256MB
    -c effective_cache_size=1GB
    -c min_wal_size=2GB
    -c max_wal_size=4GB
```

### Redis

Edit `docker-compose.yml`:

```yaml
command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
```

## 🔐 Security in Production

### Change All Default Credentials

Edit `.env`:

```bash
POSTGRES_PASSWORD=<strong-random-password>
REDIS_PASSWORD=<strong-random-password>
MINIO_ROOT_PASSWORD=<strong-random-password>
GRAFANA_PASSWORD=<strong-random-password>
```

### Use Secrets Management

For production, use Docker Secrets:

```bash
echo "my-secure-password" | docker secret create db_password -
```

### Enable SSL/TLS

```nginx
# Add nginx reverse proxy to docker-compose.yml
# Configure SSL certificates
```

### Network Isolation

```yaml
# Only expose necessary ports
ports:
  - "8000:8000"  # Agent API
  # Don't expose internal databases
```

## 📛 Environment Variables

Complete list of supported environment variables:

```bash
# Application
ENVIRONMENT=production
LOG_LEVEL=INFO

# LLM Configuration
STRANDS_MODEL_PROVIDER=bedrock
STRANDS_MODEL_ID=us.amazon.nova-pro-v1:0
AWS_REGION=us-west-2

# Database
DATABASE_URL=postgresql://...
POSTGRES_DB=pepperjavis
POSTGRES_USER=pepperjavis
POSTGRES_PASSWORD=...

# Cache
REDIS_URL=redis://...
REDIS_PASSWORD=...

# Storage
MINIO_URL=http://minio:9000
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=...
MINIO_BUCKET=pepperjavis

# Observability
JAEGER_AGENT_HOST=jaeger
JAEGER_AGENT_PORT=6831
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:14268/api/traces
```

## 🚀 Deployment to Production

### Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml pepperjavis
```

### Using Kubernetes

```bash
# Convert docker-compose to Kubernetes manifests
kompose convert

# Deploy to Kubernetes
kubectl apply -f .
```

### Using AWS ECS

```bash
# Create ECS task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create ECS service
aws ecs create-service --cluster pepperjavis --service-name agent --task-definition pepperjavis:1
```

## 📞 Support

- **Issues**: Check Docker logs: `docker-compose logs [service]`
- **Documentation**: See main README.md
- **API Docs**: http://localhost:8000/docs
- **GitHub**: https://github.com/klogins-hash/pepperjavis-agent

---

**Deployment Complete!** 🎉

Your PepperJarvis Agent is now running with full observability and data persistence.
