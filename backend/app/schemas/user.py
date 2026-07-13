from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import TimestampSchema


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=128)
    email: EmailStr
    password: str = Field(min_length=8)
    role_name: str


class UserOut(TimestampSchema):
    name: str
    email: EmailStr
    role_id: str
    is_active: bool
