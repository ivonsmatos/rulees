from pydantic import BaseModel


class BillingLimitItem(BaseModel):
    event_type: str
    used: float
    limit: float
    remaining: float


class BillingCostItem(BaseModel):
    event_type: str
    quantity: float
    unit_cost_usd: float
    estimated_cost_usd: float


class BillingStatusResponse(BaseModel):
    tenant_id: str
    plan_name: str
    status: str
    limits: list[BillingLimitItem]
    estimated_costs: list[BillingCostItem] = []
