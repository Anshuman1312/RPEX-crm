from __future__ import annotations

import hashlib
import uuid
import time
from io import BytesIO
from typing import Any
from urllib.parse import quote
from urllib.request import Request, urlopen

from app.core.config import get_settings


def _cloudinary_base_url(cloud_name: str) -> str:
    return f"https://res.cloudinary.com/{cloud_name}"


def _upload_api_url(cloud_name: str, resource_type: str) -> str:
    return f"https://api.cloudinary.com/v1_1/{cloud_name}/{resource_type}/upload"


def _sign_params(params: dict[str, Any], api_secret: str) -> str:
    signing_string = "&".join(f"{key}={value}" for key, value in sorted(params.items()) if value not in (None, ""))
    return hashlib.sha1(f"{signing_string}{api_secret}".encode("utf-8")).hexdigest()


def signed_delivery_url(public_id: str, resource_type: str = "image") -> str:
    settings = get_settings()
    cloud_name = getattr(settings, "cloudinary_cloud_name", "")
    if not cloud_name:
        return public_id

    safe_public_id = quote(str(public_id).lstrip("/"), safe="/")
    safe_resource_type = quote(resource_type or "image", safe="")
    return f"{_cloudinary_base_url(cloud_name)}/{safe_resource_type}/upload/{safe_public_id}"


def upload_bytes(
    file_bytes: bytes,
    public_id: str,
    folder: str = "rpex_documents",
    resource_type: str = "image",
) -> dict[str, Any]:
    settings = get_settings()
    cloud_name = getattr(settings, "cloudinary_cloud_name", "")
    api_key = getattr(settings, "cloudinary_api_key", "")
    api_secret = getattr(settings, "cloudinary_api_secret", "")

    if not (cloud_name and api_key and api_secret):
        raise RuntimeError("Cloudinary is not configured")

    timestamp = int(time.time())
    payload = {
        "folder": folder,
        "public_id": public_id,
        "timestamp": timestamp,
    }
    signature = _sign_params(payload, api_secret)

    boundary = uuid.uuid4().hex
    body = BytesIO()

    def write_field(name: str, value: str | int) -> None:
        body.write(f"--{boundary}\r\n".encode("utf-8"))
        body.write(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"))
        body.write(f"{value}\r\n".encode("utf-8"))

    for key, value in {
        **payload,
        "api_key": api_key,
        "signature": signature,
    }.items():
        write_field(key, value)

    body.write(f"--{boundary}\r\n".encode("utf-8"))
    body.write(
        f'Content-Disposition: form-data; name="file"; filename="{quote(public_id, safe="")}"\r\n'.encode("utf-8")
    )
    body.write(b"Content-Type: application/octet-stream\r\n\r\n")
    body.write(file_bytes)
    body.write(f"\r\n--{boundary}--\r\n".encode("utf-8"))

    request = Request(
        _upload_api_url(cloud_name, resource_type),
        data=body.getvalue(),
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )

    with urlopen(request, timeout=60) as response:
        response_body = response.read().decode("utf-8")

    import json

    return json.loads(response_body)
