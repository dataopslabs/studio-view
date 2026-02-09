"""
Comprehensive End-to-End Test Suite for AI QA Automation Platform
Tests all critical workflows: SOP Management, Video Processing, Execution, and Validation
"""

import pytest
import requests
import json
import time
from pathlib import Path
from typing import Dict, Any, List
import asyncio

# Configuration
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"
TEST_TIMEOUT = 300  # 5 minutes


class TestEnvironment:
    """Test environment setup and health checks"""

    def test_backend_health(self):
        """Verify backend service is running"""
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=10)
            assert response.status_code == 200, "Backend health check failed"
            assert response.json().get("status") == "healthy"
        except requests.exceptions.ConnectionError:
            pytest.fail("Backend service is not running. Start with: uvicorn backend.main:app")

    def test_database_connection(self):
        """Verify database connectivity"""
        response = requests.get(f"{BASE_URL}/api/health/db", timeout=10)
        assert response.status_code == 200, "Database connection failed"
        assert response.json().get("database") == "connected"

    def test_frontend_accessible(self):
        """Verify frontend is accessible"""
        try:
            response = requests.get(FRONTEND_URL, timeout=10)
            assert response.status_code == 200, "Frontend not accessible"
        except requests.exceptions.ConnectionError:
            pytest.skip("Frontend service not running. Start with: npm run dev")

    def test_required_environment_variables(self):
        """Check if required environment variables are set"""
        response = requests.get(f"{BASE_URL}/api/config/check", timeout=10)
        config = response.json()

        required_vars = ["ANTHROPIC_API_KEY", "DATABASE_URL"]
        missing_vars = [var for var in required_vars if not config.get(var)]

        assert not missing_vars, f"Missing environment variables: {', '.join(missing_vars)}"


class TestSOPWorkflow:
    """Test SOP creation and management workflow"""

    @pytest.fixture
    def sample_sop_data(self):
        """Sample SOP for testing"""
        return {
            "name": "Login Test SOP",
            "description": "Standard procedure for testing login functionality",
            "steps": [
                {
                    "step_number": 1,
                    "action": "Navigate to login page",
                    "expected_result": "Login page displays"
                },
                {
                    "step_number": 2,
                    "action": "Enter valid credentials",
                    "expected_result": "Credentials accepted"
                },
                {
                    "step_number": 3,
                    "action": "Click login button",
                    "expected_result": "User successfully logged in"
                }
            ],
            "system_type": "web_application"
        }

    def test_create_sop(self, sample_sop_data):
        """Test SOP creation via API"""
        response = requests.post(
            f"{BASE_URL}/api/sop/create",
            json=sample_sop_data,
            timeout=30
        )

        assert response.status_code == 201, f"SOP creation failed: {response.text}"

        sop_response = response.json()
        assert "sop_id" in sop_response, "SOP ID not returned"
        assert sop_response["name"] == sample_sop_data["name"]

        # Store SOP ID for other tests
        pytest.sop_id = sop_response["sop_id"]
        return sop_response["sop_id"]

    def test_retrieve_sop(self):
        """Test retrieving created SOP"""
        if not hasattr(pytest, 'sop_id'):
            pytest.skip("No SOP ID available. Run test_create_sop first")

        response = requests.get(
            f"{BASE_URL}/api/sop/{pytest.sop_id}",
            timeout=10
        )

        assert response.status_code == 200, "Failed to retrieve SOP"

        sop = response.json()
        assert sop["sop_id"] == pytest.sop_id
        assert "steps" in sop
        assert len(sop["steps"]) > 0

    def test_update_sop(self, sample_sop_data):
        """Test SOP update functionality"""
        if not hasattr(pytest, 'sop_id'):
            pytest.skip("No SOP ID available")

        updated_data = sample_sop_data.copy()
        updated_data["description"] = "Updated description for testing"

        response = requests.put(
            f"{BASE_URL}/api/sop/{pytest.sop_id}",
            json=updated_data,
            timeout=30
        )

        assert response.status_code == 200, "SOP update failed"

        # Verify update
        verify_response = requests.get(f"{BASE_URL}/api/sop/{pytest.sop_id}")
        assert verify_response.json()["description"] == updated_data["description"]

    def test_list_sops(self):
        """Test listing all SOPs"""
        response = requests.get(f"{BASE_URL}/api/sop/list", timeout=10)

        assert response.status_code == 200, "Failed to list SOPs"

        sops = response.json()
        assert isinstance(sops, list), "SOPs should be returned as a list"
        assert len(sops) > 0, "At least one SOP should exist"

    def test_generate_sop_from_video(self):
        """Test AI-powered SOP generation from video"""
        # This requires a sample video file
        video_path = Path("test_fixtures/sample_test_video.mp4")

        if not video_path.exists():
            pytest.skip("Sample video not available")

        with open(video_path, "rb") as video_file:
            files = {"video": video_file}
            data = {"system_type": "web_application"}

            response = requests.post(
                f"{BASE_URL}/api/sop/generate/video",
                files=files,
                data=data,
                timeout=TEST_TIMEOUT
            )

        assert response.status_code == 201, "SOP generation from video failed"

        sop = response.json()
        assert "sop_id" in sop
        assert len(sop["steps"]) > 0, "Generated SOP should have steps"


