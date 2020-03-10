import factory
import pytest
from django.core.management import call_command
from pytest_factoryboy import register

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


@register
class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Category

    name = factory.Sequence(lambda n: f"Test Category {n}")
    english = factory.Sequence(lambda n: f"English Category {n}")
    french = factory.Sequence(lambda n: f"Category en Francais {n}")


@register
class SizeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Size

    name = factory.Sequence(lambda n: f"Test Size {n}")


@register
class FnacRangeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.FnacRange

    name = factory.Sequence(lambda n: f"Test Range {n}")
    sku = factory.Sequence(lambda n: f"RNG_123-HBC-3D{n}")
    category = None


@register
class FnacProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.FnacProduct

    name = factory.Sequence(lambda n: f"Test Product {n}")
    sku = factory.Sequence(lambda n: f"ABC-678-CD{n}")
    fnac_range = factory.SubFactory(FnacRangeFactory)
    barcode = "985161566"
    description = "A product\nIt's good."
    colour = "Red"
    price = 455
    brand = "Stock Inc"
    english_size = "UK 5"
    french_size = factory.SubFactory(SizeFactory)
    stock_level = 54
    image_1 = "81916118.jpg"
    image_2 = "152411896.jpg"
    image_3 = "9489220.jpg"
    image_4 = ""
    do_not_create = False
    created = False


@register
class TranslationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Translation

    product = factory.SubFactory(FnacProductFactory)
    name = factory.Sequence(lambda n: f"Nom on Francais {n}")
    description = "Un Product\nBien"
    colour = "Rouge"
