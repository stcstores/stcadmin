from unittest import mock

import pytest
from django.urls import reverse

from fba.views.fba import FBAProfitList


@pytest.fixture
def template():
    return "fba/profit_list.html"


def test_template_name_attribute(template):
    assert FBAProfitList.template_name == template


@pytest.fixture
def products():
    return [mock.Mock(pk=i) for i in range(3)]


@pytest.fixture
def fees(products):
    return [mock.Mock(product=product) for product in products]


@pytest.fixture
def mock_fba_profit_model(fees):
    with mock.patch("fba.views.fba.models.FBAProfit") as m:
        m.objects.current.return_value.order_by.return_value.select_related.return_value = (
            fees
        )
        yield m


@pytest.fixture
def url(mock_fba_profit_model):
    return reverse("fba:profit_list")


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_uses_template(template, get_response):
    assert template in [t.name for t in get_response.templates]


@pytest.mark.django_db
def test_status_code(get_response):
    assert get_response.status_code == 200


@pytest.mark.django_db
def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


@pytest.mark.django_db
def test_gets_queryset(mock_fba_profit_model, get_response):
    mock_fba_profit_model.objects.current.assert_called_once_with()
    mock_fba_profit_model.objects.current.return_value.order_by.assert_called_once_with(
        "product"
    )
    mock_fba_profit_model.objects.current.return_value.order_by.return_value.select_related.assert_called_once_with(
        "product", "product__product_range", "region", "region__country", "last_order"
    )


@pytest.mark.django_db
def test_profit_calculations_in_context(mock_fba_profit_model, fees, get_response):
    expected = {fee.product: [fee] for fee in fees}
    assert get_response.context["profit_calculations"] == expected
