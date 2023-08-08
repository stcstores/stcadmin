import pytest
from django.urls import reverse


@pytest.fixture
def reorder(reorder_factory):
    return reorder_factory.create()


@pytest.fixture
def url():
    return reverse("restock:restock_list")


@pytest.fixture
def get_response(url, group_logged_in_client):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "restock/restock_list.html" in (t.name for t in get_response.templates)


@pytest.mark.django_db
def test_suppliers_in_context(reorder, get_response):
    assert reorder.product.supplier in get_response.context["suppliers"]
