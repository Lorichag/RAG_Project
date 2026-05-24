from minio import Minio
from minio.error import S3Error
from app.config import settings


class MinIOStore:
    def __init__(self):
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=False,
        )
        self.bucket = settings.minio_bucket

    def ensure_bucket(self) -> None:
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def upload_text(self, object_name: str, content: str) -> None:
        data = content.encode("utf-8")
        self.client.put_object(
            self.bucket,
            object_name,
            data,
            length=len(data),
            content_type="text/plain",
        )

    def download_text(self, object_name: str) -> str:
        obj = self.client.get_object(self.bucket, object_name)
        return obj.read().decode("utf-8")
