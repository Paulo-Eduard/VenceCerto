"""Recomendação explicável de promoções. Nunca altera preços sozinha."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")

# (dias restantes <=, desconto %) — do mais urgente ao menos urgente
DEFAULT_TIERS: tuple[tuple[int, Decimal], ...] = (
    (3, Decimal(50)),
    (7, Decimal(35)),
    (15, Decimal(20)),
    (30, Decimal(10)),
)


@dataclass(frozen=True)
class Recommendation:
    discount_percent: Decimal
    promo_price: Decimal
    margin_amount: Decimal
    margin_percent: Decimal
    below_cost: bool
    requires_admin_approval: bool
    reason: str


def _money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def recommend_promotion(
    cost_price: Decimal,
    sale_price: Decimal,
    days_left: int,
    quantity: int,
    tiers: tuple[tuple[int, Decimal], ...] = DEFAULT_TIERS,
    allow_below_cost: bool = False,
) -> Recommendation | None:
    """Retorna None se o lote não deve entrar em promoção."""
    if cost_price < 0 or sale_price <= 0:
        raise ValueError("Preços inválidos")
    if quantity <= 0 or days_left < 0:
        return None  # esgotado ou vencido: não se promove

    discount = next((pct for limit, pct in sorted(tiers) if days_left <= limit), None)
    if discount is None:
        return None

    raw_price = _money(sale_price * (Decimal(100) - discount) / Decimal(100))
    below_cost = raw_price < cost_price
    reason = f"Faltam {days_left} dia(s) para vencer; {quantity} un. em estoque; faixa de {discount}% de desconto."

    if below_cost and not allow_below_cost:
        promo = _money(cost_price)
        effective = (Decimal(100) * (sale_price - promo) / sale_price).quantize(CENT)
        reason += " Desconto limitado ao preço de custo (sem prejuízo)."
        return _build(cost_price, promo, effective, False, False, reason)

    if below_cost:
        reason += " Preço abaixo do custo: exige autorização de administrador."
    return _build(cost_price, raw_price, discount, below_cost, below_cost, reason)


def _build(
    cost: Decimal,
    promo: Decimal,
    discount: Decimal,
    below_cost: bool,
    needs_admin: bool,
    reason: str,
) -> Recommendation:
    margin = _money(promo - cost)
    margin_pct = _money(margin / promo * 100) if promo > 0 else Decimal("0.00")
    return Recommendation(discount, promo, margin, margin_pct, below_cost, needs_admin, reason)