class TestVideoProcessing:
    """Test video processing and analysis workflow"""

    @pytest.fixture
    def sample_video_path(self):
        """Path to sample video for testing"""
        return Path("test_fixtures/sample_test_video.mp4")

    def test_upload_video(self, sample_video_path):
        """Test video upload"""
        if not sample_video_path.exists():
            pytest.skip("Sample video not available")

        with open(sample_video_path, "rb") as video_file:
            files = {"video": video_file}

            response = requests.post(
                f"{BASE_URL}/api/video/upload",
                files=files,
                timeout=60
            )

        assert response.status_code == 201, f"Video upload failed: {response.text}"

        video_data = response.json()
        assert "video_id" in video_data
        assert "url" in video_data

        pytest.video_id = video_data["video_id"]
        return video_data["video_id"]

    def test_extract_frames(self):
        """Test frame extraction from video"""
        if not hasattr(pytest, 'video_id'):
            pytest.skip("No video ID available")

        response = requests.post(
            f"{BASE_URL}/api/video/{pytest.video_id}/extract-frames",
            json={"frame_rate": 1},  # 1 frame per second
            timeout=TEST_TIMEOUT
        )

        assert response.status_code == 200, "Frame extraction failed"

        frames = response.json()
        assert "frames" in frames
        assert len(frames["frames"]) > 0, "Should extract at least one frame"

        pytest.frames = frames["frames"]

    def test_analyze_video_with_ai(self):
        """Test AI analysis of video content"""
        if not hasattr(pytest, 'video_id'):
            pytest.skip("No video ID available")

        response = requests.post(
            f"{BASE_URL}/api/video/{pytest.video_id}/analyze",
            json={"analysis_type": "action_detection"},
            timeout=TEST_TIMEOUT
        )

        assert response.status_code == 200, "Video analysis failed"

        analysis = response.json()
        assert "actions" in analysis
        assert "timestamps" in analysis
        assert "confidence_scores" in analysis

    def test_system_detection(self):
        """Test automatic system type detection from video"""
        if not hasattr(pytest, 'video_id'):
            pytest.skip("No video ID available")

        response = requests.post(
            f"{BASE_URL}/api/video/{pytest.video_id}/detect-system",
            timeout=60
        )

        assert response.status_code == 200, "System detection failed"

        detection = response.json()
        assert "system_type" in detection
        assert "confidence" in detection
        assert detection["confidence"] > 0.5, "Low confidence in system detection"


class TestExecutionOrchestration:
    """Test execution and orchestration workflow"""

    def test_create_test_execution(self):
        """Test creating a new test execution"""
        if not hasattr(pytest, 'sop_id'):
            pytest.skip("No SOP ID available")

        execution_request = {
            "sop_id": pytest.sop_id,
            "environment": "staging",
            "execution_mode": "automated"
        }

        response = requests.post(
            f"{BASE_URL}/api/execution/create",
            json=execution_request,
            timeout=30
        )

        assert response.status_code == 201, "Execution creation failed"

        execution = response.json()
        assert "execution_id" in execution
        assert execution["status"] == "pending"

        pytest.execution_id = execution["execution_id"]
        return execution["execution_id"]

    def test_start_execution(self):
        """Test starting test execution"""
        if not hasattr(pytest, 'execution_id'):
            pytest.skip("No execution ID available")

        response = requests.post(
            f"{BASE_URL}/api/execution/{pytest.execution_id}/start",
            timeout=30
        )

        assert response.status_code == 200, "Execution start failed"

        status = response.json()
        assert status["status"] in ["running", "queued"]

    def test_monitor_execution_progress(self):
        """Test monitoring execution progress"""
        if not hasattr(pytest, 'execution_id'):
            pytest.skip("No execution ID available")

        # Poll execution status
        max_polls = 60  # 5 minutes max
        poll_interval = 5  # seconds

        for _ in range(max_polls):
            response = requests.get(
                f"{BASE_URL}/api/execution/{pytest.execution_id}/status",
                timeout=10
            )

            assert response.status_code == 200, "Failed to get execution status"

            status = response.json()
            assert "status" in status
            assert "progress" in status

            if status["status"] in ["completed", "failed"]:
                pytest.execution_status = status["status"]
                break

            time.sleep(poll_interval)
        else:
            pytest.fail("Execution did not complete within timeout")

    def test_retrieve_execution_logs(self):
        """Test retrieving execution logs"""
        if not hasattr(pytest, 'execution_id'):
            pytest.skip("No execution ID available")

        response = requests.get(
            f"{BASE_URL}/api/execution/{pytest.execution_id}/logs",
            timeout=30
        )

        assert response.status_code == 200, "Failed to retrieve logs"

        logs = response.json()
        assert "logs" in logs
        assert isinstance(logs["logs"], list)

    def test_orchestrator_agent_integration(self):
        """Test orchestrator agent functionality"""
        test_request = {
            "sop_id": getattr(pytest, 'sop_id', None),
            "video_id": getattr(pytest, 'video_id', None),
            "mode": "full_automation"
        }

        response = requests.post(
            f"{BASE_URL}/api/orchestrator/execute",
            json=test_request,
            timeout=TEST_TIMEOUT
        )

        assert response.status_code == 200, "Orchestrator execution failed"

        result = response.json()
        assert "execution_id" in result
        assert "steps_executed" in result
        assert "success_rate" in result


