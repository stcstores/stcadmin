import datetime as dt
from collections import Counter
from decimal import Decimal
from unittest import mock

import pytest
from django.urls import reverse
from django.utils.timezone import make_aware

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
    assert not_processed_fba_order.priority_temp is False


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
    date = make_aware(dt.datetime(2023, 10, 25))
    order = fba_order_factory.create(created_at=date, product__sku="AAA-BBB-CCC")
    assert str(order) == "AAA-BBB-CCC - 2023-10-25"


@pytest.mark.django_db
@pytest.mark.parametrize("priority,expected", ((False, False), (True, True)))
def test_is_prioritised_method(priority, expected, fba_order_factory):
    order = fba_order_factory.create(priority_temp=priority)
    assert order.is_prioritised() == expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    "closed_at,expected", ((None, False), (make_aware(dt.datetime(2023, 10, 1)), True))
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
    assert ready_fba_order.priority_temp is False
    assert ready_fba_order.on_hold is False
    assert ready_fba_order.is_stopped is False


@pytest.mark.django_db
@pytest.mark.parametrize(
    "box_weight,quantity_sent,expected",
    (
        (None, None, False),
        (None, 5, False),
        (Decimal("3.5"), None, False),
        (Decimal("3.5"), 5, True),
    ),
)
def test_details_complete(box_weight, quantity_sent, expected, fba_order_factory):
    order = fba_order_factory.create(box_weight=box_weight, quantity_sent=quantity_sent)
    assert order.details_complete() is expected


@pytest.mark.django_db
def test_prioritise(fba_order_factory):
    order = fba_order_factory.create(status_not_processed=True)
    order.prioritise()
    assert order.priority_temp is True


@pytest.mark.django_db
def test_duplicate(fulfilled_fba_order):
    duplicate = fulfilled_fba_order.duplicate()
    assert duplicate.pk != fulfilled_fba_order.pk
    assert duplicate.product == fulfilled_fba_order.product
    assert duplicate.product_weight == fulfilled_fba_order.product.weight_grams
    assert duplicate.product_hs_code == fulfilled_fba_order.product.hs_code
    assert duplicate.product_asin == fulfilled_fba_order.product_asin
    assert (
        duplicate.product_purchase_price == fulfilled_fba_order.product_purchase_price
    )
    assert duplicate.product_is_multipack == fulfilled_fba_order.product_is_multipack
    assert duplicate.region == fulfilled_fba_order.region
    assert duplicate.selling_price == fulfilled_fba_order.selling_price
    assert duplicate.FBA_fee == fulfilled_fba_order.FBA_fee
    assert duplicate.aproximate_quantity == fulfilled_fba_order.aproximate_quantity
    assert duplicate.small_and_light == fulfilled_fba_order.small_and_light
    assert duplicate.is_fragile == fulfilled_fba_order.is_fragile
    assert (
        duplicate.update_stock_level_when_complete
        == fulfilled_fba_order.update_stock_level_when_complete
    )
    assert duplicate.is_combinable == fulfilled_fba_order.is_combinable

    assert duplicate.fulfilled_by is None
    assert duplicate.closed_at is None
    assert duplicate.quantity_sent is None
    assert duplicate.box_weight is None
    assert duplicate.notes == ""
    assert duplicate.priority_temp is False
    assert duplicate.printed is False
    assert duplicate.on_hold is False
    assert duplicate.is_stopped is False
    assert duplicate.stopped_reason is None
    assert duplicate.stopped_at is None
    assert duplicate.stopped_until is None


@pytest.mark.django_db
@pytest.mark.parametrize(
    "quantity_sent,aprox_quantity,stock_level,expected",
    (
        (5, 6, None, 6),
        (None, 6, None, 6),
        (None, 6, 12, 6),
        (5, 6, 12, 5),
        (5, 6, 3, 3),
    ),
)
def test_duplicate_sets_aprox_quantity(
    quantity_sent, aprox_quantity, stock_level, expected, fba_order_factory
):
    order = fba_order_factory.create(
        quantity_sent=quantity_sent, aproximate_quantity=aprox_quantity
    )
    duplicate = order.duplicate(stock_level=stock_level)
    assert duplicate.aproximate_quantity == expected


