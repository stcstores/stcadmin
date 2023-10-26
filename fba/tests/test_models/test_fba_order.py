import datetime as dt
from decimal import Decimal

import pytest
from django.urls import reverse

from fba import models
from home.models import Staff
from inventory.models import BaseProduct

# Test Not Processed FBA order


@pytest.fixture
def not_processed_fba_order(fba_order_factory):
    return fba_order_factory(status_not_processed=True)


@pytest.mark.django_db
def test_not_processed_fba_order_full_clean(not_processed_fba_order):
    not_processed_fba_order.full_clean()


@pytest.mark.django_db
def test_not_processed_fba_order_status(not_processed_fba_order):
    assert (
        models.FBAOrder.objects.get(id=not_processed_fba_order.id).status
        == models.FBAOrder.NOT_PROCESSED
    )


@pytest.mark.django_db
def test_not_processed_fba_order_created_at_attribute(not_processed_fba_order):
    assert isinstance(not_processed_fba_order.created_at, dt.datetime)


@pytest.mark.django_db
def test_not_processed_fba_order_modified_at_attribute(not_processed_fba_order):
    assert isinstance(not_processed_fba_order.modified_at, dt.datetime)


@pytest.mark.django_db
def test_not_processed_fba_order_fulfiled_by_attribute(not_processed_fba_order):
    assert not_processed_fba_order.fulfilled_by is None


@pytest.mark.django_db
def test_not_processed_fba_order_closed_at_attribute(not_processed_fba_order):
    assert not_processed_fba_order.closed_at is None


@pytest.mark.django_db
def test_not_processed_fba_order_region_attribute(not_processed_fba_order):
    assert isinstance(not_processed_fba_order.region, models.FBARegion)


@pytest.mark.django_db
def test_not_processed_fba_order_product_attribute(not_processed_fba_order):
    assert isinstance(not_processed_fba_order.product, BaseProduct)


@pytest.mark.django_db
def test_not_processed_fba_order_product_weight_attribute(not_processed_fba_order):
    assert isinstance(not_processed_fba_order.product_weight, int)


@pytest.mark.django_db
def test_not_processed_fba_order_product_hs_code_attribute(not_processed_fba_order):
    assert isinstance(not_processed_fba_order.product_hs_code, str)


@pytest.mark.django_db
def test_not_processed_fba_order_product_asin_attribute(not_processed_fba_order):
    assert isinstance(not_processed_fba_order.product_asin, str)


@pytest.mark.django_db
def test_not_processed_fba_order_product_purchase_price_attribute(
    not_processed_fba_order,
):
    assert isinstance(not_processed_fba_order.product_purchase_price, str)


@pytest.mark.django_db
def test_not_processed_fba_order_product_is_multipack_attribute(
    not_processed_fba_order,
):
    assert not_processed_fba_order.product_is_multipack is False


@pytest.mark.django_db
def test_not_processed_fba_order_selling_price_attribute(not_processed_fba_order):
    assert isinstance(not_processed_fba_order.selling_price, int)


@pytest.mark.django_db
def test_not_processed_fba_order_fba_fee_attribute(not_processed_fba_order):
    assert isinstance(not_processed_fba_order.FBA_fee, int)


@pytest.mark.django_db
def test_not_processed_fba_order_aproximate_quantity_attribute(
    not_processed_fba_order,
):
    assert isinstance(not_processed_fba_order.aproximate_quantity, int)


@pytest.mark.django_db
def test_not_processed_fba_order_quantity_sent_attribute(not_processed_fba_order):
    assert not_processed_fba_order.quantity_sent is None


@pytest.mark.django_db
def test_not_processed_fba_order_box_weight_attribute(not_processed_fba_order):
    assert not_processed_fba_order.box_weight is None


@pytest.mark.django_db
def test_not_processed_fba_order_notes_attribute(not_processed_fba_order):
    assert isinstance(not_processed_fba_order.notes, str)


@pytest.mark.django_db
def test_not_processed_fba_order_priority_attribute(not_processed_fba_order):
    assert not_processed_fba_order.priority == models.FBAOrder.MAX_PRIORITY


@pytest.mark.django_db
def test_not_processed_fba_order_printed_attribute(not_processed_fba_order):
    assert not_processed_fba_order.printed is False


@pytest.mark.django_db
def test_not_processed_fba_order_small_and_light_attribute(not_processed_fba_order):
    assert not_processed_fba_order.small_and_light is False


@pytest.mark.django_db
def test_not_processed_fba_order_on_hold_attribute(not_processed_fba_order):
    assert not_processed_fba_order.on_hold is False


