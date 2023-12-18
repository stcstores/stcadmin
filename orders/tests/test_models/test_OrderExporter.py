import datetime as dt
from unittest.mock import Mock

import pytest

from orders.models.order import OrderExporter


@pytest.fixture
def order(order_factory, product_sale_factory):
    order = order_factory.create()
    product_sale_factory.create(order=order)
    return order


@pytest.fixture
def undispatched_order(order_factory, product_sale_factory):
    order = order_factory.create(dispatched_at=None)
    product_sale_factory.create(order=order)
    return order


@pytest.fixture
def order_row(order):
    return OrderExporter().make_row(order)


def test_format_date():
    date = dt.datetime(2022, 5, 6, 11, 22, 13, 25)
    assert OrderExporter.format_date(date) == "2022-05-06"


def test_format_currency():
    assert OrderExporter.format_currency(520) == "5.20"


def test_format_currency_with_none():
    assert OrderExporter.format_currency(None) is None


@pytest.mark.django_db
def test_order_row_includes_order_id(order, order_row):
    assert order_row[OrderExporter.ORDER_ID] == order.order_id


@pytest.mark.django_db
def test_order_row_includes_date_recieved(order, order_row):
    assert order_row[OrderExporter.DATE_RECIEVED] == OrderExporter.format_date(
        order.recieved_at
    )


@pytest.mark.django_db
def test_order_row_includes_date_dispatched(order, order_row):
    assert order_row[
        OrderExporter.DATE_DISPATCHED
    ] == OrderExporter()._order_dispatched_value(order)


@pytest.mark.django_db
def test_order_dispatched_value(order):
    assert OrderExporter()._order_dispatched_value(
        order
    ) == order.dispatched_at.strftime("%Y-%m-%d")


@pytest.mark.django_db
def test_order_dispatched_value_with_undispatched_order(undispatched_order):
    assert OrderExporter()._order_dispatched_value(undispatched_order) == "UNDISPATCHED"


@pytest.mark.django_db
def test_order_row_includes_country(order, order_row):
    assert order_row[OrderExporter.COUNTRY] == order.country.name


@pytest.mark.django_db
def test_order_row_includes_channel(order, order_row):
    assert order_row[OrderExporter.CHANNEL] == order.channel.name


@pytest.mark.django_db
def test_order_row_handles_missing_channel(order):
    order.channel = None
    order_row = OrderExporter().make_row(order)
    assert order_row[OrderExporter.CHANNEL] is None


@pytest.mark.django_db
def test_order_row_includes_tracking_number(order, order_row):
    assert order_row[OrderExporter.TRACKING_NUMBER] == order.tracking_number


@pytest.mark.django_db
def test_order_row_includes_shipping_service(order, order_row):
    assert order_row[OrderExporter.SHIPPING_SERVICE] == order.shipping_service.name


@pytest.mark.django_db
def test_order_row_handles_missing_shipping_service(order):
    order.shipping_service = None
    order_row = OrderExporter().make_row(order)
    assert order_row[OrderExporter.SHIPPING_SERVICE] is None


@pytest.mark.django_db
def test_order_row_includes_shipping_price(order, order_row):
    assert order_row[OrderExporter.SHIPPING_PRICE] == OrderExporter.format_currency(
        order.calculated_shipping_price
    )


@pytest.mark.django_db
def test_order_row_includes_currency(order, order_row):
    assert order_row[OrderExporter.CURRENCY] == order.currency.code


@pytest.mark.django_db
def test_order_row_handles_missing_currency(order):
    order.currency = None
    order_row = OrderExporter().make_row(order)
    assert order_row[OrderExporter.CURRENCY] is None


@pytest.mark.django_db
def test_order_row_includes_total_paid(order, order_row):
    assert order_row[OrderExporter.TOTAL_PAID] == OrderExporter.format_currency(
        order.total_paid
    )


@pytest.mark.django_db
def test_order_row_includes_total_paid_GBP(order, order_row):
    assert order_row[OrderExporter.WEIGHT] == order.total_weight()


@pytest.mark.django_db
def test_order_row_includes_weight(order, order_row):
    assert order_row[OrderExporter.TOTAL_PAID_GBP] == OrderExporter.format_currency(
        order.total_paid_GBP
    )


@pytest.mark.django_db
def test_order_row_includes_channel_fee(order, order_row):
    assert order_row[OrderExporter.CHANNEL_FEE] == OrderExporter.format_currency(
        order.channel_fee_paid()
    )


@pytest.mark.django_db
def test_order_row_handels_error_calculating_channel_fee(order):
    order.channel_fee_paid = Mock(side_effect=Exception("test exception"))
    order_row = OrderExporter().make_row(order)
    assert order_row[OrderExporter.CHANNEL_FEE] is None


@pytest.mark.django_db
def test_order_row_includes_purchase_price(order, order_row):
    assert order_row[OrderExporter.PURCHASE_PRICE] == OrderExporter.format_currency(
        order.purchase_price()
    )


@pytest.mark.django_db
def test_order_row_handels_error_calculating_purchase_price(order):
    order.purchase_price = Mock(side_effect=Exception("test exception"))
    order_row = OrderExporter().make_row(order)
    assert order_row[OrderExporter.PURCHASE_PRICE] is None


@pytest.mark.django_db
def test_order_row_includes_tax(order, order_row):
    assert order_row[OrderExporter.TAX] == OrderExporter.format_currency(order.tax_GBP)


@pytest.mark.django_db
def test_order_row_includes_profit(order, order_row):
    assert order_row[OrderExporter.PROFIT] == OrderExporter.format_currency(
        order.profit()
    )


@pytest.mark.django_db
def test_order_row_handels_error_calculating_profit(order):
    order.profit = Mock(side_effect=Exception("test exception"))
    order_row = OrderExporter().make_row(order)
    assert order_row[OrderExporter.PROFIT] is None


@pytest.mark.django_db
def test_order_row_includes_profit_percentage(order, order_row):
    assert order_row[OrderExporter.PROFIT_PERCENTAGE] == order.profit_percentage()


@pytest.mark.django_db
def test_order_row_handels_error_calculating_profit_percentage(order):
    order.profit_percentage = Mock(side_effect=Exception("test exception"))
    order_row = OrderExporter().make_row(order)
    assert order_row[OrderExporter.PROFIT_PERCENTAGE] is None
