"""
RenderingVideo Python SDK
Official Python SDK for the RenderingVideo API

Usage:
    from renderingvideo import Client

    client = Client(api_key="sk-xxx")

    # Video operations
    task = client.video.create(config={...})
    client.video.render(task_id=task.task_id)

    # File operations
    upload = client.files.upload(file="/path/to/image.png")

    # Preview operations
    preview = client.preview.create({...})

    # Credits
    credits = client.get_credits()
"""

from .client import Client
from .video import VideoClient
from .files import FilesClient
from .preview import PreviewClient
from .types import (
    VideoConfig,
    Task,
    TaskList,
    Credits,
    Asset,
    FileList,
    UploadResult,
    Preview,
    DeleteResult,
    RenderingVideoError,
    AuthenticationError,
    InsufficientCreditsError,
    ValidationError,
    NotFoundError,
    RateLimitError,
    AlreadyRenderingError,
    RemoteError,
)

__version__ = "1.0.0.2"
__all__ = [
    # Main client
    "Client",
    # Sub-clients
    "VideoClient",
    "FilesClient",
    "PreviewClient",
    # Types
    "VideoConfig",
    "Task",
    "TaskList",
    "Credits",
    "Asset",
    "FileList",
    "UploadResult",
    "Preview",
    "DeleteResult",
    # Exceptions
    "RenderingVideoError",
    "AuthenticationError",
    "InsufficientCreditsError",
    "ValidationError",
    "NotFoundError",
    "RateLimitError",
    "AlreadyRenderingError",
    "RemoteError",
]
