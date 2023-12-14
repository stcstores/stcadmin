import datetime as dt

import pytest
from django.urls import reverse

from restock.forms import UpdateSuplierOrderDateForm


@pytest.fixture
def supplier(supplier_factory):
    return supplier_factory.create()


@pytest.fixture
def url(supplier):
    return reverse(
        "restock:update_supplier_last_order_date", kwargs={"pk": supplier.pk}
    )


@pytest.fixture
def new_date():
    return dt.date(year=2023, month=10, day=9)


@pytest.fixture
def post_data(new_date):
    return {"last_ordered_from": new_date.strftime("%d/%m/%Y")}


@pytest.fixture
def get_response(url, group_logged_in_client):
    return group_logged_in_client.get(url)


@pytest.fixture
def post_response(url, group_logged_in_client, post_data):
    return group_logged_in_client.post(url, post_data)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "restock/update_supplier_last_ordered.html" in [
        t.name for t in get_response.templates
    ]


@pytest.mark.django_db
def test_form_in_context(get_response):
    assert isinstance(get_response.context["form"], UpdateSuplierOrderDateForm)


@pytest.mark.django_db
def test_updates_supplier(supplier, new_date, post_response):
    supplier.refresh_from_db()
    assert supplier.last_ordered_from == new_date


@pytest.mark.django_db
def test_redirects(supplier, post_response):
    assert post_response["location"] == supplier.get_absolute_url()
