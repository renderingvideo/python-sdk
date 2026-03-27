"""
Tests for PreviewClient
"""

import pytest
from unittest.mock import patch
from renderingvideo.preview import PreviewClient
from renderingvideo.types import Preview, Task, DeleteResult


class TestPreviewClient:
    """Test PreviewClient methods"""

    @pytest.fixture
    def client(self):
        """Create a preview client for testing"""
        return PreviewClient(
            base_url="https://test.api.com",
            api_key="sk-test123456789",
            timeout=30
        )

    def test_client_initialization(self, client):
        """Test preview client initialization"""
        assert client._base_url == "https://test.api.com"
        assert client._api_key == "sk-test123456789"
        assert client._timeout == 30

    @patch('renderingvideo.preview.PreviewClient._request')
    def test_create_preview(self, mock_request, client):
        """Test creating a preview"""
        mock_request.return_value = {
            "success": True,
            "tempId": "temp_abc123",
            "previewUrl": "https://example.com/preview/temp_abc123",
            "viewerUrl": "https://example.com/view/temp_abc123",
            "expiresIn": "7d",
            "note": "Preview links are temporary"
        }

        preview = client.create(
            config={
                "meta": {"version": "2.0.0"},
                "tracks": []
            }
        )

        assert isinstance(preview, Preview)
        assert preview.temp_id == "temp_abc123"
        assert preview.expires_in == "7d"

    @patch('renderingvideo.preview.PreviewClient._request')
    def test_get_preview(self, mock_request, client):
        """Test getting a preview"""
        mock_request.return_value = {
            "success": True,
            "tempId": "temp_abc123",
            "config": {
                "meta": {"version": "2.0.0"},
                "tracks": []
            }
        }

        preview = client.get(temp_id="temp_abc123")

        assert isinstance(preview, Preview)
        assert preview.temp_id == "temp_abc123"
        assert preview.config is not None

    @patch('renderingvideo.preview.PreviewClient._request')
    def test_delete_preview(self, mock_request, client):
        """Test deleting a preview"""
        mock_request.return_value = {
            "success": True,
            "tempId": "temp_abc123",
            "deleted": True,
            "message": "Temp preview deleted successfully"
        }

        result = client.delete(temp_id="temp_abc123")

        assert isinstance(result, DeleteResult)
        assert result.deleted is True

    @patch('renderingvideo.preview.PreviewClient._request')
    def test_convert_preview(self, mock_request, client):
        """Test converting preview to permanent task"""
        mock_request.return_value = {
            "success": True,
            "tempId": "temp_abc123",
            "converted": True,
            "taskId": "abc123",
            "videoTaskId": "vt_001",
            "message": "Temp preview cloned to a permanent task successfully"
        }

        task = client.convert(temp_id="temp_abc123", category="api")

        assert isinstance(task, Task)
        assert task.task_id == "abc123"

    @patch('renderingvideo.preview.PreviewClient._request')
    def test_render_preview(self, mock_request, client):
        """Test converting and rendering preview"""
        mock_request.return_value = {
            "success": True,
            "tempId": "temp_abc123",
            "converted": True,
            "taskId": "abc123",
            "renderTaskId": "rt_001",
            "status": "rendering",
            "message": "Rendering started"
        }

        task = client.render(
            temp_id="temp_abc123",
            webhook_url="https://example.com/webhook",
            num_workers=5
        )

        assert isinstance(task, Task)
        assert task.task_id == "abc123"
        assert task.status == "rendering"

        call_args = mock_request.call_args
        assert call_args[1]["data"]["webhook_url"] == "https://example.com/webhook"
        assert call_args[1]["data"]["num_workers"] == 5
