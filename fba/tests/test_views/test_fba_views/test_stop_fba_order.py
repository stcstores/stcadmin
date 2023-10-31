import datetime as dt
from unittest import mock

import pytest
from django.urls import reverse

from fba.forms import StopFBAOrderForm
from fba.models import FBAOrder
from fba.views.fba import StopFBAOrder


def test_model_attribute():
    assert StopFBAOrder.model == FBAOrder


def test_form_class_attribute():
    assert StopFBAOrder.form_class == StopFBAOrderForm


def test_template_name_attribute():
    assert StopFBAOrder.template_name == "fba/stop_fba_order_form.html"


@pytest.fixture
def order(fba_order_factory):
    return fba_order_factory.create(status_not_processed=True)


@pytest.fixture
def url(order):
    return reverse("fba:stop_fba_order", args=[order.pk])


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


def test_uses_template(get_response):
    assert "fba/stop_fba_order_form.html" in (t.name for t in get_response.templates)


def test_status_code(get_response):
    assert get_response.status_code == 200


def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


def test_form_in_context(get_response):
    assert isinstance(get_response.context["form"], StopFBAOrderForm)


@mock.patch("fba.views.fba.timezone.now")
def test_get_initial(mock_now):
    initial = StopFBAOrder().get_initial()
    assert initial == {
        "is_stopped": True,
        "stopped_at": mock_now.return_value.strftime("%d/%m/%Y"),
    }


@pytest.fixture
def form_data():
    return {
        "is_stopped": True,
        "stopped_until": dt.datetime(2023, 3, 3).strftime("%d/%m/%Y"),
        "stopped_reason": "B",
    }


@pytest.fixture
def invalid_form_data(form_data):
    form_data["stopped_until"] = "invalid"
    return form_data


@pytest.fixture
def post_response(group_logged_in_client, url, form_data):
    return group_logged_in_client.post(url, form_data)


@pytest.mark.django_db
def test_updates_order(form_data, order, post_response):
    order.refresh_from_db()
    assert order.is_stopped is True


def test_redirect(post_response, order):
    assert post_response.status_code == 302
    assert post_response["Location"] == reverse("fba:update_fba_order", args=[order.pk])


def test_invalid_item_form(group_logged_in_client, url, invalid_form_data):
    response = group_logged_in_client.post(url, invalid_form_data)
    assert response.status_code == 200
    assert response.context["form"].errors