@pytest.mark.django_db
def test_not_processed_fba_order_update_stock_level_when_complete_attribute(
    not_processed_fba_order,
):
    assert not_processed_fba_order.update_stock_level_when_complete is True


@pytest.mark.django_db
def test_not_processed_fba_order_is_combinable_attribute(not_processed_fba_order):
    assert not_processed_fba_order.is_combinable is False


@pytest.mark.django_db
def test_not_processed_fba_order_is_fragile_attribute(not_processed_fba_order):
    assert not_processed_fba_order.is_fragile is False


@pytest.mark.django_db
def test_not_processed_fba_order_is_stopped_attribute(not_processed_fba_order):
    assert not_processed_fba_order.is_stopped is False


@pytest.mark.django_db
def test_not_processed_fba_order_stopped_reason_attribute(not_processed_fba_order):
    assert not_processed_fba_order.stopped_reason is None


@pytest.mark.django_db
def test_not_processed_fba_order_stopped_at_attribute(not_processed_fba_order):
    assert not_processed_fba_order.stopped_at is None


@pytest.mark.django_db
def test_not_processed_fba_order_stopped_until_attribute(not_processed_fba_order):
    assert not_processed_fba_order.stopped_until is None


# Test Ready FBA Order


@pytest.fixture
def ready_fba_order(fba_order_factory):
    return fba_order_factory(status_ready=True)


@pytest.mark.django_db
def test_clean_ready_fba_order(ready_fba_order):
    ready_fba_order.full_clean()


@pytest.mark.django_db
def test_ready_fba_order_status(ready_fba_order):
    assert (
        models.FBAOrder.objects.get(id=ready_fba_order.id).status
        == models.FBAOrder.READY
    )


@pytest.mark.django_db
def test_ready_fba_order_fulfilled_by_attribute(ready_fba_order):
    assert ready_fba_order.fulfilled_by is None


@pytest.mark.django_db
def test_ready_fba_order_closed_at_attribute(ready_fba_order):
    assert ready_fba_order.closed_at is None


@pytest.mark.django_db
def test_ready_fba_order_quantity_sent_attribute(ready_fba_order):
    assert isinstance(ready_fba_order.quantity_sent, int)


@pytest.mark.django_db
def test_ready_fba_order_box_weight_attribute(ready_fba_order):
    assert isinstance(ready_fba_order.box_weight, Decimal)


@pytest.mark.django_db
def test_ready_fba_order_printed_attribute(ready_fba_order):
    assert ready_fba_order.printed is True


@pytest.mark.django_db
def test_ready_fba_order_is_stopped_attribute(ready_fba_order):
    assert ready_fba_order.is_stopped is False


@pytest.mark.django_db
def test_ready_fba_order_stopped_reason_attribute(ready_fba_order):
    assert ready_fba_order.stopped_reason is None


@pytest.mark.django_db
def test_ready_fba_order_stopped_at_attribute(ready_fba_order):
    assert ready_fba_order.stopped_at is None


@pytest.mark.django_db
def test_ready_fba_order_stopped_until_attribute(ready_fba_order):
    assert ready_fba_order.stopped_until is None


# Test Printed FBA Order


@pytest.fixture
def printed_fba_order(fba_order_factory):
    return fba_order_factory(status_printed=True)


@pytest.mark.django_db
def test_clean_printed_fba_order(printed_fba_order):
    printed_fba_order.full_clean()


@pytest.mark.django_db
def test_printed_fba_order_status(printed_fba_order):
    assert (
        models.FBAOrder.objects.get(id=printed_fba_order.id).status
        == models.FBAOrder.PRINTED
    )


@pytest.mark.django_db
def test_printed_fba_order_fulfilled_by_attribute(printed_fba_order):
    assert printed_fba_order.fulfilled_by is None


@pytest.mark.django_db
def test_printed_fba_order_closed_at_attribute(printed_fba_order):
    assert printed_fba_order.closed_at is None


@pytest.mark.django_db
def test_printed_fba_order_quantity_sent_attribute(printed_fba_order):
    assert printed_fba_order.quantity_sent is None


@pytest.mark.django_db
def test_printed_fba_order_box_weight_attribute(printed_fba_order):
    assert printed_fba_order.box_weight is None


@pytest.mark.django_db
def test_printed_fba_order_printed_attribute(printed_fba_order):
    assert printed_fba_order.printed is True


@pytest.mark.django_db
def test_printed_fba_order_on_hold_attribute(printed_fba_order):
    assert printed_fba_order.on_hold is False


@pytest.mark.django_db
def test_printed_fba_order_is_stopped_attribute(printed_fba_order):
    assert printed_fba_order.is_stopped is False


