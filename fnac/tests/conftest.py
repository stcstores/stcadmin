import pytest
from django.core.management import call_command

from fnac import models


@pytest.fixture
def add_fixture(django_db_setup, django_db_blocker):
    def _add_fixture(fixture_name):
        with django_db_blocker.unblock():
            call_command("loaddata", fixture_name)

    return _add_fixture


@pytest.fixture
def fnac_db_fixtures(add_fixture):
    add_fixture("shipping/currency")


@pytest.fixture
def make_category():
    def _category(
        name="Test Category", english="Category Name", french="Le Typology Nom"
    ):
        category = models.Category(name=name, english=english, french=french)
        category.save()
        return category

    return _category


@pytest.fixture
def make_size():
    def _size(name="Large"):
        size = models.Size(name=name)
        size.save()
        return size

    return _size


@pytest.fixture
def make_fnac_range(make_category):
    def _fnac_range(name="Test", sku="RNG_123-HBC-3D2", category=None):
        fnac_range = models.FnacRange(name=name, sku=sku, category=category)
        fnac_range.save()
        return fnac_range

    return _fnac_range


@pytest.fixture
def make_fnac_product(make_fnac_range):
    def _make_fnac_product(
        name="Test Product",
        sku="ABC-678-CDF",
        fnac_range=None,
        barcode="985161566",
        description="A product\nIt's good.",
        colour="Red",
        price=455,
        brand="Stock Inc",
        english_size=None,
        french_size=None,
        stock_level=54,
        do_not_create=False,
        created=False,
    ):
        fnac_product = models.FnacProduct(
            name=name,
            sku=sku,
            fnac_range=fnac_range or make_fnac_range(),
            barcode=barcode,
            description=description,
            colour=colour,
            price=price,
            brand=brand,
            english_size=english_size,
            french_size=french_size,
            stock_level=stock_level,
            do_not_create=do_not_create,
            created=created,
        )
        fnac_product.save()
        return fnac_product

    return _make_fnac_product


@pytest.fixture
def make_translation(make_fnac_product):
    def _make_translation(
        product=None,
        name="Nom on Francais",
        description="Un Product\nBien",
        colour="Rouge",
    ):
        translation = models.Translation(
            product=product or make_fnac_product(),
            name=name,
            description=description,
            colour=colour,
        )
        translation.save()
        return translation

    return _make_translation
