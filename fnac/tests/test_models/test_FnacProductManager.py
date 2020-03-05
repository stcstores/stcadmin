import pytest

from fnac import models


@pytest.mark.django_db
def test_out_of_stock_method(fnac_product_factory):
    fnac_product_factory.create(stock_level=5)
    out_of_stock = fnac_product_factory.create(stock_level=0)
    assert list(models.FnacProduct.objects.out_of_stock()) == [out_of_stock]


@pytest.mark.django_db
def test_in_stock_method(fnac_product_factory):
    in_stock = fnac_product_factory.create(stock_level=5)
    fnac_product_factory.create(stock_level=0)
    assert list(models.FnacProduct.objects.in_stock()) == [in_stock]


@pytest.mark.django_db
def test_translated_method(fnac_product_factory, translation_factory):
    translated = fnac_product_factory.create()
    fnac_product_factory.create()
    translation_factory.create(product=translated)
    assert list(models.FnacProduct.objects.translated()) == [translated]


@pytest.mark.django_db
def test_translated_does_not_return_when_name_missing(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create()
    translation_factory.create(product=product, name="")
    assert product not in models.FnacProduct.objects.translated()


@pytest.mark.django_db
def test_translated_does_not_return_when_description_missing(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create()
    translation_factory.create(product=product, description="")
    assert product not in models.FnacProduct.objects.translated()


@pytest.mark.django_db
def test_translated_does_not_return_when_product_has_colour_but_translation_does_not(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create(colour="red")
    translation_factory.create(product=product, colour="")
    assert product not in models.FnacProduct.objects.translated()


@pytest.mark.django_db
def test_translated_does_return_when_product_and_translation_have_colour(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create(colour="red")
    translation_factory.create(product=product, colour="rouge")
    assert product in models.FnacProduct.objects.translated()


@pytest.mark.django_db
def test_translated_returns_when_nether_product_not_translation_have_colour(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create(colour="")
    translation_factory.create(product=product, colour="")
    assert product in models.FnacProduct.objects.translated()


@pytest.mark.django_db
def test_not_translated_method(fnac_product_factory, translation_factory):
    translated = fnac_product_factory.create()
    not_translated = fnac_product_factory.create()
    translation_factory.create(product=translated)
    assert list(models.FnacProduct.objects.not_translated()) == [not_translated]


@pytest.mark.django_db
def test_not_translated_returns_when_translation_exists_without_name(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create()
    translation_factory.create(product=product, name="")
    assert product in models.FnacProduct.objects.not_translated()


@pytest.mark.django_db
def test_not_translated_returns_when_translation_exists_without_description(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create()
    translation_factory.create(product=product, description="")
    assert product in models.FnacProduct.objects.not_translated()


@pytest.mark.django_db
def test_not_translated_returns_when_translation_and_product_has_colour_bud_description_does_not(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create(colour="Red")
    translation_factory.create(product=product, colour="")
    assert product in models.FnacProduct.objects.not_translated()


@pytest.mark.django_db
def test_not_translated_does_not_return_when_translation_and_product_both_have_colour(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create(colour="Red")
    translation_factory.create(product=product, colour="Rouge")
    assert product not in models.FnacProduct.objects.not_translated()


@pytest.mark.django_db
def test_not_translated_does_not_return_when_neither_translation_or_product_have_colour(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create(colour="")
    translation_factory.create(product=product, colour="")
    assert product not in models.FnacProduct.objects.not_translated()


@pytest.mark.django_db
@pytest.mark.parametrize("barcode,returned", [("954123687121", True), ("", False)])
def test_barcode_valid(fnac_product_factory, barcode, returned):
    product = fnac_product_factory.create(barcode=barcode)
    assert (product in models.FnacProduct.objects.barcode_valid()) is returned


@pytest.mark.django_db
@pytest.mark.parametrize("barcode,returned", [("954123687121", False), ("", True)])
def test_barcode_invalid(fnac_product_factory, barcode, returned):
    product = fnac_product_factory.create(barcode=barcode)
    assert (product in models.FnacProduct.objects.barcode_invalid()) is returned


@pytest.mark.django_db
@pytest.mark.parametrize("image,returned", [("954123687121.jpg", True), ("", False)])
def test_has_image(fnac_product_factory, image, returned):
    product = fnac_product_factory.create(image_1=image)
    assert (product in models.FnacProduct.objects.has_image()) is returned


@pytest.mark.django_db
@pytest.mark.parametrize("image,returned", [("954123687121.jpg", False), ("", True)])
def test_missing_image(fnac_product_factory, image, returned):
    product = fnac_product_factory.create(image_1=image)
    assert (product in models.FnacProduct.objects.missing_image()) is returned


@pytest.mark.django_db
def test_size_valid_returns_when_product_has_no_english_size_and_no_french_size(
    fnac_product_factory,
):
    product = fnac_product_factory.create(english_size="", french_size=None)
    assert product in models.FnacProduct.objects.size_valid()


@pytest.mark.django_db
def test_size_valid_does_not_return_when_product_has_english_size_but_not_french_size(
    fnac_product_factory,
):
    product = fnac_product_factory.create(english_size="Red", french_size=None)
    assert product not in models.FnacProduct.objects.size_valid()


@pytest.mark.django_db
def test_size_valid_returns_when_product_has_no_english_size_but_does_have_french_size(
    fnac_product_factory, size_factory
):
    french_size = size_factory(name="Rouge")
    product = fnac_product_factory.create(english_size="", french_size=french_size)
    assert product in models.FnacProduct.objects.size_valid()


@pytest.mark.django_db
def test_size_valid_returns_when_product_has_no_english_and_french_size(
    fnac_product_factory, size_factory
):
    french_size = size_factory(name="Rouge")
    product = fnac_product_factory.create(english_size="Red", french_size=french_size)
    assert product in models.FnacProduct.objects.size_valid()


@pytest.mark.django_db
def test_size_invalid_does_not_return_when_product_has_no_english_size_and_no_french_size(
    fnac_product_factory,
):
    product = fnac_product_factory.create(english_size="", french_size=None)
    assert product not in models.FnacProduct.objects.size_invalid()


@pytest.mark.django_db
def test_size_invalid_returns_when_product_has_english_size_but_not_french_size(
    fnac_product_factory,
):
    product = fnac_product_factory.create(english_size="Red", french_size=None)
    assert product in models.FnacProduct.objects.size_invalid()


@pytest.mark.django_db
def test_size_invalid_does_not_return_when_product_has_no_english_size_but_does_have_french_size(
    fnac_product_factory, size_factory
):
    french_size = size_factory(name="Rouge")
    product = fnac_product_factory.create(english_size="", french_size=french_size)
    assert product not in models.FnacProduct.objects.size_invalid()


@pytest.mark.django_db
def test_size_invalid_does_not_return_when_product_has_english_size_and_french_size(
    fnac_product_factory, size_factory
):
    french_size = size_factory(name="Rouge")
    product = fnac_product_factory.create(english_size="Red", french_size=french_size)
    assert product not in models.FnacProduct.objects.size_invalid()


@pytest.mark.django_db
def test_has_category_returns_when_product_has_category(
    category_factory, fnac_range_factory, fnac_product_factory
):
    category = category_factory.create()
    fnac_range = fnac_range_factory.create(category=category)
    product = fnac_product_factory.create(fnac_range=fnac_range)
    assert product in models.FnacProduct.objects.has_category()


@pytest.mark.django_db
def test_has_category_does_not_return_when_product_has_no_category(
    fnac_range_factory, fnac_product_factory
):
    fnac_range = fnac_range_factory.create(category=None)
    product = fnac_product_factory.create(fnac_range=fnac_range)
    assert product not in models.FnacProduct.objects.has_category()


@pytest.mark.django_db
def test_missing_category_returns_when_product_has_no_category(
    fnac_range_factory, fnac_product_factory
):
    fnac_range = fnac_range_factory.create(category=None)
    product = fnac_product_factory.create(fnac_range=fnac_range)
    assert product in models.FnacProduct.objects.missing_category()


@pytest.mark.django_db
def test_missing_category_does_not_return_when_product_has_category(
    category_factory, fnac_range_factory, fnac_product_factory
):
    category = category_factory.create()
    fnac_range = fnac_range_factory.create(category=category)
    product = fnac_product_factory.create(fnac_range=fnac_range)
    assert product not in models.FnacProduct.objects.missing_category()


@pytest.mark.django_db
def test_has_price_returns_when_product_has_price(fnac_product_factory):
    product = fnac_product_factory.create(price=550)
    assert product in models.FnacProduct.objects.has_price()


@pytest.mark.django_db
def test_has_price_does_not_return_when_product_has_no_price(fnac_product_factory):
    product = fnac_product_factory.create(price=None)
    assert product not in models.FnacProduct.objects.has_price()


@pytest.mark.django_db
def test_missing_price_returns_when_product_has_no_price(fnac_product_factory):
    product = fnac_product_factory.create(price=None)
    assert product in models.FnacProduct.objects.missing_price()


@pytest.mark.django_db
def test_missing_price_does_not_return_when_product_has_price(fnac_product_factory):
    product = fnac_product_factory.create(price=550)
    assert product not in models.FnacProduct.objects.missing_price()


@pytest.mark.django_db
def test_has_description_returns_when_product_has_description(fnac_product_factory):
    product = fnac_product_factory.create(description="Description")
    assert product in models.FnacProduct.objects.has_description()


@pytest.mark.django_db
def test_has_description_does_not_return_when_product_has_no_description(
    fnac_product_factory,
):
    product = fnac_product_factory.create(description="")
    assert product not in models.FnacProduct.objects.has_description()


@pytest.mark.django_db
def test_missing_description_returns_when_product_has_no_description(
    fnac_product_factory,
):
    product = fnac_product_factory.create(description="")
    assert product in models.FnacProduct.objects.missing_description()


@pytest.mark.django_db
def test_missing_description_does_not_return_when_product_has_description(
    fnac_product_factory,
):
    product = fnac_product_factory.create(description="Description")
    assert product not in models.FnacProduct.objects.missing_description()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "product_kwargs,returned",
    [
        ({"do_not_create": False, "created": False}, True),
        ({"do_not_create": True, "created": False}, False),
        ({"do_not_create": False, "created": True}, False),
        ({"do_not_create": True, "created": True}, False),
    ],
)
def test_to_create_manager(fnac_product_factory, product_kwargs, returned):
    product = fnac_product_factory(**product_kwargs)
    assert (product in models.FnacProduct.to_create.all()) is returned


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
        ({"description": "", "barcode": "5449762114", "image_1": "img.jpg"}, True,),
        ({"description": "Description", "barcode": "", "image_1": "img.jpg"}, True,),
        ({"description": "Description", "barcode": "5449762114", "image_1": ""}, True,),
    ],
)
def test_missing_inventory_information(fnac_product_factory, product_kwargs, returned):
    product = fnac_product_factory.create(**product_kwargs)
    assert (
        product in models.FnacProduct.objects.missing_inventory_information()
    ) is returned


@pytest.mark.django_db
def test_to_create_manager_subclasses_FnacProductManager(fnac_product_factory):
    product = fnac_product_factory.create(stock_level=0)
    assert list(models.FnacProduct.objects.out_of_stock()) == [product]
