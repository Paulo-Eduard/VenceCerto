from datetime import date

import pytest

from app.services import demo

TODAY = date(2026, 11, 22)


def test_classify_service():
    out = demo.classify(demo.ClassifyIn(expiry_date=date(2026, 11, 27), quantity_available=5, today=TODAY))
    assert out == {"status": "vencimento_urgente", "days_until_expiry": 5}


def test_pvps_service_prefers_earliest_expiry():
    lots = [
        demo.LotIn(id=1, expiry_date=date(2026, 12, 20), received_date=TODAY, quantity_available=10),
        demo.LotIn(id=2, expiry_date=date(2026, 11, 28), received_date=TODAY, quantity_available=10),
    ]
    out = demo.pvps(demo.PvpsIn(lots=lots, quantity=12, today=TODAY))
    assert out["allocations"] == [{"lot_id": 2, "quantity": 10}, {"lot_id": 1, "quantity": 2}]


def test_promotion_service():
    out = demo.promotion(demo.PromoIn(cost_price="5.00", sale_price="10.00", days_left=5, quantity=20))
    assert out["recommended"] and out["promo_price"] == "6.50"
    assert demo.promotion(demo.PromoIn(cost_price="5", sale_price="10", days_left=90, quantity=1))["recommended"] is False


def test_reorder_service():
    out = demo.reorder(demo.ReorderIn(daily_sales=[10] * 8, current_stock=25, lead_time_days=2,
                                      min_stock=5, max_stock=100))
    assert out["reorder"] and out["reorder_point"] == 40 and out["suggested_quantity"] == 75


def test_validation_rejects_negative_quantity():
    with pytest.raises(ValueError):
        demo.ClassifyIn(expiry_date=TODAY, quantity_available=-1)
