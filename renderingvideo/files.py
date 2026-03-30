"""
File upload and management API client
"""

import json
import os
from os import PathLike
from typing import Optional, Dict, Any, List, Union, BinaryIO
from .types import FileList, UploadResult, DeleteResult, Asset, RenderingVideoError


class FilesClient:
    """Client for file upload and management API operations"""

    # Supported MIME type prefixes
    SUPPORTED_TYPES = {
        "image": ["jpeg", "png", "webp", "gif", "svg+xml", "avif", "heic", "heif"],
        "video": ["mp4", "webm", "ogg", "quicktime"],
        "audio": ["mpeg", "mp3", "wav", "ogg", "aac", "flac"],
    }

    def __init__(self, base_url: str, api_key: str, timeout: int = 300):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout  # Longer timeout for uploads

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
        }

    def _request_upload(
        self,
        files: List[tuple],
    ) -> Dict[str, Any]:
        """Make multipart/form-data upload request"""
        import urllib.request
        import urllib.error
        import uuid

        boundary = f"----WebKitFormBoundary{uuid.uuid4().hex[:16]}"
        headers = self._get_headers()
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"

        body_parts = []

        for field_name, file_input, filename in files:
            # Determine MIME type
            ext = os.path.splitext(filename)[1].lower().lstrip(".")
            mime_type = self._get_mime_type(ext)

            if isinstance(file_input, (str, PathLike)):
                with open(file_input, "rb") as f:
                    file_content = f.read()
            else:
                if hasattr(file_input, "seek"):
                    file_input.seek(0)
                file_content = file_input.read()
                if isinstance(file_content, str):
                    file_content = file_content.encode("utf-8")

            body_parts.append(f"--{boundary}".encode())
            body_parts.append(
                f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"'.encode()
            )
            body_parts.append(f"Content-Type: {mime_type}".encode())
            body_parts.append(b"")
            body_parts.append(file_content)

        body_parts.append(f"--{boundary}--".encode())
        body = b"\r\n".join(body_parts)

        url = f"{self._base_url}/api/v1/upload"
        req = urllib.request.Request(
            url,
            data=body,
            headers=headers,
            method="POST",
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
            elif e.code == 400:
                from .types import ValidationError
                raise ValidationError(message, code, error_data, e.code)
            elif e.code == 402:
                from .types import InsufficientCreditsError
                raise InsufficientCreditsError(message, code, error_data, e.code)
            else:
                raise RenderingVideoError(message, code, error_data, e.code)
        except urllib.error.URLError as e:
            raise RenderingVideoError(f"Network error: {e.reason}", "NETWORK_ERROR")

    def _get_mime_type(self, ext: str) -> str:
        """Get MIME type from file extension"""
        ext_map = {
            # Images
            "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "png": "image/png",
            "webp": "image/webp",
            "gif": "image/gif",
            "svg": "image/svg+xml",
            "avif": "image/avif",
            "heic": "image/heic",
            "heif": "image/heif",
            # Videos
            "mp4": "video/mp4",
            "webm": "video/webm",
            "ogv": "video/ogg", "ogg": "video/ogg",
            "mov": "video/quicktime",
            # Audio
            "mp3": "audio/mpeg",
            "mpeg": "audio/mpeg",
            "wav": "audio/wav",
            "aac": "audio/aac",
            "flac": "audio/flac",
        }
        return ext_map.get(ext.lower(), "application/octet-stream")

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request"""
        import urllib.request
        import urllib.parse
        import urllib.error

        url = f"{self._base_url}{endpoint}"

        if params:
            url += "?" + urllib.parse.urlencode(params)

        headers = {"Authorization": f"Bearer {self._api_key}"}

        req = urllib.request.Request(
            url,
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
            elif e.code == 404:
                from .types import NotFoundError
                raise NotFoundError(message, code, error_data, e.code)
            elif e.code == 400:
                from .types import ValidationError
                raise ValidationError(message, code, error_data, e.code)
            else:
                raise RenderingVideoError(message, code, error_data, e.code)
        except urllib.error.URLError as e:
            raise RenderingVideoError(f"Network error: {e.reason}", "NETWORK_ERROR")

    def upload(
        self,
        file: Optional[Union[str, PathLike[str], BinaryIO]] = None,
        files: Optional[List[Union[str, PathLike[str], BinaryIO]]] = None,
        file_paths: Optional[List[str]] = None,
    ) -> UploadResult:
        """
        Upload one or more files

        Args:
            file: Single file path or file-like object
            files: List of file paths or file-like objects
            file_paths: Alternative name for files parameter

        Returns:
            UploadResult: Upload result with list of assets

        Example:
            # Upload single file
            result = client.files.upload(file="/path/to/image.png")

            # Upload multiple files
            result = client.files.upload(files=["/path/to/image.png", "/path/to/video.mp4"])
        """
        upload_files = []

        # Handle single file
        if file:
            if isinstance(file, (str, PathLike)):
                filename = os.path.basename(os.fspath(file))
                upload_files.append(("file", file, filename))
            else:
                # File-like object
                filename = os.path.basename(getattr(file, "name", "file"))
                upload_files.append(("file", file, filename))

        # Handle multiple files
        file_list = files or file_paths
        if file_list:
            for i, f in enumerate(file_list):
                if isinstance(f, (str, PathLike)):
                    filename = os.path.basename(os.fspath(f))
                    upload_files.append(("files", f, filename))
                else:
                    # File-like object
                    filename = os.path.basename(getattr(f, "name", f"file_{i}"))
                    upload_files.append(("files", f, filename))

        if not upload_files:
            raise ValueError("No files provided. Specify 'file' or 'files' parameter.")

        result = self._request_upload(upload_files)
        return UploadResult.from_dict(result)

    def list(
        self,
        page: int = 1,
        limit: int = 20,
        type: Optional[str] = None,
    ) -> FileList:
        """
        List uploaded files

        Args:
            page: Page number (default: 1)
            limit: Items per page (default: 20, max: 100)
            type: Filter by file type (image, video, audio)

        Returns:
            FileList: List of files with pagination info
        """
        params = {"page": page, "limit": limit}
        if type:
            params["type"] = type

        result = self._request("GET", "/api/v1/files", params=params)
        return FileList.from_dict(result)

    def get(self, file_id: str) -> Asset:
        """
        Get file details by ID (searches through list)

        Args:
            file_id: The file ID

        Returns:
            Asset: File details
        """
        # API doesn't have a single file endpoint, so we search paginated results.
        page = 1
        while True:
            files = self.list(page=page, limit=100)
            for asset in files.files:
                if asset.id == file_id:
                    return asset

            if (files.page * files.limit) >= files.total:
                break

            page += 1

        from .types import NotFoundError
        raise NotFoundError(f"File not found: {file_id}", "NOT_FOUND")

    def delete(self, file_id: str) -> DeleteResult:
        """
        Delete a file permanently

        Args:
            file_id: The file ID

        Returns:
            DeleteResult: Delete result
        """
        result = self._request("DELETE", f"/api/v1/files/{file_id}")
        return DeleteResult.from_dict(result, "fileId")
