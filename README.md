# 📋 Cross-Marketplace Laptop Intelligence System

A focused laptop intelligence system for business laptops from HP and Lenovo. Built to deliver production-ready API with authentication, LLM-powered chat, and recommendation system with citations.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)

## 🎯 Client Requirements

**Target Products:**

- HP ProBook 450 G10, ProBook 440 G11
- Lenovo ThinkPad E14 Gen 5 (Intel & AMD)

**Deliverables:**

- ✅ Production-ready REST API with JWT authentication
- ✅ Database with catalog, specs, reviews, price history
- 🔄 LLM-powered chat and recommendation system
- 📋 Optional frontend UI
- ✅ Documentation and deployment artifacts

## 🌟 Features

- 🔐 **JWT Authentication** - All endpoints protected with authentication
- 🔍 **Product Catalog** - Complete laptop specifications and variants
- 📊 **Price History** - Historical pricing trends
- ⭐ **Reviews Intelligence** - Customer reviews with sentiment analysis
- 🤖 **AI Chat** - Natural language queries with Gemini Pro
- 💡 **Enhanced Recommendations** - AI-powered suggestions with use-case scoring
- 🔍 **Advanced Search** - Multi-criteria filtering with price, brand, rating
- 🧠 **Product Q&A** - AI-powered product questions with confidence scoring
- 🎁 **Dynamic Offers** - Real-time promotions and discount calculations
- 📈 **Analytics Dashboard** - System metrics and search trends
- 🐳 **Docker Ready** - Single-command deployment

## 🚀 Quick Start with Docker

### Prerequisites