@pytest.mark.django_db
def test_printed_fba_order_stopped_reason_attribute(printed_fba_order):
    assert printed_fba_order.stopped_reason is None


@pytest.mark.django_db
def test_printed_fba_order_stopped_at_attribute(printed_fba_order):
    assert printed_fba_order.stopped_at is None


@pytest.mark.django_db
def test_printed_fba_order_stopped_until_attribute(printed_fba_order):
    assert printed_fba_order.stopped_until is None


# Test On Hold FBA Order


@pytest.fixture
def on_hold_fba_order(fba_order_factory):
    return fba_order_factory(status_on_hold=True)


@pytest.mark.django_db
def test_clean_on_hold_fba_order(on_hold_fba_order):
    on_hold_fba_order.full_clean()


@pytest.mark.django_db
def test_on_hold_fba_order_status(on_hold_fba_order):
    assert (
        models.FBAOrder.objects.get(id=on_hold_fba_order.id).status
        == models.FBAOrder.ON_HOLD
    )


@pytest.mark.django_db
def test_on_hold_fba_order_fulfilled_by_attribute(on_hold_fba_order):
    assert on_hold_fba_order.fulfilled_by is None


@pytest.mark.django_db
def test_on_hold_fba_order_closed_at_attribute(on_hold_fba_order):
    assert on_hold_fba_order.closed_at is None


@pytest.mark.django_db
def test_on_hold_fba_order_quantity_sent_attribute(on_hold_fba_order):
    assert on_hold_fba_order.quantity_sent is None


@pytest.mark.django_db
def test_on_hold_fba_order_box_weight_attribute(on_hold_fba_order):
    assert on_hold_fba_order.box_weight is None


@pytest.mark.django_db
def test_on_hold_fba_order_printed_attribute(on_hold_fba_order):
    assert on_hold_fba_order.printed is False


@pytest.mark.django_db
def test_on_hold_fba_order_on_hold_attribute(on_hold_fba_order):
    assert on_hold_fba_order.on_hold is True


@pytest.mark.django_db
def test_on_hold_fba_order_is_stopped_attribute(on_hold_fba_order):
    assert on_hold_fba_order.is_stopped is False


@pytest.mark.django_db
def test_on_hold_fba_order_stopped_reason_attribute(on_hold_fba_order):
    assert on_hold_fba_order.stopped_reason is None


@pytest.mark.django_db
def test_on_hold_fba_order_stopped_at_attribute(on_hold_fba_order):
    assert on_hold_fba_order.stopped_at is None


@pytest.mark.django_db
def test_on_hold_fba_order_stopped_until_attribute(on_hold_fba_order):
    assert on_hold_fba_order.stopped_until is None


# Test Fulfilled FBA Order


@pytest.fixture
def fulfilled_fba_order(fba_order_factory):
    return fba_order_factory(status_fulfilled=True)


@pytest.mark.django_db
def test_clean_fulfilled_fba_order(fulfilled_fba_order):
    fulfilled_fba_order.full_clean()


@pytest.mark.django_db
def test_fulfilled_fba_order_status(fulfilled_fba_order):
    assert (
        models.FBAOrder.objects.get(id=fulfilled_fba_order.id).status
        == models.FBAOrder.FULFILLED
    )


@pytest.mark.django_db
def test_fulfilled_fba_order_fulfilled_by_attribute(fulfilled_fba_order):
    assert isinstance(fulfilled_fba_order.fulfilled_by, Staff)


@pytest.mark.django_db
def test_fulfilled_fba_order_closed_at_attribute(fulfilled_fba_order):
    assert isinstance(fulfilled_fba_order.closed_at, dt.datetime)


@pytest.mark.django_db
def test_fulfilled_fba_order_quantity_sent_attribute(fulfilled_fba_order):
    assert isinstance(fulfilled_fba_order.quantity_sent, int)


@pytest.mark.django_db
def test_fulfilled_fba_order_box_weight_attribute(fulfilled_fba_order):
    assert isinstance(fulfilled_fba_order.box_weight, Decimal)


@pytest.mark.django_db
def test_fulfilled_fba_order_printed_attribute(fulfilled_fba_order):
    assert fulfilled_fba_order.printed is True


@pytest.mark.django_db
def test_fulfilled_fba_order_on_hold_attribute(fulfilled_fba_order):
    assert fulfilled_fba_order.on_hold is False


@pytest.mark.django_db
def test_fulfilled_fba_order_is_stopped_attribute(fulfilled_fba_order):
    assert fulfilled_fba_order.is_stopped is False


@pytest.mark.django_db
def test_fulfilled_fba_order_stopped_reason_attribute(fulfilled_fba_order):
    assert fulfilled_fba_order.stopped_reason is None


