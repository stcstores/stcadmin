import pytest
from django.contrib import messages
from django.urls import reverse

from fba import forms, models


@pytest.fixture
def shipment_order(fba_shipment_order_factory):
    return fba_shipment_order_factory.create()


@pytest.fixture
def url(shipment_order):
    return reverse("fba:create_package", args=[shipment_order.pk])


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "fba/shipments/create_shipment/package_form.html" in [
        t.name for t in get_response.templates
    ]


@pytest.mark.django_db
def test_status_code(get_response):
    assert get_response.status_code == 200


@pytest.mark.django_db
def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


def test_form_in_context(get_response):
    assert isinstance(get_response.context["form"], forms.PackageForm)


def test_formset_in_context(get_response):
    assert isinstance(get_response.context["item_formset"], forms.ItemFormset)


@pytest.mark.django_db
def test_get_initial(get_response, shipment_order):
    assert get_response.context["form"].initial == {"shipment_order": shipment_order}


@pytest.fixture
def form_data(shipment_order):
    return {
        "length_cm": "50",
        "width_cm": "50",
        "height_cm": "50",
        "shipment_order": shipment_order.pk,
        "shipment_item-TOTAL_FORMS": "1",
        "shipment_item-INITIAL_FORMS": "0",
        "shipment_item-MIN_NUM_FORMS": "0",
        "shipment_item-MAX_NUM_FORMS": "1000",
        "shipment_item-0-sku": "AAA-BBB-CCC",
        "shipment_item-0-description": "Product Description",
        "shipment_item-0-quantity": "5",
        "shipment_item-0-weight_kg": "25",
        "shipment_item-0-value": "25.67",
        "shipment_item-0-country_of_origin": "United Kingdom",
        "shipment_item-0-hr_code": "999999999999",
        "shipment_item-0-package": "",
        "shipment_item-0-id": "",
    }


@pytest.fixture
def form_data_with_invalid_item(form_data):
    form_data["shipment_item-0-weight_kg"] = "invalid"


@pytest.fixture
def post_response(group_logged_in_client, url, form_data):
    return group_logged_in_client.post(url, form_data)


@pytest.mark.django_db
def test_creates_package(post_response, shipment_order):
    assert models.FBAShipmentPackage.objects.filter(
        shipment_order=shipment_order
    ).exists()


@pytest.mark.django_db
def test_creates_item(post_response, form_data, shipment_order):
    assert models.FBAShipmentItem.objects.filter(
        package__shipment_order=shipment_order
    ).exists()


@pytest.mark.django_db
def test_redirect(post_response, shipment_order):
    assert post_response.status_code == 302
    assert post_response["Location"] == reverse(
        "fba:update_shipment", args=[shipment_order.pk]
    )


@pytest.mark.django_db
def test_sets_message(group_logged_in_client, url, form_data, shipment_order):
    response = group_logged_in_client.post(url, form_data, follow=True)
    package = models.FBAShipmentPackage.objects.get(shipment_order=shipment_order)
    message = list(response.context["messages"])[0]
    assert message.message == (
        f"Package {package.package_number} added to "
        f"Shipment {shipment_order.order_number}."
    )
    assert message.level == messages.SUCCESS


@pytest.mark.django_db
def test_invalid_item_form(group_logged_in_client, url, form_data_with_invalid_item):
    response = group_logged_in_client.post(url, form_data_with_invalid_item)
    assert response.status_code == 200
    assert response.context["form"].errors
