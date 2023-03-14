import pytest
from django.urls import reverse


@pytest.fixture
def supplier(supplier_factory):
    return supplier_factory.create()


@pytest.fixture
def supplier_contacts(supplier_contact_factory, supplier):
    return supplier_contact_factory.create_batch(3, supplier=supplier)


@pytest.fixture
def url(supplier):
    return reverse("inventory:supplier", kwargs={"pk": supplier.pk})


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "inventory/supplier.html" in (t.name for t in get_response.templates)


@pytest.mark.django_db
def test_supplier_in_context(supplier, get_response):
    assert get_response.context["supplier"] == supplier


@pytest.mark.django_db
def test_contacts_in_context(supplier_contacts, get_response):
    assert set(get_response.context["contacts"]) == set(supplier_contacts)