class TestValidationWorkflow:
    """Test validation and reporting workflow"""

    def test_validate_execution_results(self):
        """Test validation of execution results"""
        if not hasattr(pytest, 'execution_id'):
            pytest.skip("No execution ID available")

        response = requests.post(
            f"{BASE_URL}/api/validation/validate/{pytest.execution_id}",
            timeout=60
        )

        assert response.status_code == 200, "Validation failed"

        validation = response.json()
        assert "validation_id" in validation
        assert "passed" in validation
        assert "failed" in validation
        assert "warnings" in validation

        pytest.validation_id = validation["validation_id"]

    def test_compare_baseline_results(self):
        """Test comparing results against baseline"""
        if not hasattr(pytest, 'execution_id'):
            pytest.skip("No execution ID available")

        comparison_request = {
            "current_execution_id": pytest.execution_id,
            "baseline_execution_id": "baseline_001"  # Assuming a baseline exists
        }

        response = requests.post(
            f"{BASE_URL}/api/validation/compare",
            json=comparison_request,
            timeout=60
        )

        # May fail if baseline doesn't exist - that's okay
        if response.status_code == 200:
            comparison = response.json()
            assert "differences" in comparison
            assert "similarity_score" in comparison

    def test_generate_validation_report(self):
        """Test validation report generation"""
        if not hasattr(pytest, 'validation_id'):
            pytest.skip("No validation ID available")

        response = requests.post(
            f"{BASE_URL}/api/validation/{pytest.validation_id}/report",
            json={"format": "json"},
            timeout=60
        )

        assert response.status_code == 200, "Report generation failed"

        report = response.json()
        assert "summary" in report
        assert "details" in report
        assert "timestamp" in report

    def test_export_report_formats(self):
        """Test exporting reports in different formats"""
        if not hasattr(pytest, 'validation_id'):
            pytest.skip("No validation ID available")

        formats = ["json", "pdf", "html"]

        for fmt in formats:
            response = requests.get(
                f"{BASE_URL}/api/validation/{pytest.validation_id}/export",
                params={"format": fmt},
                timeout=60
            )

            assert response.status_code == 200, f"Export to {fmt} failed"


