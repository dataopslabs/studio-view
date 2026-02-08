# AI-Powered QA Automation Platform

An intelligent platform that uses AI and video analysis to automatically generate Standard Operating Procedures (SOPs) and execute business process automation workflows.

## Overview

The AI-Powered QA Automation Platform leverages Google's Gemini AI multimodal capabilities to:

- Analyze business process videos
- Extract workflow steps and system interactions
- Generate structured SOPs automatically
- Map processes to enterprise systems (ECM, ERP, etc.)
- Extract data using Google DocumentAI
- Validate and execute automated processes using ADK

## Architecture

### System Components

1. **Frontend (Next.js/React)**: User interface for video upload and results visualization
2. **Backend (FastAPI)**: Core API with routing and orchestration
3. **AI Agents**: Specialized agents for different processing tasks
4. **External Services**: Gemini AI, Google DocumentAI, Cloud SQL

### Key Workflows

- **Video Analysis**: Extract workflow information from video uploads
- **SOP Generation**: Create structured Standard Operating Procedures
- **Data Extraction**: Use DocumentAI to extract fields from documents
- **Validation**: Compare extracted data with database records
- **Execution**: Generate and run ADK code for process automation

## Project Structure

```
qa-automation-platform/
├── frontend/                 # Next.js React application
│   ├── src/
│   │   └── lib/
│   │       └── api.ts       # API client
│   ├── package.json
│   ├── tsconfig.json
│   └── next.config.js
├── backend/                 # FastAPI backend
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration settings
│   ├── models/              # Pydantic models
│   │   ├── sop.py
│   │   ├── systems.py
│   │   └── validation.py
│   ├── routers/             # API route handlers
│   │   ├── video.py
│   │   ├── sop.py
│   │   ├── execution.py
│   │   └── validation.py
│   ├── services/            # Business logic
│   │   ├── video_analyzer.py
│   │   ├── sop_generator.py
│   │   ├── system_detector.py
│   │   ├── code_generator.py
│   │   ├── execution_engine.py
│   │   └── validation_engine.py
│   └── requirements.txt
├── agents/                  # AI Agent implementations
│   ├── video_agent.py       # Video analysis agent
│   ├── ecm_agent.py         # ECM mapping agent
│   ├── validation_agent.py  # Validation agent
│   └── orchestrator/
│       └── final_adk_end2end.py
├── docker-compose.yml       # Docker compose configuration
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Node.js 16+
- Google Cloud Account with:
  - Gemini API enabled
  - DocumentAI API enabled
  - Cloud SQL instance (PostgreSQL)
- Valid API credentials

## Setup & Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd qa-automation-platform
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
- `GOOGLE_API_KEY`: Your Google Gemini API key
- `GOOGLE_CLOUD_PROJECT`: Your GCP project ID
- `DATABASE_URL`: PostgreSQL connection string
- Other configuration as needed

### 3. Using Docker Compose (Recommended)

```bash
docker-compose up -d
```

This will start:
- Backend API (port 8000)
- Frontend application (port 3000)
- PostgreSQL database (port 5432)

### 4. Manual Setup

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### Health Check
- `GET /health` - Application health status
- `GET /` - API information

### Video Processing
- `POST /api/videos/upload` - Upload a video for analysis
- `GET /api/videos/{videoId}/status` - Get video processing status
- `GET /api/videos/{videoId}/analysis` - Get analysis results
- `DELETE /api/videos/{videoId}` - Delete a video

### SOP Management
- `POST /api/sops/generate` - Generate SOP from video
- `GET /api/sops/{sopId}` - Get specific SOP
- `GET /api/sops/` - List all SOPs
- `PUT /api/sops/{sopId}` - Update SOP
- `DELETE /api/sops/{sopId}` - Delete SOP
- `POST /api/sops/{sopId}/export` - Export SOP

### Execution
- `POST /api/executions/run` - Run SOP execution
- `GET /api/executions/{executionId}` - Get execution status
- `GET /api/executions/{executionId}/logs` - Get execution logs
- `POST /api/executions/{executionId}/cancel` - Cancel execution
- `POST /api/executions/{executionId}/retry` - Retry execution

### Validation
- `POST /api/validation/validate` - Validate SOP
- `GET /api/validation/{validationId}` - Get validation results
- `GET /api/validation/{validationId}/summary` - Get validation summary
- `GET /api/validation/sop/{sopId}/validations` - Get SOP validations
- `GET /api/validation/dashboard` - Get validation dashboard
- `POST /api/validation/{validationId}/re-run` - Re-run validation
- `POST /api/validation/{validationId}/export` - Export validation results

## Usage Flow

1. **Upload Video**: User uploads a business process video via the frontend
2. **Video Analysis**: Backend analyzes video using Gemini AI
3. **Extract Workflow**: Identifies systems, steps, and data patterns
4. **Generate SOP**: Creates structured JSON SOP document
5. **ECM Mapping**: Map SOP steps to enterprise attributes
6. **Data Extraction**: Use DocumentAI to extract relevant fields
7. **Database Write**: Store extracted data in PostgreSQL
8. **Validation**: Compare extracted data with source video metadata
9. **ADK Generation**: Generate Python ADK code for process automation
10. **Execution**: Run generated code and return status report

## Configuration

### Environment Variables

See `.env.example` for all available configuration options:

- `GOOGLE_API_KEY`: Gemini API key (required)
- `GOOGLE_CLOUD_PROJECT`: GCP project ID
- `DATABASE_URL`: PostgreSQL connection string
- `ENVIRONMENT`: dev/prod/staging
- `DEBUG`: Enable debug logging
- And more...

### Backend Settings

Edit `backend/config.py` for application-level settings:

```python
class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_TITLE: str = "AI QA Automation Platform"
    # ... more settings
```

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Backend linting
cd backend
pylint **/*.py

# Frontend linting
cd frontend
npm run lint
```

### Building for Production

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm run build
npm run start
```

## Troubleshooting

### Database Connection Issues

Ensure PostgreSQL is running and credentials in `.env` are correct:

```bash
psql postgresql://user:password@localhost:5432/qa_automation
```

### API Connection Issues

Check backend health status:

```bash
curl http://localhost:8000/health
```

### Gemini API Errors

Verify API key and quota:
- Check Google Cloud Console
- Ensure Generative AI API is enabled
- Verify quota limits

### Video Upload Issues

- Check file size (max 5GB by default)
- Verify file format (mp4, avi, mov, mkv)
- Ensure disk space available

## Production Deployment

1. Update `.env` with production credentials
2. Set `ENVIRONMENT=production` and `DEBUG=false`
3. Use production database
4. Configure CORS origins for your domain
5. Set up monitoring and logging
6. Use HTTPS/SSL certificates
7. Deploy using Docker or Kubernetes

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request
5. Ensure all checks pass

## License

Proprietary - All rights reserved

## Support

For issues and questions, contact: support@example.com
