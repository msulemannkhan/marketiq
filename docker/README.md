# Docker Setup Guide

## Available Environments

### Development (`docker-compose.dev.yml`)
- **Hot reload enabled** - code changes automatically refresh the server
- Source code mounted as volume
- DEBUG mode enabled
- Container: `laptop_intelligence_backend_dev`

### Staging (`docker-compose.staging.yml`)
- Production-like environment without Nginx
- Direct backend access for testing
- Container: `marketiq_backend`

### Production (`docker-compose.prod.yml`)
- Full production setup with Nginx reverse proxy
- SSL/HTTPS support
- Load balancing ready
- Container: `marketiq_backend`

## Usage

### Development Mode (with hot reload)
```bash
# From project root
cd docker/compose
docker-compose -f docker-compose.dev.yml up --build

# Or using different port
DB_PORT=5435 BACKEND_PORT=8006 docker-compose -f docker-compose.dev.yml up
```

### Staging
```bash
cd docker/compose
docker-compose -f docker-compose.staging.yml up --build
```

### Production
```bash
cd docker/compose
docker-compose -f docker-compose.prod.yml up --build
```

## Hot Reload Development

The development setup includes:
- ✅ Source code volume mount (`./backend:/app`)
- ✅ Uvicorn `--reload` flag
- ✅ Separate `Dockerfile.dev` for development
- ✅ DEBUG mode enabled

**Benefits:**
- No container rebuilds needed for code changes
- Instant server restart on file changes
- Faster development iteration

## Port Configuration

Default ports (can be overridden with environment variables):
- Database: 5434 (dev), 5434 (staging/prod)
- Backend: 8005 (configurable via `BACKEND_PORT`)
- Data Loader: 6335 (dev only)
- Nginx: 80, 443 (prod only)

## Environment Variables

Required in `.env` file:
```
DB_PORT=5434
BACKEND_PORT=8005
GEMINI_API_KEY=your_key
PINECONE_API_KEY=your_key
PINECONE_INDEX=laptop-intelligence
JWT_SECRET=your_secret
```