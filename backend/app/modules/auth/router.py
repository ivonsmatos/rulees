from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import RequestContext, get_current_user, get_request_context
from app.core.errors import bad_request, conflict, forbidden, not_found
from app.modules.audit.service import write_audit_log
from app.modules.auth.models import Tenant, TenantInvite, TenantMember, User
from app.modules.auth.schemas import (
    AuthResponse,
    LoginRequest,
    MeResponse,
    RegisterRequest,
    TenantAccessResponse,
    TenantInviteCreate,
    TenantInviteResponse,
    TenantMemberResponse,
    TenantMemberUpdate,
    TenantResponse,
    UserResponse,
)
from app.modules.auth.service import login_user, register_user
from app.modules.permissions.service import require_permission

router = APIRouter()


@router.post("/register", response_model=AuthResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    return register_user(db, payload)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    return login_user(db, payload)


@router.get("/me", response_model=MeResponse)
def me(context: RequestContext = Depends(get_request_context)) -> MeResponse:
    tenant = TenantResponse.model_validate(context.tenant)
    tenant.role = context.role
    return MeResponse(user=context.user, tenant=tenant)


@router.get("/tenants", response_model=list[TenantAccessResponse])
def list_user_tenants(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TenantAccessResponse]:
    memberships = list(
        db.scalars(
            select(TenantMember)
            .where(TenantMember.user_id == user.id)
            .order_by(TenantMember.created_at.asc())
        )
    )
    responses: list[TenantAccessResponse] = []
    for membership in memberships:
        tenant = db.get(Tenant, membership.tenant_id)
        if tenant is None:
            continue
        tenant_response = TenantResponse.model_validate(tenant)
        tenant_response.role = membership.role
        responses.append(
            TenantAccessResponse(
                id=membership.id,
                user_id=membership.user_id,
                role=membership.role,
                created_at=membership.created_at,
                tenant=tenant_response,
            )
        )
    return responses


@router.get("/tenant/members", response_model=list[TenantMemberResponse])
def list_tenant_members(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[TenantMemberResponse]:
    require_permission(context, "tenant.member.view")
    memberships = list(
        db.scalars(
            select(TenantMember)
            .where(TenantMember.tenant_id == context.tenant_id)
            .order_by(TenantMember.created_at.asc())
        )
    )
    responses: list[TenantMemberResponse] = []
    for membership in memberships:
        response = TenantMemberResponse.model_validate(membership)
        user = db.get(User, membership.user_id)
        response.user = UserResponse.model_validate(user) if user else None
        responses.append(response)
    return responses


@router.patch("/tenant/members/{member_id}", response_model=TenantMemberResponse)
def update_tenant_member(
    member_id: str,
    payload: TenantMemberUpdate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> TenantMemberResponse:
    require_permission(context, "tenant.member.manage")
    membership = db.get(TenantMember, member_id)
    if membership is None or membership.tenant_id != context.tenant_id:
        raise not_found("Tenant member not found")
    if payload.role == "admin" and context.role != "admin":
        raise forbidden("Only admins can assign admin role")
    if membership.role == "admin" and payload.role != "admin":
        admin_count = db.scalar(
            select(func.count(TenantMember.id)).where(
                TenantMember.tenant_id == context.tenant_id,
                TenantMember.role == "admin",
            )
        )
        if admin_count is not None and admin_count <= 1:
            raise bad_request("Tenant must keep at least one admin")
    membership.role = payload.role
    db.flush()
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="tenant.member.update",
        resource_type="tenant_member",
        resource_id=membership.id,
        details={"member_user_id": membership.user_id, "role": membership.role},
    )
    db.commit()
    db.refresh(membership)
    response = TenantMemberResponse.model_validate(membership)
    user = db.get(User, membership.user_id)
    response.user = UserResponse.model_validate(user) if user else None
    return response


@router.get("/tenant/invites", response_model=list[TenantInviteResponse])
def list_tenant_invites(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[TenantInvite]:
    require_permission(context, "tenant.invite.view")
    return list(
        db.scalars(
            select(TenantInvite)
            .where(TenantInvite.tenant_id == context.tenant_id)
            .order_by(TenantInvite.created_at.desc())
        )
    )


@router.get("/invites/pending", response_model=list[TenantInviteResponse])
def list_pending_invites(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TenantInviteResponse]:
    invites = list(
        db.scalars(
            select(TenantInvite)
            .where(TenantInvite.email == user.email, TenantInvite.status == "pending")
            .order_by(TenantInvite.created_at.desc())
        )
    )
    responses: list[TenantInviteResponse] = []
    for invite in invites:
        response = TenantInviteResponse.model_validate(invite)
        tenant = db.get(Tenant, invite.tenant_id)
        if tenant:
            tenant_response = TenantResponse.model_validate(tenant)
            tenant_response.role = invite.role
            response.tenant = tenant_response
        responses.append(response)
    return responses


@router.post("/tenant/invites", response_model=TenantInviteResponse)
def create_tenant_invite(
    payload: TenantInviteCreate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> TenantInvite:
    require_permission(context, "tenant.invite.create")
    if payload.role == "admin" and context.role != "admin":
        raise forbidden("Only admins can assign admin role")
    email = payload.email.lower()
    existing_member = (
        db.query(TenantMember)
        .join(User, TenantMember.user_id == User.id)
        .filter(TenantMember.tenant_id == context.tenant_id, User.email == email)
        .first()
    )
    if existing_member:
        raise conflict("User is already a tenant member")
    invite = db.scalar(
        select(TenantInvite).where(
            TenantInvite.tenant_id == context.tenant_id,
            TenantInvite.email == email,
        )
    )
    if invite and invite.status == "pending":
        raise conflict("Invite already pending")
    if invite is None:
        invite = TenantInvite(
            tenant_id=context.tenant_id,
            email=email,
            role=payload.role,
            invited_by=context.user_id,
        )
        db.add(invite)
    else:
        invite.role = payload.role
        invite.status = "pending"
        invite.invited_by = context.user_id
        invite.accepted_by = None
        invite.accepted_at = None
    db.flush()
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="tenant.invite.create",
        resource_type="tenant_invite",
        resource_id=invite.id,
        details={"email": invite.email, "role": invite.role},
    )
    db.commit()
    db.refresh(invite)
    return invite


@router.post("/tenant/invites/{invite_id}/accept", response_model=TenantMemberResponse)
def accept_tenant_invite(
    invite_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TenantMemberResponse:
    invite = db.get(TenantInvite, invite_id)
    if invite is None:
        raise not_found("Invite not found")
    if invite.status != "pending":
        raise bad_request("Invite is not pending")
    if invite.email != user.email:
        raise not_found("Invite not found")
    membership = db.scalar(
        select(TenantMember).where(
            TenantMember.tenant_id == invite.tenant_id,
            TenantMember.user_id == user.id,
        )
    )
    if membership is None:
        membership = TenantMember(
            tenant_id=invite.tenant_id,
            user_id=user.id,
            role=invite.role,
        )
        db.add(membership)
    else:
        membership.role = invite.role
    invite.status = "accepted"
    invite.accepted_by = user.id
    invite.accepted_at = datetime.now(timezone.utc)
    db.flush()
    write_audit_log(
        db,
        tenant_id=invite.tenant_id,
        user_id=user.id,
        action="tenant.invite.accept",
        resource_type="tenant_invite",
        resource_id=invite.id,
    )
    db.commit()
    db.refresh(membership)
    response = TenantMemberResponse.model_validate(membership)
    response.user = UserResponse.model_validate(user)
    return response
