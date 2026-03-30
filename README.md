# RenderingVideo Python SDK

Official Python SDK for the RenderingVideo API. Create and render videos programmatically with ease.

## Installation

```bash
pip install renderingvideo
```

## Quick Start

```python
from renderingvideo import Client

# Initialize client with your API key
client = Client(api_key="sk-your-api-key")

# Create a video task
task = client.video.create(
    config={
        "meta": {
            "version": "2.0.0",
            "width": 1920,
            "height": 1080,
            "fps": 30,
            "background": "#000000"
        },
        "tracks": [
            {
                "clips": [
                    {
                        "type": "text",
                        "text": "Hello World",
                        "start": 0,
                        "duration": 5
                    }
                ]
            }
        ]
    }
)

print(f"Task ID: {task.task_id}")
print(f"Preview URL: {task.preview_url}")

# Trigger rendering
render_task = client.video.render(
    task_id=task.task_id,
    webhook_url="https://your-server.com/webhook"  # Optional
)
print(f"Status: {render_task.status}")
```

## Features

- **Video Management**: Create, list, get, and delete video tasks
- **Rendering**: Trigger and monitor video rendering
- **File Upload**: Upload images, videos, and audio files
- **File Management**: List and delete uploaded files
- **Preview Links**: Create temporary preview links without consuming credits
- **Credit Management**: Check your credit balance
- **Webhook Support**: Configure webhooks for completion notifications
- **Type Safety**: Full type hints for better IDE support
- **Zero Dependencies**: Uses only Python standard library

## API Reference

### Client Initialization

```python
from renderingvideo import Client

client = Client(
    api_key="sk-xxx",                   # Required: Your API key
    base_url="https://renderingvideo.com",  # Optional: Custom API URL
    timeout=30                          # Optional: Request timeout in seconds
)
```

### Video Operations

```python
# Create a video task (does not start rendering)
task = client.video.create(
    config={...},                       # Required: Video configuration
    metadata={"project_id": "proj_123"} # Optional: Custom metadata
)

# List video tasks
tasks = client.video.list(
    page=1,                             # Page number
    limit=20,                           # Items per page (max 100)
    status="completed"                  # Filter by status
)

# Get task details
task = client.video.get(task_id="abc123")

# Trigger rendering
task = client.video.render(
    task_id="abc123",
    webhook_url="https://...",          # Optional: Completion webhook
    num_workers=5                       # Optional: Number of workers
)

# Delete a video task
result = client.video.delete(task_id="abc123")
print(f"Deleted: {result.deleted}")
print(f"Remote deleted: {result.remote_deleted}")
```

### File Operations

```python
# Upload single file
result = client.files.upload(file="/path/to/image.png")

# Upload multiple files
result = client.files.upload(files=[
    "/path/to/image.png",
    "/path/to/video.mp4"
])

print(f"Uploaded {result.count} files")
for asset in result.assets:
    print(f"  - {asset.name}: {asset.url}")

# List uploaded files
files = client.files.list(
    page=1,
    limit=20,
    type="image"                        # Filter by: image, video, audio
)

# Delete a file
result = client.files.delete(file_id="asset_001")
```

### Preview Operations

Preview links are temporary (7 days), don't consume credits, and don't produce downloadable videos.

```python
# Create a preview link
preview = client.preview.create({...})
print(f"Preview URL: {preview.preview_url}")
print(f"Expires in: {preview.expires_in}")

# Get preview config
preview = client.preview.get(temp_id="temp_abc123")

# Convert preview to permanent task (preview link still works)
task = client.preview.convert(temp_id="temp_abc123")

# Convert and render in one step
task = client.preview.render(
    temp_id="temp_abc123",
    category="api",                     # Optional
    webhook_url="https://...",          # Optional
    num_workers=5                       # Optional
)

# Delete a preview link
result = client.preview.delete(temp_id="temp_abc123")
```

### Credits

```python
# Get credit balance
credits = client.get_credits()
print(f"Available credits: {credits.credits}")
```

## Task Status Values

| Status | Description |
|--------|-------------|
| `created` | Task created, not yet rendering |
| `rendering` | Currently rendering |
| `completed` | Rendering finished successfully |
| `failed` | Rendering failed |

## Error Handling

```python
from renderingvideo import (
    RenderingVideoError,
    AuthenticationError,
    InsufficientCreditsError,
    ValidationError,
    NotFoundError,
    RateLimitError,
    AlreadyRenderingError,
)

try:
    task = client.video.create(config={...})
except InsufficientCreditsError as e:
    print(f"Not enough credits: {e.message}")
    print(f"Error code: {e.code}")
except ValidationError as e:
    print(f"Invalid config: {e.message}")
except NotFoundError as e:
    print(f"Resource not found: {e.message}")
except AlreadyRenderingError as e:
    print(f"Task is already rendering: {e.message}")
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
except RenderingVideoError as e:
    print(f"API error [{e.code}]: {e.message}")
    print(f"Details: {e.details}")
```

## Credit Calculation

Cost = Video duration (seconds) × Quality multiplier

| Quality | Short Edge | Multiplier |
|---------|------------|------------|
| 720p | ≥720px | 1.0 |
| 1080p | ≥1080px | 1.5 |
| 2K | ≥1440px | 2.0 |

## Webhook Notifications

When rendering completes, the webhook receives:

```json
{
    "taskId": "abc123def456",
    "renderTaskId": "rt_002",
    "status": "completed",
    "videoUrl": "https://storage.../videos/abc123.mp4",
    "error": null,
    "timestamp": "2026-03-23T10:00:00.000Z"
}
```

## Supported File Types

| Category | Types |
|----------|-------|
| Image | JPEG, PNG, WebP, GIF, SVG, AVIF, HEIC, HEIF |
| Video | MP4, WebM, OGG, MOV |
| Audio | MP3, WAV, AAC, FLAC, OGG |

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black renderingvideo/
isort renderingvideo/

# Type check
mypy renderingvideo/
```

## Building and Publishing

```bash
# Build the package
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

## License

MIT License
