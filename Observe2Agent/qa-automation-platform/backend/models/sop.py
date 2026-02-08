"""
Pydantic models for Standard Operating Procedures (SOPs).
Defines the structure of SOP steps and complete SOP documents.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class SOPStep(BaseModel):
    """A single step in a Standard Operating Procedure."""

    step_number: int = Field(..., description="Sequence number of the step")
    title: str = Field(..., description="Title of the step")
    description: str = Field(..., description="Detailed description of what to do")
    system_involved: str = Field(..., description="System or application involved in this step")
    action_type: str = Field(
        ..., description="Type of action (click, input, navigate, wait, etc.)"
    )
    element_identifier: Optional[str] = Field(
        None, description="XPath, ID, or element selector"
    )
    expected_output: Optional[str] = Field(None, description="Expected result of the step")
    screenshot_reference: Optional[str] = Field(None, description="Reference to screenshot URL")
    timestamp: Optional[float] = Field(None, description="Timestamp in video where this step occurs")
    duration: Optional[float] = Field(None, description="Duration of this step in seconds")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "step_number": 1,
                "title": "Login to SAP",
                "description": "Open SAP application and enter credentials",
                "system_involved": "SAP",
                "action_type": "click",
                "element_identifier": "//input[@id='username']",
                "expected_output": "User logged in successfully",
                "timestamp": 0.0,
                "duration": 15.5,
            }
        }


class SOPDocument(BaseModel):
    """A complete Standard Operating Procedure document."""

    id: Optional[str] = Field(None, description="Unique identifier for the SOP")
    title: str = Field(..., description="Title of the SOP")
    description: str = Field(..., description="Overall description of the process")
    version: str = Field(default="1.0", description="Version number of the SOP")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    video_source_id: str = Field(..., description="ID of the source video")
    systems_involved: List[str] = Field(default_factory=list, description="List of systems used")
    steps: List[SOPStep] = Field(..., description="Ordered list of SOP steps")
    execution_time_estimate: Optional[float] = Field(
        None, description="Estimated execution time in minutes"
    )
    success_criteria: Optional[str] = Field(None, description="Definition of successful completion")
    preconditions: Optional[str] = Field(None, description="Prerequisites before execution")
    postconditions: Optional[str] = Field(None, description="State after execution")
    error_handling: Optional[str] = Field(None, description="How to handle errors")
    notes: Optional[str] = Field(None, description="Additional notes and observations")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "title": "Create Purchase Order in SAP",
                "description": "Process for creating and submitting a purchase order",
                "version": "1.0",
                "video_source_id": "video-12345",
                "systems_involved": ["SAP", "Email"],
                "steps": [
                    {
                        "step_number": 1,
                        "title": "Login",
                        "description": "Open SAP",
                        "system_involved": "SAP",
                        "action_type": "click",
                    }
                ],
                "execution_time_estimate": 10.5,
            }
        }


class SOPGenerationRequest(BaseModel):
    """Request to generate an SOP from video analysis."""

    video_id: str = Field(..., description="ID of the uploaded video")
    include_screenshots: bool = Field(default=True, description="Include screenshots in SOP")
    detail_level: str = Field(
        default="detailed",
        description="Level of detail: summary, detailed, expert",
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "video_id": "video-12345",
                "include_screenshots": True,
                "detail_level": "detailed",
            }
        }


class SOPResponse(BaseModel):
    """Response containing generated SOP."""

    success: bool
    sop: Optional[SOPDocument] = None
    error: Optional[str] = None
    processing_time: float = Field(..., description="Time taken to generate SOP in seconds")
