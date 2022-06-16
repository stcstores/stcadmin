import tempfile

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import reverse
from django.test import override_settings
from pytest_django.asserts import assertTemplateUsed

from feedback.models import Feedback, UserFeedback


@pytest.fixture
def refund(
    db,
    refund_factory,
    product_sale_factory,
    product_refund_factory,
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
def other_product(product_sale_factory, refund):
    return product_sale_factory.create(order=refund.order)


@pytest.fixture
def url(db):
    def _url(refund):
        return f"/orders/refund/{refund.id}/"

    return _url


@pytest.fixture
def valid_get_response(refund, valid_get_request, url):
    return valid_get_request(url(refund))


@pytest.fixture
def valid_get_response_content(refund, url, valid_get_request):
    return valid_get_request(url(refund)).content.decode("utf8")


def test_logged_in_get(refund, url, logged_in_client):
    response = logged_in_client.get(url(refund))
    assert response.status_code == 403


def test_logged_out_get(refund, client, url):
    response = client.get(url(refund))
    assert response.status_code == 302


def test_logged_in_group_get(refund, group_logged_in_client, url):
    response = group_logged_in_client.get(url(refund))
    assert response.status_code == 200


def test_logged_in_post(refund, url, logged_in_client):
    response = logged_in_client.post(url(refund))
    assert response.status_code == 403


def test_logged_out_post(refund, client, url):
    response = client.post(url(refund))
    assert response.status_code == 302


def test_logged_in_group_post(refund, group_logged_in_client, url):
    response = group_logged_in_client.post(url(refund))
    assert response.status_code == 405


def test_uses_template(valid_get_response):
    assert (
        assertTemplateUsed(valid_get_response, "orders/refunds/refund.html")
        is not False
    )


def test_refund_in_context(refund, valid_get_response):
    assert valid_get_response.context["refund"] == refund


def test_order_in_context(refund, valid_get_response):
    assert valid_get_response.context["order"] == refund.order


def test_products_in_context(refund, valid_get_response):
    assert list(valid_get_response.context["products"]) == list(refund.products.all())


def test_other_products_in_context(refund, other_product, valid_get_response):
    assert list(valid_get_response.context["other_products"]) == [other_product]


def test_order_id_in_response(refund, valid_get_response_content):
    assert refund.order.order_id in valid_get_response_content


def test_notes_in_response(refund, valid_get_response_content):
    assert refund.notes in valid_get_response_content


def test_links_to_set_notes(refund, valid_get_response_content):
    assert (
        reverse("orders:set_refund_notes", args=[refund.pk])
        in valid_get_response_content
    )


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


@pytest.mark.django_db
def test_links_to_create_feedback_for_packing_mistake(
    group_logged_in_client,
    url,
    packing_mistake_refund_factory,
    product_sale_factory,
    product_refund_factory,
):
    refund = packing_mistake_refund_factory.create()
    product = product_sale_factory.create(order=refund.order)
    product_refund_factory.create(refund=refund, product=product)
    response = group_logged_in_client.get(url(refund))
    content = response.content.decode("utf8")
    assert reverse("orders:add_packing_mistake_feedback", args=[refund.id]) in content


@pytest.mark.django_db
def test_links_to_feedback_page_when_feedback_exists(
    group_logged_in_client,
    url,
    packing_mistake_refund_factory,
    product_sale_factory,
    product_refund_factory,
):
    refund = packing_mistake_refund_factory.create()
    product = product_sale_factory.create(order=refund.order)
    product_refund_factory.create(refund=refund, product=product)
    feedback = UserFeedback.objects.create(
        feedback_type=Feedback.objects.create(
            name="Packing Mistake",
            image=SimpleUploadedFile(
                name="test_image.jpg", content=b"", content_type="image/jpeg"
            ),
        ),
        user=refund.order.packed_by,
        order_id=refund.order.order_id,
    )
    response = group_logged_in_client.get(url(refund))
    content = response.content.decode("utf8")
    assert feedback.get_absolute_url() in content
