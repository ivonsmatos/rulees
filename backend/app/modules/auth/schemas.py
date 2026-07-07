from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    organization_name: str = Field(min_length=2, max_length=160)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TenantResponse(BaseModel):
    id: str
    name: str
    slug: str
    role: str = "admin"

    model_config = ConfigDict(from_attributes=True)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    tenant: TenantResponse


class MeResponse(BaseModel):
    user: UserResponse
    tenant: TenantResponse


class TenantAccessResponse(BaseModel):
    id: str
    user_id: str
    role: str
    created_at: datetime
    tenant: TenantResponse


class TenantMemberResponse(BaseModel):
    id: str
    tenant_id: str
    user_id: str
    role: str
    created_at: datetime
    user: UserResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class TenantInviteCreate(BaseModel):
    email: EmailStr
    role: str = Field(default="member", pattern="^(admin|manager|member|viewer)$")


class TenantMemberUpdate(BaseModel):
    role: str = Field(pattern="^(admin|manager|member|viewer)$")


class TenantInviteResponse(BaseModel):
    id: str
    tenant_id: str
    email: EmailStr
    role: str
    status: str
    invited_by: str
    accepted_by: str | None
    accepted_at: datetime | None
    created_at: datetime
    tenant: TenantResponse | None = None

    model_config = ConfigDict(from_attributes=True)
