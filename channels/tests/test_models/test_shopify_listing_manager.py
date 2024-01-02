from decimal import Decimal
from unittest import mock

import pytest

from channels.models.shopify_models import ShopifyListingManager


@pytest.fixture
def mock_session():
    with mock.patch("channels.models.shopify_models.shopify_listing.session") as m:
        yield m


@pytest.fixture
def mock_products():
    with mock.patch("channels.models.shopify_models.shopify_listing.products") as m:
        yield m


@pytest.fixture
def mock_shopify_manager():
    with mock.patch(
        "channels.models.shopify_models.shopify_listing.ShopifyManager"
    ) as m:
        yield m


def test_get_shopify_product_method(mock_session, mock_products):
    product_id = 3267980498
    value = ShopifyListingManager._get_shopify_product(product_id)
    mock_products.get_product_by_id.assert_called_once_with(product_id=product_id)
    assert value == mock_products.get_product_by_id.return_value


def test_get_options_method_with_single_product(mock_session, mock_products):
    listing = mock.Mock()
    listing.variations.count = 1
    assert ShopifyListingManager._get_options(listing) is None


def test_get_options_method(mock_session, mock_products):
    listing = mock.Mock()
    listing.variations.count = 3
    value = ShopifyListingManager._get_options(listing)
    mock_products.create_options.assert_called_once_with(
        listing.product_range.variation_option_values.return_value
    )
    assert value == mock_products.create_options.return_value


def test_set_variant_details(mock_session, mock_products):
    variant = mock.Mock()
    product = mock.Mock(
        sku="AAA-BBB-CCC",
        barcode="999999999999",
        weight_grams=500,
    )
    variation = mock.Mock(product=product, price=Decimal(21.45))
    ShopifyListingManager._set_variant_details(variant=variant, variation=variation)
    assert variant.sku == product.sku
    assert variant.barcode == product.barcode
    assert variant.grams == product.weight_grams
    assert variant.price == float(variation.price)
    assert variant.weight_unit == "g"
    assert variant.tracked is True


def test_set_product_details(mock_session, mock_products):
    listing = mock.Mock(title="Listing Title", description="Description Text")
    listing.product_range.products.variations.return_value.first.return_value.brand.name = (
        "Brand Name"
    )
    listing.tags.values_list.return_value = ["A", "B", "C"]
    product = mock.Mock()
    ShopifyListingManager._set_product_details(product=product, listing=listing)
    assert product.title == listing.title
    assert product.body_html == listing.description
    assert product.vendor == "Brand Name"
    assert product.tags == "A,B,C"


@pytest.mark.django_db
def test_set_customs_information(mock_session, mock_products, product_factory):
    products = product_factory.create_batch(3)
    variants = [mock.Mock(sku=product.sku) for product in products]
    shopify_product = mock.Mock(variants=variants)
    expected_calls = (
        mock.call(
            inventory_item_id=variants[i].inventory_item_id,
            country_of_origin_code="CN",
            hs_code=products[i].hs_code,
        )
        for i in range(len(products))
    )
    ShopifyListingManager._set_customs_information(shopify_product)
    mock_products.set_customs_information.assert_has_calls(expected_calls)


def test_de_duplicate_images_method(mock_session, mock_products):
    image_1 = mock.Mock(id=1111)
    duplicate_image = mock.Mock(id=1111)
    image_2 = mock.Mock(id=2222)
    value = ShopifyListingManager.de_duplicate_images(
        [image_1, duplicate_image, image_2]
    )
    assert value == [image_1, image_2]


def test_set_collections_method(mock_shopify_manager):
    collections = [mock.Mock(), mock.Mock()]
    shopify_product = mock.Mock()
    shopify_listing_object = mock.Mock()
    shopify_listing_object.collections.all.return_value = collections
    expected_calls = (
        mock.call(product_id=shopify_product.id, collection_id=collection.collection_id)
        for collection in collections
    )
    ShopifyListingManager._set_collections(
        shopify_product=shopify_product, shopify_listing_object=shopify_listing_object
    )
    mock_shopify_manager.add_product_to_collection.assert_has_calls(expected_calls)


def test_update_collections_method(mock_shopify_manager):
    shopify_product = mock.Mock()
    shopify_listing_object = mock.Mock()
    ShopifyListingManager._set_collections = mock.Mock()
    ShopifyListingManager._update_collections(
        shopify_product=shopify_product, shopify_listing_object=shopify_listing_object
    )
    mock_shopify_manager.remove_product_from_all_collections.assert_called_once_with(
        product_id=shopify_product.id
    )
    ShopifyListingManager._set_collections.assert_called_once_with(
        shopify_product=shopify_product, shopify_listing_object=shopify_listing_object
    )


