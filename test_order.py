import pytest

from order import Order, OrderStatus


def test_apply_fill_updates_filled_quantity():
    order = Order("MSFT", "buy", 100)
    order.apply_fill(40, 10)
    assert order.filled_quantity == 40
    assert order.status == OrderStatus.PARTIALLY_FILLED


def test_apply_fill_raises_error_if_fill_exceeds_quantity():
    order = Order("MSFT", "buy", 100)
    order.apply_fill(40, 11)
    order.apply_fill(40, 12)
    with pytest.raises(ValueError, match="exceeds"):
        order.apply_fill(30, 13)
    assert order.filled_quantity == 80
    assert order.status == OrderStatus.PARTIALLY_FILLED
    assert len(order.fills) == 2


def test_apply_fill_updates_status_to_fully_filled_if_fill_equals_quantity():
    order = Order("MSFT", "buy", 100)
    order.apply_fill(30, 14)
    order.apply_fill(30, 15)
    order.apply_fill(40, 16)
    assert order.filled_quantity == 100
    assert order.status == OrderStatus.FULLY_FILLED


def test_rejects_zero_or_negative_fill_quantity():
    order = Order("MSFT", "buy", 100)
    with pytest.raises(ValueError, match="0 or negative"):
        order.apply_fill(0, 17)
    with pytest.raises(ValueError, match="0 or negative"):
        order.apply_fill(-1, 18)
    assert order.filled_quantity == 0
    assert order.status == OrderStatus.NEW


def test_rejects_zero_or_negative_fill_price():
    order = Order("TSLA", "sell", 100)
    with pytest.raises(ValueError, match="0 or negative"):
        order.apply_fill(50, 0)
    with pytest.raises(ValueError, match="0 or negative"):
        order.apply_fill(50, -1)
    assert order.filled_quantity == 0
    assert order.status == "new"


def test_calculates_volume_weighted_average_price_of_fills():
    order = Order("MSFT", "buy", 100)
    order.apply_fill(30, 14)
    order.apply_fill(30, 15)
    order.apply_fill(40, 16)
    assert order.calculate_volume_weighted_average_price() == pytest.approx(15.1)


def test_volume_weighted_average_price_is_none_if_no_fills():
    order = Order("MSFT", "buy", 100)
    assert order.calculate_volume_weighted_average_price() is None


def test_cancel_new_order_sets_status_to_cancelled():
    order = Order("MSFT", "buy", 100)
    order.cancel()
    assert order.status == OrderStatus.CANCELLED


def test_cancel_partially_filled_order_sets_status_to_cancelled():
    order = Order("MSFT", "buy", 100)
    order.apply_fill(30, 14)
    order.cancel()
    assert order.status == OrderStatus.CANCELLED
    assert order.filled_quantity == 30


def test_fully_filled_order_cannot_be_cancelled():
    order = Order("MSFT", "buy", 100)
    order.apply_fill(100, 14)
    with pytest.raises(ValueError, match="Cannot cancel"):
        order.cancel()
    assert order.status == OrderStatus.FULLY_FILLED
    assert order.filled_quantity == 100


def test_cancelled_order_cannot_be_cancelled():
    order = Order("MSFT", "buy", 100)
    order.cancel()
    assert order.status == OrderStatus.CANCELLED
    with pytest.raises(ValueError, match="Cannot cancel"):
        order.cancel()


def test_cancelled_order_cannot_accept_fills():
    order = Order("MSFT", "buy", 100)
    order.cancel()
    assert order.status == OrderStatus.CANCELLED
    with pytest.raises(ValueError, match="Cannot apply fill"):
        order.apply_fill(50, 21)
    assert order.filled_quantity == 0
    assert order.status == OrderStatus.CANCELLED
    assert len(order.fills) == 0


def test_fully_filled_order_cannot_accept_fills():
    order = Order("MSFT", "buy", 100)
    order.apply_fill(100, 20)
    assert order.status == OrderStatus.FULLY_FILLED
    with pytest.raises(ValueError, match="Cannot apply fill"):
        order.apply_fill(50, 21)
    assert order.filled_quantity == 100
    assert order.status == OrderStatus.FULLY_FILLED
    assert len(order.fills) == 1


def test_rejected_order_cannot_be_cancelled():
    order = Order("MSFT", "sell", 100)
    order.reject()
    with pytest.raises(ValueError, match="Cannot cancel"):
        order.cancel()
    assert order.status == OrderStatus.REJECTED


def test_new_order_reject_sets_status_to_rejected():
    order = Order("MSFT", "buy", 100)
    assert order.status == OrderStatus.NEW
    order.reject()
    assert order.status == OrderStatus.REJECTED


def test_partially_filled_or_fully_filled_order_cannot_be_rejected():
    order = Order("MSFT", "buy", 100)
    order.apply_fill(50, 22)
    with pytest.raises(ValueError, match="Cannot reject"):
        order.reject()
    assert order.status == OrderStatus.PARTIALLY_FILLED
    order.apply_fill(50, 23)
    with pytest.raises(ValueError, match="Cannot reject"):
        order.reject()
    assert order.status == OrderStatus.FULLY_FILLED


def test_cancelled_order_cannot_be_rejected():
    order = Order("MSFT", "sell", 100)
    order.cancel()
    with pytest.raises(ValueError, match="Cannot reject"):
        order.reject()
    assert order.status == OrderStatus.CANCELLED


def test_rejected_order_cannot_be_rejected():
    order = Order("MSFT", "sell", 100)
    order.reject()
    with pytest.raises(ValueError, match="Cannot reject"):
        order.reject()


def test_rejected_order_cannot_accept_fills():
    order = Order("MSFT", "buy", 100)
    order.reject()
    assert order.status == OrderStatus.REJECTED
    with pytest.raises(ValueError, match="Cannot apply fill"):
        order.apply_fill(50, 21)
    assert order.filled_quantity == 0
    assert order.status == OrderStatus.REJECTED
    assert len(order.fills) == 0
