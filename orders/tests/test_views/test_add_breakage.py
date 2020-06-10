import pytest
from django.shortcuts import reverse
from pytest_django.asserts import assertTemplateUsed

from orders import models


@pytest.fixture
def url():
    return "/orders/add_breakage/"


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


@pytest.fixture
def valid_get_response_content(valid_get_response):
    return valid_get_response.content.decode("utf8")


@pytest.fixture
def packer(cloud_commerce_user_factory):
    return cloud_commerce_user_factory.create()


@pytest.fixture
def form_data(packer):
    return {
        "product_sku": "4HJ-UL4-9YT",
        "order_id": "0238490383",
        "note": "A breakage note",
        "packer": packer.id,
    }


def test_logged_in_get(url, logged_in_client):
    response = logged_in_client.get(url)
    assert response.status_code == 403


def test_logged_out_get(client, url):
    response = client.get(url)
    assert response.status_code == 302


def test_logged_in_group_get(group_logged_in_client, url):
    response = group_logged_in_client.get(url)
    assert response.status_code == 200


def test_logged_in_post(url, logged_in_client):
    response = logged_in_client.post(url)
    assert response.status_code == 403


def test_logged_out_post(client, url):
    response = client.post(url)
    assert response.status_code == 302


def test_logged_in_group_post(group_logged_in_client, url, form_data):
    response = group_logged_in_client.post(url, form_data)
    assert response.status_code == 302


def test_uses_template(valid_get_response):
    assert (
        assertTemplateUsed(valid_get_response, "orders/breakage_form.html") is not False
    )


def test_breakage_is_created(group_logged_in_client, url, form_data):
    group_logged_in_client.post(url, form_data)
    assert models.Breakage.objects.filter(
        product_sku=form_data["product_sku"],
        order_id=form_data["order_id"],
        note=form_data["note"],
        packer__id=form_data["packer"],
    ).exists()


def test_redirects(group_logged_in_client, url, form_data):
    response = group_logged_in_client.post(url, form_data)
    assert response.url == reverse("orders:breakages")