@pytest.mark.django_db
def test_fulfilled_fba_order_stopped_at_attribute(fulfilled_fba_order):
    assert fulfilled_fba_order.stopped_at is None


@pytest.mark.django_db
def test_fulfilled_fba_order_stopped_until_attribute(fulfilled_fba_order):
    assert fulfilled_fba_order.stopped_until is None


# Test Stopped FBA Order


@pytest.fixture
def stopped_fba_order(fba_order_factory):
    return fba_order_factory(status_stopped=True)


@pytest.mark.django_db
def test_clean_stopped_fba_order(stopped_fba_order):
    stopped_fba_order.full_clean()


@pytest.mark.django_db
def test_stopped_fba_order_status(stopped_fba_order):
    assert (
        models.FBAOrder.objects.get(id=stopped_fba_order.id).status
        == models.FBAOrder.STOPPED
    )


@pytest.mark.django_db
def test_stopped_fba_order_fulfilled_by_attribute(stopped_fba_order):
    assert stopped_fba_order.fulfilled_by is None


@pytest.mark.django_db
def test_stopped_fba_order_closed_at_attribute(stopped_fba_order):
    assert stopped_fba_order.closed_at is None


@pytest.mark.django_db
def test_stopped_fba_order_quantity_sent_attribute(stopped_fba_order):
    assert stopped_fba_order.quantity_sent is None


@pytest.mark.django_db
def test_stopped_fba_order_box_weight_attribute(stopped_fba_order):
    assert stopped_fba_order.box_weight is None


@pytest.mark.django_db
def test_stopped_fba_order_printed_attribute(stopped_fba_order):
    assert stopped_fba_order.printed is True


@pytest.mark.django_db
def test_stopped_fba_order_on_hold_attribute(stopped_fba_order):
    assert stopped_fba_order.on_hold is False


@pytest.mark.django_db
def test_stopped_fba_order_is_stopped_attribute(stopped_fba_order):
    assert stopped_fba_order.is_stopped is True


@pytest.mark.django_db
def test_stopped_fba_order_stopped_reason_attribute(stopped_fba_order):
    assert isinstance(stopped_fba_order.stopped_reason, str)


@pytest.mark.django_db
def test_stopped_fba_order_stopped_at_attribute(stopped_fba_order):
    assert isinstance(stopped_fba_order.stopped_at, dt.datetime)


@pytest.mark.django_db
def test_stopped_fba_order_stopped_until_attribute(stopped_fba_order):
    assert isinstance(stopped_fba_order.stopped_until, dt.datetime)


# Test Methods


@pytest.mark.django_db
def test_str_method(fba_order_factory):
    date = dt.datetime(2023, 10, 25)
    order = fba_order_factory.create(created_at=date, product__sku="AAA-BBB-CCC")
    assert str(order) == "AAA-BBB-CCC - 2023-10-25"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "priority,expected", ((models.FBAOrder.MAX_PRIORITY, False), (998, True), (1, True))
)
def test_is_prioritised_method(priority, expected, fba_order_factory):
    order = fba_order_factory.create(priority=priority)
    assert order.is_prioritised() == expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    "closed_at,expected", ((None, False), (dt.datetime(2023, 10, 1), True))
)
def test_is_closed_method(closed_at, expected, fba_order_factory):
    order = fba_order_factory.create(closed_at=closed_at)
    assert order.is_closed() is expected


@pytest.mark.django_db
def test_get_absolute_url_method(not_processed_fba_order):
    assert not_processed_fba_order.get_absolute_url() == reverse(
        "fba:update_fba_order", args=[not_processed_fba_order.pk]
    )


@pytest.mark.django_db
def test_get_get_fulfillment_url_method(printed_fba_order):
    assert printed_fba_order.get_fulfillment_url() == reverse(
        "fba:fulfill_fba_order", args=[printed_fba_order.pk]
    )


@pytest.mark.django_db
def test_close_method(ready_fba_order):
    ready_fba_order.close()
    ready_fba_order.refresh_from_db()
    assert isinstance(ready_fba_order.closed_at, dt.datetime)
    assert ready_fba_order.priority == models.FBAOrder.MAX_PRIORITY
    assert ready_fba_order.on_hold is False
    assert ready_fba_order.is_stopped is False


@pytest.mark.django_db
def test_prioritise(fba_order_factory):
    orders = fba_order_factory.create_batch(3, status_not_processed=True)
    orders[0].prioritise()
    assert orders[0].priority == 1
    orders[1].prioritise()
    for order in orders:
        order.refresh_from_db()
    assert orders[1].priority == 1
    assert orders[0].priority == 2
    assert orders[2].priority == models.FBAOrder.MAX_PRIORITY
