import os
import tempfile
from io import BytesIO

import pytest
from django.conf import settings
from django.core.files import File
from django.test import override_settings
from PIL import Image

from orders import models


@pytest.fixture
def refund(refund_factory):
    return refund_factory.create()


@pytest.fixture
def product_refund(product_refund_factory, refund):
    return product_refund_factory.create(refund=refund, product__order=refund.order)


@pytest.fixture
def image():
    tmp = BytesIO()
    image = Image.new("RGBA", size=(700, 500), color=(155, 0, 0))
    image.save(tmp, "png")
    tmp.name = "test.png"
    tmp.seek(0)
    return File(tmp)


@pytest.fixture
def new_refund_image(refund, product_refund, image):
    refund_image = models.RefundImage(
        refund=refund, product_refund=product_refund, image=image, thumbnail=image
    )
    refund_image.save()
    refund_image.refresh_from_db()
    return refund_image


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
@pytest.mark.django_db
def test_sets_refund(new_refund_image, refund):
    assert new_refund_image.refund == refund


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
@pytest.mark.django_db
def test_sets_product_refund(new_refund_image, product_refund):
    assert new_refund_image.product_refund == product_refund


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
@pytest.mark.django_db
def test_sets_image(new_refund_image):
    assert bool(new_refund_image.image) is True


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
@pytest.mark.django_db
def test_sets_thumbnail(new_refund_image):
    assert bool(new_refund_image.thumbnail) is True


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
@pytest.mark.django_db
def test_image_path(new_refund_image, image):
    assert os.path.dirname(new_refund_image.image.path) == os.path.join(
        settings.MEDIA_ROOT,
        "refunds",
        "images",
        str(new_refund_image.refund.id),
        str(new_refund_image.product_refund.id),
    )


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
@pytest.mark.django_db
def test_thumb_path(new_refund_image, image):
    assert os.path.dirname(new_refund_image.thumbnail.path) == os.path.join(
        settings.MEDIA_ROOT,
        "refunds",
        "thumbs",
        str(new_refund_image.refund.id),
        str(new_refund_image.product_refund.id),
    )


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
@pytest.mark.django_db
def test_image_size(new_refund_image):
    assert new_refund_image.image_height == 500
    assert new_refund_image.image_width == 700


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
@pytest.mark.django_db
def test_thumb_size(new_refund_image):
    assert new_refund_image.thumb_height <= models.RefundImage.THUMB_SIZE
    assert new_refund_image.thumb_width <= models.RefundImage.THUMB_SIZE
