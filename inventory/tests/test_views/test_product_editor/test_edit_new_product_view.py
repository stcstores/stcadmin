import pytest
from django.urls import reverse

from inventory import models


@pytest.fixture
def product_range(product_range_factory):
    return product_range_factory.create(status=models.ProductRange.CREATING)


@pytest.fixture
def colour_option(variation_option_factory):
    return variation_option_factory.create(name="Colour")


@pytest.fixture
def size_option(variation_option_factory):
    return variation_option_factory.create(name="Size")


@pytest.fixture
def products(
    colour_option,
    size_option,
    product_range,
    product_factory,
    variation_option_value_factory,
):
    products = []
    for colour in ("Red", "Green", "Blue"):
        for size in ("Small", "Medium", "Large"):
            product = product_factory.create(product_range=product_range)
            variation_option_value_factory.create(
                variation_option=colour_option, product=product, value=colour
            )
            variation_option_value_factory.create(
                variation_option=size_option, product=product, value=size
            )
            products.append(product)
    return products


@pytest.fixture
def url(products, product_range):
    return reverse("inventory:edit_new_product", kwargs={"range_pk": product_range.pk})


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "inventory/product_editor/edit_new_product.html" in (
        t.name for t in get_response.templates
    )


@pytest.mark.django_db
def test_product_range_in_context(product_range, get_response):
    assert get_response.context["product_range"] == product_range


@pytest.mark.django_db
def test_get_variation_matrix(products, get_response):
    variation_matrix = get_response.context["variations"]
    assert isinstance(variation_matrix, dict)
    for colour in ("Red", "Green", "Blue"):
        for size in ("Small", "Medium", "Large"):
            assert (colour, size) in variation_matrix.keys()
    for product in products:
        assert product in variation_matrix.values()


@pytest.mark.django_db
def test_none_in_variation_matrix_for_non_existant_variations(
    products, group_logged_in_client, url
):
    products[0].delete()
    variation_matrix = group_logged_in_client.get(url).context["variations"]
    assert variation_matrix[("Red", "Small")] is None
