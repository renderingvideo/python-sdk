"""
Type definitions for the RenderingVideo SDK
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class VideoConfig:
    """Video configuration schema"""
    meta: Dict[str, Any] = field(default_factory=lambda: {"version": "2.0.0"})
    tracks: List[Dict[str, Any]] = field(default_factory=list)
    assets: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "meta": self.meta,
            "tracks": self.tracks,
        }
        if self.assets:
            result["assets"] = self.assets
        return result


@dataclass
class Task:
    """Video render task"""
    task_id: str
    video_task_id: Optional[str] = None
    render_task_id: Optional[str] = None
    preview_url: Optional[str] = None
    viewer_url: Optional[str] = None
    config_url: Optional[str] = None
    video_url: Optional[str] = None
    status: str = "created"
    quality: Optional[str] = None
    cost: int = 0
    cost_credits: Optional[int] = None
    remaining_credits: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    already_rendered: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        return cls(
            task_id=data.get("taskId", ""),
            video_task_id=data.get("videoTaskId"),
            render_task_id=data.get("renderTaskId"),
            preview_url=data.get("previewUrl"),
            viewer_url=data.get("viewerUrl"),
            config_url=data.get("configUrl"),
            video_url=data.get("videoUrl"),
            status=data.get("status", "created"),
            quality=data.get("quality"),
            cost=data.get("cost", 0),
            cost_credits=data.get("costCredits"),
            remaining_credits=data.get("remainingCredits"),
            width=data.get("width"),
            height=data.get("height"),
            duration=data.get("duration"),
            created_at=cls._parse_datetime(data.get("createdAt")),
            completed_at=cls._parse_datetime(data.get("completedAt")),
            metadata=data.get("metadata"),
            message=data.get("message"),
            already_rendered=data.get("alreadyRendered"),
        )

    @staticmethod
    def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None


@dataclass
class TaskList:
    """List of video tasks"""
    tasks: List[Task]
    page: int
    limit: int
    total: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskList":
        pagination = data.get("pagination", {})
        return cls(
            tasks=[Task.from_dict(t) for t in data.get("tasks", [])],
            page=pagination.get("page", 1),
            limit=pagination.get("limit", 20),
            total=pagination.get("total", 0),
        )


@dataclass
class Credits:
    """Credit balance information"""
    credits: int
    currency: str = "credits"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Credits":
        return cls(
            credits=data.get("credits", 0),
            currency=data.get("currency", "credits"),
        )


@dataclass
class Asset:
    """Uploaded file asset"""
    id: str
    name: str
    url: str
    type: str
    mime_type: str
    size: int
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Asset":
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            url=data.get("url", ""),
            type=data.get("type", ""),
            mime_type=data.get("mimeType", ""),
            size=data.get("size", 0),
            created_at=cls._parse_datetime(data.get("createdAt")),
        )

    @staticmethod
    def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None


@dataclass
class FileList:
    """List of uploaded files"""
    files: List[Asset]
    page: int
    limit: int
    total: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FileList":
        pagination = data.get("pagination", {})
        return cls(
            files=[Asset.from_dict(f) for f in data.get("files", [])],
            page=pagination.get("page", 1),
            limit=pagination.get("limit", 20),
            total=pagination.get("total", 0),
        )


@dataclass
class UploadResult:
    """Result of file upload"""
    count: int
    message: str
    assets: List[Asset]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UploadResult":
        return cls(
            count=data.get("count", 0),
            message=data.get("message", ""),
            assets=[Asset.from_dict(a) for a in data.get("assets", [])],
        )


@dataclass
class Preview:
    """Temporary preview link"""
    temp_id: str
    preview_url: str
    viewer_url: Optional[str] = None
    expires_in: str = "7d"
    config: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Preview":
        return cls(
            temp_id=data.get("tempId", ""),
            preview_url=data.get("previewUrl", ""),
            viewer_url=data.get("viewerUrl"),
            expires_in=data.get("expiresIn", "7d"),
            config=data.get("config"),
            message=data.get("message") or data.get("note"),
        )


@dataclass
class DeleteResult:
    """Result of delete operation"""
    success: bool
    id: str
    deleted: bool
    remote_deleted: Optional[bool] = None
    message: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any], id_field: str = "taskId") -> "DeleteResult":
        return cls(
            success=data.get("success", False),
            id=data.get(id_field, ""),
            deleted=data.get("deleted", False),
            remote_deleted=data.get("remoteDeleted"),
            message=data.get("message", ""),
        )


class RenderingVideoError(Exception):
    """Base exception for RenderingVideo SDK"""
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict] = None, status_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
        self.status_code = status_code


class AuthenticationError(RenderingVideoError):
    """Authentication failed (401)"""
    pass


class InsufficientCreditsError(RenderingVideoError):
    """Not enough credits (402)"""
    pass


class ValidationError(RenderingVideoError):
    """Invalid request data (400)"""
    pass


class NotFoundError(RenderingVideoError):
    """Resource not found (404)"""
    pass


class RateLimitError(RenderingVideoError):
    """Rate limit exceeded (429)"""
    pass


class AlreadyRenderingError(RenderingVideoError):
    """Task is already rendering"""
    pass


class RemoteError(RenderingVideoError):
    """Upstream service error"""
    pass
