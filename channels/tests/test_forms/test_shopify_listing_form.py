import pytest
from django import forms
from django_summernote.widgets import SummernoteInplaceWidget

from channels.forms import ShopifyListingForm


@pytest.fixture
def shopify_listing(shopify_listing_factory):
    return shopify_listing_factory.create()


@pytest.fixture
def product_range(product_range_factory):
    return product_range_factory.create()


@pytest.fixture
def form_data(product_range):
    return {
        "product_range": product_range,
        "title": "Listing Title",
        "description": "Listing Description",
    }


def test_product_range_field_uses_hidden_input_widget():
    form = ShopifyListingForm()
    assert isinstance(form.fields["product_range"].widget, forms.HiddenInput)


def test_description_field_uses_summernote_widget():
    form = ShopifyListingForm()
    assert isinstance(form.fields["description"].widget, SummernoteInplaceWidget)


@pytest.mark.django_db
def test_object_creation(form_data):
    form = ShopifyListingForm(form_data)
    assert form.is_valid() is True
    form.save()
    assert form.instance.pk
    assert form.instance.title == form_data["title"]


@pytest.mark.django_db
def test_object_update(shopify_listing, form_data):
    form = ShopifyListingForm(form_data, instance=shopify_listing)
    assert form.is_valid() is True
    form.save()
    shopify_listing.refresh_from_db()
    assert shopify_listing.title == form_data["title"]
