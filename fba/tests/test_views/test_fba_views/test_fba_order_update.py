from unittest import mock

import pytest
from django.contrib import messages
from django.urls import reverse

from fba.forms import FBAOrderForm
from fba.models import FBAOrder
from fba.views.fba import FBAOrderUpdate


def test_template_name_attribute():
    assert FBAOrderUpdate.template_name == "fba/fbaorder_form.html"


def test_form_class_attribute():
    assert FBAOrderUpdate.form_class == FBAOrderForm


def test_model_attribute():
    assert FBAOrderUpdate.model == FBAOrder


@pytest.fixture
def fba_order(fba_order_factory):
    return fba_order_factory.create()


@pytest.fixture
def mock_stock_manager():
    with mock.patch("fba.views.fba.StockManager") as m:
        yield m


@pytest.fixture
def url(mock_stock_manager, fba_order):
    return reverse("fba:update_fba_order", args=[fba_order.pk])


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


def test_uses_template(get_response):
    assert "fba/fbaorder_form.html" in [t.name for t in get_response.templates]


def test_status_code(get_response):
    assert get_response.status_code == 200


def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


def test_product_in_context(get_response, fba_order):
    assert get_response.context["product"] == fba_order.product


def test_stock_level_in_context(mock_stock_manager, get_response):
    value = get_response.context["stock_level"]
    assert value == mock_stock_manager.get_stock_level.return_value


def test_form_in_context(get_response):
    assert isinstance(get_response.context["form"], FBAOrderForm)


@pytest.mark.django_db
def test_get_stock_level(mock_stock_manager, fba_order):
    value = FBAOrderUpdate().get_stock_level(fba_order.product)
    mock_stock_manager.get_stock_level.assert_called_once_with(fba_order.product)
    assert value == mock_stock_manager.get_stock_level.return_value


@pytest.mark.django_db
def test_get_stock_level_with_error(mock_stock_manager, fba_order):
    mock_stock_manager.get_stock_level.side_effect = Exception()
    value = FBAOrderUpdate().get_stock_level(fba_order.product)
    mock_stock_manager.get_stock_level.assert_called_once_with(fba_order.product)
    assert value == 0


def test_initial(get_response, fba_order):
    assert get_response.context["form"].initial["country"] == fba_order.region.country


@pytest.fixture
def form_data(fba_order):
    return {
        "region": fba_order.region.pk,
        "product_asin": "ntYNHeMhdpbWKp",
        "selling_price": 2182,
        "FBA_fee": 709,
        "aproximate_quantity": 328,
        "is_combinable": False,
        "on_hold": False,
        "is_fragile": False,
        "notes": "Long produce matter.",
        "product": fba_order.product.pk,
        "product_weight": 2325,
        "product_hs_code": "xUANQwJwUfMUwE",
        "product_purchase_price": "52.49",
        "product_is_multipack": False,
    }


@pytest.fixture
def form_data_with_invalid_item(form_data):
    form_data["region"] = 657890
    return form_data


@pytest.fixture
def post_response(group_logged_in_client, url, form_data):
    return group_logged_in_client.post(url, form_data)


def test_updates_order(post_response, fba_order, form_data):
    fba_order.refresh_from_db()
    assert fba_order.notes == form_data["notes"]


def test_redirect(post_response, fba_order):
    assert post_response.status_code == 302
    assert post_response["Location"] == fba_order.get_absolute_url()


def test_adds_message(group_logged_in_client, url, form_data):
    response = group_logged_in_client.post(url, form_data, follow=True)
    message = list(response.context["messages"])[0]
    assert message.message == "FBA order updated."
    assert message.level == messages.SUCCESS


def test_invalid_data(group_logged_in_client, url, form_data_with_invalid_item):
    response = group_logged_in_client.post(url, form_data_with_invalid_item)
    assert response.status_code == 200
