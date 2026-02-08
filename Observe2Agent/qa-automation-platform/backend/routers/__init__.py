"""
API routers package for the QA Automation Platform.
Contains all API endpoint definitions.
"""

from .video import router as video_router
from .sop import router as sop_router
from .execution import router as execution_router
from .validation import router as validation_router

__all__ = [
    "video_router",
    "sop_router",
    "execution_router",
    "validation_router",
]
