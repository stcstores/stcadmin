import pytest
from django.urls import reverse

from fba import forms


@pytest.fixture
def destination(fba_shipment_destination_factory):
    return fba_shipment_destination_factory.create()


@pytest.fixture
def url(destination):
    return reverse("fba:update_shipment_destination", args=[destination.pk])


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
def test_updates_destination(destination, post_response, form_data):
    destination.refresh_from_db()
    assert destination.name == form_data["name"]
    assert destination.recipient_name == form_data["recipient_name"]
    assert destination.contact_telephone == form_data["contact_telephone"]
    assert destination.address_line_1 == form_data["address_line_1"]
    assert destination.address_line_2 == form_data["address_line_2"]
    assert destination.address_line_3 == form_data["address_line_3"]
    assert destination.city == form_data["city"]
    assert destination.state == form_data["state"]
    assert destination.country == form_data["country"]
    assert destination.country_iso == form_data["country_iso"]
    assert destination.postcode == form_data["postcode"]


@pytest.mark.django_db
def test_redirect(post_response):
    assert post_response.status_code == 302
    assert post_response["Location"] == reverse("fba:shipment_destinations")
