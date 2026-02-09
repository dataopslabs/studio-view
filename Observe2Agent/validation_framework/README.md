# AI QA Automation Platform - End-to-End Validation Framework

## Overview

This comprehensive validation framework provides automated and manual testing tools to validate all aspects of the AI QA Automation Platform. It covers:

- **SOP Creation & Management** - Creating, editing, and managing Standard Operating Procedures
- **Video Processing & Analysis** - Video upload, frame extraction, and AI-powered analysis
- **Test Execution & Orchestration** - Running tests through the orchestrator agent
- **Validation & Reporting** - Results validation, comparison, and report generation
- **Agent Integration** - Testing all AI agents and their interactions
- **Performance & Reliability** - Load testing, error handling, and data integrity

## Contents

```
validation_framework/
├── README.md                           # This file
├── run_validation.py                   # Main validation runner script
├── test_e2e_comprehensive.py           # Comprehensive automated test suite
├── E2E_Validation_Checklist.docx       # Manual validation checklist
├── test_fixtures/                      # Test data and sample files
│   └── sample_sop.json                 # Sample SOP for testing
└── reports/                            # Generated test reports (created during execution)
```

## Prerequisites

### System Requirements
- Python 3.9 or higher
- Node.js 18+ and npm
- Docker and Docker Compose (for containerized deployment)
- Minimum 8GB RAM
- Minimum 20GB disk space

### Python Dependencies
Install required Python packages:

```bash
pip install pytest requests pytest-html pytest-asyncio
```

### Environment Setup

1. **Configure environment variables**

   Copy `.env.example` to `.env` in the project root:
   ```bash
   cp ../qa-automation-platform/.env.example ../qa-automation-platform/.env
   ```

   Update the following variables:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   DATABASE_URL=postgresql://user:password@localhost/qa_automation
   BACKEND_URL=http://localhost:8000
   FRONTEND_URL=http://localhost:3000
   ```

2. **Start the application**

   Navigate to the project root and start services:
   ```bash
   cd ../qa-automation-platform

   # Option 1: Using Docker Compose (recommended)
   docker-compose up -d

   # Option 2: Manual startup
   # Terminal 1 - Backend
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload

   # Terminal 2 - Frontend
   cd frontend
   npm install
   npm run dev
   ```

3. **Verify services are running**
   - Backend: http://localhost:8000/health
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs

## Usage

### Quick Start - Automated Validation

Run the complete automated validation suite:

```bash
cd validation_framework
python run_validation.py
```

This will:
1. Check all prerequisites
2. Run comprehensive E2E tests
3. Execute custom validation checks
4. Generate detailed reports
5. Display summary of results

### Running Specific Test Suites

Run only specific test categories:

```bash
# Environment and setup tests
pytest test_e2e_comprehensive.py::TestEnvironment -v

# SOP workflow tests
pytest test_e2e_comprehensive.py::TestSOPWorkflow -v

# Video processing tests
pytest test_e2e_comprehensive.py::TestVideoProcessing -v

# Execution orchestration tests
pytest test_e2e_comprehensive.py::TestExecutionOrchestration -v

# Validation workflow tests
pytest test_e2e_comprehensive.py::TestValidationWorkflow -v

# Agent integration tests
pytest test_e2e_comprehensive.py::TestAgentIntegration -v

