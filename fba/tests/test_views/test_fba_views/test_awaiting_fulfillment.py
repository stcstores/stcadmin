from unittest import mock

import pytest
from django.urls import reverse

from fba.models import FBAOrder
from fba.views.fba import Awaitingfulfillment


def test_template_name_attribute():
    assert Awaitingfulfillment.template_name == "fba/awaiting_fulfillment.html"


def test_model_attribute():
    assert Awaitingfulfillment.model == FBAOrder


def test_paginate_by_attribute():
    assert Awaitingfulfillment.paginate_by == 50


def test_orphans_attribute():
    assert Awaitingfulfillment.orphans == 3


@pytest.fixture
def region(fba_region_factory):
    return fba_region_factory.create()


@pytest.fixture
def inactive_region(fba_region_factory):
    return fba_region_factory.create(active=False)


@pytest.fixture
def url():
    return reverse("fba:awaiting_fulfillment")


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


def test_uses_template(get_response):
    assert "fba/awaiting_fulfillment.html" in [t.name for t in get_response.templates]


def test_status_code(get_response):
    assert get_response.status_code == 200


def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


@pytest.mark.django_db
def test_region_in_context(region, inactive_region, get_response):
    regions = get_response.context["regions"]
    assert regions.contains(region)
    assert regions.contains(inactive_region) is False


def test_statuses_in_context(get_response):
    assert get_response.context["statuses"] == [
        FBAOrder.READY,
        FBAOrder.PRINTED,
        FBAOrder.NOT_PROCESSED,
    ]


def test_page_range_in_context(get_response):
    assert isinstance(get_response.context["page_range"], list)


def test_object_list_in_context(get_response):
    assert "object_list" in get_response.context


def test_object_list_in_context_not_empty(
    group_logged_in_client, url, fba_order_factory
):
    order = fba_order_factory.create(status_not_processed=True)
    response = group_logged_in_client.get(url)
    assert order in response.context["object_list"]


def test_get_page_range_with_low_page_count():
    paginator = mock.Mock(num_pages=6)
    assert Awaitingfulfillment().get_page_range(paginator=paginator) == [
        1,
        2,
        3,
        4,
        5,
        6,
    ]


def test_get_page_range_with_high_page_count():
    paginator = mock.Mock(num_pages=13)
    assert Awaitingfulfillment().get_page_range(paginator=paginator) == [
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


def test_filter_by_region(fba_order_factory, group_logged_in_client, url):
    expected_order = fba_order_factory.create()
    unexpected_order = fba_order_factory.create()
    params = {"region": expected_order.region.id}
    response = group_logged_in_client.get(url, params)
    assert response.context["object_list"].contains(expected_order)
    assert response.context["object_list"].contains(unexpected_order) is False


@pytest.fixture
def not_processed_fba_order(fba_order_factory):
    return fba_order_factory(status_not_processed=True)


@pytest.fixture
def ready_fba_order(fba_order_factory):
    return fba_order_factory(status_ready=True)


@pytest.fixture
def printed_fba_order(fba_order_factory):
    return fba_order_factory(status_printed=True)


@pytest.fixture
def fulfilled_fba_order(fba_order_factory):
    return fba_order_factory(status_fulfilled=True)


@pytest.fixture
def on_hold_fba_order(fba_order_factory):
    return fba_order_factory(status_on_hold=True)


@pytest.fixture
def stopped_fba_order(fba_order_factory):
    return fba_order_factory(status_stopped=True)


@pytest.mark.parametrize(
    "status,not_processed_included,printed_included,ready_included",
    (
        (FBAOrder.READY, False, False, True),
        (FBAOrder.PRINTED, False, True, False),
        (FBAOrder.NOT_PROCESSED, True, False, False),
    ),
)
@pytest.mark.django_db
def test_filter_by_status(
    status,
    not_processed_included,
    printed_included,
    ready_included,
    not_processed_fba_order,
    ready_fba_order,
    printed_fba_order,
    fulfilled_fba_order,
    on_hold_fba_order,
    stopped_fba_order,
    group_logged_in_client,
    url,
):
    params = {"status": status}
    response = group_logged_in_client.get(url, params)
    values = response.context["object_list"]
    assert values.contains(not_processed_fba_order) is not_processed_included
    assert values.contains(ready_fba_order) is ready_included
    assert values.contains(printed_fba_order) is printed_included
    assert values.contains(fulfilled_fba_order) is False
    assert values.contains(on_hold_fba_order) is False
    assert values.contains(stopped_fba_order) is False


def test_search_terms_matches_product_sku(
    fba_order_factory, group_logged_in_client, url
):
    expected_order = fba_order_factory.create()
    unexpected_order = fba_order_factory.create()
    params = {"search_term": expected_order.product.sku}
    response = group_logged_in_client.get(url, params)
    assert response.context["object_list"].contains(expected_order)
    assert response.context["object_list"].contains(unexpected_order) is False


def test_search_terms_matches_product_range_name(
    fba_order_factory, group_logged_in_client, url
):
    expected_order = fba_order_factory.create()
    unexpected_order = fba_order_factory.create()
    params = {"search_term": expected_order.product.product_range.name}
    response = group_logged_in_client.get(url, params)
    assert response.context["object_list"].contains(expected_order)
    assert response.context["object_list"].contains(unexpected_order) is False


def test_search_terms_matches_asin(fba_order_factory, group_logged_in_client, url):
    expected_order = fba_order_factory.create()
    unexpected_order = fba_order_factory.create()
    params = {"search_term": expected_order.product_asin}
    response = group_logged_in_client.get(url, params)
    assert response.context["object_list"].contains(expected_order)
    assert response.context["object_list"].contains(unexpected_order) is False


def test_search_terms_matches_barcode(fba_order_factory, group_logged_in_client, url):
    expected_order = fba_order_factory.create()
    unexpected_order = fba_order_factory.create()
    params = {"search_term": expected_order.product.barcode}
    response = group_logged_in_client.get(url, params)
    assert response.context["object_list"].contains(expected_order)
    assert response.context["object_list"].contains(unexpected_order) is False


def test_search_terms_matches_range_sku(fba_order_factory, group_logged_in_client, url):
    expected_order = fba_order_factory.create()
    unexpected_order = fba_order_factory.create()
    params = {"search_term": expected_order.product.product_range.sku}
    response = group_logged_in_client.get(url, params)
    assert response.context["object_list"].contains(expected_order)
    assert response.context["object_list"].contains(unexpected_order) is False


def test_search_terms_matches_supplier_sku(
    fba_order_factory, group_logged_in_client, url
):
    expected_order = fba_order_factory.create()
    unexpected_order = fba_order_factory.create()
    params = {"search_term": expected_order.product.supplier_sku}
    response = group_logged_in_client.get(url, params)
    assert response.context["object_list"].contains(expected_order)
    assert response.context["object_list"].contains(unexpected_order) is False


def test_search_terms_matches_order_pk(fba_order_factory, group_logged_in_client, url):
    expected_order = fba_order_factory.create()
    unexpected_order = fba_order_factory.create()
    params = {"search_term": expected_order.pk}
    response = group_logged_in_client.get(url, params)
    assert response.context["object_list"].contains(expected_order)
    assert response.context["object_list"].contains(unexpected_order) is False
