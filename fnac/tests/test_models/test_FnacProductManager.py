import pytest

from fnac import models


@pytest.mark.django_db
@pytest.mark.parametrize(
    "product_kwargs,returned",
    [
        ({"created": False, "do_not_create": False, "stock_level": 5}, True),
        ({"created": True, "do_not_create": False, "stock_level": 5}, False),
        ({"created": False, "do_not_create": True, "stock_level": 5}, False),
        ({"created": True, "do_not_create": True, "stock_level": 5}, False),
        ({"created": False, "do_not_create": False, "stock_level": 0}, False),
        ({"created": True, "do_not_create": False, "stock_level": 0}, False),
        ({"created": False, "do_not_create": True, "stock_level": 0}, False),
        ({"created": True, "do_not_create": True, "stock_level": 0}, False),
    ],
)
def test_to_be_created_method(fnac_product_factory, product_kwargs, returned):
    product = fnac_product_factory.create(**product_kwargs)
    assert (product in models.FnacProduct.objects.to_be_created()) is returned


@pytest.mark.django_db
@pytest.mark.parametrize(
    "product_kwargs,returned",
    [
        ({"created": False, "do_not_create": False, "stock_level": 0}, True),
        ({"created": True, "do_not_create": False, "stock_level": 0}, True),
        ({"created": False, "do_not_create": True, "stock_level": 0}, False),
        ({"created": True, "do_not_create": True, "stock_level": 0}, False),
        ({"created": False, "do_not_create": False, "stock_level": 5}, False),
        ({"created": True, "do_not_create": False, "stock_level": 5}, False),
        ({"created": False, "do_not_create": True, "stock_level": 5}, False),
        ({"created": True, "do_not_create": True, "stock_level": 5}, False),
    ],
)
def test_out_of_stock_method(fnac_product_factory, product_kwargs, returned):
    product = fnac_product_factory.create(**product_kwargs)
    assert (product in models.FnacProduct.objects.out_of_stock()) is returned


@pytest.mark.django_db
@pytest.mark.parametrize(
    "product_kwargs,returned",
    [
        ({"created": False, "do_not_create": False, "stock_level": 0}, False),
        ({"created": True, "do_not_create": False, "stock_level": 0}, False),
        ({"created": False, "do_not_create": True, "stock_level": 0}, False),
        ({"created": True, "do_not_create": True, "stock_level": 0}, False),
        ({"created": False, "do_not_create": False, "stock_level": 5}, True),
        ({"created": True, "do_not_create": False, "stock_level": 5}, True),
        ({"created": False, "do_not_create": True, "stock_level": 5}, False),
        ({"created": True, "do_not_create": True, "stock_level": 5}, False),
    ],
)
def test_in_stock_method(fnac_product_factory, product_kwargs, returned):
    product = fnac_product_factory.create(**product_kwargs)
    assert (product in models.FnacProduct.objects.in_stock()) is returned


@pytest.mark.django_db
@pytest.mark.parametrize(
    "product_kwargs,translation_kwargs,returned",
    [
        ({}, {}, True),
        ({"colour": ""}, {}, True),
        ({"colour": "Red"}, {}, True),
        ({"colour": ""}, {"colour": ""}, True),
        ({}, None, False),
        ({"created": True}, None, False),
        ({"do_not_create": True}, None, False),
        ({"created": True, "do_not_create": True}, None, False),
        ({"created": True}, {}, True),
        ({"do_not_create": True}, {}, False),
        ({"created": True, "do_not_create": True}, {}, False),
        ({}, {"name": ""}, False),
        ({}, {"description": ""}, False),
        ({}, {"name": "", "description": ""}, False),
        ({"colour": "Red"}, {"colour": ""}, False),
        ({"colour": "Red"}, {"name": ""}, False),
        ({"colour": "Red"}, {"colour": "", "name": ""}, False),
        ({"colour": ""}, {"colour": "", "name": ""}, False),
        ({"colour": "", "created": True}, {}, True),
        ({"colour": "", "do_not_create": True}, {}, False),
        ({"description": ""}, {}, False),
        ({"barcode": ""}, {}, False),
        ({"image_1": ""}, {}, False),
    ],
)
def test_translated_method(
    fnac_product_factory,
    translation_factory,
    product_kwargs,
    translation_kwargs,
    returned,
):
    product = fnac_product_factory.create(**product_kwargs)
    if translation_kwargs is not None:
        translation_factory.create(product=product, **translation_kwargs)
    assert (product in models.FnacProduct.objects.translated()) is returned


