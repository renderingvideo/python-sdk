"""
Basic usage examples for the RenderingVideo Python SDK
"""

from renderingvideo import Client

# Initialize the client with your API key
client = Client(api_key="sk-your-api-key")

# ==========================================
# Example 1: Create and render a simple video
# ==========================================

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
                        "duration": 5,
                        "style": {
                            "fontSize": 72,
                            "color": "#FFFFFF"
                        }
                    }
                ]
            }
        ]
    }
)

print(f"Task created: {task.task_id}")
print(f"Preview URL: {task.preview_url}")

# Trigger rendering
render_task = client.video.render(
    task_id=task.task_id,
    webhook_url="https://your-server.com/webhook"  # Optional
)

print(f"Rendering started: {render_task.status}")


# ==========================================
# Example 2: List and filter tasks
# ==========================================

# List all completed tasks
completed_tasks = client.video.list(
    page=1,
    limit=10,
    status="completed"
)

for task in completed_tasks.tasks:
    print(f"Task {task.task_id}: {task.status}")
    if task.video_url:
        print(f"  Video URL: {task.video_url}")


# ==========================================
# Example 3: Upload files
# ==========================================

# Upload a single file
upload_result = client.files.upload(file="/path/to/image.png")
print(f"Uploaded {upload_result.count} file(s)")

for asset in upload_result.assets:
    print(f"  {asset.name}: {asset.url}")

# Upload multiple files
upload_result = client.files.upload(files=[
    "/path/to/image1.png",
    "/path/to/image2.jpg",
    "/path/to/video.mp4"
])


# ==========================================
# Example 4: Create preview link (no credits)
# ==========================================

# Create a temporary preview (valid for 7 days)
preview = client.preview.create(
    config={
        "meta": {"version": "2.0.0", "width": 1920, "height": 1080},
        "tracks": [
            {
                "clips": [
                    {"type": "text", "text": "Preview Test", "start": 0, "duration": 3}
                ]
            }
        ]
    }
)

print(f"Preview URL: {preview.preview_url}")
print(f"Expires in: {preview.expires_in}")

# Convert preview to permanent task when ready
permanent_task = client.preview.convert(temp_id=preview.temp_id)
print(f"Converted to task: {permanent_task.task_id}")


# ==========================================
# Example 5: Check credits
# ==========================================

credits = client.get_credits()
print(f"Available credits: {credits.credits}")


# ==========================================
# Example 6: Error handling
# ==========================================

from renderingvideo import (
    RenderingVideoError,
    InsufficientCreditsError,
    ValidationError,
    NotFoundError,
)

try:
    task = client.video.create(config={"invalid": "config"})
except ValidationError as e:
    print(f"Invalid configuration: {e.message}")
except InsufficientCreditsError as e:
    print(f"Not enough credits: {e.message}")
except RenderingVideoError as e:
    print(f"API error [{e.code}]: {e.message}")


# ==========================================
# Example 7: Delete a task
# ==========================================

result = client.video.delete(task_id="task_to_delete")
print(f"Deleted: {result.deleted}")
print(f"Remote deleted: {result.remote_deleted}")
