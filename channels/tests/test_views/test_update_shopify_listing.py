from unittest import mock

import pytest
from django.forms import BaseFormSet
from django.urls import reverse

from channels.forms import ShopifyListingForm
from channels.models.shopify_models import ShopifyListing
from channels.views import UpdateShopifyListing


@pytest.fixture
def template():
    return "channels/shopify/shopify_listing_form.html"


def test_template_name_attribute(template):
    assert UpdateShopifyListing.template_name == template


def test_form_class_attribute():
    assert UpdateShopifyListing.form_class == ShopifyListingForm


def test_model_attribute():
    assert UpdateShopifyListing.model == ShopifyListing


@pytest.fixture
def product_range(product_range_factory):
    return product_range_factory.create()


@pytest.fixture
def products(product_range, product_factory):
    return product_factory.create_batch(3, product_range=product_range)


@pytest.fixture
def shopify_listing(shopify_listing_factory, product_range):
    return shopify_listing_factory.create(product_range=product_range)


@pytest.fixture
def url(shopify_listing):
    return reverse("channels:update_shopify_listing", args=[shopify_listing.pk])


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


def test_uses_template(template, get_response):
    assert template in [t.name for t in get_response.templates]


def test_status_code(get_response):
    assert get_response.status_code == 200


def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


def test_form_in_context(get_response):
    assert isinstance(get_response.context["form"], ShopifyListingForm)


def test_formset_in_context(get_response):
    assert isinstance(get_response.context["formset"], BaseFormSet)


@pytest.fixture
def form_data(product_range):
    return {
        "product_range": product_range.pk,
        "title": "Title",
        "description": "Description",
    }


@pytest.fixture
def invalid_form_data(form_data):
    form_data["product_range"] = 345467890
    return form_data


@pytest.fixture
def mock_get_form(product_range):
    with mock.patch("channels.views.UpdateShopifyListing.get_form") as m:
        m.return_value.is_valid.return_value = True
        m.return_value.save.return_value = product_range
        yield m


@pytest.fixture
def mock_variation_formset():
    with mock.patch("channels.views.forms.VariationFormset") as m:
        m.is_valid.return_value.return_value = True
        yield m


@pytest.fixture
def post_response(group_logged_in_client, url, form_data):
    return group_logged_in_client.post(url, form_data)


@pytest.mark.django_db
def test_redirect(mock_get_form, mock_variation_formset, post_response, product_range):
    assert post_response.status_code == 302
    assert post_response["Location"] == reverse(
        "channels:update_shopify_collections", kwargs={"pk": product_range.pk}
    )


def test_invalid_post(group_logged_in_client, url, invalid_form_data):
    response = group_logged_in_client.post(url, invalid_form_data)
    assert response.status_code == 200


@pytest.mark.django_db
def test_saves_form(mock_get_form, mock_variation_formset, post_response):
    mock_get_form.return_value.save.assert_called_once_with()


@pytest.mark.django_db
def test_saves_formset(mock_get_form, mock_variation_formset, post_response):
    mock_variation_formset.return_value.save.assert_called_once_with()
