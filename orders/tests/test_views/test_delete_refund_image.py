import pytest
from pytest_django.asserts import assertTemplateUsed

from orders import models


@pytest.fixture
def refund(
    refund_factory, product_sale_factory, packing_record_factory, product_refund_factory
):
    return refund_factory.create()


@pytest.fixture
def image(refund_image_factory, refund):
    return refund_image_factory.create(refund=refund)


@pytest.fixture
def url(db, image):
    return f"/orders/refund/delete_image/{image.id}/"


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


@pytest.fixture
def valid_get_response_content(url, valid_get_request):
    return valid_get_request(url).content.decode("utf8")


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


def test_logged_in_group_post(group_logged_in_client, url):
    response = group_logged_in_client.post(url)
    assert response.status_code == 302


def test_uses_template(valid_get_response):
    assert (
        assertTemplateUsed(
            valid_get_response, "orders/refunds/confirm_refund_image_delete.html"
        )
        is not False
    )


@pytest.mark.django_db
def test_post_deletes_image(image, group_logged_in_client, url):
    group_logged_in_client.post(url)
    assert models.RefundImage.objects.filter(id=image.id).exists() is False


@pytest.mark.django_db
def test_post_redirects(image, group_logged_in_client, url):
    response = group_logged_in_client.post(url)
    assert response.url == image.refund.get_absolute_url()
