from unittest import mock

import pytest
from django.urls import reverse

from inventory import forms
from inventory.views.product_editor import EditAllVariations


@pytest.fixture
def product_range(product_range_factory):
    return product_range_factory.create()


@pytest.fixture
def products(product_range, product_factory):
    return product_factory.create_batch(3, product_range=product_range)


@pytest.fixture
def url(product_range):
    return reverse(
        "inventory:edit_all_variations", kwargs={"range_pk": product_range.pk}
    )


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
        "inventory.views.product_editor.EditAllVariations.get_form_class",
    ) as mock_get_form_class:
        mock_form_class = mock.Mock()
        mock_form_class.return_value = mock_formset
        mock_get_form_class.return_value = mock_form_class
        yield mock_form_class


@pytest.fixture
def post_response(post_data, group_logged_in_client, url):
    return group_logged_in_client.post(url, post_data)


def test_uses_product_formset():
    form_class = EditAllVariations().get_form_class()
    assert form_class == forms.ProductFormset


@pytest.mark.django_db
def test_uses_template(mock_form_class, get_response):
    assert "inventory/product_editor/edit_all_variations.html" in [
        t.name for t in get_response.templates
    ]


@pytest.mark.django_db
def test_get_form_kwargs(mock_form_class, product_range, products, get_response):
    form_kwargs = mock_form_class.call_args.kwargs["form_kwargs"]
    assert isinstance(form_kwargs, list)
    assert len(form_kwargs) == len(products)
    for item in form_kwargs:
        assert item["instance"] in products


@pytest.mark.django_db
def test_form_in_context(mock_form_class, mock_formset, get_response):
    assert get_response.context["formset"] == mock_formset


@pytest.mark.django_db
def test_product_range_in_context(mock_form_class, product_range, get_response):
    assert get_response.context["product_range"] == product_range


@pytest.mark.django_db
def test_variations_in_context(mock_form_class, product_range, products, get_response):
    assert get_response.context["variations"] == product_range.variation_option_values()


@pytest.mark.django_db
def test_form_is_saved(mock_form_class, mock_forms, group_logged_in_client, url):
    group_logged_in_client.post(url, {})
    for form in mock_forms:
        form.save.assert_called_once_with()


@pytest.mark.django_db
def test_success_redirect(mock_form_class, group_logged_in_client, url, product_range):
    response = group_logged_in_client.post(url, {})
    assert response.status_code == 302
    assert response["location"] == reverse(
        "inventory:add_images", kwargs={"range_pk": product_range.pk}
    )
