import pytest
from django.urls import reverse

from inventory.models import SupplierContact


@pytest.fixture
def supplier_contact(supplier_contact_factory):
    return supplier_contact_factory.create()


@pytest.fixture
def url(supplier_contact):
    return reverse(
        "inventory:delete_supplier_contact",
        kwargs={"pk": supplier_contact.pk},
    )


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.fixture
def post_data(supplier_contact):
    return {}


@pytest.fixture
def post_response(group_logged_in_client, url, post_data):
    return group_logged_in_client.post(url, post_data)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "inventory/suppliers/suppliercontact_confirm_delete.html" in (
        t.name for t in get_response.templates
    )


@pytest.mark.django_db
def test_form_in_context(get_response):
    assert "form" in get_response.context


@pytest.mark.django_db
def test_contact_is_deleted(post_response, supplier_contact):
    assert SupplierContact.objects.filter(pk=supplier_contact.pk).exists() is False


@pytest.mark.django_db
def test_success_redirect(supplier_contact, post_response):
    assert post_response.status_code == 302
    assert post_response["location"] == reverse(
        "inventory:supplier", args=[supplier_contact.supplier.id]
    )
