from urllib.parse import quote
from ._http import request_json, send
"""
Video API client
"""

from typing import Optional, Dict, Any
from .types import Task, TaskList, DeleteResult, RenderingVideoError


class VideoClient:
    """Client for video-related API operations"""

    def __init__(self, base_url: str, api_key: str, timeout: int = 30, agent_auth=None):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._agent_auth = agent_auth
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
        return request_json(self._base_url, self._api_key, self._timeout, method, endpoint, data=data, params=params, agent_auth=self._agent_auth)

    def create(
        self,
        config: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        title: Optional[str] = None,
        category: Optional[str] = None,
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
        if metadata is not None:
            data["metadata"] = metadata
        if title is not None:
            data["title"] = title
        if category is not None:
            data["category"] = category

        result = self._request("POST", "/api/v1/video", data=data)
        return Task.from_dict(result)

    def list(
        self,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
        category: Optional[str] = None,
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
        if category is not None:
            params["category"] = category

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
        result = self._request("GET", f"/api/v1/video/{quote(task_id, safe='')}")
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
        result = self._request("DELETE", f"/api/v1/video/{quote(task_id, safe='')}")
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
        if num_workers is not None:
            data["num_workers"] = num_workers

        result = self._request("POST", f"/api/v1/video/{quote(task_id, safe='')}/render", data=data)
        return Task.from_dict(result)

    def create_and_render(self, config, metadata=None, webhook_url=None, num_workers=5, title=None, category=None):
        """Create then render once. If rendering fails, the created task ID is attached to the error."""
        task = self.create(config, metadata=metadata, title=title, category=category)
        try:
            return self.render(task.task_id, webhook_url=webhook_url, num_workers=num_workers)
        except RenderingVideoError as error:
            error.details["taskId"] = task.task_id
            raise
