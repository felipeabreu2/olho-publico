from __future__ import annotations

from typing import BinaryIO

import boto3


def r2_endpoint_url(account_id: str) -> str:
    return f"https://{account_id}.r2.cloudflarestorage.com"


def make_r2_client(account_id: str, access_key: str, secret_key: str):
    """Cria cliente S3-compatible apontando para Cloudflare R2."""
    return boto3.client(
        service_name="s3",
        endpoint_url=r2_endpoint_url(account_id),
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
    )


def upload_bytes(
    client,
    bucket: str,
    key: str,
    data: bytes,
    content_type: str = "application/octet-stream",
) -> None:
    client.put_object(Bucket=bucket, Key=key, Body=data, ContentType=content_type)


def upload_fileobj(client, bucket: str, key: str, fileobj: BinaryIO) -> None:
    client.upload_fileobj(Fileobj=fileobj, Bucket=bucket, Key=key)


def download_bytes(client, bucket: str, key: str) -> bytes:
    resp = client.get_object(Bucket=bucket, Key=key)
    return resp["Body"].read()
