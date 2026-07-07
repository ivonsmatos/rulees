import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import bad_request, conflict
from app.core.security import create_access_token, hash_password, verify_password
from app.modules.audit.service import write_audit_log
from app.modules.auth.models import Tenant, TenantMember, User
from app.modules.auth.schemas import AuthResponse, LoginRequest, RegisterRequest, TenantResponse
from app.modules.billing.service import get_or_create_billing_profile


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "tenant"


def _unique_slug(db: Session, base: str) -> str:
    slug = base
    index = 2
    while db.scalar(select(Tenant).where(Tenant.slug == slug)) is not None:
        slug = f"{base}-{index}"
        index += 1
    return slug


def register_user(db: Session, payload: RegisterRequest) -> AuthResponse:
    existing = db.scalar(select(User).where(User.email == payload.email.lower()))
    if existing:
        raise conflict("Email already registered")

    user = User(
        name=payload.name.strip(),
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
    )
    tenant = Tenant(
        name=payload.organization_name.strip(),
        slug=_unique_slug(db, _slugify(payload.organization_name)),
    )
    db.add_all([user, tenant])
    db.flush()
    membership = TenantMember(tenant_id=tenant.id, user_id=user.id, role="admin")
    db.add(membership)
    get_or_create_billing_profile(db, tenant_id=tenant.id)
    write_audit_log(
        db,
        tenant_id=tenant.id,
        user_id=user.id,
        action="auth.register",
        resource_type="tenant",
        resource_id=tenant.id,
    )
    db.commit()
    db.refresh(user)
    db.refresh(tenant)
    tenant_response = TenantResponse.model_validate(tenant)
    tenant_response.role = membership.role
    return AuthResponse(
        access_token=create_access_token(user.id),
        user=user,
        tenant=tenant_response,
    )


def login_user(db: Session, payload: LoginRequest) -> AuthResponse:
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise bad_request("Invalid email or password")
    membership = db.scalars(
        select(TenantMember).where(TenantMember.user_id == user.id).order_by(TenantMember.created_at.asc())
    ).first()
    if membership is None:
        raise bad_request("User has no tenant")
    tenant = db.get(Tenant, membership.tenant_id)
    tenant_response = TenantResponse.model_validate(tenant)
    tenant_response.role = membership.role
    return AuthResponse(
        access_token=create_access_token(user.id),
        user=user,
        tenant=tenant_response,
    )
