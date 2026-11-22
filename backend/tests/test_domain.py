from datetime import date, timedelta
from decimal import Decimal

import pytest

from app.domain.expiry import ExpiryThresholds, LotStatus, classify_lot
from app.domain.promotions import recommend_promotion
from app.domain.pvps import (
    InsufficientStockError,
    LotView,
    allocate_pvps,
    eligible_lots,
)

TODAY = date(2026, 11, 22)


def d(n: int) -> date:
    return TODAY + timedelta(days=n)


# ---------- validade ----------
@pytest.mark.parametrize(
    ("days", "qty", "expected"),
    [
        (60, 10, LotStatus.OK),
        (31, 10, LotStatus.OK),
        (30, 10, LotStatus.NEAR),
        (8, 10, LotStatus.NEAR),
        (7, 10, LotStatus.URGENT),
        (0, 10, LotStatus.URGENT),
        (-1, 10, LotStatus.EXPIRED),
        (60, 0, LotStatus.DEPLETED),
        (-5, 0, LotStatus.DEPLETED),
    ],
)
def test_classify(days, qty, expected):
    assert classify_lot(d(days), qty, TODAY) == expected


def test_classify_custom_thresholds():
    t = ExpiryThresholds(near_days=10, urgent_days=2)
    assert classify_lot(d(10), 1, TODAY, t) == LotStatus.NEAR
    assert classify_lot(d(2), 1, TODAY, t) == LotStatus.URGENT
    assert classify_lot(d(11), 1, TODAY, t) == LotStatus.OK


def test_invalid_inputs():
    with pytest.raises(ValueError):
        classify_lot(d(5), -1, TODAY)
    with pytest.raises(ValueError):
        ExpiryThresholds(near_days=3, urgent_days=5)


# ---------- PVPS ----------
def lot(i, exp, qty, rec=-10):
    return LotView(i, d(exp), d(rec), qty)


def test_pvps_orders_by_expiry_and_splits():
    lots = [lot(1, 30, 10), lot(2, 5, 4), lot(3, 15, 10)]
    alloc = allocate_pvps(lots, 8, TODAY)
    assert [(a.lot_id, a.quantity) for a in alloc] == [(2, 4), (3, 4)]


def test_pvps_skips_expired_and_empty():
    lots = [lot(1, -2, 50), lot(2, 10, 0), lot(3, 20, 5)]
    assert [x.id for x in eligible_lots(lots, TODAY)] == [3]
    with pytest.raises(InsufficientStockError) as exc:
        allocate_pvps(lots, 6, TODAY)
    assert exc.value.available == 5


def test_pvps_lot_expiring_today_is_valid():
    assert allocate_pvps([lot(1, 0, 3)], 3, TODAY)[0].lot_id == 1


def test_pvps_tie_breaks_by_received_then_id():
    lots = [lot(2, 10, 5, rec=-1), lot(1, 10, 5, rec=-20)]
    assert allocate_pvps(lots, 1, TODAY)[0].lot_id == 1


@pytest.mark.parametrize("q", [0, -3])
def test_pvps_rejects_non_positive(q):
    with pytest.raises(ValueError):
        allocate_pvps([lot(1, 5, 5)], q, TODAY)


def test_pvps_never_exceeds_lot_balance():
    lots = [lot(1, 5, 3), lot(2, 9, 3)]
    alloc = allocate_pvps(lots, 6, TODAY)
    assert sum(a.quantity for a in alloc) == 6
    assert all(a.quantity <= 3 for a in alloc)


# ---------- promoções ----------
def test_promo_tiers_and_margin():
    r = recommend_promotion(Decimal("5.00"), Decimal("10.00"), 5, 20)
    assert r is not None
    assert r.discount_percent == Decimal("35")
    assert r.promo_price == Decimal("6.50")
    assert r.margin_amount == Decimal("1.50")
    assert not r.below_cost and not r.requires_admin_approval
    assert "5 dia(s)" in r.reason


def test_promo_none_when_far_expired_or_empty():
    assert recommend_promotion(Decimal("5"), Decimal("10"), 90, 5) is None
    assert recommend_promotion(Decimal("5"), Decimal("10"), -1, 5) is None
    assert recommend_promotion(Decimal("5"), Decimal("10"), 2, 0) is None


def test_promo_capped_at_cost_without_authorization():
    r = recommend_promotion(Decimal("8.00"), Decimal("10.00"), 1, 5)  # 50% -> 5.00 < custo
    assert r.promo_price == Decimal("8.00")
    assert r.margin_amount == Decimal("0.00")
    assert not r.below_cost and not r.requires_admin_approval


def test_promo_below_cost_needs_admin_when_allowed():
    r = recommend_promotion(Decimal("8.00"), Decimal("10.00"), 1, 5, allow_below_cost=True)
    assert r.promo_price == Decimal("5.00")
    assert r.below_cost and r.requires_admin_approval


def test_promo_rejects_bad_prices():
    with pytest.raises(ValueError):
        recommend_promotion(Decimal("1"), Decimal("0"), 3, 1)
