# CLAUDE.md - Project Intelligence for Observe2Agent

This file provides context for AI assistants (Claude, Copilot, etc.) working on this codebase. It describes architecture, conventions, and operational guidelines.

## Project Summary

**Observe2Agent** is an AI-powered QA automation platform that converts business process videos into executable automation workflows. It uses Google Gemini multimodal AI for video analysis, generates structured SOPs, and produces runnable code across ADK, Selenium, and Playwright frameworks.

**Repository:** `https://github.com/dataopslabs/studio-view.git`
**Primary path:** `Observe2Agent/qa-automation-platform/`

## Architecture Overview

```
Frontend (Next.js/React :3000)
    |
Backend API (FastAPI :8000)
    |
    +-- Routers (video, sop, execution, validation)
    +-- Services (video_analyzer, sop_generator, code_generator, etc.)
    +-- Agents (video_agent, ecm_agent, validation_agent)
    |
External: Google Gemini AI, DocumentAI, Cloud Storage
    |
PostgreSQL 15 (:5432)
```

## Key Directories & Files

### Backend (`backend/`)
- `main.py` - FastAPI app entry point; initializes CORS, routers, exception handlers, lifecycle events
- `config.py` - Pydantic `BaseSettings` class loading from `.env`; all settings are env-configurable
- `models/` - Pydantic v2 data models (sop.py, systems.py, validation.py)
- `routers/` - API endpoint handlers; each file maps to a URL prefix (`/api/videos`, `/api/sops`, etc.)
- `services/` - Business logic layer; each service encapsulates one domain:
  - `video_analyzer.py` - Gemini multimodal video analysis
  - `system_detector.py` - Enterprise system identification
  - `sop_generator.py` - SOP document generation with detail levels (summary/detailed/expert)
  - `code_generator.py` - Multi-framework code generation (ADK, Selenium, Playwright)
  - `execution_engine.py` - Background code execution with monitoring
  - `validation_engine.py` - Result comparison and reporting

### Agents (`agents/`)
- `video_agent.py` - VideoAnalysisAgent: multimodal analysis, workflow extraction, system identification
- `ecm_agent.py` - ECMAgent: process-to-system mapping, integration configuration
- `validation_agent.py` - ValidationAgent: fuzzy matching validation with tolerance thresholds
- `orchestrator/final_adk_end2end.py` - End-to-end ADK orchestration coordinator

### Frontend (`frontend/`)
- `src/lib/api.ts` - Typed Axios-based API client organized by domain (videoAPI, sopAPI, executionAPI, validationAPI)
- Uses Next.js 14, React 18, TypeScript, Tailwind CSS, Zustand for state management

### Tests (`tests/`)
- `e2e_simulation.py` - Comprehensive standalone E2E test (no external APIs needed); includes unit tests, pipeline tests, multi-framework comparison, and artifact export

## Code Conventions

### Python (Backend)
- **Framework:** FastAPI with async endpoints
- **Models:** Pydantic v2 with `BaseModel` and `BaseSettings`
- **Imports:** Standard library first, then third-party, then local modules
- **Naming:** snake_case for functions/variables, PascalCase for classes
- **Config:** All configuration via environment variables through `config.py`
- **Error handling:** Global exception handler in `main.py`, service-level try/except with logging
- **Async:** Background tasks for long-running operations (video analysis, execution)
- **Logging:** Python `logging` module with structured format

### TypeScript (Frontend)
- **Framework:** Next.js 14 with React 18
- **API calls:** Centralized in `api.ts` using Axios with response interceptors
- **State:** Zustand store for global state
- **Styling:** Tailwind CSS utility classes
- **Types:** TypeScript strict mode; interfaces for API response types

### Docker
- `docker-compose.yml` defines 3 services: backend, frontend, postgres
- Backend installs deps at runtime via compose command
- Frontend node_modules excluded from volume mount
- PostgreSQL uses Alpine image with health checks

## Common Tasks

### Running the E2E Test
```bash
cd Observe2Agent/qa-automation-platform/tests
python e2e_simulation.py
```
This exercises the full pipeline with mock data and produces colored terminal output. It runs:
1. Unit tests for all 8 components (40+ assertions)
2. E2E pipeline with ADK
3. Multi-framework comparison (ADK, Selenium, Playwright)
4. Artifact export to `test_output/`

### Starting the Application
```bash
# Docker (recommended)
cd Observe2Agent/qa-automation-platform
docker-compose up -d

# Manual
cd backend && pip install -r requirements.txt && python -m uvicorn main:app --reload
cd frontend && npm install && npm run dev
```

### Adding a New API Endpoint
1. Define Pydantic models in `backend/models/`
2. Create service logic in `backend/services/`
3. Add router handler in `backend/routers/`
4. Register router in `backend/main.py` via `app.include_router()`
5. Add corresponding API client method in `frontend/src/lib/api.ts`

### Adding a New Automation Framework
1. Add generator method in `backend/services/code_generator.py` (follow `_generate_adk` pattern)
2. Add framework handling in `backend/services/execution_engine.py`
3. Add framework option in `tests/e2e_simulation.py` `CodeGenerator` class
4. Update framework enum/validation in models

## API Structure

All API routes follow RESTful conventions under `/api/`:
- `POST` for creation/execution
- `GET` for retrieval
- `PUT` for updates
- `DELETE` for deletion

Response format is consistent JSON:
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

Error responses include `success: false` with error details. In debug mode, stack traces are included.

## Environment Variables

Critical variables (must be set):
- `GOOGLE_API_KEY` - Gemini API key
- `GOOGLE_CLOUD_PROJECT` - GCP project ID
- `DATABASE_URL` - PostgreSQL connection string

See `.env.example` for the full list with descriptions.

## Data Flow

```
Video File
  -> VideoUploader (validate, store)
  -> VideoAnalyzer (Gemini multimodal analysis)
  -> SystemDetector (classify enterprise systems)
  -> SOPGenerator (create structured SOP document)
  -> ECMMapper (map to enterprise attributes)
  -> CodeGenerator (produce ADK/Selenium/Playwright code)
  -> ExecutionEngine (run generated code)
  -> ValidationEngine (compare results, generate report)
```

Each stage is independent and can be invoked separately via API or through the orchestrator for full pipeline execution.

## Key Design Decisions

1. **Service layer pattern** - Business logic separated from API handlers for testability
2. **Multi-framework code generation** - ADK for agents, Selenium for legacy, Playwright for modern async
3. **Pydantic v2** - Type-safe data models with env-based configuration
4. **Background execution** - Long-running tasks (video analysis, code execution) run asynchronously
5. **Standalone E2E tests** - Full pipeline testable without external APIs using mock data
6. **Confidence scoring** - System detection and validation use configurable thresholds
7. **Export flexibility** - SOPs and validation reports exportable in JSON, CSV, Markdown, and HTML

## Gotchas & Notes

- The `backend/main.py` uses deprecated `@app.on_event("startup")` - consider migrating to lifespan context manager
- `config.py` uses `class Config` inside Settings (Pydantic v1 style) instead of `model_config` (Pydantic v2 style)
- The frontend `api.ts` defines API methods but actual page components are not yet fully implemented
- Video analysis currently requires Gemini API access; the E2E simulation provides mock fallback
- The code generator outputs code as strings; generated files are written to temp directories during execution
- CORS is configured for localhost by default; update for production domains
- PostgreSQL credentials in docker-compose use defaults; change for any non-development deployment
