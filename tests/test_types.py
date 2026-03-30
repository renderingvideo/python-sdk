"""
Tests for type definitions
"""

import pytest
from datetime import datetime
from renderingvideo.types import (
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
)


class TestVideoConfig:
    """Test VideoConfig dataclass"""

    def test_default_config(self):
        """Test default video configuration"""
        config = VideoConfig()
        assert config.meta["version"] == "2.0.0"
        assert config.tracks == []
        assert config.assets is None

    def test_to_dict(self):
        """Test config serialization"""
        config = VideoConfig(
            meta={"version": "2.0.0", "width": 1920},
            tracks=[{"clips": []}]
        )
        result = config.to_dict()
        assert "meta" in result
        assert "tracks" in result
        assert "video" not in result
        assert "assets" not in result

    def test_to_dict_with_assets(self):
        """Test config serialization with assets"""
        config = VideoConfig(
            assets={"images": {"logo": "url"}}
        )
        result = config.to_dict()
        assert "assets" in result


class TestTask:
    """Test Task dataclass"""

    def test_from_dict(self):
        """Test task creation from API response"""
        data = {
            "taskId": "abc123",
            "videoTaskId": "vt_001",
            "status": "completed",
            "videoUrl": "https://example.com/video.mp4",
            "width": 1920,
            "height": 1080,
            "duration": 10,
            "costCredits": 15,
            "createdAt": "2026-03-19T10:00:00Z",
        }
        task = Task.from_dict(data)
        assert task.task_id == "abc123"
        assert task.video_task_id == "vt_001"
        assert task.status == "completed"
        assert task.video_url == "https://example.com/video.mp4"
        assert task.width == 1920
        assert task.height == 1080
        assert task.duration == 10
        assert task.cost_credits == 15
        assert task.created_at is not None

    def test_from_dict_minimal(self):
        """Test task creation with minimal data"""
        data = {"taskId": "abc123"}
        task = Task.from_dict(data)
        assert task.task_id == "abc123"
        assert task.status == "created"


class TestCredits:
    """Test Credits dataclass"""

    def test_from_dict(self):
        """Test credits creation from API response"""
        data = {"credits": 1000, "currency": "credits"}
        credits = Credits.from_dict(data)
        assert credits.credits == 1000
        assert credits.currency == "credits"


class TestAsset:
    """Test Asset dataclass"""

    def test_from_dict(self):
        """Test asset creation from API response"""
        data = {
            "id": "asset_001",
            "name": "image.png",
            "url": "https://example.com/image.png",
            "type": "image",
            "mimeType": "image/png",
            "size": 12345,
            "createdAt": "2026-03-19T10:00:00Z",
        }
        asset = Asset.from_dict(data)
        assert asset.id == "asset_001"
        assert asset.name == "image.png"
        assert asset.type == "image"
        assert asset.mime_type == "image/png"


class TestPreview:
    """Test Preview dataclass"""

    def test_from_dict(self):
        """Test preview creation from API response"""
        data = {
            "tempId": "temp_abc123",
            "previewUrl": "https://example.com/preview/temp_abc123",
            "viewerUrl": "https://example.com/view/temp_abc123",
            "expiresIn": "7d",
        }
        preview = Preview.from_dict(data)
        assert preview.temp_id == "temp_abc123"
        assert preview.preview_url == "https://example.com/preview/temp_abc123"
        assert preview.expires_in == "7d"


class TestExceptions:
    """Test exception classes"""

    def test_rendering_video_error(self):
        """Test base exception"""
        error = RenderingVideoError("Test error", "TEST_CODE", {"key": "value"})
        assert str(error) == "Test error"
        assert error.code == "TEST_CODE"
        assert error.details == {"key": "value"}

    def test_authentication_error(self):
        """Test authentication exception"""
        error = AuthenticationError("Invalid API key", "INVALID_API_KEY")
        assert "Invalid API key" in str(error)
        assert error.code == "INVALID_API_KEY"

    def test_insufficient_credits_error(self):
        """Test insufficient credits exception"""
        error = InsufficientCreditsError("Not enough credits", "INSUFFICIENT_CREDITS")
        assert "Not enough credits" in str(error)
        assert error.code == "INSUFFICIENT_CREDITS"

    def test_validation_error(self):
        """Test validation exception"""
        error = ValidationError("Invalid config", "INVALID_CONFIG")
        assert "Invalid config" in str(error)
        assert error.code == "INVALID_CONFIG"

    def test_not_found_error(self):
        """Test not found exception"""
        error = NotFoundError("Task not found", "NOT_FOUND")
        assert "Task not found" in str(error)
        assert error.code == "NOT_FOUND"
