from minio import Minio
from minio.error import S3Error
from settings import settings
import io

client = Minio(
    settings.minio_endpoint,
    access_key=settings.minio_access_key,
    secret_key=settings.minio_secret_key,
    secure=False,
)

def ensure_bucket():
    if not client.bucket_exists(settings.minio_bucket):
        client.make_bucket(settings.minio_bucket)
        # Public read policy
        import json
        policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{settings.minio_bucket}/*"]
            }]
        }
        client.set_bucket_policy(settings.minio_bucket, json.dumps(policy))

def upload_image(key: str, data: bytes, content_type: str = "image/jpeg") -> str:
    ensure_bucket()
    client.put_object(
        settings.minio_bucket,
        key,
        io.BytesIO(data),
        length=len(data),
        content_type=content_type,
    )
    return key

def delete_image(key: str):
    try:
        client.remove_object(settings.minio_bucket, key)
    except S3Error:
        pass

def get_image_url(key: str | None) -> str | None:
    if not key:
        return None
    # Public URL (MinIO отдаёт напрямую)
    return f"http://localhost:9000/{settings.minio_bucket}/{key}"
