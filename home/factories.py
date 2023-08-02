"""Model factories for the home app."""


import datetime as dt

import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from factory import faker
from factory.django import DjangoModelFactory

from home import models


class GroupFactory(DjangoModelFactory):
    class Meta:
        model = Group

    name = faker.Faker("text", max_nb_chars=20)


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()
        skip_postgeneration_save = True

    username = factory.Faker("pystr", min_chars=10, max_chars=150)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.PostGenerationMethodCall("set_password", "Password")
    email = factory.Faker("email")
    is_staff = False
    is_active = True
    is_superuser = False
    last_login = faker.Faker(
        "date_time_this_decade",
        before_now=True,
        after_now=False,
        tzinfo=dt.timezone.utc,
    )
    date_joined = faker.Faker(
        "date_time_this_decade",
        before_now=True,
        after_now=False,
        tzinfo=dt.timezone.utc,
    )


class StaffFactory(DjangoModelFactory):
    class Meta:
        model = models.Staff
        skip_postgeneration_save = True

    stcadmin_user = factory.RelatedFactory(UserFactory)
    first_name = factory.Faker("first_name")
    second_name = factory.Faker("last_name")
    email_address = factory.Faker("email")
    hidden = False


class ExternalLinkFactory(DjangoModelFactory):
    class Meta:
        model = models.ExternalLink

    name = factory.Faker("company")
    url = factory.Faker("uri")
    ordering = 3
