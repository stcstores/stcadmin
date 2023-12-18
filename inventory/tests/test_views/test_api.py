import json
from unittest import mock

import pytest
from django.urls import reverse

from inventory import models


@mock.patch("inventory.views.api.models.new_product_sku")
def test_get_new_sku_view_calls_new_product_sku(
    mock_new_product_sku, group_logged_in_client
):
    group_logged_in_client.post(reverse("inventory:get_new_sku"))
    mock_new_product_sku.assert_called_once_with()


@mock.patch("inventory.views.api.models.new_product_sku")
def test_get_new_sku_view_returns_new_sku(mock_new_product_sku, group_logged_in_client):
    mock_new_product_sku.return_value = "TEST_SKU"
    response = group_logged_in_client.post(reverse("inventory:get_new_sku"))
    mock_new_product_sku.assert_called_once_with()
    assert response.content.decode("utf8") == mock_new_product_sku.return_value


@mock.patch("inventory.views.api.models.new_range_sku")
def test_get_new_range_sku_view_calls_new_product_sku(
    mock_new_range_sku, group_logged_in_client
):
    group_logged_in_client.post(reverse("inventory:get_new_range_sku"))
    mock_new_range_sku.assert_called_once_with()


@mock.patch("inventory.views.api.models.new_range_sku")
def test_get_new_range_sku_view_returns_new_sku(
    mock_new_range_sku, group_logged_in_client
):
    mock_new_range_sku.return_value = "TEST_SKU"
    response = group_logged_in_client.post(reverse("inventory:get_new_range_sku"))
    mock_new_range_sku.assert_called_once_with()
    assert response.content.decode("utf8") == mock_new_range_sku.return_value


@pytest.mark.django_db
def test_new_brand_creates_brand(group_logged_in_client):
    name = "New Test Brand"
    response = group_logged_in_client.post(
        reverse("inventory:new_brand"), {"name": name}
    )
    instance = models.Brand.objects.get(name=name)
    assert response.content.decode("utf8") == json.dumps(
        {"name": instance.name, "id": instance.pk}
    )


@pytest.mark.django_db
def test_new_manufacturer_creates_manufacturer(group_logged_in_client):
    name = "New Test Manufacturer"
    response = group_logged_in_client.post(
        reverse("inventory:new_manufacturer"), {"name": name}
    )
    instance = models.Manufacturer.objects.get(name=name)
    assert response.content.decode("utf8") == json.dumps(
        {"name": instance.name, "id": instance.pk}
    )


@pytest.mark.django_db
def test_new_supplier_creates_supplier(group_logged_in_client):
    name = "New Test Supplier"
    response = group_logged_in_client.post(
        reverse("inventory:new_supplier"), {"name": name}
    )
    instance = models.Supplier.objects.get(name=name)
    assert response.content.decode("utf8") == json.dumps(
        {"name": instance.name, "id": instance.pk}
    )


@pytest.fixture
def product_range(product_range_factory):
    return product_range_factory.create()


@pytest.fixture
def products(product_range, product_factory):
    return product_factory.create_batch(3, product_range=product_range)


@pytest.mark.django_db
def test_variation_list_context_contains_products(
    product_range, products, group_logged_in_client
):
    response = group_logged_in_client.get(
        reverse(
            "inventory:variation_list", kwargs={"product_range_pk": product_range.pk}
        )
    )
    assert list(response.context["products"]) == list(
        models.BaseProduct.objects.filter(
            product_range__id=product_range.id
        ).variations()
    )


@pytest.mark.django_db
def test_variation_list_uses_template(product_range, products, group_logged_in_client):
    response = group_logged_in_client.get(
        reverse(
            "inventory:variation_list", kwargs={"product_range_pk": product_range.pk}
        )
    )
    assert "inventory/product_search/variation_list.html" in [
        t.name for t in response.templates
    ]
