from datetime import datetime

import factory
import pytest
from django.core.management import call_command
from django.utils import timezone
from pytest_factoryboy import register

from fnac import models
from inventory.models import ProductExport


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
    requires_colour = False


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
    category = factory.SubFactory(CategoryFactory)


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


@register
class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Comment

    comment = "A description of the shipping times\n2 days"


@register
class MissingInformationExportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.MissingInformationExport

    export = factory.django.FileField(filename="fnac_missing_information.xlsx")


@register
class InventoryProductExportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductExport

    name = factory.Sequence(lambda n: f"ProductExport{n}")
    timestamp = timezone.make_aware(datetime(2020, 3, 1))
    export_file = factory.django.FileField()


@register
class InventoryImportFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.InventoryImport

    timestamp = datetime(2020, 3, 1)
    export = factory.SubFactory(InventoryProductExportFactory)


@register
class OfferUpdateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.OfferUpdate

    export = factory.django.FileField(filename="fnac_offer_update.csv")


@register
class NewProductExportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.NewProductExport

    export = factory.django.FileField(filename="fnac_new_products.xlsx")
