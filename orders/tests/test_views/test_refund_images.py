import tempfile

import pytest
from django.shortcuts import reverse
from django.test import override_settings
from pytest_django.asserts import assertTemplateUsed


@pytest.fixture
def refund(
    refund_factory, product_sale_factory, packing_record_factory, product_refund_factory
):
    refund = refund_factory.create()
    product = product_sale_factory.create(order=refund.order)
    product_refund_factory.create(refund=refund, product=product)
    return refund


@pytest.fixture
def image(refund, refund_image_factory):
    return refund_image_factory.create(refund=refund)


@pytest.fixture
def product_image(refund, refund_image_factory):
    return refund_image_factory.create(
        refund=refund, product_refund=refund.products.first()
    )


@pytest.fixture
def url(db, refund):
    return f"/orders/refund/images/{refund.id}/"


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
    assert response.status_code == 405


def test_uses_template(valid_get_response):
    assert (
        assertTemplateUsed(valid_get_response, "orders/refunds/refund_images.html")
        is not False
    )


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_shows_images(image, valid_get_response_content):
    assert f'src="{image.thumbnail.url}"' in valid_get_response_content


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_shows_product_images(product_image, valid_get_response_content):
    assert f'src="{product_image.thumbnail.url}"' in valid_get_response_content


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_links_to_images(image, valid_get_response_content):
    assert f'href="{image.image.url}"' in valid_get_response_content


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_links_to_product_images(product_image, valid_get_response_content):
    assert f'href="{product_image.image.url}"' in valid_get_response_content


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_links_to_delete_images(image, valid_get_response_content):
    assert (
        reverse("orders:delete_refund_image", args=[image.id])
        in valid_get_response_content
    )


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_links_to_delete_product_images(product_image, valid_get_response_content):
    assert (
        reverse("orders:delete_refund_image", args=[product_image.id])
        in valid_get_response_content
    )


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_links_to_add_images(image, valid_get_response_content):
    assert (
        reverse("orders:add_refund_images", args=[image.refund.id])
        in valid_get_response_content
    )


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_links_to_add_product_images(product_image, valid_get_response_content):
    assert (
        reverse(
            "orders:add_refund_images",
            args=[product_image.refund.id, product_image.product_refund.id],
        )
        in valid_get_response_content
    )