@mock.patch("channels.models.shopify_models.shopify_listing.ProductRangeImageLink")
def test_get_product_range_images_method(mock_product_range_image_link):
    product_range = mock.Mock()
    image_links = [mock.Mock(), mock.Mock(), mock.Mock()]
    mock_product_range_image_link.objects.filter.return_value = image_links
    value = ShopifyListingManager._get_product_range_images(product_range=product_range)
    mock_product_range_image_link.objects.filter.assert_called_once_with(
        product_range=product_range
    )
    assert value == [image_link.image for image_link in image_links]


@mock.patch("channels.models.shopify_models.shopify_listing.BaseProduct")
@mock.patch("channels.models.shopify_models.shopify_listing.ProductImageLink")
def test_get_product_images_method(mock_product_image_link, mock_base_product):
    variant = mock.Mock()
    image_links = [mock.Mock(), mock.Mock(), mock.Mock()]
    mock_product_image_link.objects.filter.return_value = image_links
    value = ShopifyListingManager._get_product_images(variant=variant)
    mock_base_product.objects.get.assert_called_once_with(sku=variant.sku)
    mock_product_image_link.objects.filter.assert_called_once_with(
        product=mock_base_product.objects.get.return_value
    )
    assert value == [image_link.image for image_link in image_links]


@mock.patch(
    "channels.models.shopify_models.shopify_listing.ShopifyListingManager._get_listing_images"
)
def test_set_listing_images_method(
    mock_get_listing_images, mock_products, mock_session
):
    shopify_product = mock.Mock()
    product_range = mock.Mock()
    images = [mock.Mock(), mock.Mock(), mock.Mock(), mock.Mock(), mock.Mock()]
    variant_images = {images[2]: [1111, 2222], images[4]: [3333, 4444, 5555]}
    mock_get_listing_images.return_value = (images, variant_images)
    ShopifyListingManager._set_listing_images(
        shopify_product=shopify_product, product_range=product_range
    )
    ShopifyListingManager._get_listing_images.assert_called_once_with(
        shopify_product=shopify_product, product_range=product_range
    )
    product_images_calls = [
        mock.call(product_id=shopify_product.id, image_url=image.square_image.url)
        for image in images
    ]
    variation_image_calls = [
        mock.call(
            product_id=shopify_product.id,
            image_url=image.square_image.url,
            variant_ids=variant_ids,
        )
        for image, variant_ids in variant_images.items()
    ]
    mock_products.add_product_image.assert_has_calls(
        product_images_calls + variation_image_calls
    )


@mock.patch(
    "channels.models.shopify_models.shopify_listing.ShopifyListingManager.de_duplicate_images"
)
@mock.patch(
    "channels.models.shopify_models.shopify_listing.ShopifyListingManager._get_product_range_images"
)
@mock.patch(
    "channels.models.shopify_models.shopify_listing.ShopifyListingManager._get_product_images"
)
def test_get_listing_images_method(
    mock_get_product_images, mock_get_product_range_images, mock_de_duplicate_images
):
    images = [mock.Mock() for _ in range(10)]
    variants = [mock.Mock() for _ in range(4)]
    shopify_product = mock.Mock(variants=variants)
    product_range = mock.Mock()
    range_images = [images[i] for i in [0, 1, 2, 3]]
    product_iages = [
        [images[i] for i in [4, 5, 6]],
        [images[i] for i in [7, 8, 9]],
        [],
        [images[i] for i in [4, 8, 9]],
    ]
    mock_get_product_range_images.return_value = range_images
    mock_get_product_images.side_effect = product_iages
    (
        returned_images,
        returned_variant_images,
    ) = ShopifyListingManager._get_listing_images(
        shopify_product=shopify_product, product_range=product_range
    )
    ShopifyListingManager._get_product_range_images.assert_called_once_with(
        product_range
    )
    ShopifyListingManager._get_product_images.assert_has_calls(
        (mock.call(variant) for variant in variants)
    )
    mock_de_duplicate_images.assert_called_once_with(
        [
            images[0],
            images[1],
            images[2],
            images[3],
            images[5],
            images[6],
            images[8],
            images[9],
            images[8],
            images[9],
        ]
    )
    assert returned_images == mock_de_duplicate_images.return_value
    assert returned_variant_images == {
        images[4]: [variants[0].id, variants[3].id],
        images[7]: [variants[1].id],
    }


