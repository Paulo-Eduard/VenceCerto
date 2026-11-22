"""PVPS — Primeiro que Vence, Primeiro que Sai (regra pura).

A persistência e o bloqueio de concorrência (SELECT ... FOR UPDATE) ficam na
camada de serviço; aqui só se decide *de quais lotes* e *quanto* baixar.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


class InsufficientStockError(Exception):
    def __init__(self, requested: int, available: int) -> None:
        super().__init__(f"Estoque insuficiente: pedido={requested}, disponível={available}")
        self.requested = requested
        self.available = available


@dataclass(frozen=True)
class LotView:
    id: int
    expiry_date: date
    received_date: date
    quantity_available: int


@dataclass(frozen=True)
class Allocation:
    lot_id: int
    quantity: int


def eligible_lots(lots: list[LotView], today: date) -> list[LotView]:
    """Somente lotes não vencidos e com saldo, ordenados por validade crescente."""
    valid = [x for x in lots if x.quantity_available > 0 and x.expiry_date >= today]
    return sorted(valid, key=lambda x: (x.expiry_date, x.received_date, x.id))


def allocate_pvps(lots: list[LotView], quantity: int, today: date) -> list[Allocation]:
    if quantity <= 0:
        raise ValueError("Quantidade deve ser positiva")
    candidates = eligible_lots(lots, today)
    total = sum(x.quantity_available for x in candidates)
    if total < quantity:
        raise InsufficientStockError(quantity, total)

    remaining = quantity
    result: list[Allocation] = []
    for lot in candidates:
        if remaining == 0:
            break
        take = min(lot.quantity_available, remaining)
        result.append(Allocation(lot.id, take))
        remaining -= take
    return result
