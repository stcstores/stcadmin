import pytest
from django.urls import reverse

from fba import forms
from fba.models import FBAShipmentDestination


@pytest.fixture
def url():
    return reverse("fba:create_shipment_destination")


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "fba/shipments/shipment_destination_form.html" in (
        t.name for t in get_response.templates
    )


@pytest.mark.django_db
def test_status_code(get_response):
    assert get_response.status_code == 200


@pytest.mark.django_db
def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


def test_form_in_context(get_response):
    assert isinstance(get_response.context["form"], forms.ShipmentDestinationForm)


@pytest.fixture
def form_data():
    return {
        "name": "A",
        "recipient_name": "B",
        "contact_telephone": "C",
        "address_line_1": "D",
        "address_line_2": "E",
        "address_line_3": "F",
        "city": "G",
        "state": "H",
        "country": "I",
        "country_iso": "J",
        "postcode": "K",
    }


@pytest.fixture
def post_response(group_logged_in_client, url, form_data):
    return group_logged_in_client.post(url, form_data)


@pytest.mark.django_db
def test_creates_destination(post_response, form_data):
    assert FBAShipmentDestination.objects.filter(**form_data).exists() is True


@pytest.mark.django_db
def test_redirect(post_response):
    assert post_response.status_code == 302
    assert post_response["Location"] == reverse("fba:shipment_destinations")
