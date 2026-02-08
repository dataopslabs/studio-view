"""
Pydantic models for validation results and test execution reports.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class ValidationStatus(str, Enum):
    """Status of validation execution."""

    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    PARTIAL = "partial"
    ERROR = "error"


class ValidationStep(BaseModel):
    """Result of a single validation step."""

    step_number: int = Field(..., description="Step number from SOP")
    title: str = Field(..., description="Step title")
    status: ValidationStatus = Field(..., description="Status of this step")
    expected: str = Field(..., description="Expected result")
    actual: Optional[str] = Field(None, description="Actual result obtained")
    match_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="How well actual matches expected"
    )
    error_message: Optional[str] = Field(None, description="Error message if validation failed")
    screenshot: Optional[str] = Field(None, description="Screenshot URL of validation result")
    duration: float = Field(default=0.0, description="Time taken for this step in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "step_number": 1,
                "title": "Login to SAP",
                "status": "passed",
                "expected": "User logged in successfully",
                "actual": "User logged in successfully",
                "match_score": 1.0,
                "duration": 15.5,
            }
        }


class ValidationReport(BaseModel):
    """Complete validation report for an SOP execution."""

    id: Optional[str] = Field(None, description="Unique validation ID")
    sop_id: str = Field(..., description="ID of the SOP being validated")
    execution_id: str = Field(..., description="ID of the execution")
    overall_status: ValidationStatus = Field(..., description="Overall validation status")
    total_steps: int = Field(..., description="Total number of steps validated")
    passed_steps: int = Field(default=0, description="Number of passed steps")
    failed_steps: int = Field(default=0, description="Number of failed steps")
    skipped_steps: int = Field(default=0, description="Number of skipped steps")
    success_rate: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Percentage of successful steps"
    )
    validation_steps: List[ValidationStep] = Field(
        default_factory=list, description="Results for each step"
    )
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    total_duration: float = Field(default=0.0, description="Total execution time in seconds")
    environment: Optional[str] = Field(None, description="Environment where validation ran")
    browser: Optional[str] = Field(None, description="Browser used for automation")
    os: Optional[str] = Field(None, description="Operating system")
    execution_logs: Optional[str] = Field(None, description="Detailed execution logs")
    screenshots: List[str] = Field(default_factory=list, description="Screenshot URLs")
    error_summary: Optional[str] = Field(None, description="Summary of errors found")
    recommendations: Optional[List[str]] = Field(None, description="Recommendations for fixing issues")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "sop_id": "sop-12345",
                "execution_id": "exec-12345",
                "overall_status": "passed",
                "total_steps": 5,
                "passed_steps": 5,
                "success_rate": 1.0,
            }
        }


class ValidationRequest(BaseModel):
    """Request to validate an SOP."""

    sop_id: str = Field(..., description="ID of the SOP to validate")
    environment: Optional[str] = Field(default="test", description="Environment to run against")
    headless: bool = Field(default=True, description="Run browser in headless mode")
    timeout: int = Field(default=300, description="Validation timeout in seconds")
    retry_failed: bool = Field(default=True, description="Retry failed steps")
    max_retries: int = Field(default=2, description="Maximum retries per step")
    capture_screenshots: bool = Field(default=True, description="Capture screenshots")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "sop_id": "sop-12345",
                "environment": "test",
                "headless": True,
                "timeout": 300,
            }
        }


class ValidationResponse(BaseModel):
    """Response from validation execution."""

    success: bool = Field(..., description="Whether validation was successful")
    validation_id: str = Field(..., description="ID of the validation report")
    status: ValidationStatus = Field(..., description="Validation status")
    success_rate: float = Field(..., ge=0.0, le=1.0, description="Success rate 0-1")
    report: Optional[ValidationReport] = None
    error: Optional[str] = None
    processing_time: float = Field(..., description="Time taken in seconds")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "success": True,
                "validation_id": "val-12345",
                "status": "passed",
                "success_rate": 1.0,
                "processing_time": 120.5,
            }
        }


class DataValidationResult(BaseModel):
    """Result of data extraction and validation."""

    field_name: str = Field(..., description="Name of the field validated")
    expected_value: Any = Field(..., description="Expected value")
    actual_value: Optional[Any] = Field(None, description="Actual value extracted")
    data_type: str = Field(..., description="Data type (string, number, date, etc.)")
    is_valid: bool = Field(..., description="Whether data is valid")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in extraction")
    error_message: Optional[str] = Field(None, description="Error if invalid")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "field_name": "PO_Number",
                "expected_value": "PO-12345",
                "actual_value": "PO-12345",
                "data_type": "string",
                "is_valid": True,
                "confidence": 0.99,
            }
        }
