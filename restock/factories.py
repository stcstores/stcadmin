import datetime as dt

import factory

from inventory.factories import ProductFactory
from restock import models


class ReorderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Reorder

    class Params:
        closed = False

    product = factory.SubFactory(ProductFactory)
    count = factory.Faker("pyint", min_value=1, max_value=1000)
    comment = factory.Faker("text", max_nb_chars=50)
    created_at = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )
    modified_at = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )
    closed_at = factory.Maybe(
        "closed",
        factory.Faker("date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc),
        None,
    )
