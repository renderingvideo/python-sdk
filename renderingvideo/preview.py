"""
Preview API client for temporary preview links
"""

from typing import Optional, Dict, Any
from .types import Preview, Task, DeleteResult, RenderingVideoError


class PreviewClient:
    """Client for preview-related API operations"""

    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request"""
        import json
        import urllib.request
        import urllib.parse
        import urllib.error

        url = f"{self._base_url}{endpoint}"

        if params:
            url += "?" + urllib.parse.urlencode(params)

        headers = self._get_headers()
        body = json.dumps(data).encode("utf-8") if data else None

        req = urllib.request.Request(
            url,
            data=body,
            headers=headers,
            method=method,
        )

        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            try:
                error_data = json.loads(error_body)
            except json.JSONDecodeError:
                error_data = {"error": error_body}

            message = error_data.get("error", str(e))
            code = error_data.get("code", "UNKNOWN_ERROR")

            if e.code == 401:
                from .types import AuthenticationError
                raise AuthenticationError(message, code, error_data, e.code)
            elif e.code == 402:
                from .types import InsufficientCreditsError
                raise InsufficientCreditsError(message, code, error_data, e.code)
            elif e.code == 400:
                from .types import ValidationError, AlreadyRenderingError
                if code == "ALREADY_RENDERING":
                    raise AlreadyRenderingError(message, code, error_data, e.code)
                raise ValidationError(message, code, error_data, e.code)
            elif e.code == 404:
                from .types import NotFoundError
                raise NotFoundError(message, code, error_data, e.code)
            elif e.code == 429:
                from .types import RateLimitError
                raise RateLimitError(message, code, error_data, e.code)
            else:
                raise RenderingVideoError(message, code, error_data, e.code)
        except urllib.error.URLError as e:
            raise RenderingVideoError(f"Network error: {e.reason}", "NETWORK_ERROR")

    def create(
        self,
        config: Dict[str, Any],
    ) -> Preview:
        """
        Create a temporary preview link (7 days validity, no credits consumed)

        Preview links:
        - Valid for 7 days
        - Do NOT consume credits
        - Do NOT produce a downloadable video file
        - Use for testing and previewing configurations
        - Sends the full video schema directly as the request body

        Args:
            config: Video configuration following JSON Schema

        Returns:
            Preview: Preview info with tempId and previewUrl

        Example:
            preview = client.preview.create(
                {
                    "meta": {"version": "2.0.0", "width": 1920, "height": 1080},
                    "tracks": [{"clips": [{"type": "text", "text": "Hello", "start": 0, "duration": 5}]}]
                }
            )
            print(f"Preview URL: {preview.preview_url}")
        """
        result = self._request("POST", "/api/v1/preview", data=config)
        return Preview.from_dict(result)

    def get(self, temp_id: str) -> Preview:
        """
        Get preview config by temp ID

        Args:
            temp_id: The temporary preview ID

        Returns:
            Preview: Preview info with config
        """
        result = self._request("GET", f"/api/v1/preview/{temp_id}")
        return Preview.from_dict(result)

    def delete(self, temp_id: str) -> DeleteResult:
        """
        Delete a temporary preview link

        Args:
            temp_id: The temporary preview ID

        Returns:
            DeleteResult: Delete result
        """
        result = self._request("DELETE", f"/api/v1/preview/{temp_id}")
        return DeleteResult.from_dict(result, "tempId")

    def convert(
        self,
        temp_id: str,
        category: Optional[str] = None,
    ) -> Task:
        """
        Clone a temporary preview into a permanent video task

        The temporary link itself remains usable after conversion.

        Args:
            temp_id: The temporary preview ID
            category: Optional category for the new permanent task

        Returns:
            Task: The created permanent task

        Example:
            task = client.preview.convert(temp_id="temp_abc123")
            print(f"New task ID: {task.task_id}")
        """
        data: Dict[str, Any] = {}
        if category:
            data["category"] = category

        result = self._request("POST", f"/api/v1/preview/{temp_id}/convert", data=data)
        return Task.from_dict(result)

    def render(
        self,
        temp_id: str,
        category: Optional[str] = None,
        webhook_url: Optional[str] = None,
        num_workers: int = 5,
    ) -> Task:
        """
        Clone a temporary preview into a permanent task and immediately start rendering

        This is a convenience method that combines convert + render in one step.

        Args:
            temp_id: The temporary preview ID
            category: Optional category for the new permanent task (default: "api")
            webhook_url: Optional webhook URL for completion notification
            num_workers: Number of render workers (default: 5)

        Returns:
            Task: Task info with render details

        Example:
            task = client.preview.render(
                temp_id="temp_abc123",
                webhook_url="https://your-server.com/webhook"
            )
            print(f"Task ID: {task.task_id}, Status: {task.status}")
        """
        data: Dict[str, Any] = {}
        if category:
            data["category"] = category
        if webhook_url:
            data["webhook_url"] = webhook_url
        if num_workers:
            data["num_workers"] = num_workers

        result = self._request("POST", f"/api/v1/preview/{temp_id}/render", data=data)
        return Task.from_dict(result)
