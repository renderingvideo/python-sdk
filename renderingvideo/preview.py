from urllib.parse import quote
from ._http import request_json, send
"""
Preview API client for temporary preview links
"""

from typing import Optional, Dict, Any
from .types import Preview, Task, DeleteResult, RenderingVideoError


class PreviewClient:
    """Client for preview-related API operations"""

    def __init__(self, base_url: str, api_key: str, timeout: int = 30, agent_auth=None):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._agent_auth = agent_auth
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
        return request_json(self._base_url, self._api_key, self._timeout, method, endpoint, data=data, params=params, agent_auth=self._agent_auth)

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
        result = self._request("GET", f"/api/v1/preview/{quote(temp_id, safe='')}")
        return Preview.from_dict(result)

    def delete(self, temp_id: str) -> DeleteResult:
        """
        Delete a temporary preview link

        Args:
            temp_id: The temporary preview ID

        Returns:
            DeleteResult: Delete result
        """
        result = self._request("DELETE", f"/api/v1/preview/{quote(temp_id, safe='')}")
        return DeleteResult.from_dict(result, "tempId")

    def convert(
        self,
        temp_id: str,
        category: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
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
        if metadata is not None:
            data["metadata"] = metadata

        result = self._request("POST", f"/api/v1/preview/{quote(temp_id, safe='')}/convert", data=data)
        return Task.from_dict(result)

    def render(
        self,
        temp_id: str,
        category: Optional[str] = None,
        webhook_url: Optional[str] = None,
        num_workers: int = 5,
        metadata: Optional[Dict[str, Any]] = None,
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
        if metadata is not None:
            data["metadata"] = metadata
        if webhook_url:
            data["webhook_url"] = webhook_url
        if num_workers is not None:
            data["num_workers"] = num_workers

        result = self._request("POST", f"/api/v1/preview/{quote(temp_id, safe='')}/render", data=data)
        return Task.from_dict(result)
