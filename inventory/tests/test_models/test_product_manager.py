import pytest

from inventory import models


@pytest.fixture
def base_product(base_product_factory):
    return base_product_factory.create()


@pytest.fixture
def product(product_factory):
    return product_factory.create()


@pytest.fixture
def initial_variation(initial_variation_factory):
    return initial_variation_factory.create()


@pytest.fixture
def multipack_product(multipack_product_factory):
    return multipack_product_factory.create()


@pytest.fixture
def combination_product(combination_product_factory):
    return combination_product_factory.create()


@pytest.mark.django_db
def test_sorts_by_range_order(product_range_factory, product_factory):
    product_range = product_range_factory.create()
    for i in reversed(range(3)):
        product_factory.create(product_range=product_range, range_order=i)
    queryset = models.BaseProduct.objects.filter(product_range=product_range)
    for i, product in enumerate(queryset):
        assert product.range_order == i


@pytest.mark.django_db
@pytest.mark.parametrize(
    "status,included",
    (
        (models.ProductRange.COMPLETE, True),
        (models.ProductRange.CREATING, False),
        (models.ProductRange.ERROR, False),
    ),
)
def test_complete_filter(status, included, product_factory):
    product = product_factory.create(product_range__status=status)
    qs = models.BaseProduct.objects.complete()
    assert (product in qs) is included


@pytest.mark.django_db
@pytest.mark.parametrize(
    "status,included",
    (
        (models.ProductRange.COMPLETE, False),
        (models.ProductRange.CREATING, True),
        (models.ProductRange.ERROR, False),
    ),
)
def test_incomplete_filter(status, included, product_factory):
    product = product_factory.create(product_range__status=status)
    qs = models.BaseProduct.objects.incomplete()
    assert (product in qs) is included


@pytest.mark.django_db
def test_simple_filter_returns_base_product(base_product):
    assert base_product in models.BaseProduct.objects.simple()


@pytest.mark.django_db
def test_simple_filter_returns_product(product):
    assert product in models.BaseProduct.objects.simple()


@pytest.mark.django_db
def test_simple_filter_does_not_return_initial_vairiation(initial_variation):
    assert initial_variation not in models.BaseProduct.objects.simple()


@pytest.mark.django_db
def test_simple_filter_does_not_return_multipack_product(multipack_product):
    assert multipack_product not in models.BaseProduct.objects.simple()


@pytest.mark.django_db
def test_simple_filter_does_not_return_combination_product(combination_product):
    assert combination_product not in models.BaseProduct.objects.simple()


@pytest.mark.django_db
def test_variations_filter_returns_base_product(base_product):
    assert base_product in models.BaseProduct.objects.variations()


@pytest.mark.django_db
def test_variations_filter_returns_product(product):
    assert product in models.BaseProduct.objects.variations()


@pytest.mark.django_db
def test_variations_filter_does_not_return_initial_vairiation(initial_variation):
    assert initial_variation not in models.BaseProduct.objects.variations()


@pytest.mark.django_db
def test_variations_filter_returns_multipack_product(multipack_product):
    assert multipack_product in models.BaseProduct.objects.variations()


@pytest.mark.django_db
def test_variations_filter_returns_combination_product(combination_product):
    assert combination_product in models.BaseProduct.objects.variations()


@pytest.mark.django_db
def test_active_returns_not_archived_products(product_factory):
    product = product_factory.create(is_archived=False)
    assert product in models.BaseProduct.objects.active()


@pytest.mark.django_db
def test_active_does_not_return_archived_products(product_factory):
    product = product_factory.create(is_archived=True)
    assert product not in models.BaseProduct.objects.active()


@pytest.mark.django_db
def test_does_not_return_non_matching_products(product):
    assert product not in models.BaseProduct.objects.text_search("josdggnjgsdlkhsdfoh")


@pytest.mark.django_db
def test_text_search_matches_on_range_name(product):
    assert product in models.BaseProduct.objects.text_search(product.product_range.name)


@pytest.mark.django_db
def test_text_search_matches_on_range_sku(product):
    assert product in models.BaseProduct.objects.text_search(product.product_range.sku)


@pytest.mark.django_db
def test_text_search_matches_on_sku(product):
    assert product in models.BaseProduct.objects.text_search(product.sku)


@pytest.mark.django_db
def test_text_search_matches_on_supplier_sku(product):
    assert product in models.BaseProduct.objects.text_search(product.supplier_sku)


@pytest.mark.django_db
def test_text_search_matches_on_barcode(product):
    assert product in models.BaseProduct.objects.text_search(product.barcode)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "arg,archived,included",
    (
        (None, False, True),
        (None, True, True),
        (True, False, False),
        (True, True, True),
        (False, False, True),
        (False, True, False),
    ),
)
def test_archived_filter(arg, archived, included, product_factory):
    product = product_factory.create(is_archived=archived)
    qs = models.BaseProduct.objects.text_search(product.sku, archived=arg)
    assert (product in qs) is included
