import os
import uuid
from fastapi import UploadFile
from app.config import settings

ALLOWED_EXTENSIONS = {".txt", ".csv", ".dxf", ".dwg", ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".zip", ".rar"}

async def save_upload_file(upload_file: UploadFile, subdir: str = "general") -> str:
    """Save uploaded file and return its path relative to uploads dir."""
    ext = os.path.splitext(upload_file.filename or "file")[1].lower()
    safe_name = f"{uuid.uuid4().hex}{ext}"
    upload_path = os.path.join(settings.UPLOAD_DIR, subdir)
    os.makedirs(upload_path, exist_ok=True)
    file_path = os.path.join(upload_path, safe_name)

    content = await upload_file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    return os.path.join(subdir, safe_name)

def delete_file(file_path: str) -> bool:
    full_path = os.path.join(settings.UPLOAD_DIR, file_path)
    if os.path.exists(full_path):
        os.remove(full_path)
        return True
    return False
