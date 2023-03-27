import pytest
from django.urls import reverse

from inventory import models


@pytest.fixture
def supplier(supplier_factory):
    return supplier_factory.create()


@pytest.fixture
def url(supplier):
    return reverse(
        "inventory:create_supplier_contact", kwargs={"supplier_pk": supplier.pk}
    )


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.fixture
def post_data(supplier):
    return {
        "supplier": supplier.pk,
        "name": "New Supplier Contact",
        "phone": "9092990030",
        "email": "noone@nowhere.com",
        "note": "some text",
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
def test_supplier_in_context(get_response, supplier):
    assert get_response.context["supplier"] == supplier


@pytest.mark.django_db
def test_get_initial(get_response, supplier):
    assert get_response.context["form"].initial["supplier"] == supplier


@pytest.mark.django_db
def test_form_is_saved(post_response):
    assert post_response.status_code == 302
    assert models.SupplierContact.objects.filter(name="New Supplier Contact").exists()


@pytest.mark.django_db
def test_success_redirect(supplier, post_data, group_logged_in_client, url):
    response = group_logged_in_client.post(url, post_data)
    object = models.SupplierContact.objects.get(
        supplier=supplier, name="New Supplier Contact"
    )
    assert response.status_code == 302
    assert response["location"] == object.get_absolute_url()
