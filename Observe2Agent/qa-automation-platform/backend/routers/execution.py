"""
Automation execution API endpoints.
Handles code generation, execution, and execution monitoring.
"""

import logging
import asyncio
from typing import Dict, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from models.sop import SOPDocument
from services.code_generator import CodeGenerator
from services.execution_engine import ExecutionEngine
from routers.sop import sop_store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/executions", tags=["executions"])

# Initialize services
code_generator = CodeGenerator()
execution_engine = ExecutionEngine()

# In-memory storage for execution results
execution_store = {}


class ExecutionRequest(BaseModel):
    """Request to execute an SOP."""

    sop_id: str
    framework: str = "adk"  # adk, selenium, playwright
    timeout: int = 300
    headless: bool = True
    environment: str = "test"
    metadata: Optional[Dict] = None


class ExecutionResponse(BaseModel):
    """Response from execution request."""

    success: bool
    execution_id: str
    sop_id: str
    status: str
    message: Optional[str] = None


class ExecutionStatusResponse(BaseModel):
    """Response with execution status details."""

    execution_id: str
    sop_id: str
    status: str
    progress: float
    results: Optional[Dict] = None
    error: Optional[str] = None


@router.post("/run", response_model=ExecutionResponse)
async def run_execution(
    request: ExecutionRequest, background_tasks: BackgroundTasks
) -> ExecutionResponse:
    """
    Execute an SOP automation.

    Args:
        request: Execution request with SOP ID and options
        background_tasks: Background task scheduler

    Returns:
        ExecutionResponse with execution ID and initial status

    Raises:
        HTTPException: If SOP not found
    """
    logger.info(f"Executing SOP: {request.sop_id} with framework: {request.framework}")

    try:
        # Get SOP
        if request.sop_id not in sop_store:
            raise HTTPException(status_code=404, detail=f"SOP not found: {request.sop_id}")

        sop = sop_store[request.sop_id]

        # Generate code
        logger.info(f"Generating {request.framework} code")
        agent_code = code_generator.generate_adk_code(sop, request.framework)

        # Generate execution ID
        import uuid

        execution_id = f"exec-{uuid.uuid4().hex[:8]}"

        # Store execution info
        execution_store[execution_id] = {
            "sop_id": request.sop_id,
            "status": "pending",
            "progress": 0,
            "framework": request.framework,
        }

        # Schedule background execution
        background_tasks.add_task(
            _execute_in_background,
            execution_id,
            sop,
            agent_code,
            request.framework,
            request.timeout,
            request.headless,
        )

        logger.info(f"Execution scheduled: {execution_id}")

        return ExecutionResponse(
            success=True,
            execution_id=execution_id,
            sop_id=request.sop_id,
            status="pending",
            message="Execution scheduled and will begin shortly",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scheduling execution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


@router.get("/{execution_id}", response_model=ExecutionStatusResponse)
async def get_execution_status(execution_id: str) -> ExecutionStatusResponse:
    """
    Get the status of an execution.

    Args:
        execution_id: ID of the execution

    Returns:
        ExecutionStatusResponse with current status

    Raises:
        HTTPException: If execution not found
    """
    logger.info(f"Getting execution status: {execution_id}")

    if execution_id not in execution_store:
        raise HTTPException(status_code=404, detail=f"Execution not found: {execution_id}")

    exec_data = execution_store[execution_id]

    return ExecutionStatusResponse(
        execution_id=execution_id,
        sop_id=exec_data.get("sop_id"),
        status=exec_data.get("status", "unknown"),
        progress=exec_data.get("progress", 0),
        results=exec_data.get("results"),
        error=exec_data.get("error"),
    )


@router.get("/{execution_id}/logs")
async def get_execution_logs(execution_id: str) -> dict:
    """
    Get execution logs.

    Args:
        execution_id: ID of the execution

    Returns:
        Logs as string

    Raises:
        HTTPException: If execution not found
    """
    logger.info(f"Getting execution logs: {execution_id}")

    if execution_id not in execution_store:
        raise HTTPException(status_code=404, detail=f"Execution not found: {execution_id}")

    logs = execution_engine.get_execution_logs(execution_id)

    return {
        "execution_id": execution_id,
        "logs": logs,
    }


@router.post("/{execution_id}/cancel")
async def cancel_execution(execution_id: str) -> dict:
    """
    Cancel a running execution.

    Args:
        execution_id: ID of the execution to cancel

    Returns:
        Cancellation status

    Raises:
        HTTPException: If execution not found
    """
    logger.info(f"Cancelling execution: {execution_id}")

    if execution_id not in execution_store:
        raise HTTPException(status_code=404, detail=f"Execution not found: {execution_id}")

    exec_data = execution_store[execution_id]

    if exec_data["status"] in ["completed", "failed", "cancelled"]:
        raise HTTPException(
            status_code=400, detail=f"Cannot cancel execution with status: {exec_data['status']}"
        )

    # Mark as cancelled
    exec_data["status"] = "cancelled"
    exec_data["error"] = "Execution cancelled by user"

    logger.info(f"Execution cancelled: {execution_id}")

    return {
        "success": True,
        "execution_id": execution_id,
        "status": "cancelled",
    }


@router.post("/{execution_id}/retry")
async def retry_execution(
    execution_id: str, background_tasks: BackgroundTasks
) -> ExecutionResponse:
    """
    Retry a failed execution.

    Args:
        execution_id: ID of the execution to retry
        background_tasks: Background task scheduler

    Returns:
        ExecutionResponse with new execution ID

    Raises:
        HTTPException: If execution not found
    """
    logger.info(f"Retrying execution: {execution_id}")

    if execution_id not in execution_store:
        raise HTTPException(status_code=404, detail=f"Execution not found: {execution_id}")

    original_exec = execution_store[execution_id]
    sop_id = original_exec.get("sop_id")

    if sop_id not in sop_store:
        raise HTTPException(status_code=404, detail=f"SOP not found: {sop_id}")

    # Create new execution ID
    import uuid

    new_execution_id = f"exec-{uuid.uuid4().hex[:8]}"

    sop = sop_store[sop_id]
    agent_code = code_generator.generate_adk_code(sop, original_exec.get("framework", "adk"))

    execution_store[new_execution_id] = {
        "sop_id": sop_id,
        "status": "pending",
        "progress": 0,
        "framework": original_exec.get("framework", "adk"),
        "retry_of": execution_id,
    }

    # Schedule execution
    background_tasks.add_task(
        _execute_in_background,
        new_execution_id,
        sop,
        agent_code,
        original_exec.get("framework", "adk"),
        300,
        True,
    )

    return ExecutionResponse(
        success=True,
        execution_id=new_execution_id,
        sop_id=sop_id,
        status="pending",
        message="Execution retry scheduled",
    )


async def _execute_in_background(
    execution_id: str,
    sop: SOPDocument,
    agent_code: Dict[str, str],
    framework: str,
    timeout: int,
    headless: bool,
):
    """
    Background task to execute automation.

    Args:
        execution_id: ID of the execution
        sop: SOP document to execute
        agent_code: Generated code
        framework: Framework to use
        timeout: Execution timeout
        headless: Headless mode flag
    """
    logger.info(f"Starting background execution: {execution_id}")

    try:
        # Update status
        execution_store[execution_id]["status"] = "running"
        execution_store[execution_id]["progress"] = 0.1

        # Execute based on framework
        if framework == "adk":
            result = await execution_engine.execute_adk_agent(
                agent_code, sop.id, timeout, headless
            )
        elif framework == "selenium":
            selenium_code = agent_code.get(f"{sop.id}_selenium.py", "")
            result = await execution_engine.execute_selenium_script(
                selenium_code, sop.id, timeout
            )
        elif framework == "playwright":
            playwright_code = agent_code.get(f"{sop.id}_playwright.py", "")
            result = await execution_engine.execute_playwright_script(
                playwright_code, sop.id, timeout
            )
        else:
            raise ValueError(f"Unknown framework: {framework}")

        # Update execution store
        execution_store[execution_id]["status"] = (
            "completed" if result.get("success") else "failed"
        )
        execution_store[execution_id]["progress"] = 1.0
        execution_store[execution_id]["results"] = result

        logger.info(f"Background execution completed: {execution_id}")

    except Exception as e:
        logger.error(f"Background execution failed: {execution_id}: {str(e)}")
        execution_store[execution_id]["status"] = "failed"
        execution_store[execution_id]["error"] = str(e)
