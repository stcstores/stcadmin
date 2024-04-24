from unittest import mock

import pytest
from django.urls import reverse

from fba.views.fba import FBAProductProfit


@pytest.fixture
def template():
    return "fba/profit.html"


def test_template_name_attribute(template):
    assert FBAProductProfit.template_name == template


@pytest.fixture
def product(product_factory):
    return product_factory.create()


@pytest.fixture
def mock_fba_profit_model():
    with mock.patch("fba.views.fba.models.FBAProfit") as m:
        yield m


@pytest.fixture
def url(mock_fba_profit_model, product):
    return reverse("fba:product_profit", args=[product.pk])


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
def test_product_in_context(product, get_response):
    assert get_response.context["product"] == product


@pytest.mark.django_db
def test_profit_calculations_in_context(mock_fba_profit_model, product, get_response):
    mock_fba_profit_model.objects.current.assert_called_once_with()
    mock_fba_profit_model.objects.current.return_value.filter.assert_called_once_with(
        product=product
    )
    assert (
        get_response.context["profit_calculations"]
        == mock_fba_profit_model.objects.current.return_value.filter.return_value
    )
