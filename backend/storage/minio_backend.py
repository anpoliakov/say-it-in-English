import io
import json

from minio import Minio
from minio.error import S3Error


class MinioStorageBackend:
    """MinIO / S3-совместимое хранилище."""

    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        secure: bool = False,
    ) -> None:
        self._client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )
        self._bucket = bucket
        self._endpoint = endpoint

    def ensure_bucket(self) -> None:
        if not self._client.bucket_exists(self._bucket):
            self._client.make_bucket(self._bucket)
            policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{self._bucket}/*"],
                }],
            }
            self._client.set_bucket_policy(self._bucket, json.dumps(policy))

    def upload(self, key: str, data: bytes, content_type: str = "image/jpeg") -> str:
        self.ensure_bucket()
        self._client.put_object(
            self._bucket,
            key,
            io.BytesIO(data),
            length=len(data),
            content_type=content_type,
        )
        return key

    def delete(self, key: str) -> None:
        try:
            self._client.remove_object(self._bucket, key)
        except S3Error:
            pass

    def get_url(self, key: str | None) -> str | None:
        if not key:
            return None
        return f"http://{self._endpoint}/{self._bucket}/{key}"
