import datetime as dt
from unittest import mock

import pytest
from django.db.models import Q
from django.utils.timezone import make_aware

from fba.forms import StoppedOrderFilter


@pytest.fixture
def order(fba_order_factory):
    return fba_order_factory.create(status_stopped=True)


@pytest.fixture
def not_stopped_order(fba_order_factory):
    return fba_order_factory.create(status_not_processed=True)


@pytest.fixture
def date():
    return dt.date(2023, 3, 3)


@pytest.mark.django_db
def test_supplier_filter(fba_order_factory, supplier_factory):
    order = fba_order_factory.create(status_stopped=True)
    other_supplier = supplier_factory.create()
    form = StoppedOrderFilter()
    choices = form.fields["supplier"].choices
    assert choices[0] == ("", "---------")
    assert (order.product.supplier.pk, order.product.supplier.name) in choices
    assert (other_supplier.pk, other_supplier.name) not in choices


@pytest.mark.django_db
def test_clean_clean_stopped_from_method(date):
    form = StoppedOrderFilter({"stopped_from": date})
    assert form.is_valid() is True
    assert form.cleaned_data["stopped_from"] == make_aware(
        dt.datetime.combine(date, dt.datetime.min.time())
    )


@pytest.mark.django_db
def test_clean_clean_stopped_to_method(date):
    form = StoppedOrderFilter({"stopped_to": date})
    assert form.is_valid() is True
    assert form.cleaned_data["stopped_to"] == make_aware(
        dt.datetime.combine(date, dt.datetime.max.time())
    )


@pytest.mark.django_db
def test_query_kwargs():
    data = {
        "stopped_from": "A",
        "stopped_to": "B",
        "country": "E",
        "supplier": "F",
    }
    assert StoppedOrderFilter().query_kwargs(data) == {
        "stopped_at__gte": "A",
        "stopped_at__lte": "B",
        "region__name": "E",
        "product__supplier": "F",
        "closed_at__isnull": True,
    }


@pytest.mark.django_db
def test_text_search():
    search_text = "search text"
    qs = mock.Mock()
    StoppedOrderFilter().text_search(search_text, qs)
    qs.filter.assert_called_once_with(
        Q(
            Q(product__sku__icontains=search_text)
            | Q(product__product_range__name__icontains=search_text)
            | Q(product_asin__icontains=search_text)
        )
    )


@pytest.mark.django_db
def test_search_by_sku(order):
    form = StoppedOrderFilter({"search": order.product.sku})
    assert form.is_valid()
    assert order in form.get_queryset()


@pytest.mark.django_db
def test_orders_by_stopped_until():
    form = StoppedOrderFilter({})
    assert form.is_valid()
    qs = form.get_queryset()
    assert 'ORDER BY "fba_fbaorder"."stopped_until" ASC' in str(qs.query)


@pytest.mark.django_db
def test_does_not_return_orders_that_are_not_stopped(not_stopped_order):
    form = StoppedOrderFilter({})
    assert form.is_valid()
    qs = form.get_queryset()
    assert qs.contains(not_stopped_order) is False
