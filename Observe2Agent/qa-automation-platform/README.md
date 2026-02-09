# Observe2Agent: AI-Powered QA Automation Platform

An intelligent platform that transforms business process videos into executable automation workflows using Google Gemini AI multimodal analysis, SOP generation, and multi-framework code execution.

## Overview

The Observe2Agent platform bridges the gap between manual business processes and automated testing by leveraging AI to:

- **Analyze business process videos** using Google Gemini multimodal AI to extract workflow steps, detect enterprise systems, and identify data patterns
- **Generate Standard Operating Procedures (SOPs)** as structured, machine-readable documents from video analysis
- **Map processes to enterprise systems** (SAP, Salesforce, Oracle, etc.) with ECM integration
- **Extract structured data** from documents using Google DocumentAI
- **Generate executable automation code** across three frameworks: ADK (Google Agent Development Kit), Selenium, and Playwright
- **Validate and execute** automated workflows with detailed reporting and recommendations

## Architecture

```
                    +------------------+
                    |   Frontend       |
                    |   (Next.js/React)|
                    +--------+---------+
                             |
                    +--------v---------+
                    |   Backend API    |
                    |   (FastAPI)      |
                    +--------+---------+
                             |
              +--------------+--------------+
              |              |              |
     +--------v---+  +------v------+  +----v--------+
     |  Routers   |  |  Services   |  |   Agents    |
     |  (API)     |  |  (Logic)    |  |   (AI)      |
     +------------+  +------+------+  +----+--------+
                            |              |
                   +--------v--------------v--------+
                   |      External Services         |
                   |  Gemini AI | DocumentAI | GCS  |
                   +---------------+----------------+
                                   |
                          +--------v--------+
                          |   PostgreSQL    |
                          |   Database      |
                          +-----------------+
```

### System Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | Next.js 14, React 18, TypeScript, Tailwind CSS | Video upload UI, results visualization, dashboard |
| **Backend** | FastAPI 0.104, Python 3.9+, Pydantic 2.5 | REST API, routing, orchestration, business logic |
| **AI Agents** | Google Gemini, custom agent classes | Video analysis, ECM mapping, validation |
| **Database** | PostgreSQL 15 (Alpine) | Persistent storage for SOPs, results, metadata |
| **External** | Gemini AI, DocumentAI, Cloud Storage | AI inference, document extraction, file storage |

### Processing Pipeline

```
1. Video Upload       -> File validation, storage, background scheduling
2. Video Analysis     -> Gemini multimodal: frame + audio extraction
3. System Detection   -> Enterprise system identification with confidence scoring
4. SOP Generation     -> Structured JSON SOP with steps, criteria, preconditions
5. ECM Mapping        -> Map workflow steps to enterprise system attributes
6. Data Extraction    -> Google DocumentAI structured field extraction
7. Database Write     -> Persist extracted data to PostgreSQL
8. Validation         -> Compare extracted vs source video metadata
9. Code Generation    -> Generate Python code (ADK/Selenium/Playwright)
10. Execution         -> Run automation, capture results, screenshots, logs
```

## Project Structure

```
Observe2Agent/qa-automation-platform/
├── frontend/                       # Next.js React application
│   ├── src/
│   │   └── lib/
│   │       └── api.ts              # Typed API client (Axios)
│   ├── package.json                # Dependencies & scripts
│   └── tsconfig.json               # TypeScript config
├── backend/                        # FastAPI backend
│   ├── main.py                     # Application entry point, CORS, middleware
│   ├── config.py                   # Pydantic settings (env-based)
│   ├── requirements.txt            # Python dependencies
│   ├── Dockerfile                  # Container image definition
│   ├── models/                     # Pydantic data models
│   │   ├── sop.py                  # SOPDocument, SOPStep, SOPGenerationRequest
│   │   ├── systems.py              # DetectedSystem, SystemIntegrationConfig
│   │   └── validation.py           # ValidationReport, ValidationStep
│   ├── routers/                    # API route handlers
│   │   ├── video.py                # Video upload & analysis endpoints
│   │   ├── sop.py                  # SOP CRUD & export endpoints
│   │   ├── execution.py            # Automation execution endpoints
│   │   └── validation.py           # Validation & testing endpoints
│   └── services/                   # Business logic layer
│       ├── video_analyzer.py       # Gemini-based video analysis
│       ├── system_detector.py      # Enterprise system detection
│       ├── sop_generator.py        # SOP document generation
│       ├── code_generator.py       # Multi-framework code generation
│       ├── execution_engine.py     # Code execution & monitoring
│       └── validation_engine.py    # Result validation & reporting
├── agents/                         # AI Agent implementations
│   ├── video_agent.py              # Multimodal video understanding agent
│   ├── ecm_agent.py                # ECM system mapping agent
│   ├── validation_agent.py         # Automated validation agent
│   └── orchestrator/
│       └── final_adk_end2end.py    # End-to-end ADK orchestration
├── tests/
│   └── e2e_simulation.py           # Comprehensive E2E simulation test suite
├── docker-compose.yml              # Docker orchestration (3 services)
├── .env.example                    # Environment variables template
└── README.md                       # This file
```

