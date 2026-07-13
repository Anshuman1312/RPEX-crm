from pydantic import BaseModel, Field

from app.schemas.common import TimestampSchema


class WebsiteCreate(BaseModel):
    name: str = Field(min_length=2, max_length=128)
    domain: str
    status: bool = True


class WebsiteOut(TimestampSchema):
    name: str
    domain: str
    status: bool