- Docker & Docker Compose installed
- API Keys: [Google AI Studio](https://aistudio.google.com/apikey) (Gemini), [Pinecone](https://app.pinecone.io/) (Vector DB)

### One-Command Deployment

**1. Clone and Configure**

```bash
git clone <repository-url>
cd review-intelligence-system

# Copy and edit environment file
cp .env.example .env
# Edit .env with your API keys (GEMINI_API_KEY, PINECONE_API_KEY)
```

**2. Start Everything**

```bash
# Windows PowerShell
.\scripts\deployment\start-system.ps1

# Linux/macOS
chmod +x scripts/deployment/start-system.sh
./scripts/deployment/start-system.sh

# Manual Docker (from docker/compose directory)
cd docker/compose
docker-compose -f docker-compose.dev.yml up --build -d

# Alternative: Using env file flag from any directory
docker-compose --env-file .env -f docker/compose/docker-compose.dev.yml up -d

# Alternative: Export environment variables before running
export $(cat .env | xargs) && docker-compose -f docker/compose/docker-compose.dev.yml up -d

# Clear Docker cache if you have build issues
docker-compose -f docker/compose/docker-compose.dev.yml down
docker system prune -f
docker-compose -f docker/compose/docker-compose.dev.yml up --build -d
```

**Note on Environment Variables:**
Docker Compose needs access to your `.env` file. Options:

1. Run from `docker/compose/` directory (a symlink to root `.env` is already created)
2. Use `--env-file` flag to specify the `.env` location
3. Export variables to your shell before running Docker Compose

**3. Test the System**

```bash
# Windows PowerShell
.\scripts\deployment\test-api.ps1

# Manual API test
curl http://localhost:8005/health
```

### 🌐 Access URLs

After deployment (default ports - configurable in .env):

- **API Documentation**: http://localhost:8005/docs
- **Health Check**: http://localhost:8005/health
- **Database**: localhost:5434 (admin/admin123)

### 🐳 Docker Services

The system runs these containers:

- **PostgreSQL Database** (port 5434) - Product data, reviews, users
- **Backend API** (port 8005) - FastAPI with Gemini agent
- **Data Loader** (port 6335) - Loads sample data and sets up Pinecone embeddings

## 📊 Data Management

### Sample Data (Default)

The system automatically loads sample data for the 4 target laptops:

- **HP ProBook 450 G10** - Business laptop with Intel processors
- **HP ProBook 440 G11** - Compact business laptop
- **Lenovo ThinkPad E14 Gen 5 (Intel)** - Enterprise laptop with Intel chips
- **Lenovo ThinkPad E14 Gen 5 (AMD)** - Enterprise laptop with AMD processors

Each includes pricing, specifications, reviews, and availability data.

### 📁 Data Ingestion Pipelines

Add your own data to the system using these pipelines:

#### **1. Load from Product Configuration**

```bash
# Load directly from data/product_configurations.json
docker-compose exec backend python scripts/load_from_config.py

# Convert configuration to sample format first
docker-compose exec backend python scripts/convert_product_config.py
```

#### **2. Ingest JSON Product Data**

```bash
# Put your scraped JSON files in:
# data/scraped/hp/hp_probook_440_g11.json
# data/scraped/lenovo/thinkpad_e14_gen5_intel.json

# Then run the ingestion pipeline
docker-compose exec backend python scripts/ingest_products.py
```

#### **3. Ingest PDF Documents**

```bash
# Put your PDF spec sheets in:
# data/pdfs/hp_probook_440_spec.pdf
# data/pdfs/thinkpad_e14_manual.pdf

# Then run the PDF ingestion pipeline
docker-compose exec backend python scripts/ingest_pdfs.py
```

#### **4. Complete Data Ingestion**

```bash
# Run all ingestion pipelines at once
docker-compose exec backend python scripts/ingest_all.py
```

#### **5. Generate Vector Embeddings**

```bash
# Generate embeddings for semantic search
docker-compose exec backend python scripts/setup_embeddings.py
```

### 🧪 Test Data Ingestion

```bash
# Test product search functionality
docker-compose exec backend python scripts/test_product_search.py

# Test PDF document search
docker-compose exec backend python scripts/test_pdf_search.py
```

### 📋 Key Scripts Reference

All scripts are located in `backend/scripts/` and should be run from the backend container:

```bash
# Core Data Scripts
docker-compose exec backend python scripts/load_sample_reviews.py        # Load default sample data
docker-compose exec backend python scripts/setup_embeddings.py           # Generate vector embeddings
docker-compose exec backend python scripts/load_from_config.py          # Load from product_configurations.json

# Data Ingestion Pipelines
docker-compose exec backend python scripts/ingest_products.py           # Ingest JSON product data
docker-compose exec backend python scripts/ingest_pdfs.py              # Ingest PDF documents
docker-compose exec backend python scripts/ingest_all.py               # Run all ingestion pipelines

# Testing Scripts
docker-compose exec backend python scripts/test_product_search.py       # Test product search
docker-compose exec backend python scripts/test_pdf_search.py          # Test document search

# Utility Scripts
docker-compose exec backend python scripts/convert_product_config.py    # Convert config to sample format
docker-compose exec backend python scripts/recreate_pinecone_index.py   # Recreate vector index
```

### 📥 HP JSON Data Import

To import HP JSON data from another PC, use the upload endpoint:

```bash
# Upload and import HP JSON file
curl -X POST "http://localhost:8005/api/v1/data/import/upload" \
  -F "file=@/path/to/your/hp_data.json" \
  -F "override_existing=true" \
  -F "validate_only=false"

# Validate JSON file structure first (recommended)
curl -X POST "http://localhost:8005/api/v1/data/import/upload" \
  -F "file=@/path/to/your/hp_data.json" \
  -F "validate_only=true"

# Check import status
curl -X GET "http://localhost:8005/api/v1/data/import/status"

# Import from file path (if JSON is already on server)
curl -X POST "http://localhost:8005/api/v1/data/import/file-path" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/server/hp_data.json",
    "override_existing": true,
    "validate_only": false
  }'
```

## 🏗️ Simplified Architecture

```
┌─────────────────────────────────────────────────────┐
│              Frontend (Optional)                    │
├─────────────────────────────────────────────────────┤
│          FastAPI Backend (main.py)                  │
│     JWT Auth + All Endpoints + Models               │
├─────────────────────────────────────────────────────┤
│  PostgreSQL     │    Pinecone     │   Gemini Pro    │
│  (Primary DB)   │  (Vector Search) │   (LLM Chat)    │
└─────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend (Monolithic):**

- Python 3.11+ with FastAPI 0.109.0
- PostgreSQL 16+ (primary storage)
- SQLAlchemy (ORM) + Pydantic (validation)
- JWT authentication with passlib

**AI/ML Services:**

- Google Gemini Pro (chat & recommendations)
- Pinecone (vector database for semantic search)
- Sentence-Transformers (embeddings)

**Deployment:**

- Docker & Docker Compose
- Single container for backend + PostgreSQL

## 🔌 API Endpoints (18 Total - All require JWT Authentication except health)

### Authentication

- `POST /auth/register` - User registration
- `POST /auth/login` - User login (returns JWT token)

### Product Catalog

- `GET /api/v1/products` - List all laptops with pagination
- `GET /api/v1/products/{id}` - Get specific laptop details
- `GET /api/v1/products/{id}/variants` - Get laptop configurations/SKUs
- `GET /api/v1/products/{id}/price-history` - Price trend data

### Search & Discovery

- `GET /api/v1/search` - Basic product search
- `GET /api/v1/search/advanced` ✨ - **Enhanced multi-criteria search**
- `GET /api/v1/search/semantic` - Vector-based semantic search

### Reviews & Intelligence

- `GET /api/v1/products/{id}/reviews` - Get product reviews
- `GET /api/v1/products/{id}/reviews/analysis` ✨ - **Enhanced sentiment analysis**

### AI-Powered Features

- `POST /api/v1/chat` - LLM chat interface (Gemini integration)
- `POST /api/v1/compare` - Product comparison
- `POST /api/v1/ai/recommendations` ✨ - **Enhanced AI recommendations**

### Enhanced Business Features

- `GET /api/v1/products/{id}/qa` ✨ - **AI-powered product Q&A**
- `GET /api/v1/products/{id}/offers` ✨ - **Dynamic offers & promotions**
- `GET /api/v1/analytics/dashboard` ✨ - **Real-time analytics dashboard**

### System

- `GET /health` - Health check endpoint (no auth required)
- `GET /` - Root endpoint

## 📋 Environment Configuration

Create a `.env` file in the root directory:

```env
# Port Configuration (Change these to avoid conflicts)
DB_PORT=5434
BACKEND_PORT=8005
DATA_LOADER_PORT=6335

# Database Configuration
DATABASE_URL=postgresql://admin:admin123@localhost:5434/laptop_intelligence

# AI/LLM Configuration
GEMINI_API_KEY=your_gemini_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment_here
PINECONE_INDEX=laptop-intelligence

# Security
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Application Configuration
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:8005,http://127.0.0.1:8005
DEBUG=true
LOAD_SAMPLE_DATA=true
```

## 📊 API Usage Examples

### 1. Register & Login

```bash
# Register a new user
curl -X POST "http://localhost:8005/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'

# Login to get JWT token
curl -X POST "http://localhost:8005/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

### 2. Access Protected Endpoints

```bash
# Get laptop catalog (replace YOUR_JWT_TOKEN)
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "http://localhost:8005/api/v1/catalog"

# Search laptops
curl -X POST "http://localhost:8005/api/v1/search" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "HP",
    "min_price": 500,
    "max_price": 1500
  }'

# Chat with AI
curl -X POST "http://localhost:8005/api/v1/chat" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What laptop do you recommend for programming under $1200?"
  }'

# Get recommendations
curl -X POST "http://localhost:8005/api/v1/recommendations" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "budget": 1000,
    "use_case": "business"
  }'
```

## 🧪 Testing

```bash
# Install dependencies and run tests
cd backend
pip install -r requirements.txt
pytest

# Test API manually with curl (after starting the server)
# Check health endpoint (no auth required)
curl http://localhost:8005/health
```

## 📋 Production Deployment

### Using Deployment Scripts

```bash
# Windows PowerShell
scripts/deployment/deploy.ps1

# Linux/macOS
scripts/deployment/deploy.sh
```

### Manual Production Setup

```bash
# Set production environment variables
export ENVIRONMENT=production
export DEBUG=false
export JWT_SECRET=your-very-secure-production-secret

# Start with production settings
docker-compose up --build -d

# Verify deployment
scripts/deployment/verify-deployment.ps1  # or .sh
```

## 🔧 Troubleshooting

### Environment Variable Warnings

If you see warnings like:

```
level=warning msg="The \"GEMINI_API_KEY\" variable is not set. Defaulting to a blank string."
```

**Solutions:**

1. **Ensure `.env` file exists in root directory:**

   ```bash
   ls -la .env  # Should show your .env file
   ```

2. **Create symlink in docker/compose directory (already done):**

   ```bash
   cd docker/compose
   ln -s ../../.env .env
   ```

3. **Use --env-file flag:**

   ```bash
   docker-compose --env-file .env -f docker/compose/docker-compose.dev.yml up -d
   ```

4. **Verify environment variables are loaded:**

   ```bash
   # Check if variables are set
   docker-compose -f docker/compose/docker-compose.dev.yml config | grep API_KEY

   # Check running container environment
   docker exec laptop_intelligence_backend_dev env | grep API_KEY
   ```

### Common Issues

- **Port already in use**: Change ports in `.env` file (BACKEND_PORT, DB_PORT)
- **Database connection failed**: Ensure PostgreSQL container is healthy
- **API key errors**: Verify your Gemini and Pinecone API keys are valid
- **Docker build fails**: Clear cache with `docker system prune -a`

## 📁 Project Structure

```
review-intelligence-system/
├── backend/
│   ├── main.py                 # Complete FastAPI application
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile             # Container configuration
├── scripts/
│   ├── docker/
│   │   └── init-db.sql        # Database initialization
│   └── deployment/            # All deployment scripts
├── data/
│   ├── demo/                  # Client requirements
│   ├── pdfs/                  # Canonical specifications
│   └── sample/               # Sample data
├── docker-compose.yml         # Service orchestration
├── .env                      # Environment configuration
├── CLAUDE.md                 # Development guide
├── PLAN.md                   # Implementation plan
└── README.md                 # This file
```

## 📄 License

This project is built for demonstrating a laptop intelligence system as per client requirements.

---

**🎯 Focus: Delivering production-ready API with authentication, LLM integration, and comprehensive laptop intelligence capabilities.**
