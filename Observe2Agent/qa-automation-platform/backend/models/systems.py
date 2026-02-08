"""
Pydantic models for detected enterprise systems and applications.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class SystemType(str, Enum):
    """Types of enterprise systems that can be detected."""

    ERP = "ERP"
    CRM = "CRM"
    HCM = "HCM"
    DOCUMENT_MANAGEMENT = "Document Management"
    WORKFLOW = "Workflow"
    REPORTING = "Reporting"
    EMAIL = "Email"
    COLLABORATION = "Collaboration"
    OTHER = "Other"


class DetectedSystem(BaseModel):
    """Information about a detected system or application."""

    name: str = Field(..., description="Name of the system")
    system_type: SystemType = Field(..., description="Type of system")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    url: Optional[str] = Field(None, description="URL or endpoint of the system")
    version: Optional[str] = Field(None, description="Detected version if available")
    ui_elements_detected: List[str] = Field(
        default_factory=list, description="UI elements identified"
    )
    authentication_type: Optional[str] = Field(
        None, description="Type of authentication (SSO, basic, etc.)"
    )
    timestamp: Optional[float] = Field(None, description="When detected in video (seconds)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "name": "SAP ERP",
                "system_type": "ERP",
                "confidence": 0.95,
                "url": "https://sap.company.com",
                "version": "S/4HANA 2021",
                "ui_elements_detected": ["Fiori interface", "Transaction codes"],
                "authentication_type": "SSO",
                "timestamp": 5.0,
            }
        }


class SystemsDetectionResult(BaseModel):
    """Result of system detection from video analysis."""

    video_id: str = Field(..., description="ID of the analyzed video")
    detected_systems: List[DetectedSystem] = Field(
        default_factory=list, description="List of detected systems"
    )
    total_systems_found: int = Field(default=0, description="Count of systems detected")
    analysis_confidence: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Overall confidence of analysis"
    )
    processing_time: float = Field(..., description="Time taken for detection in seconds")
    detected_workflows: Optional[List[str]] = Field(
        default=None, description="Detected workflow patterns"
    )
    data_patterns: Optional[Dict[str, Any]] = Field(
        None, description="Detected data handling patterns"
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "video_id": "video-12345",
                "detected_systems": [
                    {
                        "name": "SAP ERP",
                        "system_type": "ERP",
                        "confidence": 0.95,
                    }
                ],
                "total_systems_found": 1,
                "analysis_confidence": 0.92,
                "processing_time": 45.5,
            }
        }


class SystemIntegrationConfig(BaseModel):
    """Configuration for integrating with a detected system."""

    system_name: str = Field(..., description="Name of the system")
    api_endpoint: Optional[str] = Field(None, description="API endpoint URL")
    authentication_config: Optional[Dict[str, Any]] = Field(
        None, description="Authentication details"
    )
    request_format: Optional[str] = Field(
        default="json", description="Expected request format"
    )
    response_format: Optional[str] = Field(
        default="json", description="Response format"
    )
    timeout: int = Field(default=30, description="Request timeout in seconds")
    retry_count: int = Field(default=3, description="Number of retries")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional config")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "system_name": "SAP ERP",
                "api_endpoint": "https://sap.api.company.com",
                "authentication_config": {"type": "oauth2"},
            }
        }
