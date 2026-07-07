from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import RequestContext, get_request_context
from app.modules.billing.schemas import BillingStatusResponse
from app.modules.billing.service import billing_status
from app.modules.permissions.service import require_permission

router = APIRouter()


@router.get("/billing/status", response_model=BillingStatusResponse)
def status(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> dict:
    require_permission(context, "billing.view")
    return billing_status(db, tenant_id=context.tenant_id)
