import factory
from factory import fuzzy
from factory.django import DjangoModelFactory

from inventory.factories import SupplierFactory
from labelmaker import models


class SizeChartFactory(DjangoModelFactory):
    class Meta:
        model = models.SizeChart

    supplier = factory.SubFactory(SupplierFactory)
    name = fuzzy.FuzzyText()


class SizeChartSizeFactory(DjangoModelFactory):
    class Meta:
        model = models.SizeChartSize

    size_chart = factory.SubFactory(SizeChartFactory)
    sort = 0
    name = fuzzy.FuzzyText()
    uk_size = fuzzy.FuzzyText()
    eu_size = fuzzy.FuzzyText()
    us_size = fuzzy.FuzzyText()
    au_size = fuzzy.FuzzyText()
