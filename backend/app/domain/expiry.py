"""Classificação de lotes por validade (regra pura, sem I/O)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class LotStatus(StrEnum):
    OK = "dentro_da_validade"
    NEAR = "proximo_do_vencimento"
    URGENT = "vencimento_urgente"
    EXPIRED = "vencido"
    DEPLETED = "esgotado"


@dataclass(frozen=True)
class ExpiryThresholds:
    """Prazos em dias, configuráveis por estabelecimento/categoria."""

    near_days: int = 30
    urgent_days: int = 7

    def __post_init__(self) -> None:
        if self.urgent_days < 0 or self.near_days < self.urgent_days:
            raise ValueError("Esperado 0 <= urgent_days <= near_days")


def days_until_expiry(expiry_date: date, today: date) -> int:
    return (expiry_date - today).days


def classify_lot(
    expiry_date: date,
    quantity_available: int,
    today: date,
    thresholds: ExpiryThresholds = ExpiryThresholds(),
) -> LotStatus:
    if quantity_available < 0:
        raise ValueError("Quantidade disponível não pode ser negativa")
    if quantity_available == 0:
        return LotStatus.DEPLETED
    days = days_until_expiry(expiry_date, today)
    if days < 0:
        return LotStatus.EXPIRED
    if days <= thresholds.urgent_days:
        return LotStatus.URGENT
    if days <= thresholds.near_days:
        return LotStatus.NEAR
    return LotStatus.OK
