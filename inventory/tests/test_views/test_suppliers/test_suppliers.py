import pytest
from django.urls import reverse


@pytest.fixture
def suppliers(supplier_factory):
    return supplier_factory.create_batch(3)


@pytest.fixture
def url():
    return reverse("inventory:suppliers")


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "inventory/suppliers.html" in (t.name for t in get_response.templates)


@pytest.mark.django_db
def test_suppliers_in_context(suppliers, get_response):
    assert set(get_response.context["suppliers"]) == set(suppliers)