# Performance tests
pytest test_e2e_comprehensive.py::TestPerformanceAndReliability -v
```

### Running Individual Tests

Run a specific test function:

```bash
pytest test_e2e_comprehensive.py::TestSOPWorkflow::test_create_sop -v
pytest test_e2e_comprehensive.py::TestVideoProcessing::test_upload_video -v
```

### Manual Validation

For manual testing and checklist-based validation:

1. Open `E2E_Validation_Checklist.docx`
2. Follow the checklist systematically
3. Check off completed items
4. Document any issues in the Notes column
5. Complete the Summary section at the end

## Test Coverage

### 1. Environment Setup & Prerequisites (TestEnvironment)
- Backend health check
- Database connectivity
- Frontend accessibility
- Environment variable validation

### 2. SOP Creation & Management (TestSOPWorkflow)
- Manual SOP creation via API
- SOP retrieval and listing
- SOP update functionality
- AI-powered SOP generation from video
- SOP management operations (search, filter, duplicate, delete)

### 3. Video Processing & Analysis (TestVideoProcessing)
- Video file upload
- Frame extraction with configurable rates
- AI-powered video analysis
- Action detection and timestamping
- System type detection (web, mobile, desktop, API)

### 4. Test Execution & Orchestration (TestExecutionOrchestration)
- Test execution creation
- Execution initiation and queuing
- Real-time progress monitoring
- Orchestrator agent coordination
- Multiple agent invocation
- Execution completion and artifact storage

### 5. Validation & Reporting (TestValidationWorkflow)
- Execution result validation
- Baseline comparison
- Report generation in multiple formats
- Export functionality (JSON, PDF, HTML)

### 6. Agent Integration (TestAgentIntegration)
- Video Agent functionality
- Validation Agent operations
- ECM Agent code generation
- Orchestrator coordination between agents
- Error handling and recovery

### 7. Performance & Reliability (TestPerformanceAndReliability)
- Concurrent execution handling
- API response time benchmarks
- Large file processing
- Error handling and graceful degradation
- Data integrity validation

### 8. Data Integrity (TestDataIntegrity)
- SOP data consistency
- Execution history integrity
- Cross-operation data validation

## Understanding Test Results

### Test Output

Tests provide detailed output:
- ✓ **PASSED** - Test completed successfully
- ✗ **FAILED** - Test failed, see error details
- **SKIPPED** - Test skipped (usually due to missing prerequisites)
- **ERROR** - Test encountered an unexpected error

### Generated Reports

After running tests, check these files:

1. **validation_results.json** - Detailed JSON report with all test results
2. **test_results.xml** - JUnit XML format for CI/CD integration
3. **test_report.html** - Human-readable HTML report (if pytest-html installed)

### Exit Codes

- **0** - All tests passed
- **1** - Some tests failed
- **130** - Interrupted by user (Ctrl+C)

## Configuration

### Timeouts

Adjust timeouts in `test_e2e_comprehensive.py`:

```python
BASE_URL = "http://localhost:8000"  # Backend URL
FRONTEND_URL = "http://localhost:3000"  # Frontend URL
TEST_TIMEOUT = 300  # Maximum time for long operations (seconds)
```

### Test Data

Add or modify test fixtures in `test_fixtures/`:

- `sample_sop.json` - Sample SOP data
- Add `sample_test_video.mp4` - Sample video for video processing tests
- Add additional test data as needed

## Troubleshooting

### Common Issues

**Issue: "Backend service is not running"**
- Solution: Start the backend service: `uvicorn backend.main:app --reload`
- Verify: `curl http://localhost:8000/health`

**Issue: "Frontend not accessible"**
- Solution: Start frontend: `npm run dev` in frontend directory
- Verify: Open http://localhost:3000 in browser

**Issue: "Database connection failed"**
- Solution: Ensure PostgreSQL is running
- Check DATABASE_URL in .env file
- Run migrations if needed

**Issue: "Missing environment variables"**
- Solution: Copy `.env.example` to `.env` and fill in required values
- Ensure ANTHROPIC_API_KEY is set

**Issue: "Test times out"**
- Solution: Increase TEST_TIMEOUT in test file
- Check if AI services are responding
- Verify network connectivity

**Issue: "Module not found" errors**
- Solution: Install missing dependencies: `pip install -r requirements.txt`
- Ensure you're in correct Python environment

### Test Data Setup

Some tests require sample data:

1. **Sample Video**: Place a test video at `test_fixtures/sample_test_video.mp4`
2. **Baseline Execution**: Some comparison tests need a baseline execution ID

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install pytest requests pytest-html

      - name: Start services
        run: |
          docker-compose up -d
          sleep 30  # Wait for services to be ready

      - name: Run E2E validation
        run: |
          cd validation_framework
          python run_validation.py

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: validation_framework/validation_results.json
```

## Best Practices

1. **Run Prerequisites Check First**: Always verify environment before running full suite
2. **Start with Environment Tests**: Ensure system is healthy before functional tests
3. **Use Manual Checklist**: Combine automated and manual testing for comprehensive coverage
4. **Document Issues**: Note any failures or issues in the validation checklist
5. **Run Regularly**: Execute E2E validation after significant changes
6. **Monitor Performance**: Track execution times to identify degradation
7. **Keep Test Data Updated**: Maintain relevant and current test fixtures
8. **Review Logs**: Check execution logs for warnings even if tests pass

## Extending the Framework

### Adding New Tests

1. Create new test class in `test_e2e_comprehensive.py`:

```python
class TestNewFeature:
    """Test new feature functionality"""

    def test_new_functionality(self):
        """Test description"""
        response = requests.post(f"{BASE_URL}/api/new-endpoint")
        assert response.status_code == 200
```

2. Add to validation runner in `run_validation.py` if needed

3. Update manual checklist with new validation items

### Adding Test Fixtures

1. Create fixture file in `test_fixtures/`
2. Reference in pytest fixtures:

```python
@pytest.fixture
def my_test_data():
    with open("test_fixtures/my_data.json") as f:
        return json.load(f)
```

## Support

For issues or questions:

1. Check this README for troubleshooting guidance
2. Review test output and logs for specific errors
3. Consult the main project documentation
4. Check API documentation at http://localhost:8000/docs

## Version History

- **v1.0.0** (2025-02-09)
  - Initial comprehensive E2E validation framework
  - Automated test suite covering all critical workflows
  - Manual validation checklist
  - Test fixtures and sample data
  - Validation runner with reporting

## License

Part of the AI QA Automation Platform project.