def test_get_variants_method(mock_products, mock_session):
    variants = [mock.Mock(price=Decimal("3.99")) for i in range(3)]
    variants[0].product.variation.return_value = {"Size": "Small", "Colour": "Red"}
    variants[1].product.variation.return_value = {"Size": "Medium", "Colour": "Green"}
    variants[2].product.variation.return_value = {"Size": "Large", "Colour": "Blue"}
    shopify_listing_object = mock.Mock()
    shopify_listing_object.variations.all.return_value = variants
    options = [mock.Mock() for _ in range(2)]
    options[0].name = "Size"
    options[1].name = "Colour"
    value = ShopifyListingManager._get_variants(shopify_listing_object, options=options)
    assert value == [mock_products.create_variation.return_value] * 3
    mock_products.create_variation.assert_has_calls(
        (
            mock.call(
                sku=variant.product.sku,
                option_values=list(variant.product.variation.return_value.values()),
                barcode=variant.product.barcode,
                grams=variant.product.weight_grams,
                price=float(variant.price),
            )
            for variant in variants
        )
    )


@mock.patch(
    "channels.models.shopify_models.shopify_listing.ShopifyListingManager._get_shopify_product"
)
@mock.patch(
    "channels.models.shopify_models.shopify_listing.ShopifyListingManager._set_variant_details"
)
@mock.patch(
    "channels.models.shopify_models.shopify_listing.ShopifyListingManager._set_listing_images"
)
@mock.patch(
    "channels.models.shopify_models.shopify_listing.ShopifyListingManager._update_collections"
)
@mock.patch(
    "channels.models.shopify_models.shopify_listing.ShopifyListingManager._set_product_details"
)
def test_update_listing_method(
    mock_set_product_details,
    mock_update_collections,
    mock_set_listing_images,
    mock_set_variant_details,
    mock_get_shopify_product,
    mock_products,
    mock_session,
):
    shopify_listing_object = mock.Mock()
    product = mock.Mock()
    product.variants = [mock.Mock() for _ in range(3)]
    mock_get_shopify_product.return_value = product
    ShopifyListingManager.update_listing(shopify_listing_object)
    mock_get_shopify_product.assert_called_once_with(shopify_listing_object.product_id)
    mock_set_product_details.assert_called_once_with(
        product=mock_get_shopify_product.return_value, listing=shopify_listing_object
    )
    assert product.images == []
    product.save.assert_called_once_with()
    shopify_listing_object.variations.get.assert_has_calls(
        (mock.call(product__sku=variant.sku) for variant in product.variants),
    )
    mock_set_variant_details.assert_has_calls(
        mock.call(
            variant=variant,
            variation=shopify_listing_object.variations.get.return_value,
        )
        for variant in product.variants
    )
    for variant in product.variants:
        variant.save.assert_called_once_with()
    mock_set_listing_images.assert_called_once_with(
        shopify_product=mock_get_shopify_product.return_value,
        product_range=shopify_listing_object.product_range,
    )
    mock_update_collections.assert_called_once_with(
        mock_get_shopify_product.return_value, shopify_listing_object
    )


@pytest.fixture
def mock_set_collections():
    with mock.patch(
        "channels.models.shopify_models.shopify_listing.ShopifyListingManager._set_collections"
    ) as m:
        yield m


@pytest.fixture
def mock_set_listing_images():
    with mock.patch(
        "channels.models.shopify_models.shopify_listing.ShopifyListingManager._set_listing_images"
    ) as m:
        yield m


@pytest.fixture
def mock_set_customs_information():
    with mock.patch(
        "channels.models.shopify_models.shopify_listing.ShopifyListingManager._set_customs_information"
    ) as m:
        yield m


@pytest.fixture
def mock_shopify_variation():
    with mock.patch(
        "channels.models.shopify_models.shopify_listing.ShopifyVariation"
    ) as m:
        yield m


@pytest.fixture
def mock_set_variant_details():
    with mock.patch(
        "channels.models.shopify_models.shopify_listing.ShopifyListingManager._set_variant_details"
    ) as m:
        yield m


@pytest.fixture
def mock_get_variants():
    with mock.patch(
        "channels.models.shopify_models.shopify_listing.ShopifyListingManager._get_variants"
    ) as m:
        yield m


@pytest.fixture
def mock_get_options():
    with mock.patch(
        "channels.models.shopify_models.shopify_listing.ShopifyListingManager._get_options"
    ) as m:
        yield m


@pytest.fixture
def mock_create_variations():
    with mock.patch(
        "channels.models.shopify_models.shopify_listing.ShopifyListingManager._create_variations"
    ) as m:
        yield m


def test_create_listing_method_creates_product(
    mock_get_options,
    mock_get_variants,
    mock_set_customs_information,
    mock_set_listing_images,
    mock_set_collections,
    mock_session,
    mock_products,
    mock_create_variations,
):
    shopify_listing_object = mock.Mock()
    tag_names = ["A", "B", "C"]
    tags = []
    for name in tag_names:
        tag = mock.Mock()
        tag.name = name
        tags.append(tag)
    shopify_listing_object.tags.all.return_value = tags
    ShopifyListingManager.create_listing(shopify_listing_object)
    mock_get_options.assert_called_once_with(shopify_listing_object)
    mock_get_variants.assert_called_once_with(
        shopify_listing_object, options=mock_get_options.return_value
    )
    mock_products.create_product.assert_called_once_with(
        title=shopify_listing_object.title,
        body_html=shopify_listing_object.description,
        variants=mock_get_variants.return_value,
        options=mock_get_options.return_value,
        tags=tag_names,
        vendor=shopify_listing_object.product_range.products.variations.return_value.first.return_value.brand.name,
    )


