from decimal import Decimal

import pytest
from django import forms

from channels.forms import ShopifyVariationForm


@pytest.fixture
def shopify_variation(shopify_variation_factory):
    return shopify_variation_factory.create()


@pytest.fixture
def shopify_listing(shopify_listing_factory):
    return shopify_listing_factory.create()


@pytest.fixture
def product(product_factory):
    return product_factory.create()


@pytest.fixture
def form_data(shopify_listing, product):
    return {
        "listing": shopify_listing,
        "product": product,
        "price": Decimal("5.20"),
    }


def test_listing_field_uses_hidden_input_widget():
    form = ShopifyVariationForm()
    assert isinstance(form.fields["listing"].widget, forms.HiddenInput)


def test_product_field_uses_summernote_widget():
    form = ShopifyVariationForm()
    assert isinstance(form.fields["product"].widget, forms.HiddenInput)


@pytest.mark.django_db
def test_object_creation(form_data):
    form = ShopifyVariationForm(form_data)
    assert form.is_valid() is True
    form.save()
    assert form.instance.pk
    assert form.instance.price == form_data["price"]


@pytest.mark.django_db
def test_object_update(shopify_variation, shopify_listing, form_data):
    form = ShopifyVariationForm(form_data, instance=shopify_variation)
    assert form.is_valid() is True
    form.save()
    shopify_variation.refresh_from_db()
    assert shopify_variation.listing == shopify_listing
