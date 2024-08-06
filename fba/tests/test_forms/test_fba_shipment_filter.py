import datetime as dt
from unittest import mock

import pytest
from django.db.models import Q
from django.utils.timezone import make_aware

from fba.forms import FBAShipmentFilter


@pytest.fixture
def destination(fba_shipment_destination_factory):
    return fba_shipment_destination_factory.create()


@pytest.fixture
def user(user_factory):
    return user_factory.create()


@pytest.fixture
def order(parcelhub_shipment_factory, fba_shipment_order_factory, user, destination):
    order = fba_shipment_order_factory.create(user=user, destination=destination)
    parcelhub_shipment_factory.create(shipment_order=order)
    return order


@pytest.fixture
def item(fba_shipment_item_factory, order):
    return fba_shipment_item_factory.create(package__shipment_order=order)


@pytest.fixture
def date():
    return dt.date(2023, 3, 3)


@pytest.mark.django_db
def test_clean_clean_completed_from_method(date):
    form = FBAShipmentFilter({"completed_from": date})
    assert form.is_valid() is True
    assert form.cleaned_data["completed_from"] == make_aware(
        dt.datetime.combine(date, dt.datetime.min.time())
    )


@pytest.mark.django_db
def test_clean_clean_completed_to_method(date):
    form = FBAShipmentFilter({"completed_to": date})
    assert form.is_valid() is True
    assert form.cleaned_data["completed_to"] == make_aware(
        dt.datetime.combine(date, dt.datetime.max.time())
    )


@pytest.mark.django_db
def test_query_kwargs():
    data = {
        "completed_from": "A",
        "completed_to": "B",
        "destination": "C",
        "user": "D",
    }
    assert FBAShipmentFilter().query_kwargs(data) == {
        "parcelhub_shipment__created_at__gte": "A",
        "parcelhub_shipment__created_at__lte": "B",
        "destination": "C",
        "user": "D",
    }


def test_text_search():
    search_text = "search text"
    qs = mock.Mock()
    FBAShipmentFilter().text_search(search_text, qs)
    qs.filter.assert_called_once_with(
        Q(
            Q(shipment_package__shipment_item__sku__icontains=search_text)
            | Q(shipment_package__shipment_item__description__icontains=search_text)
        )
    )


def test_search_with_shipment_id():
    search_text = "STC_FBA_456"
    qs = mock.Mock()
    FBAShipmentFilter().text_search(search_text, qs)
    qs.filter.assert_called_once_with(id=456)


@pytest.mark.django_db
def test_filters_unfiled_shipments(fba_shipment_order_factory):
    order = fba_shipment_order_factory.create()
    form = FBAShipmentFilter({})
    assert form.is_valid()
    assert form.get_queryset().contains(order) is False


@pytest.mark.django_db
def test_search_by_item_sku(order, item):
    form = FBAShipmentFilter({"search": item.sku})
    assert form.is_valid()
    assert form.get_queryset().contains(order)


@pytest.mark.django_db
def test_search_by_item_description(order, item):
    form = FBAShipmentFilter({"search": item.description})
    assert form.is_valid()
    assert form.get_queryset().contains(order)


@pytest.mark.django_db
def test_search_by_destination(order, destination):
    form = FBAShipmentFilter({"destination": destination.id})
    assert form.is_valid()
    assert form.get_queryset().contains(order)


@pytest.mark.django_db
def test_search_by_user(order, user):
    form = FBAShipmentFilter({"user": user.id})
    assert form.is_valid()
    assert form.get_queryset().contains(order)


@pytest.mark.django_db
def test_orders_by_completed_at_by_default():
    form = FBAShipmentFilter({})
    assert form.is_valid()
    qs = form.get_queryset()
    assert 'ORDER BY "fba_parcelhubshipment"."created_at" DESC' in str(qs.query)
