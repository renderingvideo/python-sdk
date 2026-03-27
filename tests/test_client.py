"""
Tests for the main Client class
"""

import pytest
from renderingvideo import Client, AuthenticationError


class TestClient:
    """Test Client initialization and basic functionality"""

    def test_client_initialization_with_valid_api_key(self):
        """Test client initializes with valid API key"""
        client = Client(api_key="sk-test123456789")
        assert client is not None

    def test_client_initialization_with_invalid_api_key(self):
        """Test client raises error with invalid API key"""
        with pytest.raises(ValueError) as exc_info:
            Client(api_key="invalid-key")
        assert "Invalid API key" in str(exc_info.value)

    def test_client_initialization_with_empty_api_key(self):
        """Test client raises error with empty API key"""
        with pytest.raises(ValueError):
            Client(api_key="")

    def test_client_initialization_with_custom_base_url(self):
        """Test client initializes with custom base URL"""
        client = Client(
            api_key="sk-test123456789",
            base_url="https://custom.api.com"
        )
        assert client is not None

    def test_client_initialization_with_custom_timeout(self):
        """Test client initializes with custom timeout"""
        client = Client(
            api_key="sk-test123456789",
            timeout=60
        )
        assert client is not None

    def test_api_key_masking(self):
        """Test API key is properly masked"""
        client = Client(api_key="sk-test123456789abcdef")
        masked = client.api_key
        assert "sk-test" in masked
        assert "abcdef" not in masked
        assert "..." in masked

    def test_video_client_lazy_loading(self):
        """Test video client is lazily loaded"""
        client = Client(api_key="sk-test123456789")
        assert client._video is None
        video = client.video
        assert video is not None
        assert client._video is not None

    def test_files_client_lazy_loading(self):
        """Test files client is lazily loaded"""
        client = Client(api_key="sk-test123456789")
        assert client._files is None
        files = client.files
        assert files is not None
        assert client._files is not None

    def test_preview_client_lazy_loading(self):
        """Test preview client is lazily loaded"""
        client = Client(api_key="sk-test123456789")
        assert client._preview is None
        preview = client.preview
        assert preview is not None
        assert client._preview is not None

    def test_client_repr(self):
        """Test client string representation"""
        client = Client(api_key="sk-test123456789abcdef")
        repr_str = repr(client)
        assert "RenderingVideo" in repr_str
        assert "client" in repr_str
