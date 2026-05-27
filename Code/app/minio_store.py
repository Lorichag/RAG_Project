import json
from typing import List
import boto3
import structlog
from botocore.exceptions import BotoCoreError, ClientError
from app.config import settings

logger = structlog.get_logger()


class MinIOStore:
    RAW_PREFIX = "raw/"
    PROCESSED_PREFIX = "processed/"
    EMBEDDINGS_PREFIX = "embeddings/"

    def __init__(self):
        endpoint = settings.minio_endpoint
        if not endpoint.startswith("http"):
            endpoint = f"http://{endpoint}"

        self.bucket = settings.minio_bucket
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=settings.minio_access_key,
            aws_secret_access_key=settings.minio_secret_key,
            region_name="us-east-1",
        )

    def ensure_bucket(self) -> None:
        try:
            self.client.head_bucket(Bucket=self.bucket)
            logger.info("MinIO bucket exists", bucket=self.bucket)
        except ClientError:
            logger.info("Creating MinIO bucket", bucket=self.bucket)
            self.client.create_bucket(Bucket=self.bucket)

    def upload_document(self, local_path: str, object_name: str) -> str:
        self.ensure_bucket()
        key = f"{self.RAW_PREFIX}{object_name}"
        logger.info("Uploading document to MinIO", bucket=self.bucket, key=key)
        with open(local_path, "rb") as file_data:
            self.client.put_object(Bucket=self.bucket, Key=key, Body=file_data)
        return f"s3://{self.bucket}/{key}"

    def download_document(self, object_name: str) -> bytes:
        key = object_name if object_name.startswith(self.RAW_PREFIX) or object_name.startswith(self.PROCESSED_PREFIX) else f"{self.RAW_PREFIX}{object_name}"
        logger.info("Downloading document from MinIO", bucket=self.bucket, key=key)
        obj = self.client.get_object(Bucket=self.bucket, Key=key)
        return obj["Body"].read()

    def list_raw_documents(self) -> List[str]:
        self.ensure_bucket()
        paginator = self.client.get_paginator("list_objects_v2")
        page_iterator = paginator.paginate(Bucket=self.bucket, Prefix=self.RAW_PREFIX)
        keys: List[str] = []
        for page in page_iterator:
            for obj in page.get("Contents", []):
                key = obj["Key"]
                if key.endswith("/"):
                    continue
                keys.append(key[len(self.RAW_PREFIX) :])
        logger.info("Listed raw documents", bucket=self.bucket, count=len(keys))
        return keys

    def mark_processed(self, object_name: str) -> bool:
        raw_key = object_name if object_name.startswith(self.RAW_PREFIX) else f"{self.RAW_PREFIX}{object_name}"
        processed_key = raw_key.replace(self.RAW_PREFIX, self.PROCESSED_PREFIX, 1)
        logger.info("Marking document processed", bucket=self.bucket, raw_key=raw_key, processed_key=processed_key)
        try:
            copy_source = {"Bucket": self.bucket, "Key": raw_key}
            self.client.copy_object(Bucket=self.bucket, CopySource=copy_source, Key=processed_key)
            self.client.delete_object(Bucket=self.bucket, Key=raw_key)
            return True
        except (ClientError, BotoCoreError) as exc:
            logger.error("Failed to mark document processed", error=str(exc), raw_key=raw_key)
            return False

    def upload_metadata(self, object_name: str, metadata: dict) -> bool:
        key = object_name if object_name.startswith(self.EMBEDDINGS_PREFIX) else f"{self.EMBEDDINGS_PREFIX}{object_name}.json"
        logger.info("Uploading metadata to MinIO", bucket=self.bucket, key=key)
        try:
            self.client.put_object(Bucket=self.bucket, Key=key, Body=json.dumps(metadata).encode("utf-8"), ContentType="application/json")
            return True
        except (ClientError, BotoCoreError) as exc:
            logger.error("Failed to upload metadata", error=str(exc), key=key)
            return False

    def document_exists(self, object_name: str) -> bool:
        key = object_name if object_name.startswith(self.RAW_PREFIX) else f"{self.RAW_PREFIX}{object_name}"
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError:
            return False
