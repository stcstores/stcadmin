import pytest
from django.contrib import messages
from django.urls import reverse

from fba import forms


@pytest.fixture
def shipment_order(fba_shipment_order_factory):
    return fba_shipment_order_factory.create()


@pytest.fixture
def shipment_package(shipment_order, fba_shipment_package_factory):
    return fba_shipment_package_factory.create(shipment_order=shipment_order)


@pytest.fixture
def shipment_item(shipment_package, fba_shipment_item_factory):
    return fba_shipment_item_factory.create(package=shipment_package)


@pytest.fixture
def url(shipment_package):
    return reverse("fba:update_package", args=[shipment_package.pk])


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


@pytest.fixture
def form_data(shipment_order, shipment_package, shipment_item):
    return {
        "length_cm": 50,
        "width_cm": 50,
        "height_cm": 50,
        "shipment_order": shipment_order.pk,
        "shipment_item-TOTAL_FORMS": 1,
        "shipment_item-INITIAL_FORMS": 1,
        "shipment_item-MIN_NUM_FORMS": 0,
        "shipment_item-MAX_NUM_FORMS": 1000,
        "shipment_item-0-sku": "AAA-BBB-CCC",
        "shipment_item-0-description": "Product Description",
        "shipment_item-0-quantity": 5,
        "shipment_item-0-weight_kg": 25.0,
        "shipment_item-0-value": 25.67,
        "shipment_item-0-country_of_origin": "United Kingdom",
        "shipment_item-0-hr_code": "999999999999",
        "shipment_item-0-package": shipment_package.pk,
        "shipment_item-0-id": shipment_item.pk,
    }


@pytest.fixture
def add_item_form_data(shipment_package, form_data):
    return form_data | {
        "shipment_item-TOTAL_FORMS": 2,
        "shipment_item-1-sku": "AAA-BBB-CCC",
        "shipment_item-1-description": "Product Description",
        "shipment_item-1-quantity": 5,
        "shipment_item-1-weight_kg": 25.0,
        "shipment_item-1-value": 25.67,
        "shipment_item-1-country_of_origin": "United Kingdom",
        "shipment_item-1-hr_code": "999999999999",
        "shipment_item-1-package": shipment_package.pk,
        "shipment_item-1-id": "",
    }


@pytest.fixture
def delete_item_form_data(form_data):
    form_data["shipment_item-0-DELETE"] = "on"
    return form_data


@pytest.fixture
def form_data_incomplete(form_data):
    form_data["height_cm"] = ""
    return form_data


@pytest.fixture
def form_data_with_invalid_item(form_data):
    form_data["shipment_item-0-weight_kg"] = "invalid"
    return form_data


@pytest.fixture
def form_data_with_incomplete_item(form_data):
    form_data["shipment_item-0-hr_code"] = ""
    return form_data


@pytest.fixture
def post_response(group_logged_in_client, url, form_data):
    return group_logged_in_client.post(url, form_data)


@pytest.mark.django_db
def test_updates_package(form_data, post_response, shipment_order, shipment_package):
    shipment_package.refresh_from_db()
    assert shipment_package.shipment_order == shipment_order
    assert shipment_package.length_cm == form_data["length_cm"]


@pytest.mark.django_db
def test_updates_item(post_response, shipment_package, shipment_item):
    shipment_item.refresh_from_db()
    assert shipment_item.package == shipment_package
    assert shipment_item.value == 2567


@pytest.mark.django_db
def test_redirect(post_response, shipment_order):
    assert post_response.status_code == 302
    assert post_response["Location"] == reverse(
        "fba:update_shipment", args=[shipment_order.pk]
    )


@pytest.mark.django_db
def test_sets_message(group_logged_in_client, url, form_data, shipment_order):
    response = group_logged_in_client.post(url, form_data, follow=True)
    message = list(response.context["messages"])[0]
    assert message.message == f"Shipment Order {shipment_order.order_number} updated."
    assert message.level == messages.SUCCESS


def test_incomplete_form(group_logged_in_client, url, form_data_incomplete):
    response = group_logged_in_client.post(url, form_data_incomplete)
    assert response.status_code == 200
    assert response.context["form"].errors


@pytest.mark.django_db
def test_invalid_item_form(group_logged_in_client, url, form_data_with_invalid_item):
    response = group_logged_in_client.post(url, form_data_with_invalid_item)
    assert response.status_code == 200
    assert response.context["item_formset"].errors


@pytest.mark.django_db
def test_incomplete_item_form(
    group_logged_in_client, url, form_data_with_incomplete_item
):
    response = group_logged_in_client.post(url, form_data_with_incomplete_item)
    assert response.status_code == 200
    assert response.context["item_formset"].errors


@pytest.mark.django_db
def test_adds_new_package(
    shipment_package, group_logged_in_client, url, add_item_form_data
):
    group_logged_in_client.post(url, add_item_form_data)
    assert shipment_package.shipment_item.count() == 2


@pytest.mark.django_db
def test_deletes_package(
    shipment_package, group_logged_in_client, url, delete_item_form_data
):
    group_logged_in_client.post(url, delete_item_form_data)
    assert shipment_package.shipment_item.count() == 0
