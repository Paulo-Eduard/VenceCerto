import pytest

from app.domain.insights import (
    InsufficientHistoryError,
    MovingAverageForecaster,
    suggest_reorder,
    waste_patterns,
)

F = MovingAverageForecaster()


def test_forecast_constant_demand():
    assert F.forecast_daily_demand([10] * 14) == pytest.approx(10)


def test_forecast_weights_recent_days():
    older = [2] * 7 + [10] * 7
    assert F.forecast_daily_demand(older) > 6  # acima da média simples (6.0)


def test_forecast_needs_history_and_rejects_negatives():
    with pytest.raises(InsufficientHistoryError):
        F.forecast_daily_demand([1, 2, 3])
    with pytest.raises(ValueError):
        F.forecast_daily_demand([1] * 7 + [-1])


def test_reorder_triggers_below_point():
    s = suggest_reorder(F, [10] * 14, current_stock=25, lead_time_days=2,
                        min_stock=5, max_stock=100)
    assert s is not None
    assert s.reorder_point == 40  # 10 * (2 + 2)
    assert s.suggested_quantity == 75


def test_reorder_none_when_stock_ok_or_full():
    assert suggest_reorder(F, [10] * 14, 80, 2, 5, 100) is None
    assert suggest_reorder(F, [0] * 14, 100, 2, 5, 100) is None


def test_reorder_respects_minimum_floor_and_validation():
    s = suggest_reorder(F, [0] * 14, 3, 1, min_stock=10, max_stock=50)
    assert s.reorder_point == 10
    with pytest.raises(ValueError):
        suggest_reorder(F, [1] * 14, 1, 1, min_stock=10, max_stock=5)


def test_fallback_forecaster_pluggable():
    class Fixed:
        def forecast_daily_demand(self, daily_sales):
            return 3.0

    s = suggest_reorder(Fixed(), [], 1, 1, 0, 20)
    assert s.daily_demand == 3.0


def test_waste_patterns_ranking():
    data = [("Laticínios", 30), ("Padaria", 50), ("Laticínios", 20), ("Hortifruti", 0)]
    r = waste_patterns(data)
    assert [x.key for x in r] == ["Laticínios", "Padaria"]  # empate em 50: ordem alfabética
    assert all(x.lost_units == 50 and x.share_percent == 50.0 for x in r)
    assert waste_patterns([]) == []
    with pytest.raises(ValueError):
        waste_patterns([("x", -1)])
