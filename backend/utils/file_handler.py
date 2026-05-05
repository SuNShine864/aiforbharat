"""
utils/file_handler.py
Saves uploaded files to the local filesystem under uploads/.
"""
import os
import uuid
from fastapi import UploadFile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", "uploads"))
ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx", ".doc",".png",".jpeg",".jpg",".webp"}


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

async def save_upload(file: UploadFile, subfolder: str) -> tuple[str, str]:
    """
    Save an UploadFile to uploads/<subfolder>/<uuid>_<original_name>.

    Returns:
        (absolute_file_path, original_filename)

    Raises:
        ValueError: if the extension is not allowed.
    """
    original_name = file.filename or "upload"
    ext = os.path.splitext(original_name)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"File type '{ext}' not allowed. Permitted: {sorted(ALLOWED_EXTENSIONS)}"
        )

    _ensure_dir(UPLOAD_ROOT)  # ensure uploads/ exists first

    dest_dir = os.path.join(UPLOAD_ROOT, subfolder)
    _ensure_dir(dest_dir)     # then ensure uploads/tenders/

    unique_name = f"{uuid.uuid4().hex}_{original_name}"
    dest_path   = os.path.join(dest_dir, unique_name)

    with open(dest_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return os.path.abspath(dest_path), original_name


def delete_file(file_path: str):
    """Remove a file if it exists (silent on missing)."""
    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass