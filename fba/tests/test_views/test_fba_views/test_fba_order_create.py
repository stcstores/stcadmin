from unittest import mock

import pytest
from django.contrib import messages
from django.urls import reverse

from fba.forms import FBAOrderForm
from fba.models import FBAOrder
from fba.views.fba import FBAOrderCreate


def test_template_name_attribute():
    assert FBAOrderCreate.template_name == "fba/fbaorder_form.html"


def test_form_class_attribute():
    assert FBAOrderCreate.form_class == FBAOrderForm


@pytest.fixture
def product(product_factory):
    return product_factory.create()


@pytest.fixture
def region(fba_region_factory):
    return fba_region_factory.create(active=True)


@pytest.fixture
def other_orders(fba_order_factory, product):
    fba_order_factory.create_batch(3, status_not_processed=True, product=product)
    fba_order_factory.create(status_fulfilled=True, product=product)


@pytest.fixture
def mock_stock_manager():
    with mock.patch("fba.views.fba.StockManager") as m:
        yield m


@pytest.fixture
def url(mock_stock_manager, product):
    return reverse("fba:create_order", args=[product.pk])


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


def test_uses_template(get_response):
    assert "fba/fbaorder_form.html" in (t.name for t in get_response.templates)


def test_status_code(get_response):
    assert get_response.status_code == 200


def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


def test_form_in_context(get_response):
    assert isinstance(get_response.context["form"], FBAOrderForm)


def test_product_in_context(get_response, product):
    assert get_response.context["product"] == product


def test_stock_level_in_context(mock_stock_manager, get_response):
    value = get_response.context["stock_level"]
    assert value == mock_stock_manager.get_stock_level.return_value


def test_existing_order_count_in_context(get_response):
    assert get_response.context["existing_order_count"] == 0


@pytest.mark.django_db
def test_existing_order_count_with_existing_order(other_orders, get_response):
    assert get_response.context["existing_order_count"] == 3


@pytest.fixture
def multipack_product(multipack_product_factory):
    return multipack_product_factory.create()


@pytest.fixture
def combination_product(combination_product_link_factory):
    return combination_product_link_factory.create().combination_product


@pytest.fixture
def multipack_product_url(mock_stock_manager, multipack_product):
    return reverse("fba:create_order", args=[multipack_product.pk])


@pytest.fixture
def combination_product_url(mock_stock_manager, combination_product):
    return reverse("fba:create_order", args=[combination_product.pk])


def test_initial_data(get_response, product):
    assert get_response.context["form"].initial == {
        "product": product,
        "product_weight": product.weight_grams,
        "product_hs_code": product.hs_code,
        "product_purchase_price": product.purchase_price,
        "product_is_multipack": False,
    }


def test_initial_data_product_is_multipack_with_multipack_product(
    group_logged_in_client, multipack_product_url
):
    response = group_logged_in_client.get(multipack_product_url)
    assert response.context["form"].initial["product_is_multipack"] is True


def test_initial_data_product_is_multipack_with_combination_product(
    group_logged_in_client, combination_product_url
):
    response = group_logged_in_client.get(combination_product_url)
    assert response.context["form"].initial["product_is_multipack"] is True


@pytest.fixture
def form_data(region, product):
    return {
        "region": region.pk,
        "product_asin": "ntYNHeMhdpbWKp",
        "selling_price": 2182,
        "FBA_fee": 709,
        "aproximate_quantity": 328,
        "is_combinable": False,
        "on_hold": False,
        "is_fragile": False,
        "notes": "Long produce matter.",
        "product": product.pk,
        "product_weight": 2325,
        "product_hs_code": "xUANQwJwUfMUwE",
        "product_purchase_price": "52.49",
        "product_is_multipack": False,
    }


@pytest.fixture
def invalid_form_data(form_data):
    form_data["region"] = 345467890
    return form_data


@pytest.fixture
def post_response(group_logged_in_client, url, form_data):
    return group_logged_in_client.post(url, form_data)


def test_redirect(post_response, product):
    assert post_response.status_code == 302
    order = FBAOrder.objects.get(product=product)
    assert post_response["Location"] == order.get_absolute_url()


def test_creates_fba_order(post_response, product):
    assert FBAOrder.objects.filter(product=product).exists()


def test_invalid_post(group_logged_in_client, url, invalid_form_data):
    response = group_logged_in_client.post(url, invalid_form_data)
    assert response.status_code == 200


def test_adds_message(group_logged_in_client, url, form_data, product):
    response = group_logged_in_client.post(url, form_data, follow=True)
    message = list(response.context["messages"])[0]
    assert message.message == f"Created new FBA order for product {product.sku}."
    assert message.level == messages.SUCCESS


@pytest.mark.django_db
def test_get_stock_level(mock_stock_manager, product):
    value = FBAOrderCreate().get_stock_level(product)
    mock_stock_manager.get_stock_level.assert_called_once_with(product)
    assert value == mock_stock_manager.get_stock_level.return_value


@pytest.mark.django_db
def test_get_stock_level_with_error(mock_stock_manager, product):
    mock_stock_manager.get_stock_level.side_effect = Exception()
    value = FBAOrderCreate().get_stock_level(product)
    mock_stock_manager.get_stock_level.assert_called_once_with(product)
    assert value == 0
