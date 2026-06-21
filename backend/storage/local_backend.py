"""Local filesystem storage backend — удобно для локальной разработки и тестов без MinIO."""
from pathlib import Path


class LocalStorageBackend:
    """Stores files on the local filesystem, serves via a base URL."""

    def __init__(self, base_dir: str = "/tmp/siie_storage", base_url: str = "http://localhost:8000/static") -> None:
        self._base_dir = Path(base_dir)
        self._base_url = base_url.rstrip("/")

    def ensure_bucket(self) -> None:
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def upload(self, key: str, data: bytes, content_type: str = "image/jpeg") -> str:
        dest = self._base_dir / key
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return key

    def delete(self, key: str) -> None:
        path = self._base_dir / key
        if path.exists():
            path.unlink()

    def get_url(self, key: str | None) -> str | None:
        if not key:
            return None
        return f"{self._base_url}/{key}"