@pytest.mark.django_db
@pytest.mark.parametrize(
    "product_kwargs,translation_kwargs,returned",
    [
        ({}, None, True),
        ({}, {"name": "", "description": ""}, True),
        ({"colour": "Red"}, {"colour": ""}, True),
        ({"colour": "Red"}, {"name": ""}, True),
        ({"colour": "Red"}, {"colour": "", "name": ""}, True),
        ({"colour": ""}, {"colour": "", "name": ""}, True),
        ({}, {}, False),
        ({"colour": ""}, {}, False),
        ({"colour": "Red"}, {}, False),
        ({"colour": ""}, {"colour": ""}, False),
        ({"created": True}, None, True),
        ({"do_not_create": True}, None, False),
        ({"created": True, "do_not_create": True}, None, False),
        ({"created": True}, {}, False),
        ({"do_not_create": True}, {}, False),
        ({"created": True, "do_not_create": True}, {}, False),
        ({}, {"name": ""}, True),
        ({}, {"description": ""}, True),
        ({"colour": "", "created": True}, {}, False),
        ({"colour": "", "do_not_create": True}, {}, False),
        ({"description": ""}, {}, False),
        ({"barcode": ""}, {}, False),
        ({"image_1": ""}, {}, False),
    ],
)
def test_not_translated_method(
    fnac_product_factory,
    translation_factory,
    product_kwargs,
    translation_kwargs,
    returned,
):
    product = fnac_product_factory.create(**product_kwargs)
    if translation_kwargs is not None:
        translation_factory.create(product=product, **translation_kwargs)
    assert (product in models.FnacProduct.objects.not_translated()) is returned


@pytest.mark.django_db
@pytest.mark.parametrize(
    "product_kwargs,returned",
    [
        ({"barcode": "954123687121"}, True),
        ({"barcode": ""}, False),
        ({"barcode": "954123687121", "created": True}, True),
        ({"barcode": "954123687121", "do_not_create": True}, False),
    ],
)
def test_barcode_valid(fnac_product_factory, product_kwargs, returned):
    product = fnac_product_factory.create(**product_kwargs)
    assert (product in models.FnacProduct.objects.barcode_valid()) is returned


@pytest.mark.django_db
@pytest.mark.parametrize(
    "product_kwargs,returned",
    [
        ({"barcode": ""}, True),
        ({"barcode": "954123687121"}, False),
        ({"barcode": "954123687121", "created": True}, False),
        ({"barcode": "954123687121", "do_not_create": True}, False),
    ],
)
def test_barcode_invalid(fnac_product_factory, product_kwargs, returned):
    product = fnac_product_factory.create(**product_kwargs)
    assert (product in models.FnacProduct.objects.barcode_invalid()) is returned


@pytest.mark.django_db
@pytest.mark.parametrize(
    "product_kwargs,returned",
    [
        ({"image_1": "954123687121.jpg"}, True),
        ({"image_1": ""}, False),
        ({"image_1": "954123687121.jpg", "created": True}, True),
        ({"image_1": "954123687121.jpg", "do_not_create": True}, False),
    ],
)
def test_has_image(fnac_product_factory, product_kwargs, returned):
    product = fnac_product_factory.create(**product_kwargs)
    assert (product in models.FnacProduct.objects.has_image()) is returned


@pytest.mark.django_db
@pytest.mark.parametrize(
    "product_kwargs,returned",
    [
        ({"image_1": ""}, True),
        ({"image_1": "954123687121.jpg"}, False),
        ({"image_1": "954123687121.jpg", "created": True}, False),
        ({"image_1": "954123687121.jpg", "do_not_create": True}, False),
    ],
)
def test_missing_image(fnac_product_factory, product_kwargs, returned):
    product = fnac_product_factory.create(**product_kwargs)
    assert (product in models.FnacProduct.objects.missing_image()) is returned


@pytest.mark.django_db
@pytest.mark.parametrize(
    "product_kwargs,size_kwargs,returned",
    [
        ({"english_size": "Red", "created": True}, {"name": "Rouge"}, True),
        ({"english_size": "Red", "created": False}, {"name": "Rouge"}, True),
        ({"english_size": "", "created": True}, None, True),
        ({"english_size": "", "created": False}, None, True),
        ({"english_size": "", "created": True}, {"name": "Rouge"}, True),
        ({"english_size": "", "created": False}, {"name": "Rouge"}, True),
        ({"english_size": "Red", "created": True}, None, True),
        ({"english_size": "Red", "created": False}, None, False),
        ({"english_size": "Red", "created": True}, {"name": "Rouge"}, True),
        (
            {"english_size": "Red", "do_not_create": True, "created": True},
            {"name": "Rouge"},
            False,
        ),
        (
            {"english_size": "Red", "do_not_create": True, "created": False},
            {"name": "Rouge"},
            False,
        ),
    ],
)
def test_size_valid(
    fnac_product_factory, size_factory, product_kwargs, size_kwargs, returned
):
    if size_kwargs is not None:
        french_size = size_factory.create(**size_kwargs)
    else:
        french_size = None
    product = fnac_product_factory.create(french_size=french_size, **product_kwargs)
    assert (product in models.FnacProduct.objects.size_valid()) is returned


