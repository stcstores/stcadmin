from io import BytesIO

import pytest
from django.core.files import File
from PIL import Image

from orders import models


@pytest.fixture
def refund(db, refund_factory):
    return refund_factory.create()


@pytest.fixture
def url():
    def _url(refund, product=None):
        url = f"/orders/refund/add_images/{refund.pk}/"
        if product is not None:
            url += f"{product.pk}/"
        return url

    return _url


@pytest.fixture
def valid_get_response(refund, valid_get_request, url):
    return valid_get_request(url(refund))


@pytest.fixture
def product(refund, product_refund_factory):
    return product_refund_factory.create(
        refund=refund, product__order=refund.order, quantity=2
    )


@pytest.fixture
def image_file():
    def _image_file():
        tmp = BytesIO()
        image = Image.new("RGBA", size=(700, 500), color=(155, 0, 0))
        image.save(tmp, "png")
        tmp.name = "test.png"
        tmp.seek(0)
        return File(tmp)

    return _image_file


@pytest.fixture
def form_data(image_file):
    return {"images": [image_file()]}


def test_logged_in_get(url, refund, logged_in_client):
    response = logged_in_client.get(url(refund))
    assert response.status_code == 403


def test_logged_out_get(client, url, refund):
    response = client.get(url(refund))
    assert response.status_code == 302


def test_logged_in_group_get(group_logged_in_client, url, refund):
    response = group_logged_in_client.get(url(refund))
    assert response.status_code == 302


def test_logged_in_post(url, refund, logged_in_client, form_data):
    response = logged_in_client.post(url(refund), form_data)
    assert response.status_code == 403


def test_logged_out_post(client, url, refund, form_data):
    response = client.post(url(refund), form_data)
    assert response.status_code == 302


def test_logged_in_group_post(group_logged_in_client, url, refund, form_data):
    response = group_logged_in_client.post(url(refund), form_data)
    assert response.status_code == 302


def test_creates_image(refund, url, form_data, group_logged_in_client):
    group_logged_in_client.post(url(refund), form_data)
    assert models.RefundImage.objects.filter(refund=refund).exists()


def test_creates_images(refund, url, image_file, group_logged_in_client):
    form_data = {"images": [image_file(), image_file()]}
    group_logged_in_client.post(url(refund), form_data)
    assert models.RefundImage.objects.filter(refund=refund).count() == 2


def test_creates_product_image(refund, product, url, form_data, group_logged_in_client):
    group_logged_in_client.post(url(refund, product=product), form_data)
    assert models.RefundImage.objects.filter(
        refund=refund, product_refund=product
    ).exists()


def test_creates_product_images(
    refund, image_file, product, url, group_logged_in_client
):
    form_data = {"images": [image_file(), image_file()]}
    group_logged_in_client.post(url(refund, product=product), form_data)
    assert (
        models.RefundImage.objects.filter(refund=refund, product_refund=product).count()
        == 2
    )
