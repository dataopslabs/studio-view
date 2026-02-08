"""
SOP generation and retrieval API endpoints.
Handles SOP document generation, retrieval, and management.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from models.sop import (
    SOPDocument,
    SOPGenerationRequest,
    SOPResponse,
)
from services.video_analyzer import VideoAnalyzer
from services.system_detector import SystemDetector
from services.sop_generator import SOPGenerator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sops", tags=["SOPs"])

# Initialize services
video_analyzer = VideoAnalyzer()
system_detector = SystemDetector()
sop_generator = SOPGenerator()

# In-memory storage for demo - replace with database in production
sop_store = {}


class SOPListResponse(BaseModel):
    """Response with list of SOPs."""

    success: bool
    total: int
    sops: List[SOPDocument]


@router.post("/generate", response_model=SOPResponse)
async def generate_sop(request: SOPGenerationRequest) -> SOPResponse:
    """
    Generate an SOP from uploaded video analysis.

    Args:
        request: SOP generation request with video ID and options

    Returns:
        SOPResponse with generated SOP document

    Raises:
        HTTPException: If video or analysis not found
    """
    logger.info(f"Generating SOP from video: {request.video_id}")

    try:
        # Get video analysis
        video_analysis = video_analyzer._get_mock_analysis(request.video_id)

        if not video_analysis.get("success"):
            raise HTTPException(
                status_code=400,
                detail=f"Video analysis failed: {video_analysis.get('error')}",
            )

        # Detect systems
        systems_result = system_detector.detect_systems(
            video_analysis, request.video_id
        )
        detected_systems = [s.name for s in systems_result.detected_systems]

        # Generate SOP
        sop = sop_generator.generate_sop(
            request.video_id,
            video_analysis,
            detected_systems,
            request.detail_level,
        )

        if sop is None:
            raise HTTPException(status_code=500, detail="SOP generation failed")

        # Store SOP
        sop_store[sop.id] = sop

        logger.info(f"SOP generated successfully: {sop.id}")

        return SOPResponse(
            success=True,
            sop=sop,
            processing_time=video_analysis.get("processing_time", 0),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating SOP: {str(e)}")
        return SOPResponse(
            success=False,
            error=str(e),
            processing_time=0,
        )


@router.get("/{sop_id}", response_model=SOPDocument)
async def get_sop(sop_id: str) -> SOPDocument:
    """
    Retrieve a specific SOP by ID.

    Args:
        sop_id: ID of the SOP to retrieve

    Returns:
        SOPDocument

    Raises:
        HTTPException: If SOP not found
    """
    logger.info(f"Retrieving SOP: {sop_id}")

    if sop_id not in sop_store:
        raise HTTPException(status_code=404, detail=f"SOP not found: {sop_id}")

    return sop_store[sop_id]


@router.get("/", response_model=SOPListResponse)
async def list_sops(skip: int = 0, limit: int = 10) -> SOPListResponse:
    """
    List all SOPs with pagination.

    Args:
        skip: Number of SOPs to skip
        limit: Maximum number of SOPs to return

    Returns:
        SOPListResponse with paginated SOP list
    """
    logger.info(f"Listing SOPs (skip={skip}, limit={limit})")

    all_sops = list(sop_store.values())
    paginated_sops = all_sops[skip : skip + limit]

    return SOPListResponse(
        success=True,
        total=len(all_sops),
        sops=paginated_sops,
    )


@router.put("/{sop_id}", response_model=SOPDocument)
async def update_sop(sop_id: str, sop_update: SOPDocument) -> SOPDocument:
    """
    Update an existing SOP.

    Args:
        sop_id: ID of the SOP to update
        sop_update: Updated SOP data

    Returns:
        Updated SOPDocument

    Raises:
        HTTPException: If SOP not found
    """
    logger.info(f"Updating SOP: {sop_id}")

    if sop_id not in sop_store:
        raise HTTPException(status_code=404, detail=f"SOP not found: {sop_id}")

    # Update SOP
    sop_update.id = sop_id
    sop_store[sop_id] = sop_update

    logger.info(f"SOP updated: {sop_id}")

    return sop_update


@router.delete("/{sop_id}")
async def delete_sop(sop_id: str) -> dict:
    """
    Delete an SOP.

    Args:
        sop_id: ID of the SOP to delete

    Returns:
        Deletion status

    Raises:
        HTTPException: If SOP not found
    """
    logger.info(f"Deleting SOP: {sop_id}")

    if sop_id not in sop_store:
        raise HTTPException(status_code=404, detail=f"SOP not found: {sop_id}")

    del sop_store[sop_id]

    logger.info(f"SOP deleted: {sop_id}")

    return {
        "success": True,
        "sop_id": sop_id,
        "message": "SOP deleted successfully",
    }


@router.post("/{sop_id}/export")
async def export_sop(sop_id: str, format: str = "json") -> dict:
    """
    Export an SOP in different formats.

    Args:
        sop_id: ID of the SOP to export
        format: Export format (json, csv, markdown)

    Returns:
        Exported SOP data

    Raises:
        HTTPException: If SOP not found or format invalid
    """
    logger.info(f"Exporting SOP {sop_id} in format: {format}")

    if sop_id not in sop_store:
        raise HTTPException(status_code=404, detail=f"SOP not found: {sop_id}")

    sop = sop_store[sop_id]

    if format == "json":
        return {
            "format": "json",
            "data": sop.model_dump(),
        }

    elif format == "csv":
        # Convert to CSV format
        csv_data = "Step,Title,Description,System,Action Type,Expected Output\n"
        for step in sop.steps:
            csv_data += f"{step.step_number},{step.title},{step.description},{step.system_involved},{step.action_type},{step.expected_output}\n"

        return {
            "format": "csv",
            "data": csv_data,
        }

    elif format == "markdown":
        # Convert to Markdown format
        md_data = f"# {sop.title}\n\n"
        md_data += f"**Description:** {sop.description}\n\n"
        md_data += f"**Systems:** {', '.join(sop.systems_involved)}\n\n"
        md_data += f"**Estimated Duration:** {sop.execution_time_estimate} minutes\n\n"

        md_data += "## Steps\n\n"
        for step in sop.steps:
            md_data += f"### {step.step_number}. {step.title}\n"
            md_data += f"{step.description}\n"
            md_data += f"- **System:** {step.system_involved}\n"
            md_data += f"- **Action:** {step.action_type}\n"
            md_data += f"- **Expected Output:** {step.expected_output}\n\n"

        return {
            "format": "markdown",
            "data": md_data,
        }

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
