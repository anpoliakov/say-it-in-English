from typing import Protocol, runtime_checkable


@runtime_checkable
class StorageBackend(Protocol):
    """Абстрактный интерфейс хранилища.

    Чтобы заменить MinIO на S3, локальный диск или любой другой бэкенд —
    реализуй этот Protocol без изменения остального кода.
    """

    def ensure_bucket(self) -> None:
        """Create bucket if not exists and set public-read policy."""
        ...

    def upload(self, key: str, data: bytes, content_type: str = "image/jpeg") -> str:
        """Upload file, return the key."""
        ...

    def delete(self, key: str) -> None:
        """Delete file by key (silently ignore missing)."""
        ...

    def get_url(self, key: str | None) -> str | None:
        """Return public URL for a key, or None if key is None."""
        ...