## Prerequisites

- **Docker** and **Docker Compose** (recommended for quick start)
- **Python 3.9+** (for manual backend setup)
- **Node.js 16+** and **npm** (for manual frontend setup)
- **Google Cloud Account** with the following APIs enabled:
  - Generative AI API (Gemini)
  - DocumentAI API
  - Cloud Storage API
  - Cloud SQL (PostgreSQL)
- Valid API credentials configured in `.env`

## Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/dataopslabs/studio-view.git
cd Observe2Agent/qa-automation-platform
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes | Google Gemini API key |
| `GOOGLE_CLOUD_PROJECT` | Yes | GCP project ID |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `DOCAI_PROCESSOR_ID` | No | DocumentAI processor ID |
| `GCS_BUCKET` | No | Cloud Storage bucket name |
| `ENVIRONMENT` | No | `development` / `production` / `staging` |
| `DEBUG` | No | Enable debug logging (`true`/`false`) |

See `.env.example` for the complete list of configuration options.

### 3. Using Docker Compose (Recommended)

```bash
docker-compose up -d
```

This starts three services:

| Service | Container | Port | Description |
|---------|-----------|------|-------------|
| Backend API | `qa-automation-backend` | 8000 | FastAPI with auto-reload |
| Frontend | `qa-automation-frontend` | 3000 | Next.js dev server |
| PostgreSQL | `qa-automation-db` | 5432 | Database with health checks |

### 4. Manual Setup

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Reference

### Health & Info

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check with version and environment |
| `GET` | `/` | API info with available endpoints |
| `GET` | `/docs` | Interactive Swagger/OpenAPI documentation |

### Video Processing

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/videos/upload` | Upload a business process video |
| `GET` | `/api/videos/{videoId}/status` | Get video processing status |
| `GET` | `/api/videos/{videoId}/analysis` | Get detailed analysis results |
| `DELETE` | `/api/videos/{videoId}` | Delete a video |

### SOP Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/sops/generate` | Generate SOP from video analysis |
| `GET` | `/api/sops/{sopId}` | Get specific SOP document |
| `GET` | `/api/sops/` | List all SOPs (paginated) |
| `PUT` | `/api/sops/{sopId}` | Update SOP document |
| `DELETE` | `/api/sops/{sopId}` | Delete SOP |
| `POST` | `/api/sops/{sopId}/export` | Export SOP (JSON/CSV/Markdown) |

### Execution

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/executions/run` | Run SOP automation |
| `GET` | `/api/executions/{executionId}` | Get execution status |
| `GET` | `/api/executions/{executionId}/logs` | Get execution logs |
| `POST` | `/api/executions/{executionId}/cancel` | Cancel running execution |
| `POST` | `/api/executions/{executionId}/retry` | Retry failed execution |

### Validation & Testing

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/validation/validate` | Run validation for SOP |
| `GET` | `/api/validation/{validationId}` | Get validation results |
| `GET` | `/api/validation/{validationId}/summary` | Get validation summary |
| `GET` | `/api/validation/sop/{sopId}/validations` | Get all validations for SOP |
| `GET` | `/api/validation/dashboard` | Validation dashboard stats |
| `POST` | `/api/validation/{validationId}/re-run` | Re-run validation |
| `POST` | `/api/validation/{validationId}/export` | Export results (JSON/CSV/HTML) |

## Usage Flow

