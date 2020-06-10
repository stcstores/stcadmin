import pytest
from django.shortcuts import reverse
from pytest_django.asserts import assertTemplateUsed


@pytest.fixture
def packer(cloud_commerce_user_factory):
    return cloud_commerce_user_factory.create()


@pytest.fixture
def breakage(breakage_factory):
    return breakage_factory.create()


@pytest.fixture
def url(breakage):
    return f"/orders/update_breakage/{breakage.id}/"


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


@pytest.fixture
def valid_get_response_content(valid_get_response):
    return valid_get_response.content.decode("utf8")


@pytest.fixture
def form_data(packer):
    return {
        "product_sku": "4HJ-UL4-9YT",
        "order_id": "0238490383",
        "note": "A breakage note",
        "packer": packer.id,
    }


@pytest.mark.django_db
def test_logged_in_get(url, logged_in_client):
    response = logged_in_client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_logged_out_get(client, url):
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_logged_in_group_get(group_logged_in_client, url):
    response = group_logged_in_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_logged_in_post(url, logged_in_client):
    response = logged_in_client.post(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_logged_out_post(client, url):
    response = client.post(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_logged_in_group_post(group_logged_in_client, url, form_data):
    response = group_logged_in_client.post(url, form_data)
    assert response.status_code == 302


@pytest.mark.django_db
def test_uses_template(valid_get_response):
    assert (
        assertTemplateUsed(valid_get_response, "orders/breakage_form.html") is not False
    )


@pytest.mark.django_db
def test_breakage_is_updated(group_logged_in_client, url, form_data, breakage):
    group_logged_in_client.post(url, form_data)
    breakage.refresh_from_db()
    assert breakage.product_sku == form_data["product_sku"]
    assert breakage.order_id == form_data["order_id"]
    assert breakage.note == form_data["note"]
    assert breakage.packer.id == form_data["packer"]


@pytest.mark.django_db
def test_redirects(group_logged_in_client, url, form_data, breakage):
    response = group_logged_in_client.post(url, form_data)
    assert response.url == reverse("orders:breakages")
