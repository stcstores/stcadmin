from unittest import mock

import pytest
from django.contrib import messages
from django.urls import reverse

from inventory import forms


@pytest.fixture
def product_range(product_range_factory):
    return product_range_factory.create()


@pytest.fixture
def product(product_range, product_factory):
    return product_factory.create(product_range=product_range)


@pytest.fixture
def url(product):
    return reverse("inventory:product", kwargs={"pk": product.pk})


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.fixture
def mock_form(product):
    with mock.patch(
        "inventory.views.product.ProductView.get_form_class",
    ) as mock_get_form_class:
        mock_form = mock.Mock()
        mock_form.is_valid = mock.Mock(return_value=True)
        mock_form.save = mock.Mock(return_value=product)
        mock_get_form_class.return_value.return_value = mock_form
        yield mock_form


@pytest.fixture
def post_response(post_data, group_logged_in_client, url):
    return group_logged_in_client.post(url, post_data)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "inventory/product.html" in (t.name for t in get_response.templates)


@pytest.mark.django_db
def test_product_in_context(product, get_response):
    assert get_response.context["product"] == product


@pytest.mark.django_db
def test_product_range_in_context(product_range, get_response):
    assert get_response.context["product_range"] == product_range


@pytest.mark.django_db
def test_form_in_context(get_response):
    form = get_response.context["form"]
    assert isinstance(form, forms.EditProductForm)


@pytest.mark.django_db
def test_form_is_saved(mock_form, group_logged_in_client, url):
    group_logged_in_client.post(url, {})
    mock_form.save.assert_called_once_with()


@pytest.mark.django_db
def test_success_redirect(mock_form, group_logged_in_client, url):
    response = group_logged_in_client.post(url, {})
    assert response.status_code == 302
    assert response["location"] == url


@pytest.mark.django_db
def test_form_valid_adds_message(mock_form, group_logged_in_client, url):
    group_logged_in_client.post(url, {})
    response = group_logged_in_client.get("")
    message = list(response.context["messages"])[0]
    assert message.message == "Product Updated"
    assert message.level == messages.SUCCESS
