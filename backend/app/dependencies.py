from dataclasses import dataclass

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import forbidden, unauthorized
from app.core.security import decode_access_token
from app.db.session import get_db
from app.modules.auth.models import Tenant, TenantMember, User

bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class RequestContext:
    user: User
    tenant: Tenant
    role: str

    @property
    def user_id(self) -> str:
        return self.user.id

    @property
    def tenant_id(self) -> str:
        return self.tenant.id


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise unauthorized()
    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError:
        raise unauthorized("Invalid token")
    user = db.get(User, payload.get("sub"))
    if user is None or not user.is_active:
        raise unauthorized("Invalid user")
    return user


def get_request_context(
    x_tenant_id: str | None = Header(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RequestContext:
    query = select(TenantMember).where(TenantMember.user_id == user.id)
    if x_tenant_id:
        query = query.where(TenantMember.tenant_id == x_tenant_id)
    membership = db.scalars(query.order_by(TenantMember.created_at.asc())).first()
    if membership is None:
        raise forbidden("User has no access to the requested tenant")
    tenant = db.get(Tenant, membership.tenant_id)
    if tenant is None:
        raise forbidden("Tenant not available")
    return RequestContext(user=user, tenant=tenant, role=membership.role)
