import datetime as dt

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from inventory import models


@pytest.fixture
def product_image_link(product_image_link_factory):
    product_image_link = product_image_link_factory.create()
    product_image_link.full_clean()
    return product_image_link


@pytest.fixture
def new_product_image_link(product_factory, product_image_factory):
    product_image_link = models.ProductImageLink(
        product=product_factory.create(), image=product_image_factory.create()
    )
    product_image_link.save()
    product_image_link.full_clean()
    return product_image_link


@pytest.fixture
def create_upload_file(test_image_path):
    def _create_upload_file():
        with open(test_image_path, "rb") as f:
            return SimpleUploadedFile(name="file_name", content=f.read())

    return _create_upload_file


@pytest.fixture
def uploaded_file(create_upload_file):
    return create_upload_file()


@pytest.mark.django_db
def test_product_attribute(product_image_link):
    assert isinstance(product_image_link.product, models.BaseProduct)


@pytest.mark.django_db
def test_image_attribute(product_image_link):
    assert isinstance(product_image_link.image, models.ProductImage)


@pytest.mark.django_db
def test_created_at_attribute(product_image_link):
    assert isinstance(product_image_link.created_at, dt.datetime)


@pytest.mark.django_db
def test_modified_at_attribute(product_image_link):
    assert isinstance(product_image_link.modified_at, dt.datetime)


@pytest.mark.django_db
def test_position_attribute(product_image_link):
    assert isinstance(product_image_link.position, int)


@pytest.mark.django_db
def test_position_attribute_defaults_to_zero(new_product_image_link):
    assert new_product_image_link.position == 0


@pytest.mark.django_db
def test_get_highest_image_position_method(product_factory, product_image_link_factory):
    product = product_factory.create()
    for i in range(5):
        product_image_link_factory.create(product=product, position=i)
    assert models.ProductImageLink.objects.get_highest_image_position(product.id) == 4


@pytest.mark.django_db
def test_set_image_order_method(product_factory, product_image_link_factory):
    product = product_factory.create()
    links = product_image_link_factory.create_batch(5, product=product)
    new_order = [4, 2, 1, 0, 3]
    image_order = [links[i].image.id for i in new_order]
    models.ProductImageLink.objects.set_image_order(product.id, image_order)
    for i, link in enumerate(links):
        link.refresh_from_db()
        assert link.position == new_order.index(i)


@pytest.mark.django_db
def test_set_image_order_fails_when_passed_incorrect_image_ids(
    product_image_link_factory, product_factory
):
    product = product_factory.create()
    product_image_link_factory.create_batch(5, product=product)
    with pytest.raises(Exception):
        models.ProductImageLink.objects.set_image_order(product.id, [55, 99, 1, 22, 3])


@pytest.mark.django_db
def test_normalize_image_positions_method(product_image_link_factory, product_factory):
    product = product_factory.create()
    links = [
        product_image_link_factory.create(product=product, position=0),
        product_image_link_factory.create(product=product, position=20),
        product_image_link_factory.create(product=product, position=55),
    ]
    models.ProductImageLink.objects.normalize_image_positions(product.id)
    for i, link in enumerate(links):
        link.refresh_from_db()
        assert link.position == i


class TestAddImagesMethod:
    @pytest.fixture
    def extra_uploaded_images(self, extra_image_paths):
        images = []
        for path in extra_image_paths:
            with open(path, "rb") as f:
                images.append(SimpleUploadedFile(name="file_name", content=f.read()))
        return images

    @pytest.mark.django_db
    def test_method(self, product_factory, uploaded_file):
        product = product_factory.create()
        models.ProductImageLink.objects.add_images([product], [uploaded_file])
        assert models.ProductImageLink.objects.filter(
            product=product, position=0
        ).exists()

    @pytest.mark.django_db
    def test_method_uses_existing_image(self, product_factory, create_upload_file):
        image = models.ProductImage.objects.add_image(create_upload_file())
        product = product_factory.create()
        models.ProductImageLink.objects.add_images([product], [create_upload_file()])
        assert models.ProductImageLink.objects.filter(
            product=product, image=image, position=0
        ).exists()

    @pytest.mark.django_db
    def test_with_existing_images(
        self, product_factory, product_image_link_factory, uploaded_file
    ):
        product = product_factory.create()
        existing_links = product_image_link_factory.create_batch(5, product=product)
        models.ProductImageLink.objects.add_images([product], [uploaded_file])
        links = models.ProductImageLink.objects.filter(product=product)
        assert len(links) == 6
        for link in links:
            if link.id not in [_.id for _ in existing_links]:
                assert link.position == 5

    @pytest.mark.django_db
    def test_with_multiple_products(
        self, product_factory, uploaded_file, test_image_hash
    ):
        products = product_factory.create_batch(5)
        models.ProductImageLink.objects.add_images(products, [uploaded_file])
        for product in products:
            assert models.ProductImageLink.objects.filter(
                product=product, position=0, image__hash=test_image_hash
            ).exists()

    @pytest.mark.django_db
    def test_with_multiple_images(self, product_factory, extra_uploaded_images):
        product = product_factory.create()
        models.ProductImageLink.objects.add_images([product], extra_uploaded_images)
        assert models.ProductImageLink.objects.filter(product=product).count() == len(
            extra_uploaded_images
        )

    @pytest.mark.django_db
    def test_with_multiple_products_and_images(
        self, product_factory, extra_uploaded_images
    ):
        products = product_factory.create_batch(5)
        models.ProductImageLink.objects.add_images(products, extra_uploaded_images)
        for product in products:
            assert models.ProductImageLink.objects.filter(
                product=product
            ).count() == len(extra_uploaded_images)
