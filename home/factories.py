"""Model factories for the home app."""


import factory
from django.contrib.auth import get_user_model

from home import models


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for the home.Staff model."""

    class Meta:
        """Metaclass for home.factories.StaffFactory."""

        model = get_user_model()

    username = factory.Faker("user_name")
    password = hash("Password")
    email = factory.Faker("email")


class StaffFactory(factory.django.DjangoModelFactory):
    """Factory for the home.Staff model."""

    class Meta:
        """Metaclass for home.factories.StaffFactory."""

        model = models.Staff

    stcadmin_user = factory.RelatedFactory(UserFactory)
    first_name = factory.Faker("first_name")
    second_name = factory.Faker("last_name")
    email_address = factory.Faker("email")
    hidden = False