# Test Queryset


@pytest.mark.django_db
def test_queryset_on_hold_method(
    not_processed_fba_order,
    printed_fba_order,
    ready_fba_order,
    fulfilled_fba_order,
    on_hold_fba_order,
    stopped_fba_order,
):
    assert list(models.FBAOrder.objects.all().on_hold()) == [on_hold_fba_order]


@pytest.mark.django_db
def test_queryset_stopped_method(
    not_processed_fba_order,
    printed_fba_order,
    ready_fba_order,
    fulfilled_fba_order,
    on_hold_fba_order,
    stopped_fba_order,
):
    assert list(models.FBAOrder.objects.all().stopped()) == [stopped_fba_order]


@pytest.mark.django_db
def test_queryset_fulfilled_method(
    not_processed_fba_order,
    printed_fba_order,
    ready_fba_order,
    fulfilled_fba_order,
    on_hold_fba_order,
    stopped_fba_order,
):
    assert list(models.FBAOrder.objects.all().fulfilled()) == [fulfilled_fba_order]


@pytest.mark.django_db
def test_queryset_ready_method(
    not_processed_fba_order,
    printed_fba_order,
    ready_fba_order,
    fulfilled_fba_order,
    on_hold_fba_order,
    stopped_fba_order,
):
    assert list(models.FBAOrder.objects.all().ready()) == [ready_fba_order]


@pytest.mark.django_db
def test_queryset_printed_method(
    not_processed_fba_order,
    printed_fba_order,
    ready_fba_order,
    fulfilled_fba_order,
    on_hold_fba_order,
    stopped_fba_order,
):
    assert list(models.FBAOrder.objects.all().printed()) == [printed_fba_order]


@pytest.mark.django_db
def test_queryset_not_processed_method(
    not_processed_fba_order,
    printed_fba_order,
    ready_fba_order,
    fulfilled_fba_order,
    on_hold_fba_order,
    stopped_fba_order,
):
    assert list(models.FBAOrder.objects.all().not_processed()) == [
        not_processed_fba_order
    ]


@pytest.mark.django_db
def test_queryset_awaiting_fulfillment_method(
    not_processed_fba_order,
    printed_fba_order,
    ready_fba_order,
    fulfilled_fba_order,
    on_hold_fba_order,
    stopped_fba_order,
):
    assert Counter(models.FBAOrder.objects.all().awaiting_fulfillment()) == Counter(
        [not_processed_fba_order, ready_fba_order, printed_fba_order]
    )


@pytest.mark.django_db
def test_queryset_unfulfilled_method(
    not_processed_fba_order,
    printed_fba_order,
    ready_fba_order,
    fulfilled_fba_order,
    on_hold_fba_order,
    stopped_fba_order,
):
    assert Counter(models.FBAOrder.objects.all().unfulfilled()) == Counter(
        [
            not_processed_fba_order,
            ready_fba_order,
            printed_fba_order,
            stopped_fba_order,
            on_hold_fba_order,
        ]
    )


@pytest.fixture
def prioritised_fba_order(fba_order_factory):
    return fba_order_factory.create(status_not_processed=True, priority_temp=True)


@pytest.fixture
def unprioritised_fba_order(fba_order_factory):
    return fba_order_factory.create(status_not_processed=True, priority_temp=False)


@pytest.mark.django_db
def test_queryset_prioritised_method(prioritised_fba_order, unprioritised_fba_order):
    assert Counter(models.FBAOrder.objects.all().prioritised()) == Counter(
        [prioritised_fba_order]
    )


@pytest.mark.django_db
def test_queryset_unprioritised_method(prioritised_fba_order, unprioritised_fba_order):
    assert Counter(models.FBAOrder.objects.all().unprioritised()) == Counter(
        [unprioritised_fba_order]
    )


@pytest.mark.django_db
def test_queryset_order_by_priority_method(
    not_processed_fba_order,
    printed_fba_order,
    ready_fba_order,
    fulfilled_fba_order,
    on_hold_fba_order,
    stopped_fba_order,
    prioritised_fba_order,
):
    assert list(models.FBAOrder.objects.all().order_by_priority()) == [
        ready_fba_order,
        printed_fba_order,
        prioritised_fba_order,
        not_processed_fba_order,
    ]


