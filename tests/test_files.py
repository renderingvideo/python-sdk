"""
Tests for FilesClient
"""

import pytest
from unittest.mock import patch, MagicMock
from renderingvideo.files import FilesClient
from renderingvideo.types import FileList, UploadResult, DeleteResult


class TestFilesClient:
    """Test FilesClient methods"""

    @pytest.fixture
    def client(self):
        """Create a files client for testing"""
        return FilesClient(
            base_url="https://test.api.com",
            api_key="sk-test123456789",
            timeout=300
        )

    def test_client_initialization(self, client):
        """Test files client initialization"""
        assert client._base_url == "https://test.api.com"
        assert client._api_key == "sk-test123456789"
        assert client._timeout == 300

    def test_get_mime_type(self, client):
        """Test MIME type detection"""
        assert client._get_mime_type("jpg") == "image/jpeg"
        assert client._get_mime_type("png") == "image/png"
        assert client._get_mime_type("mp4") == "video/mp4"
        assert client._get_mime_type("mp3") == "audio/mpeg"
        assert client._get_mime_type("unknown") == "application/octet-stream"

    @patch('renderingvideo.files.FilesClient._request')
    def test_list_files(self, mock_request, client):
        """Test listing files"""
        mock_request.return_value = {
            "success": True,
            "files": [
                {
                    "id": "asset_001",
                    "name": "image.png",
                    "url": "https://example.com/image.png",
                    "type": "image",
                    "mimeType": "image/png",
                    "size": 12345,
                }
            ],
            "pagination": {"page": 1, "limit": 20, "total": 1}
        }

        result = client.list(page=1, limit=20)

        assert isinstance(result, FileList)
        assert len(result.files) == 1
        assert result.files[0].name == "image.png"

    @patch('renderingvideo.files.FilesClient._request')
    def test_list_files_with_type_filter(self, mock_request, client):
        """Test listing files with type filter"""
        mock_request.return_value = {
            "success": True,
            "files": [],
            "pagination": {"page": 1, "limit": 20, "total": 0}
        }

        client.list(page=1, limit=20, type="image")

        call_args = mock_request.call_args
        assert call_args[1]["params"]["type"] == "image"

    @patch('renderingvideo.files.FilesClient._request')
    def test_delete_file(self, mock_request, client):
        """Test deleting a file"""
        mock_request.return_value = {
            "success": True,
            "fileId": "asset_001",
            "deleted": True,
            "message": "File deleted successfully"
        }

        result = client.delete(file_id="asset_001")

        assert isinstance(result, DeleteResult)
        assert result.deleted is True

    def test_upload_no_files_raises_error(self, client):
        """Test upload without files raises error"""
        with pytest.raises(ValueError) as exc_info:
            client.upload()
        assert "No files provided" in str(exc_info.value)
