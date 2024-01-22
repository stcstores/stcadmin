from unittest import mock

import pytest
from django.urls import reverse

from fba.models import FBARegion


@pytest.fixture
def region(fba_region_factory):
    return mock.Mock()


@pytest.fixture
def form_data():
    return {
        "zero_rated": "false",
        "selling_price": "55.2",
        "region": 5,
        "purchase_price": "2",
        "quantity": "27",
        "fba_fee": "4.8",
        "weight": "220",
        "stock_level": "55",
    }


@pytest.fixture
def calculation_dict():
    return {
        "channel_fee": 8.28,
        "currency_symbol": "$",
        "vat": 9.22,
        "postage_to_fba": 2.27,
        "postage_per_item": 0.08,
        "profit": 4.16,
        "percentage": 6.07,
        "purchase_price": 14.89,
        "max_quantity": 50,
        "max_quantity_no_stock": 100,
    }


@pytest.fixture
def mock_price_calculator(calculation_dict):
    with mock.patch("fba.views.fba.models.FBAPriceCalculator") as m:
        m.return_value.to_dict.return_value = calculation_dict
        yield m


@pytest.fixture
def mock_get_object(region):
    with mock.patch("fba.views.fba.get_object_or_404") as m:
        m.return_value = region
        yield m


@pytest.fixture
def url(mock_get_object, mock_price_calculator):
    return reverse("fba:price_calculator")


@pytest.fixture
def post_response(group_logged_in_client, url, form_data):
    return group_logged_in_client.post(url, form_data)


def test_status_code(post_response):
    assert post_response.status_code == 200


def test_request_without_group(logged_in_client, url):
    assert logged_in_client.post(url).status_code == 403


def test_calls_get_object_or_404(post_response, form_data, mock_get_object):
    mock_get_object.assert_called_once_with(FBARegion, pk=form_data["region"])


def test_calculator_instanciated(
    mock_price_calculator, region, post_response, form_data
):
    mock_price_calculator.assert_called_once_with(
        selling_price=float(form_data["selling_price"]),
        region=region,
        purchase_price=float(form_data["purchase_price"]),
        fba_fee=float(form_data["fba_fee"]),
        product_weight=int(form_data["weight"]),
        stock_level=int(form_data["stock_level"]),
        zero_rated=False,
        quantity=int(form_data["quantity"]),
    )


def test_calculator_instanciated_with_zero_rated_true(
    mock_price_calculator, region, url, group_logged_in_client, form_data
):
    form_data["zero_rated"] = "true"
    group_logged_in_client.post(url, form_data)
    mock_price_calculator.assert_called_once_with(
        selling_price=float(form_data["selling_price"]),
        region=region,
        purchase_price=float(form_data["purchase_price"]),
        fba_fee=float(form_data["fba_fee"]),
        product_weight=int(form_data["weight"]),
        stock_level=int(form_data["stock_level"]),
        zero_rated=True,
        quantity=int(form_data["quantity"]),
    )


def test_caluclator_calculate_method_called(post_response, mock_price_calculator):
    mock_price_calculator.return_value.calculate.assert_called_once_with()


def test_calculator_to_dict_method_called(post_response, mock_price_calculator):
    mock_price_calculator.return_value.to_dict.assert_called_once_with()


def test_response(post_response, calculation_dict):
    assert post_response.json() == calculation_dict


def test_handles_error_instanciating_calculator(
    mock_price_calculator, group_logged_in_client, url, form_data
):
    mock_price_calculator.side_effect = Exception
    response = group_logged_in_client.post(url, form_data)
    assert response.status_code == 400


def test_handles_error_calculating(
    mock_price_calculator, group_logged_in_client, url, form_data
):
    mock_price_calculator.return_value.calculate.side_effect = Exception
    response = group_logged_in_client.post(url, form_data)
    assert response.status_code == 400


def test_handles_error_createing_response_dict(
    mock_price_calculator, group_logged_in_client, url, form_data
):
    mock_price_calculator.return_value.to_dict.side_effect = Exception
    response = group_logged_in_client.post(url, form_data)
    assert response.status_code == 400
