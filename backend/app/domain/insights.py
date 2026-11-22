"""Insights de estoque — base estatística determinística, sem serviço externo.

Arquitetura: o núcleo depende apenas do protocolo `DemandForecaster`. A implementação
padrão (`MovingAverageForecaster`) roda localmente. Um provedor de IA/ML pode ser plugado
depois implementando o mesmo protocolo; se estiver desligado ou falhar, o sistema usa o padrão.
"""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol


class DemandForecaster(Protocol):
    def forecast_daily_demand(self, daily_sales: Sequence[int]) -> float:
        """Demanda diária esperada, a partir do histórico (mais antigo -> mais recente)."""
        ...


@dataclass(frozen=True)
class MovingAverageForecaster:
    """Média móvel ponderada: dias recentes pesam mais. Exige histórico mínimo."""

    window: int = 14
    min_history: int = 7

    def forecast_daily_demand(self, daily_sales: Sequence[int]) -> float:
        if any(x < 0 for x in daily_sales):
            raise ValueError("Vendas diárias não podem ser negativas")
        if len(daily_sales) < self.min_history:
            raise InsufficientHistoryError(len(daily_sales), self.min_history)
        recent = list(daily_sales)[-self.window :]
        weights = range(1, len(recent) + 1)
        return sum(v * w for v, w in zip(recent, weights, strict=True)) / sum(weights)


class InsufficientHistoryError(Exception):
    def __init__(self, have: int, need: int) -> None:
        super().__init__(f"Histórico insuficiente: {have} dia(s), mínimo {need}")


@dataclass(frozen=True)
class ReorderSuggestion:
    daily_demand: float
    reorder_point: int
    suggested_quantity: int
    reason: str


def suggest_reorder(
    forecaster: DemandForecaster,
    daily_sales: Sequence[int],
    current_stock: int,
    lead_time_days: int,
    min_stock: int,
    max_stock: int,
    safety_days: int = 2,
) -> ReorderSuggestion | None:
    """Sugere reposição quando o estoque cai abaixo do ponto de pedido.

    ponto de pedido = demanda * (prazo de entrega + dias de segurança), nunca abaixo do mínimo.
    Quantidade = o que falta para chegar ao estoque máximo. Não cria pedidos sozinha.
    """
    if min(current_stock, lead_time_days, min_stock, safety_days) < 0 or max_stock < min_stock:
        raise ValueError("Parâmetros de estoque inválidos")
    demand = forecaster.forecast_daily_demand(daily_sales)
    point = max(min_stock, math.ceil(demand * (lead_time_days + safety_days)))
    if current_stock > point:
        return None
    qty = max(0, max_stock - current_stock)
    if qty == 0:
        return None
    reason = (
        f"Estoque {current_stock} <= ponto de pedido {point} "
        f"(demanda ~{demand:.1f}/dia, prazo {lead_time_days} d)."
    )
    return ReorderSuggestion(round(demand, 2), point, qty, reason)


@dataclass(frozen=True)
class WastePattern:
    key: str
    lost_units: int
    share_percent: float


def waste_patterns(losses: Sequence[tuple[str, int]], top: int = 5) -> list[WastePattern]:
    """Agrupa perdas por chave (categoria, fornecedor ou motivo) e ordena pelas maiores."""
    totals: dict[str, int] = defaultdict(int)
    for key, qty in losses:
        if qty < 0:
            raise ValueError("Quantidade perdida não pode ser negativa")
        totals[key] += qty
    grand = sum(totals.values())
    if grand == 0:
        return []
    ranked = sorted(((k, v) for k, v in totals.items() if v > 0), key=lambda kv: (-kv[1], kv[0]))[:top]
    return [WastePattern(k, v, round(100 * v / grand, 1)) for k, v in ranked]
