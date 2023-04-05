from unittest import mock

import pytest
from django.contrib import messages
from django.urls import reverse

from inventory import forms, models
from inventory.views.product_editor import EditNewVariation


@pytest.fixture
def product_range(product_range_factory):
    return product_range_factory.create(status=models.ProductRange.CREATING)


@pytest.fixture
def product(product_range, product_factory):
    return product_factory.create(product_range=product_range)


@pytest.fixture
def url(product):
    return reverse("inventory:edit_new_variation", kwargs={"pk": product.pk})


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.fixture
def mock_form(product):
    with mock.patch(
        "inventory.views.product_editor.EditNewVariation.get_form_class",
    ) as mock_get_form_class:
        mock_form = mock.MagicMock(instance=product)
        mock_form.is_valid = mock.Mock(return_value=True)
        mock_form.save = mock.Mock(return_value=product)
        mock_get_form_class.return_value.return_value = mock_form
        yield mock_form


@pytest.fixture
def post_response(post_data, group_logged_in_client, url):
    return group_logged_in_client.post(url, post_data)


def test_uses_form():
    form_class = EditNewVariation().get_form_class()
    assert form_class == forms.EditProductForm


@pytest.mark.django_db
def test_uses_template(mock_form, get_response):
    assert "inventory/product_editor/edit_new_variation.html" in (
        t.name for t in get_response.templates
    )


@pytest.mark.django_db
def test_form_in_context(mock_form, get_response):
    assert get_response.context["form"] == mock_form


@pytest.mark.django_db
def test_product_in_context(mock_form, product, get_response):
    assert get_response.context["product"] == product


@pytest.mark.django_db
def test_product_range_in_context(mock_form, product_range, get_response):
    assert get_response.context["product_range"] == product_range


@pytest.mark.django_db
def test_form_is_saved(mock_form, group_logged_in_client, url):
    group_logged_in_client.post(url, {})
    mock_form.save.assert_called_once_with()


@pytest.mark.django_db
def test_success_redirect(mock_form, group_logged_in_client, url, product_range):
    response = group_logged_in_client.post(url, {})
    assert response.status_code == 302
    assert response["location"] == reverse(
        "inventory:edit_new_product", kwargs={"range_pk": product_range.pk}
    )


@pytest.mark.django_db
def test_form_valid_adds_message(product, mock_form, group_logged_in_client, url):
    response = group_logged_in_client.post(url, {}, follow=True)
    message = list(response.context["messages"])[0]
    assert message.message == f"{product.full_name} Updated"
    assert message.level == messages.SUCCESS
