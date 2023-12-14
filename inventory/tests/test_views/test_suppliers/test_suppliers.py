import pytest
from django.urls import reverse


@pytest.fixture
def active_suppliers(supplier_factory):
    return supplier_factory.create_batch(3, active=True)


@pytest.fixture
def inactive_suppliers(supplier_factory):
    return supplier_factory.create_batch(3, active=False)


@pytest.fixture
def blacklisted_suppliers(supplier_factory):
    return supplier_factory.create_batch(3, blacklisted=True)


@pytest.fixture
def url():
    return reverse("inventory:suppliers")


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "inventory/suppliers/suppliers.html" in [
        t.name for t in get_response.templates
    ]


@pytest.mark.django_db
def test_active_suppliers_in_context(active_suppliers, get_response):
    assert set(get_response.context["active_suppliers"]) == set(active_suppliers)


@pytest.mark.django_db
def test_inactive_suppliers_in_context(inactive_suppliers, get_response):
    assert set(get_response.context["inactive_suppliers"]) == set(inactive_suppliers)


@pytest.mark.django_db
def test_blacklisted_suppliers_in_context(blacklisted_suppliers, get_response):
    assert set(get_response.context["blacklisted_suppliers"]) == set(
        blacklisted_suppliers
    )
