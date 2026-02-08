"""
Validation dashboard and testing API endpoints.
Handles validation execution, reporting, and result retrieval.
"""

import logging
from typing import Dict, Optional, List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from models.validation import (
    ValidationRequest,
    ValidationResponse,
    ValidationReport,
    ValidationStatus,
)
from models.sop import SOPDocument
from services.validation_engine import ValidationEngine
from services.execution_engine import ExecutionEngine
from routers.sop import sop_store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/validation", tags=["validation"])

# Initialize services
validation_engine = ValidationEngine()
execution_engine = ExecutionEngine()

# In-memory storage for validation reports
validation_store = {}


class ValidationDashboardResponse(BaseModel):
    """Response with validation dashboard data."""

    total_validations: int
    passed: int
    failed: int
    partial: int
    success_rate: float
    recent_validations: List[ValidationReport]


class ValidationSummaryResponse(BaseModel):
    """Summary of validation results."""

    validation_id: str
    sop_id: str
    status: ValidationStatus
    success_rate: float
    total_steps: int
    passed_steps: int
    failed_steps: int


@router.post("/validate", response_model=ValidationResponse)
async def validate_sop(
    request: ValidationRequest, background_tasks: BackgroundTasks
) -> ValidationResponse:
    """
    Run validation for an SOP execution.

    Args:
        request: Validation request with SOP ID and options
        background_tasks: Background task scheduler

    Returns:
        ValidationResponse with validation status

    Raises:
        HTTPException: If SOP not found
    """
    logger.info(f"Starting validation for SOP: {request.sop_id}")

    try:
        # Get SOP
        if request.sop_id not in sop_store:
            raise HTTPException(status_code=404, detail=f"SOP not found: {request.sop_id}")

        sop = sop_store[request.sop_id]

        # Generate validation ID
        import uuid

        validation_id = f"val-{uuid.uuid4().hex[:8]}"

        # Schedule background validation
        background_tasks.add_task(
            _validate_in_background,
            validation_id,
            sop,
            request,
        )

        logger.info(f"Validation scheduled: {validation_id}")

        return ValidationResponse(
            success=True,
            validation_id=validation_id,
            status=ValidationStatus.RUNNING,
            success_rate=0.0,
            processing_time=0.0,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scheduling validation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.get("/{validation_id}", response_model=ValidationReport)
async def get_validation_result(validation_id: str) -> ValidationReport:
    """
    Get validation results.

    Args:
        validation_id: ID of the validation

    Returns:
        ValidationReport with detailed results

    Raises:
        HTTPException: If validation not found
    """
    logger.info(f"Retrieving validation: {validation_id}")

    if validation_id not in validation_store:
        raise HTTPException(status_code=404, detail=f"Validation not found: {validation_id}")

    return validation_store[validation_id]


@router.get("/{validation_id}/summary", response_model=ValidationSummaryResponse)
async def get_validation_summary(validation_id: str) -> ValidationSummaryResponse:
    """
    Get validation summary.

    Args:
        validation_id: ID of the validation

    Returns:
        ValidationSummaryResponse with key metrics

    Raises:
        HTTPException: If validation not found
    """
    logger.info(f"Retrieving validation summary: {validation_id}")

    if validation_id not in validation_store:
        raise HTTPException(status_code=404, detail=f"Validation not found: {validation_id}")

    report = validation_store[validation_id]

    return ValidationSummaryResponse(
        validation_id=validation_id,
        sop_id=report.sop_id,
        status=report.overall_status,
        success_rate=report.success_rate,
        total_steps=report.total_steps,
        passed_steps=report.passed_steps,
        failed_steps=report.failed_steps,
    )


@router.get("/sop/{sop_id}/validations")
async def get_sop_validations(sop_id: str) -> dict:
    """
    Get all validations for a specific SOP.

    Args:
        sop_id: ID of the SOP

    Returns:
        List of validation reports for the SOP

    Raises:
        HTTPException: If SOP not found
    """
    logger.info(f"Retrieving validations for SOP: {sop_id}")

    if sop_id not in sop_store:
        raise HTTPException(status_code=404, detail=f"SOP not found: {sop_id}")

    # Filter validations for this SOP
    sop_validations = [
        v for v in validation_store.values() if v.sop_id == sop_id
    ]

    return {
        "sop_id": sop_id,
        "total_validations": len(sop_validations),
        "validations": sop_validations,
    }


@router.get("/dashboard")
async def get_validation_dashboard() -> ValidationDashboardResponse:
    """
    Get validation dashboard with overall statistics.

    Returns:
        ValidationDashboardResponse with dashboard data
    """
    logger.info("Retrieving validation dashboard")

    all_validations = list(validation_store.values())

    passed = sum(
        1
        for v in all_validations
        if v.overall_status == ValidationStatus.PASSED
    )
    failed = sum(
        1
        for v in all_validations
        if v.overall_status == ValidationStatus.FAILED
    )
    partial = sum(
        1
        for v in all_validations
        if v.overall_status == ValidationStatus.PARTIAL
    )

    total = len(all_validations)
    success_rate = (passed / total) if total > 0 else 0.0

    # Get recent validations
    recent = sorted(
        all_validations,
        key=lambda v: v.end_time or v.start_time,
        reverse=True,
    )[:5]

    return ValidationDashboardResponse(
        total_validations=total,
        passed=passed,
        failed=failed,
        partial=partial,
        success_rate=round(success_rate, 4),
        recent_validations=recent,
    )


@router.post("/{validation_id}/re-run")
async def rerun_validation(
    validation_id: str, background_tasks: BackgroundTasks
) -> ValidationResponse:
    """
    Re-run a validation.

    Args:
        validation_id: ID of the validation to re-run
        background_tasks: Background task scheduler

    Returns:
        ValidationResponse with new validation ID

    Raises:
        HTTPException: If validation not found
    """
    logger.info(f"Re-running validation: {validation_id}")

    if validation_id not in validation_store:
        raise HTTPException(status_code=404, detail=f"Validation not found: {validation_id}")

    original_validation = validation_store[validation_id]
    sop_id = original_validation.sop_id

    if sop_id not in sop_store:
        raise HTTPException(status_code=404, detail=f"SOP not found: {sop_id}")

    # Generate new validation ID
    import uuid

    new_validation_id = f"val-{uuid.uuid4().hex[:8]}"

    sop = sop_store[sop_id]

    # Create validation request from original
    request = ValidationRequest(
        sop_id=sop_id,
        environment=original_validation.environment or "test",
        headless=True,
    )

    # Schedule new validation
    background_tasks.add_task(
        _validate_in_background,
        new_validation_id,
        sop,
        request,
    )

    logger.info(f"Validation re-run scheduled: {new_validation_id}")

    return ValidationResponse(
        success=True,
        validation_id=new_validation_id,
        status=ValidationStatus.RUNNING,
        success_rate=0.0,
        processing_time=0.0,
    )


@router.post("/{validation_id}/export")
async def export_validation(validation_id: str, format: str = "json") -> dict:
    """
    Export validation results.

    Args:
        validation_id: ID of the validation
        format: Export format (json, csv, html)

    Returns:
        Exported validation data

    Raises:
        HTTPException: If validation not found
    """
    logger.info(f"Exporting validation {validation_id} in format: {format}")

    if validation_id not in validation_store:
        raise HTTPException(status_code=404, detail=f"Validation not found: {validation_id}")

    report = validation_store[validation_id]

    if format == "json":
        return {
            "format": "json",
            "data": report.model_dump(),
        }

    elif format == "csv":
        # Convert to CSV
        csv_data = "Step,Status,Expected,Actual,Match Score,Duration\n"
        for step in report.validation_steps:
            csv_data += f"{step.step_number},{step.status},{step.expected},{step.actual},{step.match_score},{step.duration}\n"

        return {
            "format": "csv",
            "data": csv_data,
        }

    elif format == "html":
        # Generate HTML report
        html_data = f"""
        <html>
            <head>
                <title>Validation Report: {report.id}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .header {{ background-color: #f0f0f0; padding: 20px; }}
                    .status-passed {{ color: green; }}
                    .status-failed {{ color: red; }}
                    table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f0f0f0; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Validation Report</h1>
                    <p>Validation ID: {report.id}</p>
                    <p>SOP ID: {report.sop_id}</p>
                    <p>Status: <span class="status-{report.overall_status.value}">{report.overall_status.value.upper()}</span></p>
                    <p>Success Rate: {report.success_rate * 100:.1f}%</p>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Step</th>
                            <th>Title</th>
                            <th>Status</th>
                            <th>Expected</th>
                            <th>Match Score</th>
                        </tr>
                    </thead>
                    <tbody>
        """

        for step in report.validation_steps:
            html_data += f"""
                        <tr>
                            <td>{step.step_number}</td>
                            <td>{step.title}</td>
                            <td class="status-{step.status.value}">{step.status.value}</td>
                            <td>{step.expected}</td>
                            <td>{step.match_score}</td>
                        </tr>
            """

        html_data += """
                    </tbody>
                </table>
            </body>
        </html>
        """

        return {
            "format": "html",
            "data": html_data,
        }

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")


async def _validate_in_background(
    validation_id: str,
    sop: SOPDocument,
    request: ValidationRequest,
):
    """
    Background task to run validation.

    Args:
        validation_id: ID of the validation
        sop: SOP to validate
        request: Validation request details
    """
    logger.info(f"Starting background validation: {validation_id}")

    try:
        # Mock execution result for validation
        execution_result = {
            "execution_id": f"exec-{validation_id[-8:]}",
            "success": True,
            "total_steps": len(sop.steps),
            "passed_steps": len(sop.steps),
            "failed_steps": 0,
            "steps_details": [
                {
                    "step": i + 1,
                    "status": "passed",
                    "details": {"output": "Step executed successfully", "duration": 10},
                }
                for i in range(len(sop.steps))
            ],
            "duration": sum(step.duration or 10 for step in sop.steps),
            "environment": request.environment,
        }

        # Run validation
        report = validation_engine.validate_execution(sop, execution_result, None)

        # Store result
        validation_store[validation_id] = report

        logger.info(f"Background validation completed: {validation_id}")

    except Exception as e:
        logger.error(f"Background validation failed: {validation_id}: {str(e)}")
        # Store error result
        from models.validation import ValidationReport, ValidationStatus

        error_report = ValidationReport(
            id=validation_id,
            sop_id=sop.id,
            execution_id="unknown",
            overall_status=ValidationStatus.ERROR,
            total_steps=0,
            error_summary=str(e),
        )
        validation_store[validation_id] = error_report
