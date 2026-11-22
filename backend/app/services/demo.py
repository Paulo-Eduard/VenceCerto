"""Casos de uso da demonstração: ligam schemas da API às regras de app.domain (sem I/O)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.expiry import ExpiryThresholds, classify_lot, days_until_expiry
from app.domain.insights import MovingAverageForecaster, suggest_reorder
from app.domain.promotions import recommend_promotion
from app.domain.pvps import LotView, allocate_pvps


class ClassifyIn(BaseModel):
    expiry_date: date
    quantity_available: int = Field(ge=0)
    near_days: int = Field(default=30, ge=0)
    urgent_days: int = Field(default=7, ge=0)
    today: date | None = None


class LotIn(BaseModel):
    id: int
    expiry_date: date
    received_date: date
    quantity_available: int = Field(ge=0)


class PvpsIn(BaseModel):
    lots: list[LotIn]
    quantity: int = Field(gt=0)
    today: date | None = None


class PromoIn(BaseModel):
    cost_price: Decimal = Field(ge=0)
    sale_price: Decimal = Field(gt=0)
    days_left: int
    quantity: int
    allow_below_cost: bool = False


class ReorderIn(BaseModel):
    daily_sales: list[int]
    current_stock: int = Field(ge=0)
    lead_time_days: int = Field(ge=0)
    min_stock: int = Field(ge=0)
    max_stock: int = Field(ge=0)


def classify(data: ClassifyIn) -> dict:
    today = data.today or date.today()
    thresholds = ExpiryThresholds(data.near_days, data.urgent_days)
    status = classify_lot(data.expiry_date, data.quantity_available, today, thresholds)
    return {"status": status.value, "days_until_expiry": days_until_expiry(data.expiry_date, today)}


def pvps(data: PvpsIn) -> dict:
    today = data.today or date.today()
    lots = [LotView(x.id, x.expiry_date, x.received_date, x.quantity_available) for x in data.lots]
    allocations = allocate_pvps(lots, data.quantity, today)
    return {"allocations": [{"lot_id": a.lot_id, "quantity": a.quantity} for a in allocations]}


def promotion(data: PromoIn) -> dict:
    rec = recommend_promotion(
        data.cost_price, data.sale_price, data.days_left, data.quantity,
        allow_below_cost=data.allow_below_cost,
    )
    if rec is None:
        return {"recommended": False, "reason": "Sem promoção indicada para este lote."}
    return {
        "recommended": True,
        "discount_percent": str(rec.discount_percent),
        "promo_price": str(rec.promo_price),
        "margin_amount": str(rec.margin_amount),
        "margin_percent": str(rec.margin_percent),
        "requires_admin_approval": rec.requires_admin_approval,
        "reason": rec.reason,
    }


def reorder(data: ReorderIn) -> dict:
    s = suggest_reorder(
        MovingAverageForecaster(), data.daily_sales, data.current_stock,
        data.lead_time_days, data.min_stock, data.max_stock,
    )
    if s is None:
        return {"reorder": False, "reason": "Estoque acima do ponto de pedido."}
    return {
        "reorder": True,
        "daily_demand": s.daily_demand,
        "reorder_point": s.reorder_point,
        "suggested_quantity": s.suggested_quantity,
        "reason": s.reason,
    }
