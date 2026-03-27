"""
Video API client
"""

from typing import Optional, Dict, Any
from .types import Task, TaskList, DeleteResult, RenderingVideoError


class VideoClient:
    """Client for video-related API operations"""

    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout

    def _get_headers(self, content_type: str = "application/json") -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": content_type,
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
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Task:
        """
        Create a new video task (does not start rendering)

        Args:
            config: Video configuration following JSON Schema
            metadata: Optional metadata to attach to the task

        Returns:
            Task: The created task

        Example:
            task = client.video.create(
                config={
                    "meta": {"version": "2.0.0", "width": 1920, "height": 1080, "fps": 30},
                    "tracks": [{"clips": [{"type": "text", "text": "Hello", "start": 0, "duration": 5}]}]
                }
            )
        """
        data = {"config": config}
        if metadata:
            data["metadata"] = metadata

        result = self._request("POST", "/api/v1/video", data=data)
        return Task.from_dict(result)

    def list(
        self,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
    ) -> TaskList:
        """
        List video tasks

        Args:
            page: Page number (default: 1)
            limit: Items per page (default: 20, max: 100)
            status: Filter by status (created, rendering, completed, failed)

        Returns:
            TaskList: List of tasks with pagination info
        """
        params = {"page": page, "limit": limit}
        if status:
            params["status"] = status

        result = self._request("GET", "/api/v1/video", params=params)
        return TaskList.from_dict(result)

    def get(self, task_id: str) -> Task:
        """
        Get task details by ID

        Args:
            task_id: The task ID

        Returns:
            Task: Task details
        """
        result = self._request("GET", f"/api/v1/video/{task_id}")
        return Task.from_dict(result)

    def delete(self, task_id: str) -> DeleteResult:
        """
        Delete a video task permanently

        This deletes the local task and render history.
        Also attempts to delete the upstream remote task.

        Args:
            task_id: The task ID

        Returns:
            DeleteResult: Result with deleted and remoteDeleted flags
        """
        result = self._request("DELETE", f"/api/v1/video/{task_id}")
        return DeleteResult.from_dict(result, "taskId")

    def render(
        self,
        task_id: str,
        webhook_url: Optional[str] = None,
        num_workers: int = 5,
    ) -> Task:
        """
        Trigger rendering for a task

        Args:
            task_id: The task ID
            webhook_url: Optional webhook URL for completion notification
            num_workers: Number of render workers (default: 5)

        Returns:
            Task: Updated task info with render details

        Example:
            task = client.video.render(
                task_id="abc123",
                webhook_url="https://your-server.com/webhook"
            )
        """
        data: Dict[str, Any] = {}
        if webhook_url:
            data["webhook_url"] = webhook_url
        if num_workers:
            data["num_workers"] = num_workers

        result = self._request("POST", f"/api/v1/video/{task_id}/render", data=data)
        return Task.from_dict(result)