@pytest.mark.django_db
@pytest.mark.parametrize(
    "product_kwargs,size_kwargs,returned",
    [
        ({"english_size": "Red"}, None, True),
        ({"english_size": "Red", "created": True}, {"name": "Rouge"}, False),
        ({"english_size": "Red", "created": False}, {"name": "Rouge"}, False),
        ({"english_size": "", "created": False}, None, False),
        ({"english_size": "", "created": True}, None, False),
        ({"english_size": "", "created": False}, {"name": "Rouge"}, False),
        ({"english_size": "", "created": True}, {"name": "Rouge"}, False),
        ({"english_size": "Red", "created": True}, {"name": "Rouge"}, False),
        ({"english_size": "Red", "do_not_create": True}, {"name": "Rouge"}, False),
    ],
)
def test_size_invalid(
    fnac_product_factory, size_factory, product_kwargs, size_kwargs, returned
):
    if size_kwargs is not None:
        french_size = size_factory.create(**size_kwargs)
    else:
        french_size = None
    product = fnac_product_factory.create(french_size=french_size, **product_kwargs)
    assert (product in models.FnacProduct.objects.size_invalid()) is returned


@pytest.mark.django_db
@pytest.mark.parametrize(
    "product_kwargs,has_category,returned",
    [
        ({}, True, True),
        ({}, False, False),
        ({"created": True}, True, True),
        ({"do_not_create": True}, True, False),
        ({"created": True}, False, False),
        ({"do_not_create": True}, False, False),
    ],
)
def test_has_category(
    category_factory,
    fnac_range_factory,
    fnac_product_factory,
    product_kwargs,
    has_category,
    returned,
):
    if has_category is True:
        category = category_factory.create()
    else:
        category = None
    fnac_range = fnac_range_factory.create(category=category)
    product = fnac_product_factory.create(fnac_range=fnac_range, **product_kwargs)
    assert (product in models.FnacProduct.objects.has_category()) is returned


@pytest.mark.django_db
@pytest.mark.parametrize(
    "product_kwargs,has_category,returned",
    [
        ({}, False, True),
        ({}, True, False),
        ({"created": True}, True, False),
        ({"do_not_create": True}, True, False),
        ({"created": True}, False, True),
        ({"do_not_create": True}, False, False),
    ],
)
def test_missing_category(
    category_factory,
    fnac_range_factory,
    fnac_product_factory,
    product_kwargs,
    has_category,
    returned,
):
    if has_category is True:
        category = category_factory.create()
    else:
        category = None
    fnac_range = fnac_range_factory.create(category=category)
    product = fnac_product_factory.create(fnac_range=fnac_range, **product_kwargs)
    assert (product in models.FnacProduct.objects.missing_category()) is returned


@pytest.mark.django_db
@pytest.mark.parametrize(
    "product_kwargs,returned",
    [
        ({"price": 550}, True),
        ({"price": None}, False),
        ({"created": True}, True),
        ({"do_not_create": True}, False),
    ],
)
def test_has_price(fnac_product_factory, product_kwargs, returned):
    product = fnac_product_factory.create(**product_kwargs)
    assert (product in models.FnacProduct.objects.has_price()) is returned


@pytest.mark.django_db
@pytest.mark.parametrize(
    "product_kwargs,returned",
    [
        ({"price": None}, True),
        ({"price": 550}, False),
        ({"created": True}, False),
        ({"do_not_create": True}, False),
    ],
)
def test_missing_price(fnac_product_factory, product_kwargs, returned):
    product = fnac_product_factory.create(**product_kwargs)
    assert (product in models.FnacProduct.objects.missing_price()) is returned


@pytest.mark.django_db
@pytest.mark.parametrize(
    "product_kwargs,returned",
    [
        ({"description": "product description"}, True),
        ({"description": ""}, False),
        ({"created": True}, True),
        ({"do_not_create": True}, False),
        ({"created": True}, True),
    ],
)
def test_has_description(fnac_product_factory, product_kwargs, returned):
    product = fnac_product_factory.create(**product_kwargs)
    assert (product in models.FnacProduct.objects.has_description()) is returned


@pytest.mark.django_db
@pytest.mark.parametrize(
    "product_kwargs,returned",
    [
        ({"description": ""}, True),
        ({"description": "product description"}, False),
        ({"created": True}, False),
        ({"do_not_create": True}, False),
        ({"created": True}, False),
    ],
)
def test_missing_description(fnac_product_factory, product_kwargs, returned):
    product = fnac_product_factory.create(**product_kwargs)
    assert (product in models.FnacProduct.objects.missing_description()) is returned


@pytest.mark.django_db
@pytest.mark.parametrize(
    "product_kwargs,returned",
    [
        (
            {
                "description": "Description",
                "barcode": "5449762114",
                "image_1": "img.jpg",
            },
            False,
        ),
        ({"description": "", "barcode": "5449762114", "image_1": "img.jpg"}, True),
        ({"description": "Description", "barcode": "", "image_1": "img.jpg"}, True),
        ({"description": "Description", "barcode": "5449762114", "image_1": ""}, True),
        (
            {
                "description": "",
                "barcode": "5449762114",
                "image_1": "img.jpg",
                "do_not_create": True,
            },
            False,
        ),
        (
            {
                "description": "",
                "barcode": "5449762114",
                "image_1": "img.jpg",
                "created": True,
            },
            True,
        ),
    ],
)
def test_missing_inventory_information(fnac_product_factory, product_kwargs, returned):
    product = fnac_product_factory.create(**product_kwargs)
    assert (
        product in models.FnacProduct.objects.missing_inventory_information()
    ) is returned
