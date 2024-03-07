import datetime as dt
from unittest import mock

import pytest
from django.db.models import Q
from django.utils.timezone import make_aware, now

from fba.forms import FBAOrderFilter


@pytest.fixture
def order(fba_order_factory):
    return fba_order_factory.create()


@pytest.fixture
def date():
    return dt.date(2023, 3, 3)


@pytest.mark.django_db
def test_supplier_filter(fba_order_factory, supplier_factory):
    order = fba_order_factory.create(created_at=now())
    other_supplier = supplier_factory.create()
    form = FBAOrderFilter()
    choices = form.fields["supplier"].choices
    assert choices[0] == ("", "---------")
    assert (order.product.supplier.pk, order.product.supplier.name) in choices
    assert (other_supplier.pk, other_supplier.name) not in choices


@pytest.mark.django_db
def test_supplier_filter_ignores_suppliers_from_old_orders(fba_order_factory):
    order = fba_order_factory.create(created_at=now() - dt.timedelta(days=370))
    form = FBAOrderFilter()
    choices = form.fields["supplier"].choices
    assert choices[0] == ("", "---------")
    assert (order.product.supplier.pk, order.product.supplier.name) not in choices


@pytest.mark.django_db
def test_country_empty_label():
    assert FBAOrderFilter().fields["country"].empty_label == "All"


@pytest.mark.django_db
def test_clean_date_method(date):
    time = dt.datetime.min.time()
    returned_value = FBAOrderFilter().clean_date(date, time)
    assert returned_value == make_aware(dt.datetime.combine(date, time))


@pytest.mark.django_db
def test_clean_date_method_handles_none():
    assert FBAOrderFilter().clean_date(None, dt.datetime.max.time()) is None


@pytest.mark.django_db
@mock.patch("fba.forms.FBAOrderFilter.clean_date")
def test_clean_created_from(mock_clean_date, date):
    form = FBAOrderFilter({"created_from": date})
    assert form.is_valid() is True
    mock_clean_date.assert_has_calls([mock.call(date, dt.datetime.min.time())])
    assert form.cleaned_data["created_from"] == mock_clean_date.return_value


@pytest.mark.django_db
@mock.patch("fba.forms.FBAOrderFilter.clean_date")
def test_clean_created_to(mock_clean_date, date):
    form = FBAOrderFilter({"created_to": date})
    assert form.is_valid() is True
    mock_clean_date.assert_has_calls([mock.call(date, dt.datetime.max.time())])
    assert form.cleaned_data["created_to"] == mock_clean_date.return_value


@pytest.mark.django_db
@mock.patch("fba.forms.FBAOrderFilter.clean_date")
def test_clean_fulfilled_from(mock_clean_date, date):
    form = FBAOrderFilter({"fulfilled_from": date})
    assert form.is_valid() is True
    mock_clean_date.assert_has_calls([mock.call(date, dt.datetime.min.time())])
    assert form.cleaned_data["fulfilled_from"] == mock_clean_date.return_value


@pytest.mark.django_db
@mock.patch("fba.forms.FBAOrderFilter.clean_date")
def test_clean_fulfilled_to(mock_clean_date, date):
    form = FBAOrderFilter({"fulfilled_to": date})
    assert form.is_valid() is True
    mock_clean_date.assert_has_calls([mock.call(date, dt.datetime.max.time())])
    assert form.cleaned_data["fulfilled_to"] == mock_clean_date.return_value


@pytest.mark.django_db
@pytest.mark.parametrize(
    "value,expected",
    (
        (FBAOrderFilter.PRIORITISED, True),
        (FBAOrderFilter.UNPRIORITISED, False),
        (None, None),
    ),
)
def test_clean_prioritised(value, expected):
    form = FBAOrderFilter({"prioritised": value})
    assert form.is_valid() is True
    assert form.cleaned_data["prioritised"] is expected


@pytest.mark.django_db
def test_query_kwargs():
    data = {
        "created_from": "A",
        "created_to": "B",
        "fulfilled_from": None,
        "fulfilled_to": "C",
        "status": "",
        "country": "E",
        "supplier": "F",
        "fulfilled_by": "G",
    }
    assert FBAOrderFilter().query_kwargs(data) == {
        "created_at__gte": "A",
        "created_at__lte": "B",
        "closed_at__lte": "C",
        "region__name": "E",
        "product__supplier": "F",
        "fulfilled_by": "G",
    }


@pytest.mark.django_db
def test_text_search():
    search_text = "search text"
    qs = mock.Mock()
    FBAOrderFilter().text_search(search_text, qs)
    qs.filter.assert_called_once_with(
        Q(
            Q(product__sku__icontains=search_text)
            | Q(product__product_range__name__icontains=search_text)
            | Q(tracking_numbers__tracking_number=search_text)
            | Q(product_asin__icontains=search_text)
        )
    )


@pytest.mark.django_db
def test_filter_priority_with_true():
    qs = mock.Mock()
    form = FBAOrderFilter({"prioritised": FBAOrderFilter.PRIORITISED})
    assert form.is_valid() is True
    assert form.filter_priority(qs) == qs.prioritised.return_value


@pytest.mark.django_db
def test_filter_priority_with_false():
    qs = mock.Mock()
    form = FBAOrderFilter({"prioritised": FBAOrderFilter.UNPRIORITISED})
    assert form.is_valid() is True
    assert form.filter_priority(qs) == qs.unprioritised.return_value


@pytest.mark.django_db
def test_filter_priority_with_none():
    qs = mock.Mock()
    form = FBAOrderFilter({"prioritised": None})
    assert form.is_valid() is True
    assert form.filter_priority(qs) == qs


@pytest.mark.django_db
def test_search_by_sku(order):
    form = FBAOrderFilter({"search": order.product.sku})
    assert form.is_valid()
    assert order in form.get_queryset()


@pytest.mark.django_db
def test_orders_by_created_at_by_default():
    form = FBAOrderFilter({})
    assert form.is_valid()
    qs = form.get_queryset()
    assert 'ORDER BY "fba_fbaorder"."created_at" DESC' in str(qs.query)


@pytest.mark.django_db
def test_sort_by_field():
    form = FBAOrderFilter({"sort_by": "product__sku"})
    assert form.is_valid()
    qs = form.get_queryset()
    assert 'ORDER BY "inventory_baseproduct"."sku" ASC' in str(qs.query)


@pytest.fixture
def open_order(fba_order_factory):
    return fba_order_factory.create(status_not_processed=True)


@pytest.fixture
def closed_order(fba_order_factory):
    return fba_order_factory.create(status_fulfilled=True)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "value,open_order_included,closed_order_included",
    (
        (FBAOrderFilter.CLOSED, False, True),
        (FBAOrderFilter.NOT_CLOSED, True, False),
        (None, True, True),
    ),
)
def test_closed_field(
    value, open_order_included, closed_order_included, open_order, closed_order
):
    form = FBAOrderFilter({"closed": value})
    assert form.is_valid()
    qs = form.get_queryset()
    assert qs.contains(open_order) is open_order_included
    assert qs.contains(closed_order) is closed_order_included
