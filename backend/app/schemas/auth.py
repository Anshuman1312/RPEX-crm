from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=128)
    email: EmailStr
    password: str = Field(min_length=8)
    role_name: str = Field(default="SALES")


class RegisterResponse(BaseModel):
    user_id: str
    email: EmailStr
    role: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str | None = None


class LogoutRequest(BaseModel):
    refresh_token: str
