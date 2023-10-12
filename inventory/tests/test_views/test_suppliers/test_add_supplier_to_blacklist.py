from unittest import mock

import pytest
from django.urls import reverse


@pytest.fixture
def suppliers(supplier_factory):
    return supplier_factory.create_batch(3)


@pytest.fixture
def name():
    return "Blacklisted Supplier"


@pytest.fixture
def supplier(supplier_factory):
    return supplier_factory.create()


@pytest.fixture
def mock_form(supplier):
    mock_form = mock.Mock()
    mock_form.instance = supplier
    return mock_form


@pytest.fixture
def mock_get_form_class(mock_form):
    with mock.patch(
        "inventory.views.suppliers.AddSupplierToBlacklist.get_form_class"
    ) as mock_get_form_class:
        mock_form_class = mock.Mock()
        mock_form_class.return_value = mock_form
        mock_get_form_class.return_value = mock_form_class
        yield mock_form_class


@pytest.fixture
def url():
    return reverse("inventory:add_supplier_to_blacklist")


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.fixture
def post_response(group_logged_in_client, url, name):
    return group_logged_in_client.post(url, {"name": name})


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "inventory/suppliers/add_blacklisted_supplier.html" in (
        t.name for t in get_response.templates
    )


@pytest.mark.django_db
def test_suppliers_in_context(suppliers, get_response):
    for supplier in suppliers:
        assert supplier.name in get_response.context["suppliers"]


@pytest.mark.django_db
def test_form_is_valid_called(mock_get_form_class, mock_form, post_response):
    mock_form.is_valid.assert_called_once_with()


@pytest.mark.django_db
def test_form_save_called(mock_get_form_class, mock_form, post_response):
    mock_form.save.assert_called_once_with()


@pytest.mark.django_db
def test_get_success_url(mock_get_form_class, mock_form, supplier, post_response):
    assert post_response["location"] == supplier.get_absolute_url()
