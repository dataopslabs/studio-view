# Quick Start Guide - E2E Validation

## 5-Minute Quick Start

### 1. Prerequisites Check

```bash
# Verify Python is installed
python3 --version  # Should be 3.9+

# Install required packages
pip install pytest requests pytest-html
```

### 2. Start the Application

```bash
# Navigate to your project directory
cd ../qa-automation-platform

# Start services with Docker (recommended)
docker-compose up -d

# Wait for services to start (about 30 seconds)
sleep 30

# Verify services are running
curl http://localhost:8000/health
```

### 3. Run Validation

```bash
# Go to validation framework directory
cd validation_framework

# Run automated validation
python run_validation.py
```

### 4. View Results

```bash
# Generate HTML report
python generate_validation_report.py

# Open the report in your browser
# The file is: validation_report.html
```

## Alternative: Manual Testing Only

If you prefer manual testing:

1. **Open the checklist**: `E2E_Validation_Checklist.docx`
2. **Follow each section systematically**
3. **Check off completed items**
4. **Document any issues**

## Common Commands

```bash
# Run only specific test suite
pytest test_e2e_comprehensive.py::TestSOPWorkflow -v

# Run tests with detailed output
pytest test_e2e_comprehensive.py -vv -s

# Run tests and generate HTML report
pytest test_e2e_comprehensive.py --html=report.html --self-contained-html

# Skip slow tests
pytest test_e2e_comprehensive.py -m "not slow"
```

## Troubleshooting Quick Fixes

**Backend not responding?**
```bash
cd ../qa-automation-platform/backend
uvicorn main:app --reload
```

**Frontend not loading?**
```bash
cd ../qa-automation-platform/frontend
npm run dev
```

**Database issues?**
```bash
# Check if DATABASE_URL is set in .env
cat ../qa-automation-platform/.env | grep DATABASE_URL
```

**Tests failing with "Module not found"?**
```bash
pip install pytest requests pytest-html pytest-asyncio
```

## What Gets Validated

✅ **SOP Management** - Create, edit, list SOPs
✅ **Video Processing** - Upload and analyze videos
✅ **Test Execution** - Run tests via orchestrator
✅ **Validation** - Compare results and generate reports
✅ **AI Agents** - Video, Validation, ECM, Orchestrator
✅ **Performance** - Response times, concurrent operations
✅ **Reliability** - Error handling, data integrity

## Next Steps

- Review the full [README.md](README.md) for detailed information
- Check [test_e2e_comprehensive.py](test_e2e_comprehensive.py) to see all tests
- Use [E2E_Validation_Checklist.docx](E2E_Validation_Checklist.docx) for manual validation
- Customize tests for your specific needs

## Support

For detailed troubleshooting, see the **Troubleshooting** section in [README.md](README.md).
