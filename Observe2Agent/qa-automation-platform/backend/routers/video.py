"""
Video upload and processing API endpoints.
Handles video file uploads and initial processing.
"""

import logging
import aiofiles
from typing import Optional
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel

from config import settings
from services.video_analyzer import VideoAnalyzer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/videos", tags=["videos"])

# Initialize services
video_analyzer = VideoAnalyzer()


class VideoUploadResponse(BaseModel):
    """Response for video upload."""

    success: bool
    video_id: str
    filename: str
    size: int
    message: Optional[str] = None


class VideoStatusResponse(BaseModel):
    """Response for video processing status."""

    video_id: str
    status: str
    processing_progress: float
    analysis_results: Optional[dict] = None
    error: Optional[str] = None


@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(
    file: UploadFile = File(...), background_tasks: BackgroundTasks = None
) -> VideoUploadResponse:
    """
    Upload a business process video for analysis.

    Args:
        file: Video file to upload
        background_tasks: Background task scheduler

    Returns:
        VideoUploadResponse with upload status and video ID

    Raises:
        HTTPException: If file validation fails
    """
    logger.info(f"Received video upload: {file.filename}")

    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")

        # Check file extension
        file_ext = file.filename.split(".")[-1].lower()
        if file_ext not in settings.ALLOWED_VIDEO_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type .{file_ext} not allowed. Allowed: {settings.ALLOWED_VIDEO_EXTENSIONS}",
            )

        # Create upload directory if it doesn't exist
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Generate video ID
        import uuid

        video_id = f"video-{uuid.uuid4().hex[:8]}"

        # Save file
        video_path = upload_dir / f"{video_id}_{file.filename}"

        # Check file size
        content = await file.read()
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum of {settings.MAX_UPLOAD_SIZE / 1024 / 1024:.0f}MB",
            )

        # Write file
        async with aiofiles.open(video_path, "wb") as f:
            await f.write(content)

        logger.info(f"Video saved: {video_path} (ID: {video_id})")

        # Schedule background analysis
        if background_tasks:
            background_tasks.add_task(
                _analyze_video_background, video_id, str(video_path)
            )

        return VideoUploadResponse(
            success=True,
            video_id=video_id,
            filename=file.filename,
            size=len(content),
            message="Video uploaded successfully. Analysis will begin shortly.",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/{video_id}/status", response_model=VideoStatusResponse)
async def get_video_status(video_id: str) -> VideoStatusResponse:
    """
    Get processing status of an uploaded video.

    Args:
        video_id: ID of the video

    Returns:
        VideoStatusResponse with current processing status

    Raises:
        HTTPException: If video not found
    """
    logger.info(f"Checking status for video: {video_id}")

    try:
        # Check if video exists
        upload_dir = Path(settings.UPLOAD_DIR)
        video_files = list(upload_dir.glob(f"{video_id}_*"))

        if not video_files:
            raise HTTPException(status_code=404, detail="Video not found")

        # Mock status response - in production would check actual analysis status
        return VideoStatusResponse(
            video_id=video_id,
            status="completed",
            processing_progress=1.0,
            analysis_results={
                "workflow_steps": 5,
                "systems_detected": 2,
                "confidence": 0.92,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting video status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@router.get("/{video_id}/analysis")
async def get_video_analysis(video_id: str) -> dict:
    """
    Get detailed analysis results for a video.

    Args:
        video_id: ID of the video

    Returns:
        Detailed analysis results

    Raises:
        HTTPException: If video or analysis not found
    """
    logger.info(f"Fetching analysis for video: {video_id}")

    try:
        # Check if video exists
        upload_dir = Path(settings.UPLOAD_DIR)
        video_files = list(upload_dir.glob(f"{video_id}_*"))

        if not video_files:
            raise HTTPException(status_code=404, detail="Video not found")

        # Get analysis - in production would retrieve from database/cache
        video_path = str(video_files[0])
        analysis = video_analyzer.analyze_video(video_path)

        return {
            "video_id": video_id,
            "analysis": analysis,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis retrieval failed: {str(e)}")


@router.delete("/{video_id}")
async def delete_video(video_id: str) -> dict:
    """
    Delete an uploaded video and associated data.

    Args:
        video_id: ID of the video to delete

    Returns:
        Deletion status

    Raises:
        HTTPException: If video not found or deletion fails
    """
    logger.info(f"Deleting video: {video_id}")

    try:
        # Find and delete video file
        upload_dir = Path(settings.UPLOAD_DIR)
        video_files = list(upload_dir.glob(f"{video_id}_*"))

        if not video_files:
            raise HTTPException(status_code=404, detail="Video not found")

        for video_file in video_files:
            video_file.unlink()

        logger.info(f"Video deleted: {video_id}")

        return {
            "success": True,
            "video_id": video_id,
            "message": "Video deleted successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")


async def _analyze_video_background(video_id: str, video_path: str):
    """
    Background task to analyze video.

    Args:
        video_id: ID of the video
        video_path: Path to the video file
    """
    logger.info(f"Starting background analysis for video: {video_id}")

    try:
        # Perform analysis
        analysis = video_analyzer.analyze_video(video_path)

        # Store results - in production would save to database
        logger.info(f"Background analysis completed for video: {video_id}")
        logger.debug(f"Analysis results: {analysis}")

    except Exception as e:
        logger.error(f"Background analysis failed for {video_id}: {str(e)}")
