from unittest import mock

import pytest
from django.urls import reverse

from fba.forms import FBAShipmentFilter
from fba.models import FBAShipmentExport
from fba.views.shipping import HistoricShipments


def test_template_name_attribute():
    assert HistoricShipments.template_name == "fba/shipments/historic_shipments.html"


def test_model_attribute():
    assert HistoricShipments.model == FBAShipmentExport


def test_paginate_by_attribute():
    assert HistoricShipments.paginate_by == 50


def test_orphans_attribute():
    assert HistoricShipments.orphans == 3


def test_form_class_attribute():
    assert HistoricShipments.form_class == FBAShipmentFilter


@pytest.fixture
def url():
    return reverse("fba:historic_shipments")


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "fba/shipments/historic_shipments.html" in (
        t.name for t in get_response.templates
    )


@pytest.mark.django_db
def test_status_code(get_response):
    assert get_response.status_code == 200


@pytest.mark.django_db
def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


def test_form_in_context(get_response):
    assert isinstance(get_response.context["form"], FBAShipmentFilter)


def test_page_range_in_context(get_response):
    assert isinstance(get_response.context["page_range"], list)


def test_object_list_in_context(get_response):
    assert "object_list" in get_response.context


def test_invalid_form_submission(group_logged_in_client, url):
    response = group_logged_in_client.get(url, {"destination": "hello"})
    assert response.status_code == 200
    assert response.context["object_list"] == []
    assert response.context["form"].is_valid() is False


@pytest.mark.django_db
def test_object_list_in_context_not_empty(
    group_logged_in_client, url, fba_shipment_export_factory
):
    export = fba_shipment_export_factory.create()
    response = group_logged_in_client.get(url)
    assert export in response.context["object_list"]


def test_get_page_range_with_low_page_count():
    paginator = mock.Mock(num_pages=6)
    assert HistoricShipments().get_page_range(paginator=paginator) == [1, 2, 3, 4, 5, 6]


def test_get_page_range_with_high_page_count():
    paginator = mock.Mock(num_pages=13)
    assert HistoricShipments().get_page_range(paginator=paginator) == [
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


@pytest.mark.django_db
def test_filters(fba_shipment_order_factory, group_logged_in_client, url):
    expected_order = fba_shipment_order_factory.create()
    unexpected_order = fba_shipment_order_factory.create()
    params = {"destination": expected_order.destination.id}
    response = group_logged_in_client.get(url, params)
    assert response.context["object_list"].contains(expected_order.export)
    assert response.context["object_list"].contains(unexpected_order.export) is False
