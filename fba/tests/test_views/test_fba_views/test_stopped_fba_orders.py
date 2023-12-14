from unittest import mock

import pytest
from django.urls import reverse

from fba.forms import StoppedOrderFilter
from fba.models import FBAOrder
from fba.views.fba import StoppedFBAOrders


def test_template_name_attribute():
    assert StoppedFBAOrders.template_name == "fba/stopped.html"


def test_model_attribute():
    assert StoppedFBAOrders.model == FBAOrder


def test_paginate_by_attribute():
    assert StoppedFBAOrders.paginate_by == 50


def test_orphans_attribute():
    assert StoppedFBAOrders.orphans == 3


def test_form_class_attribute():
    assert StoppedFBAOrders.form_class == StoppedOrderFilter


@pytest.fixture
def url():
    return reverse("fba:stopped")


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


def test_uses_template(get_response):
    assert "fba/stopped.html" in [t.name for t in get_response.templates]


def test_status_code(get_response):
    assert get_response.status_code == 200


def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


def test_form_in_context(get_response):
    assert isinstance(get_response.context["form"], StoppedOrderFilter)


def test_page_range_in_context(get_response):
    assert isinstance(get_response.context["page_range"], list)


def test_object_list_in_context(get_response):
    assert "object_list" in get_response.context


def test_invalid_form_submission(group_logged_in_client, url):
    response = group_logged_in_client.get(url, {"supplier": "hello"})
    assert response.status_code == 200
    assert len(response.context["object_list"]) == 0
    assert response.context["form"].is_valid() is False


def test_object_list_in_context_not_empty(
    group_logged_in_client, url, fba_order_factory
):
    order = fba_order_factory.create(status_stopped=True)
    response = group_logged_in_client.get(url)
    assert order in response.context["object_list"]


def test_get_page_range_with_low_page_count():
    paginator = mock.Mock(num_pages=6)
    assert StoppedFBAOrders().get_page_range(paginator=paginator) == [1, 2, 3, 4, 5, 6]


def test_get_page_range_with_high_page_count():
    paginator = mock.Mock(num_pages=13)
    assert StoppedFBAOrders().get_page_range(paginator=paginator) == [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        13,
    ]


def test_filters(fba_order_factory, group_logged_in_client, url):
    expected_order = fba_order_factory.create(status_stopped=True)
    unexpected_order = fba_order_factory.create(status_stopped=True)
    params = {"supplier": expected_order.product.supplier.id}
    response = group_logged_in_client.get(url, params)
    assert response.context["object_list"].contains(expected_order)
    assert response.context["object_list"].contains(unexpected_order) is False