def test_create_listing_method_creates_variations(
    mock_get_options,
    mock_get_variants,
    mock_set_customs_information,
    mock_set_listing_images,
    mock_set_collections,
    mock_session,
    mock_products,
    mock_create_variations,
):
    shopify_listing_object = mock.Mock()
    shopify_listing_object.tags.all.return_value = []
    ShopifyListingManager.create_listing(shopify_listing_object)
    mock_create_variations.assert_called_once_with(
        shopify_listing_object=shopify_listing_object,
        shopify_product=mock_products.create_product.return_value,
    )


def test_create_listing_method_sets_customs_information(
    mock_get_options,
    mock_get_variants,
    mock_set_customs_information,
    mock_set_listing_images,
    mock_set_collections,
    mock_session,
    mock_products,
    mock_create_variations,
):
    shopify_listing_object = mock.Mock()
    shopify_listing_object.tags.all.return_value = []
    ShopifyListingManager.create_listing(shopify_listing_object)
    mock_set_customs_information.assert_called_once_with(
        mock_products.create_product.return_value
    )


def test_create_listing_method_sets_listing_images(
    mock_get_options,
    mock_get_variants,
    mock_set_customs_information,
    mock_set_listing_images,
    mock_set_collections,
    mock_session,
    mock_products,
    mock_create_variations,
):
    shopify_listing_object = mock.Mock()
    shopify_listing_object.tags.all.return_value = []
    ShopifyListingManager.create_listing(shopify_listing_object)
    mock_set_listing_images.assert_called_once_with(
        mock_products.create_product.return_value, shopify_listing_object.product_range
    )


def test_create_listing_method_sets_collections(
    mock_get_options,
    mock_get_variants,
    mock_set_customs_information,
    mock_set_listing_images,
    mock_set_collections,
    mock_session,
    mock_products,
    mock_create_variations,
):
    shopify_listing_object = mock.Mock()
    shopify_listing_object.tags.all.return_value = []
    ShopifyListingManager.create_listing(shopify_listing_object)
    mock_set_collections.assert_called_once_with(
        mock_products.create_product.return_value, shopify_listing_object
    )


@pytest.fixture
def mock_transaction():
    with mock.patch("channels.models.shopify_models.shopify_listing.transaction") as m:
        yield m


def test_create_variations_sets_product_id(
    mock_transaction,
    mock_shopify_variation,
    mock_set_variant_details,
    mock_session,
    mock_products,
):
    shopify_listing_object = mock.Mock()
    shopify_product = mock.Mock(variants=[])
    ShopifyListingManager._create_variations(shopify_listing_object, shopify_product)
    assert shopify_listing_object.product_id == shopify_product.id
    shopify_listing_object.save.assert_called_once_with()


def test_create_variations_updates_variations(
    mock_transaction,
    mock_shopify_variation,
    mock_set_variant_details,
    mock_session,
    mock_products,
):
    variants = [mock.Mock() for _ in range(3)]
    variations = [mock.Mock() for _ in range(3)]
    mock_shopify_variation.objects.get.side_effect = variations
    shopify_listing_object = mock.Mock()
    shopify_product = mock.Mock(variants=variants)
    ShopifyListingManager._create_variations(shopify_listing_object, shopify_product)
    mock_shopify_variation.objects.get.assert_has_calls(
        mock.call(product__sku=variant.sku) for variant in variants
    )
    for i in range(len(variations)):
        assert variations[i].variant_id == variants[i].id
        assert variations[i].inventory_item_id == variants[i].inventory_item_id
        variations[i].save.assert_called_once_with()
    mock_set_variant_details.assert_not_called()


def test_create_variations_updates_single_variation(
    mock_transaction,
    mock_shopify_variation,
    mock_set_variant_details,
    mock_session,
    mock_products,
):
    variants = [mock.Mock()]
    variations = [mock.Mock() for _ in range(3)]
    mock_shopify_variation.objects.get.side_effect = variations
    shopify_listing_object = mock.Mock()
    shopify_product = mock.Mock(variants=variants)
    ShopifyListingManager._create_variations(shopify_listing_object, shopify_product)
    mock_set_variant_details.assert_called_once_with(
        variant=variants[0],
        variation=shopify_listing_object.variations.first.return_value,
    )
    variants[0].save.assert_called_once_with()