1. **Upload Video** - Upload a business process recording via the frontend or API
2. **AI Analysis** - Gemini multimodal AI analyzes video frames and audio
3. **System Detection** - Enterprise systems are identified with confidence scores
4. **SOP Generation** - Structured SOP document is created with steps, criteria, and metadata
5. **ECM Mapping** - SOP steps are mapped to enterprise system attributes
6. **Code Generation** - Executable automation code is generated (choose ADK, Selenium, or Playwright)
7. **Execution** - Generated code runs with step-by-step monitoring
8. **Validation** - Results are compared against expected outcomes with detailed reporting

## Testing

### End-to-End Simulation

The project includes a comprehensive E2E simulation test that exercises the entire pipeline without requiring external API connections:

```bash
cd tests
python e2e_simulation.py
```

This runs:
- **Unit tests** for all 8 pipeline components (40+ assertions)
- **E2E pipeline test** with ADK framework
- **Multi-framework comparison** (ADK, Selenium, Playwright)
- **Artifact export** to `test_output/` directory

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
npm run type-check    # TypeScript type validation
npm run lint          # ESLint checks
```

## Configuration

### Backend Settings (`backend/config.py`)

Key configuration options loaded from environment:

| Setting | Default | Description |
|---------|---------|-------------|
| `GEMINI_MODEL` | `gemini-1.5-pro-vision` | Gemini model for video analysis |
| `GEMINI_TEMPERATURE` | `0.7` | AI generation temperature |
| `GEMINI_MAX_TOKENS` | `4096` | Max tokens per response |
| `MAX_UPLOAD_SIZE` | `500MB` | Maximum video file upload size |
| `ALLOWED_VIDEO_EXTENSIONS` | `mp4,avi,mov,mkv,webm` | Accepted video formats |
| `VALIDATION_TOLERANCE` | `0.95` | Match threshold for validation |
| `VALIDATION_TIMEOUT` | `300s` | Validation timeout |
| `SYSTEM_DETECTION_THRESHOLD` | `0.7` | Confidence threshold for system detection |
| `VIDEO_FRAME_EXTRACTION_INTERVAL` | `5s` | Frame extraction frequency |

### Supported Automation Frameworks

| Framework | Use Case | Generated Files |
|-----------|----------|----------------|
| **ADK** (Google Agent Development Kit) | Full agent-based automation | Agent, Config, Orchestration (3 files) |
| **Selenium** WebDriver | Traditional web automation | Single automation script |
| **Playwright** | Modern browser automation with async | Single async automation script |

## Troubleshooting

### Database Connection Issues

```bash
# Verify PostgreSQL is running
docker ps | grep qa-automation-db

# Test connection
psql postgresql://qa_user:qa_password@localhost:5432/qa_automation
```

### API Connection Issues

```bash
# Check backend health
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs
```

### Gemini API Errors

- Verify `GOOGLE_API_KEY` is set and valid in `.env`
- Confirm the Generative AI API is enabled in Google Cloud Console
- Check API quota limits in the GCP dashboard

### Video Upload Issues

- Maximum file size: 500MB (configurable via `MAX_UPLOAD_SIZE`)
- Supported formats: MP4, AVI, MOV, MKV, WebM
- Ensure sufficient disk space at upload directory

### Docker Issues

```bash
# Rebuild containers
docker-compose down && docker-compose up -d --build

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Production Deployment

1. Set `ENVIRONMENT=production` and `DEBUG=false` in `.env`
2. Configure a production PostgreSQL instance
3. Update `CORS_ORIGINS` for your domain
4. Enable HTTPS/SSL certificates
5. Set up monitoring and centralized logging
6. Deploy using Docker Compose or Kubernetes
7. Configure proper GCP service account credentials

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React 18, Next.js 14, TypeScript 5.2, Tailwind CSS 3.3, Zustand, Recharts, Axios |
| **Backend** | Python 3.9+, FastAPI 0.104, Pydantic 2.5, SQLAlchemy 2.0, Uvicorn |
| **AI/ML** | Google Gemini 1.5 Pro Vision, Google DocumentAI, Custom AI Agents |
| **Database** | PostgreSQL 15 |
| **Infrastructure** | Docker, Docker Compose, Google Cloud Platform |

## Contributing

1. Create a feature branch from `main`
2. Make your changes following existing code patterns
3. Run the E2E simulation tests: `python tests/e2e_simulation.py`
4. Submit a pull request with a clear description
5. Ensure all checks pass

## License

Proprietary - All rights reserved

## Support

For issues and questions, please open an issue on the repository.
