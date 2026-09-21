import os
import uuid
from pathlib import Path
from werkzeug.datastructures import FileStorage

ALLOWED_EXTENSIONS = {"pdf", "ppt", "pptx"}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB


class StorageService:
    """Centralized file storage service for persistent uploads and downloads.
    Decoupled from Flask routes and adaptable to local disk or cloud/object storage.
    """

    def __init__(self, upload_dir: str = None):
        if not upload_dir:
            # Check environment variable first, else fallback to root uploads/materials
            env_dir = os.environ.get("MATERIAL_UPLOAD_DIR")
            if env_dir:
                self.upload_root = Path(env_dir).resolve()
            else:
                # Resolve relative to project root (2 levels up from backend/app)
                project_root = Path(__file__).resolve().parent.parent.parent.parent
                self.upload_root = project_root / "uploads" / "materials"
        else:
            self.upload_root = Path(upload_dir).resolve()

        self.upload_root.mkdir(parents=True, exist_ok=True)

    def is_allowed_file(self, filename: str) -> bool:
        return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

    def save_file(self, uploaded: FileStorage) -> dict:
        """Saves an uploaded file to storage and returns metadata."""
        if not uploaded or not uploaded.filename:
            raise ValueError("No file provided.")

        if not self.is_allowed_file(uploaded.filename):
            raise ValueError(f"Invalid file extension. Allowed formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}")

        # Compute file size
        uploaded.stream.seek(0, os.SEEK_END)
        size = uploaded.stream.tell()
        uploaded.stream.seek(0)

        if size > MAX_FILE_SIZE:
            raise ValueError("File size exceeds 25 MB maximum limit.")

        safe_name = Path(uploaded.filename).name
        stored_name = f"{uuid.uuid4().hex}_{safe_name}"
        dest_path = self.upload_root / stored_name

        uploaded.save(str(dest_path))

        return {
            "stored_filename": stored_name,
            "original_filename": safe_name,
            "file_size": size,
            "mime_type": uploaded.mimetype or "application/octet-stream",
            "absolute_path": str(dest_path)
        }

    def get_file_path(self, stored_filename: str) -> Path:
        """Returns the Path to the stored file, or raises FileNotFoundError."""
        file_path = self.upload_root / stored_filename
        if not file_path.is_file():
            raise FileNotFoundError(f"Stored file '{stored_filename}' not found.")
        return file_path

    def delete_file(self, stored_filename: str) -> bool:
        """Removes a stored file from disk."""
        try:
            file_path = self.upload_root / stored_filename
            if file_path.is_file():
                file_path.unlink()
                return True
        except OSError:
            pass
        return False


# Singleton default storage instance
storage_service = StorageService()
