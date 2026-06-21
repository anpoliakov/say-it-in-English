from storage.base import StorageBackend
from storage.minio_backend import MinioStorageBackend
from core.config import settings

_instance: StorageBackend | None = None


def get_storage() -> StorageBackend:
    """Singleton — вернёт один инстанс хранилища на всё время жизни приложения."""
    global _instance
    if _instance is None:
        _instance = MinioStorageBackend(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            bucket=settings.minio_bucket,
        )
    return _instance
