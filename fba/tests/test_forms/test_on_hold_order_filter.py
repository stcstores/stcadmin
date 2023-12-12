import datetime as dt
from unittest import mock

import pytest
from django.db.models import Q
from django.utils.timezone import make_aware

from fba.forms import OnHoldOrderFilter


@pytest.fixture
def order(fba_order_factory):
    return fba_order_factory.create(status_on_hold=True)


@pytest.fixture
def not_on_hold_order(fba_order_factory):
    return fba_order_factory.create(status_not_processed=True)


@pytest.fixture
def date():
    return dt.date(2023, 3, 3)


@pytest.mark.django_db
def test_supplier_filter(fba_order_factory, supplier_factory):
    order = fba_order_factory.create(status_on_hold=True)
    other_supplier = supplier_factory.create()
    form = OnHoldOrderFilter()
    choices = form.fields["supplier"].choices
    assert choices[0] == ("", "---------")
    assert (order.product.supplier.pk, order.product.supplier.name) in choices
    assert (other_supplier.pk, other_supplier.name) not in choices


@pytest.mark.django_db
def test_clean_clean_created_from_method(date):
    form = OnHoldOrderFilter({"created_from": date})
    assert form.is_valid() is True
    assert form.cleaned_data["created_from"] == make_aware(
        dt.datetime.combine(date, dt.datetime.min.time())
    )


@pytest.mark.django_db
def test_clean_clean_created_to_method(date):
    form = OnHoldOrderFilter({"created_to": date})
    assert form.is_valid() is True
    assert form.cleaned_data["created_to"] == make_aware(
        dt.datetime.combine(date, dt.datetime.max.time())
    )


@pytest.mark.django_db
def test_query_kwargs():
    data = {
        "created_from": "A",
        "created_to": "B",
        "country": "E",
        "supplier": "F",
    }
    assert OnHoldOrderFilter().query_kwargs(data) == {
        "created_at__gte": "A",
        "created_at__lte": "B",
        "region__name": "E",
        "product__supplier": "F",
        "on_hold": True,
        "closed_at__isnull": True,
    }


@pytest.mark.django_db
def test_text_search():
    search_text = "search text"
    qs = mock.Mock()
    OnHoldOrderFilter().text_search(search_text, qs)
    qs.filter.assert_called_once_with(
        Q(
            Q(product__sku__icontains=search_text)
            | Q(product__product_range__name__icontains=search_text)
            | Q(product_asin__icontains=search_text)
        )
    )


@pytest.mark.django_db
def test_search_by_sku(order):
    form = OnHoldOrderFilter({"search": order.product.sku})
    assert form.is_valid()
    assert order in form.get_queryset()


@pytest.mark.django_db
def test_orders_by_created_at_by_default():
    form = OnHoldOrderFilter({})
    assert form.is_valid()
    qs = form.get_queryset()
    assert 'ORDER BY "fba_fbaorder"."created_at" DESC' in str(qs.query)


@pytest.mark.django_db
def test_sort_by_field():
    form = OnHoldOrderFilter({"sort_by": "product__sku"})
    assert form.is_valid()
    qs = form.get_queryset()
    assert 'ORDER BY "inventory_baseproduct"."sku" ASC' in str(qs.query)


@pytest.mark.django_db
def test_does_not_return_orders_not_on_hold(not_on_hold_order):
    form = OnHoldOrderFilter({})
    assert form.is_valid()
    qs = form.get_queryset()
    assert qs.contains(not_on_hold_order) is False
