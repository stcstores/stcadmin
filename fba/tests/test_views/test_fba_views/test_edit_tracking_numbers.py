import json

import pytest
from django.contrib import messages
from django.urls import reverse

from fba.forms import TrackingNumbersForm
from fba.models import FBAOrder, FBATrackingNumber
from fba.views.fba import EditTrackingNumbers


def test_model_attribute():
    assert EditTrackingNumbers.model == FBAOrder


def test_form_class_attribute():
    assert EditTrackingNumbers.form_class == TrackingNumbersForm


def test_template_name_attribute():
    assert EditTrackingNumbers.template_name == "fba/tracking_numbers.html"


@pytest.fixture
def order(fba_order_factory):
    return fba_order_factory.create(status_ready=True)


@pytest.fixture
def url(order):
    return reverse("fba:edit_tracking_numbers", args=[order.pk])


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


def test_uses_template(get_response):
    assert "fba/tracking_numbers.html" in [t.name for t in get_response.templates]


def test_status_code(get_response):
    assert get_response.status_code == 200


def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


@pytest.fixture
def form_data():
    return {"tracking_numbers": json.dumps(["AAA", "BBB", "CCC"])}


@pytest.fixture
def invalid_form_data(form_data):
    return {"tracking_numbers": "invalid"}


@pytest.fixture
def post_response(group_logged_in_client, url, form_data):
    return group_logged_in_client.post(url, form_data)


@pytest.mark.django_db
def test_updates_order(form_data, order, post_response):
    assert FBATrackingNumber.objects.filter(fba_order=order).exists()


def test_redirect(post_response, order):
    assert post_response.status_code == 302
    assert post_response["Location"] == reverse(
        "fba:edit_tracking_numbers", args=[order.pk]
    )


def test_invalid_item_form(group_logged_in_client, url, invalid_form_data):
    with pytest.raises(json.decoder.JSONDecodeError):
        group_logged_in_client.post(url, invalid_form_data)


@pytest.mark.django_db
def test_sets_message(group_logged_in_client, url, form_data):
    response = group_logged_in_client.post(url, form_data, follow=True)
    message = list(response.context["messages"])[0]
    assert message.message == "Tracking numbers updated."
    assert message.level == messages.SUCCESS
