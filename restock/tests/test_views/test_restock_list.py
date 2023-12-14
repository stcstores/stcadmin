import pytest
from django.urls import reverse


@pytest.fixture
def open_reorder(reorder_factory):
    return reorder_factory.create(closed=False)


@pytest.fixture
def closed_reorder(reorder_factory):
    return reorder_factory.create(closed=True)


@pytest.fixture
def url():
    return reverse("restock:restock_list")


@pytest.fixture
def get_response(url, group_logged_in_client):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "restock/restock_list.html" in [t.name for t in get_response.templates]


@pytest.mark.django_db
def test_suppliers_in_context(open_reorder, get_response):
    assert open_reorder.product.supplier in get_response.context["suppliers"]


@pytest.mark.django_db
def test_closed_order_supplier_not_in_context(closed_reorder, get_response):
    assert closed_reorder.product.supplier not in get_response.context["suppliers"]
