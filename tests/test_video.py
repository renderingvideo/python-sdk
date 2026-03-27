"""
Tests for VideoClient
"""

import pytest
from unittest.mock import patch, MagicMock
from renderingvideo.video import VideoClient
from renderingvideo.types import Task, TaskList, DeleteResult


class TestVideoClient:
    """Test VideoClient methods"""

    @pytest.fixture
    def client(self):
        """Create a video client for testing"""
        return VideoClient(
            base_url="https://test.api.com",
            api_key="sk-test123456789",
            timeout=30
        )

    def test_client_initialization(self, client):
        """Test video client initialization"""
        assert client._base_url == "https://test.api.com"
        assert client._api_key == "sk-test123456789"
        assert client._timeout == 30

    @patch('renderingvideo.video.VideoClient._request')
    def test_create_task(self, mock_request, client):
        """Test creating a video task"""
        mock_request.return_value = {
            "success": True,
            "taskId": "abc123",
            "status": "created",
            "previewUrl": "https://example.com/preview/abc123",
        }

        task = client.create(
            config={
                "meta": {"version": "2.0.0"},
                "tracks": []
            }
        )

        assert task.task_id == "abc123"
        assert task.status == "created"
        mock_request.assert_called_once()

    @patch('renderingvideo.video.VideoClient._request')
    def test_create_task_with_metadata(self, mock_request, client):
        """Test creating a video task with metadata"""
        mock_request.return_value = {
            "success": True,
            "taskId": "abc123",
            "status": "created",
        }

        task = client.create(
            config={"meta": {"version": "2.0.0"}, "tracks": []},
            metadata={"project_id": "proj_123"}
        )

        call_args = mock_request.call_args
        assert "metadata" in call_args[1]["data"]
        assert call_args[1]["data"]["metadata"]["project_id"] == "proj_123"

    @patch('renderingvideo.video.VideoClient._request')
    def test_list_tasks(self, mock_request, client):
        """Test listing video tasks"""
        mock_request.return_value = {
            "success": True,
            "tasks": [
                {"taskId": "abc123", "status": "completed"},
                {"taskId": "def456", "status": "rendering"},
            ],
            "pagination": {"page": 1, "limit": 20, "total": 2}
        }

        result = client.list(page=1, limit=20)

        assert isinstance(result, TaskList)
        assert len(result.tasks) == 2
        assert result.page == 1
        assert result.total == 2

    @patch('renderingvideo.video.VideoClient._request')
    def test_list_tasks_with_status_filter(self, mock_request, client):
        """Test listing tasks with status filter"""
        mock_request.return_value = {
            "success": True,
            "tasks": [],
            "pagination": {"page": 1, "limit": 20, "total": 0}
        }

        client.list(page=1, limit=20, status="completed")

        call_args = mock_request.call_args
        assert call_args[1]["params"]["status"] == "completed"

    @patch('renderingvideo.video.VideoClient._request')
    def test_get_task(self, mock_request, client):
        """Test getting a single task"""
        mock_request.return_value = {
            "success": True,
            "taskId": "abc123",
            "status": "completed",
            "videoUrl": "https://example.com/video.mp4",
        }

        task = client.get(task_id="abc123")

        assert isinstance(task, Task)
        assert task.task_id == "abc123"
        assert task.status == "completed"

    @patch('renderingvideo.video.VideoClient._request')
    def test_delete_task(self, mock_request, client):
        """Test deleting a task"""
        mock_request.return_value = {
            "success": True,
            "taskId": "abc123",
            "deleted": True,
            "remoteDeleted": True,
            "message": "Video task deleted successfully"
        }

        result = client.delete(task_id="abc123")

        assert isinstance(result, DeleteResult)
        assert result.deleted is True
        assert result.remote_deleted is True

    @patch('renderingvideo.video.VideoClient._request')
    def test_render_task(self, mock_request, client):
        """Test triggering render"""
        mock_request.return_value = {
            "success": True,
            "taskId": "abc123",
            "renderTaskId": "rt_001",
            "status": "rendering",
        }

        task = client.render(
            task_id="abc123",
            webhook_url="https://example.com/webhook",
            num_workers=10
        )

        assert task.status == "rendering"
        assert task.render_task_id == "rt_001"

        call_args = mock_request.call_args
        assert call_args[1]["data"]["webhook_url"] == "https://example.com/webhook"
        assert call_args[1]["data"]["num_workers"] == 10
