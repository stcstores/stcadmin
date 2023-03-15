from unittest import mock

import pytest
from django.contrib import messages
from django.urls import reverse

from inventory import forms


@pytest.fixture
def product_range(product_range_factory):
    return product_range_factory.create()


@pytest.fixture
def products(product_range, product_factory):
    return product_factory.create_batch(3, product_range=product_range)


@pytest.fixture
def url(product_range):
    return reverse("inventory:product_order", kwargs={"range_pk": product_range.pk})


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.fixture
def mock_forms(products):
    return [mock.Mock() for product in products]


@pytest.fixture
def mock_formset(mock_forms):
    mock_formset = mock.MagicMock()
    mock_formset.is_valid = mock.Mock(return_value=True)
    mock_formset.__iter__.return_value = mock_forms
    return mock_formset


@pytest.fixture
def mock_form_class(mock_formset):
    with mock.patch(
        "inventory.views.product_order.ProductOrderFormSet",
    ) as mock_form_class:
        mock_form_class.return_value = mock_formset
        yield mock_form_class


@pytest.fixture
def post_data():
    return {"one": 1}


@pytest.fixture
def post_response(post_data, group_logged_in_client, url):
    return group_logged_in_client.post(url, post_data)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "inventory/product_range/product_order.html" in (
        t.name for t in get_response.templates
    )


@pytest.mark.django_db
def test_sets_up_form_set_for_get_request(mock_form_class, products, get_response):
    mock_form_class.assert_called_once_with(
        None, form_kwargs=[{"product": p} for p in products]
    )


@pytest.mark.django_db
def test_product_range_in_context(product_range, get_response):
    assert get_response.context["product_range"] == product_range


@pytest.mark.django_db
def test_formset_in_context(get_response):
    formset = get_response.context["formset"]
    assert isinstance(formset, forms.ProductOrderFormSet)


@pytest.mark.django_db
def test_form_is_saved(mock_form_class, mock_forms, group_logged_in_client, url):
    group_logged_in_client.post(url, {})
    for form in mock_forms:
        form.save.assert_called_once_with()


@pytest.mark.django_db
def test_success_redirect(mock_form_class, group_logged_in_client, url):
    response = group_logged_in_client.post(url, {})
    assert response.status_code == 302
    assert response["location"] == url


@pytest.mark.django_db
def test_form_valid_adds_message(mock_form_class, group_logged_in_client, url):
    group_logged_in_client.post(url, {})
    response = group_logged_in_client.get("")
    message = list(response.context["messages"])[0]
    assert message.message == "Variation Order Updated"
    assert message.level == messages.SUCCESS


@pytest.mark.django_db
def test_returns_get_response_for_invaild_post(post_response):
    assert post_response.status_code == 200
    assert "formset" in post_response.context