# Test Manager Methods


@pytest.fixture
def mock_get_queryset():
    with mock.patch(
        "fba.models.fba_order.FBAOrderManager.get_queryset"
    ) as mock_get_queryset:
        yield mock_get_queryset


def test_manager_on_hold_method(mock_get_queryset):
    return_value = models.fba_order.FBAOrderManager().on_hold()
    assert return_value == mock_get_queryset.return_value.on_hold.return_value


def test_manager_stopped_method(mock_get_queryset):
    return_value = models.fba_order.FBAOrderManager().stopped()
    assert return_value == mock_get_queryset.return_value.stopped.return_value


def test_manager_fulfilled_method(mock_get_queryset):
    return_value = models.fba_order.FBAOrderManager().fulfilled()
    assert return_value == mock_get_queryset.return_value.fulfilled.return_value


def test_manager_ready_method(mock_get_queryset):
    return_value = models.fba_order.FBAOrderManager().ready()
    assert return_value == mock_get_queryset.return_value.ready.return_value


def test_manager_printed_method(mock_get_queryset):
    return_value = models.fba_order.FBAOrderManager().printed()
    assert return_value == mock_get_queryset.return_value.printed.return_value


def test_manager_not_processed_method(mock_get_queryset):
    return_value = models.fba_order.FBAOrderManager().not_processed()
    assert return_value == mock_get_queryset.return_value.not_processed.return_value


def test_manager_awaiting_fulfillment_method(mock_get_queryset):
    return_value = models.fba_order.FBAOrderManager().awaiting_fulfillment()
    assert (
        return_value == mock_get_queryset.return_value.awaiting_fulfillment.return_value
    )


def test_manager_unfulfilled_method(mock_get_queryset):
    return_value = models.fba_order.FBAOrderManager().unfulfilled()
    assert return_value == mock_get_queryset.return_value.unfulfilled.return_value


def test_manager_order_by_priority_method(mock_get_queryset):
    return_value = models.fba_order.FBAOrderManager().order_by_priority()
    assert return_value == mock_get_queryset.return_value.order_by_priority.return_value


def test_manager_prioritised_method(mock_get_queryset):
    return_value = models.fba_order.FBAOrderManager().prioritised()
    assert return_value == mock_get_queryset.return_value.prioritised.return_value


def test_manager_unprioritised_method(mock_get_queryset):
    return_value = models.fba_order.FBAOrderManager().unprioritised()
    assert return_value == mock_get_queryset.return_value.unprioritised.return_value


