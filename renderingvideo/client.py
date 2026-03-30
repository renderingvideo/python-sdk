"""
Main client for the RenderingVideo SDK
"""

from typing import Optional
from .video import VideoClient
from .files import FilesClient
from .preview import PreviewClient
from .types import Credits


class Client:
    """
    Main client for the RenderingVideo API

    Usage:
        from renderingvideo import Client

        client = Client(api_key="sk-xxx")

        # Create a video task
        task = client.video.create(config={...})
        print(task.task_id)

        # Trigger rendering
        render_task = client.video.render(task_id=task.task_id)

        # Upload files
        upload = client.files.upload(file="/path/to/image.png")

        # Create preview
        preview = client.preview.create({...})
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://renderingvideo.com",
        timeout: int = 30,
    ):
        """
        Initialize the client

        Args:
            api_key: Your API key (starts with 'sk-')
            base_url: API base URL (default: https://renderingvideo.com)
            timeout: Request timeout in seconds (default: 30)
        """
        if not api_key or not api_key.startswith("sk-"):
            raise ValueError("Invalid API key. API key should start with 'sk-'")

        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

        # Lazy-loaded sub-clients
        self._video: Optional[VideoClient] = None
        self._files: Optional[FilesClient] = None
        self._preview: Optional[PreviewClient] = None

    @property
    def video(self) -> VideoClient:
        """Access video-related operations"""
        if self._video is None:
            self._video = VideoClient(self._base_url, self._api_key, self._timeout)
        return self._video

    @property
    def files(self) -> FilesClient:
        """Access file upload and management operations"""
        if self._files is None:
            # Use longer timeout for file uploads
            self._files = FilesClient(self._base_url, self._api_key, max(300, self._timeout))
        return self._files

    @property
    def preview(self) -> PreviewClient:
        """Access preview-related operations"""
        if self._preview is None:
            self._preview = PreviewClient(self._base_url, self._api_key, self._timeout)
        return self._preview

    def get_credits(self) -> Credits:
        """
        Get current credit balance

        Returns:
            Credits: Current credit information

        Example:
            credits = client.get_credits()
            print(f"Available credits: {credits.credits}")
        """
        import json
        import urllib.request
        import urllib.error

        url = f"{self._base_url}/api/v1/credits"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
        }

        req = urllib.request.Request(url, headers=headers, method="GET")

        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
                return Credits.from_dict(result)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            try:
                error_data = json.loads(error_body)
            except json.JSONDecodeError:
                error_data = {"error": error_body}

            from .types import AuthenticationError, RenderingVideoError
            if e.code == 401:
                raise AuthenticationError(
                    error_data.get("error", str(e)),
                    error_data.get("code"),
                    error_data,
                    e.code
                )
            raise RenderingVideoError(
                error_data.get("error", str(e)),
                error_data.get("code"),
                error_data,
                e.code
            )

    @property
    def api_key(self) -> str:
        """Get the API key (masked for security)"""
        if len(self._api_key) > 12:
            return f"{self._api_key[:8]}...{self._api_key[-4:]}"
        return "***"

    def __repr__(self) -> str:
        return f"<RenderingVideo client api_key={self.api_key}>"
