import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

from app.core.config import get_settings

settings = get_settings()


def configure_cloudinary() -> None:
    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )


def upload_bytes(file_bytes: bytes, public_id: str, folder: str, resource_type: str = "auto") -> dict:
    configure_cloudinary()
    return cloudinary.uploader.upload(
        file_bytes,
        public_id=public_id,
        folder=folder,
        resource_type=resource_type,
        overwrite=False,
    )


def signed_delivery_url(storage_key: str, resource_type: str = "image") -> str:
    configure_cloudinary()
    url, _ = cloudinary_url(
        storage_key,
        secure=True,
        sign_url=True,
        resource_type=resource_type,
        type="upload",
    )
    return url