@pytest.mark.django_db
@pytest.mark.parametrize(
    "closed_at,is_stopped,on_hold,box_weight,quantity_sent,printed,expected",
    (
        (
            make_aware(dt.datetime(2023, 1, 1)),
            True,
            True,
            Decimal("3.5"),
            3,
            True,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            True,
            True,
            Decimal("3.5"),
            3,
            False,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            True,
            True,
            Decimal("3.5"),
            None,
            True,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            True,
            True,
            Decimal("3.5"),
            None,
            False,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            True,
            True,
            None,
            3,
            True,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            True,
            True,
            None,
            3,
            False,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            True,
            True,
            None,
            None,
            True,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            True,
            True,
            None,
            None,
            False,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            True,
            False,
            Decimal("3.5"),
            3,
            True,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            True,
            False,
            Decimal("3.5"),
            3,
            False,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            True,
            False,
            Decimal("3.5"),
            None,
            True,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            True,
            False,
            Decimal("3.5"),
            None,
            False,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            True,
            False,
            None,
            3,
            True,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            True,
            False,
            None,
            3,
            False,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            True,
            False,
            None,
            None,
            True,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            True,
            False,
            None,
            None,
            False,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            False,
            True,
            Decimal("3.5"),
            3,
            True,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            False,
            True,
            Decimal("3.5"),
            3,
            False,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            False,
            True,
            Decimal("3.5"),
            None,
            True,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            False,
            True,
            Decimal("3.5"),
            None,
            False,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            False,
            True,
            None,
            3,
            True,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            False,
            True,
            None,
            3,
            False,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            False,
            True,
            None,
            None,
            True,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            False,
            True,
            None,
            None,
            False,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            False,
            False,
            Decimal("3.5"),
            3,
            True,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            False,
            False,
            Decimal("3.5"),
            3,
            False,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            False,
            False,
            Decimal("3.5"),
            None,
            True,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            False,
            False,
            Decimal("3.5"),
            None,
            False,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            False,
            False,
            None,
            3,
            True,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            False,
            False,
            None,
            3,
            False,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            False,
            False,
            None,
            None,
            True,
            models.FBAOrder.FULFILLED,
        ),
        (
            make_aware(dt.datetime(2023, 1, 1)),
            False,
            False,
            None,
            None,
            False,
            models.FBAOrder.FULFILLED,
        ),
        (None, True, True, Decimal("3.5"), 3, True, models.FBAOrder.ON_HOLD),
        (None, True, True, Decimal("3.5"), 3, False, models.FBAOrder.ON_HOLD),
        (None, True, True, Decimal("3.5"), None, True, models.FBAOrder.ON_HOLD),
        (None, True, True, Decimal("3.5"), None, False, models.FBAOrder.ON_HOLD),
        (None, True, True, None, 3, True, models.FBAOrder.ON_HOLD),
        (None, True, True, None, 3, False, models.FBAOrder.ON_HOLD),
        (None, True, True, None, None, True, models.FBAOrder.ON_HOLD),
        (None, True, True, None, None, False, models.FBAOrder.ON_HOLD),
        (None, True, False, Decimal("3.5"), 3, True, models.FBAOrder.STOPPED),
        (None, True, False, Decimal("3.5"), 3, False, models.FBAOrder.STOPPED),
        (None, True, False, Decimal("3.5"), None, True, models.FBAOrder.STOPPED),
        (None, True, False, Decimal("3.5"), None, False, models.FBAOrder.STOPPED),
        (None, True, False, None, 3, True, models.FBAOrder.STOPPED),
        (None, True, False, None, 3, False, models.FBAOrder.STOPPED),
        (None, True, False, None, None, True, models.FBAOrder.STOPPED),
        (None, True, False, None, None, False, models.FBAOrder.STOPPED),
        (None, False, True, Decimal("3.5"), 3, True, models.FBAOrder.ON_HOLD),
        (None, False, True, Decimal("3.5"), 3, False, models.FBAOrder.ON_HOLD),
        (None, False, True, Decimal("3.5"), None, True, models.FBAOrder.ON_HOLD),
        (None, False, True, Decimal("3.5"), None, False, models.FBAOrder.ON_HOLD),
        (None, False, True, None, 3, True, models.FBAOrder.ON_HOLD),
        (None, False, True, None, 3, False, models.FBAOrder.ON_HOLD),
        (None, False, True, None, None, True, models.FBAOrder.ON_HOLD),
        (None, False, True, None, None, False, models.FBAOrder.ON_HOLD),
        (None, False, False, Decimal("3.5"), 3, True, models.FBAOrder.READY),
        (None, False, False, Decimal("3.5"), 3, False, models.FBAOrder.READY),
        (None, False, False, Decimal("3.5"), None, True, models.FBAOrder.PRINTED),
        (
            None,
            False,
            False,
            Decimal("3.5"),
            None,
            False,
            models.FBAOrder.NOT_PROCESSED,
        ),
        (None, False, False, None, 3, True, models.FBAOrder.PRINTED),
        (None, False, False, None, 3, False, models.FBAOrder.NOT_PROCESSED),
        (None, False, False, None, None, True, models.FBAOrder.PRINTED),
        (None, False, False, None, None, False, models.FBAOrder.NOT_PROCESSED),
    ),
)
def test_manager_get_queryset_method(
    closed_at,
    is_stopped,
    on_hold,
    box_weight,
    quantity_sent,
    printed,
    expected,
    fba_order_factory,
):
    order = fba_order_factory.create(
        closed_at=closed_at,
        is_stopped=is_stopped,
        on_hold=on_hold,
        box_weight=box_weight,
        quantity_sent=quantity_sent,
        printed=printed,
    )
    assert models.FBAOrder.objects.get(pk=order.pk).status == expected