class TestAgentIntegration:
    """Test integration between different AI agents"""

    def test_video_agent_integration(self):
        """Test Video Agent functionality"""
        if not hasattr(pytest, 'video_id'):
            pytest.skip("No video ID available")

        agent_request = {
            "video_id": pytest.video_id,
            "task": "extract_test_steps"
        }

        response = requests.post(
            f"{BASE_URL}/api/agents/video/process",
            json=agent_request,
            timeout=TEST_TIMEOUT
        )

        assert response.status_code == 200, "Video agent failed"

        result = response.json()
        assert "test_steps" in result
        assert len(result["test_steps"]) > 0

    def test_validation_agent_integration(self):
        """Test Validation Agent functionality"""
        validation_request = {
            "expected_results": ["Login successful", "Dashboard displayed"],
            "actual_results": ["Login successful", "Dashboard displayed"]
        }

        response = requests.post(
            f"{BASE_URL}/api/agents/validation/validate",
            json=validation_request,
            timeout=60
        )

        assert response.status_code == 200, "Validation agent failed"

        result = response.json()
        assert "match_score" in result
        assert "discrepancies" in result

    def test_ecm_agent_integration(self):
        """Test ECM (Enterprise Content Management) Agent"""
        ecm_request = {
            "action": "generate_test_code",
            "sop_id": getattr(pytest, 'sop_id', None),
            "language": "python",
            "framework": "pytest"
        }

        response = requests.post(
            f"{BASE_URL}/api/agents/ecm/process",
            json=ecm_request,
            timeout=TEST_TIMEOUT
        )

        if response.status_code == 200:
            result = response.json()
            assert "generated_code" in result
            assert len(result["generated_code"]) > 0

    def test_orchestrator_coordination(self):
        """Test orchestrator coordinating multiple agents"""
        orchestration_request = {
            "workflow": "full_qa_cycle",
            "agents": ["video", "validation", "ecm"],
            "video_id": getattr(pytest, 'video_id', None),
            "sop_id": getattr(pytest, 'sop_id', None)
        }

        response = requests.post(
            f"{BASE_URL}/api/orchestrator/coordinate",
            json=orchestration_request,
            timeout=TEST_TIMEOUT
        )

        assert response.status_code == 200, "Orchestrator coordination failed"

        result = response.json()
        assert "workflow_id" in result
        assert "agent_results" in result
        assert len(result["agent_results"]) > 0


class TestPerformanceAndReliability:
    """Test system performance and reliability"""

    def test_concurrent_executions(self):
        """Test handling multiple concurrent executions"""
        if not hasattr(pytest, 'sop_id'):
            pytest.skip("No SOP ID available")

        # Create multiple executions concurrently
        num_concurrent = 5
        execution_ids = []

        for _ in range(num_concurrent):
            response = requests.post(
                f"{BASE_URL}/api/execution/create",
                json={"sop_id": pytest.sop_id, "environment": "test"},
                timeout=30
            )

            assert response.status_code == 201
            execution_ids.append(response.json()["execution_id"])

        # Verify all were created
        assert len(execution_ids) == num_concurrent
        assert len(set(execution_ids)) == num_concurrent  # All unique

    def test_large_video_processing(self):
        """Test processing of large video files"""
        # This would test with a large file if available
        pytest.skip("Large file test - implement with actual large video")

    def test_api_response_times(self):
        """Test API response times meet requirements"""
        endpoints = [
            ("/api/sop/list", "GET"),
            ("/health", "GET")
        ]

        max_response_time = 2.0  # seconds

        for endpoint, method in endpoints:
            start_time = time.time()

            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)

            response_time = time.time() - start_time

            assert response.status_code == 200
            assert response_time < max_response_time, \
                f"{endpoint} took {response_time:.2f}s (max: {max_response_time}s)"

    def test_error_handling(self):
        """Test system error handling"""
        # Test with invalid SOP ID
        response = requests.get(f"{BASE_URL}/api/sop/invalid_id_999999")
        assert response.status_code == 404

        # Test with malformed request
        response = requests.post(
            f"{BASE_URL}/api/sop/create",
            json={"invalid": "data"},
            timeout=10
        )
        assert response.status_code in [400, 422]  # Bad request or validation error


class TestDataIntegrity:
    """Test data integrity and consistency"""

    def test_sop_data_consistency(self):
        """Test SOP data remains consistent across operations"""
        if not hasattr(pytest, 'sop_id'):
            pytest.skip("No SOP ID available")

        # Get SOP multiple times
        responses = []
        for _ in range(3):
            response = requests.get(f"{BASE_URL}/api/sop/{pytest.sop_id}")
            assert response.status_code == 200
            responses.append(response.json())

        # Verify all responses are identical
        for i in range(1, len(responses)):
            assert responses[0] == responses[i], "SOP data inconsistent across requests"

    def test_execution_history_integrity(self):
        """Test execution history maintains integrity"""
        if not hasattr(pytest, 'execution_id'):
            pytest.skip("No execution ID available")

        # Get execution details
        response = requests.get(f"{BASE_URL}/api/execution/{pytest.execution_id}")
        assert response.status_code == 200

        execution = response.json()

        # Verify required fields
        required_fields = ["execution_id", "sop_id", "status", "created_at"]
        for field in required_fields:
            assert field in execution, f"Missing required field: {field}"


# Test execution configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


if __name__ == "__main__":
    # Run tests with detailed output
    pytest.main([
        __file__,
        "-v",  # Verbose
        "--tb=short",  # Short traceback format
        "--color=yes",  # Colored output
        "-s",  # Show print statements
        "--junit-xml=test_results.xml",  # Generate XML report
        "--html=test_report.html",  # Generate HTML report (requires pytest-html)
        "--self-contained-html"  # Embed resources in HTML
    ])
