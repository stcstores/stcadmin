import pytest
from django.urls import reverse


@pytest.fixture
def supplier_contact(supplier_contact_factory):
    return supplier_contact_factory.create()


@pytest.fixture
def url(supplier_contact):
    return reverse(
        "inventory:update_supplier_contact", kwargs={"pk": supplier_contact.pk}
    )


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.fixture
def post_data(supplier_contact):
    return {
        "supplier": supplier_contact.supplier.pk,
        "name": supplier_contact.name,
        "phone": supplier_contact.phone,
        "email": supplier_contact.email,
        "note": supplier_contact.notes,
    }


@pytest.fixture
def post_response(group_logged_in_client, url, post_data):
    return group_logged_in_client.post(url, post_data)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "inventory/suppliercontact_form.html" in (
        t.name for t in get_response.templates
    )


@pytest.mark.django_db
def test_form_in_context(get_response):
    assert "form" in get_response.context


@pytest.mark.django_db
def test_supplier_in_context(get_response, supplier_contact):
    assert get_response.context["supplier"] == supplier_contact.supplier


@pytest.mark.django_db
def test_form_is_saved(group_logged_in_client, url, post_data, supplier_contact):
    post_data["name"] == "Updated Supplier Contact Name"
    group_logged_in_client.post(url, post_data)
    supplier_contact.refresh_from_db()
    assert supplier_contact.name == post_data["name"]


@pytest.mark.django_db
def test_success_redirect(supplier_contact, post_response):
    assert post_response.status_code == 302
    assert post_response["location"] == supplier_contact.get_absolute_url()
