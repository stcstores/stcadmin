from unittest import mock

import pytest
from django.urls import reverse

from inventory import forms


@pytest.fixture
def product_range(product_range_factory):
    return product_range_factory.create()


@pytest.fixture
def product(product_range, product_factory):
    return product_factory.create(product_range=product_range)


@pytest.fixture
def initial_variation(product_range, initial_variation_factory):
    return initial_variation_factory.create(product_range=product_range)


@pytest.fixture
def url(product_range):
    return reverse(
        "inventory:create_initial_variation", kwargs={"range_pk": product_range.pk}
    )


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.fixture
def mock_form(product_range):
    with mock.patch(
        "inventory.views.product_editor.CreateInitialVariation.get_form_class",
    ) as mock_get_form_class:
        mock_form = mock.Mock()
        mock_form.is_valid = mock.Mock(return_value=True)
        mock_form.save = mock.Mock(return_value=product_range.products.all()[0])
        mock_get_form_class.return_value.return_value = mock_form
        yield mock_form


@pytest.fixture
def post_response(post_data, group_logged_in_client, url):
    return group_logged_in_client.post(url, post_data)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "inventory/product_editor/create_initial_variation.html" in (
        t.name for t in get_response.templates
    )


@pytest.mark.django_db
def test_form_in_context(get_response):
    form = get_response.context["form"]
    assert isinstance(form, forms.InitialVariationForm)


@pytest.mark.django_db
def test_product_range_in_form_initial(product_range, get_response):
    initial = get_response.context["form"].initial
    assert initial["product_range"] == product_range


@pytest.mark.django_db
def test_form_is_saved(product, mock_form, group_logged_in_client, url):
    group_logged_in_client.post(url, {})
    mock_form.save.assert_called_once_with()


@pytest.mark.django_db
def test_success_redirect_with_initial_variation(
    initial_variation, mock_form, group_logged_in_client, url, product_range
):
    response = group_logged_in_client.post(url, {})
    assert response.status_code == 302
    assert response["location"] == reverse(
        "inventory:setup_variations", kwargs={"range_pk": product_range.pk}
    )


@pytest.mark.django_db
def test_success_redirect_with_product(
    product, mock_form, group_logged_in_client, url, product_range
):
    response = group_logged_in_client.post(url, {})
    assert response.status_code == 302
    assert response["location"] == reverse(
        "inventory:add_images", kwargs={"range_pk": product_range.pk}
    )
