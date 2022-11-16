import datetime as dt

import pytest
from django.core import exceptions

from inventory import models


@pytest.fixture
def supplier(supplier_factory):
    return supplier_factory.create()


@pytest.fixture
def supplier_contact(supplier_contact_factory):
    supplier_contact = supplier_contact_factory.create()
    supplier_contact.full_clean()
    return supplier_contact


@pytest.mark.django_db
def test_has_name_attribute(supplier_contact):
    assert isinstance(supplier_contact.name, str)
    assert len(supplier_contact.name) > 0


@pytest.mark.django_db
def test_name_attribute_defaults_to_none(supplier):
    supplier_contact = models.SupplierContact.objects.create(
        supplier=supplier, phone="116816168115"
    )
    assert supplier_contact.name is None


@pytest.mark.django_db
def test_has_email_attribute(supplier_contact):
    assert isinstance(supplier_contact.email, str)
    assert len(supplier_contact.email) > 0


@pytest.mark.django_db
def test_email_attribute_defaults_to_none(supplier):
    supplier_contact = models.SupplierContact.objects.create(
        supplier=supplier, name="New Contact"
    )
    assert supplier_contact.email is None


@pytest.mark.django_db
def test_has_phone_attribute(supplier_contact):
    assert isinstance(supplier_contact.phone, str)
    assert len(supplier_contact.phone) > 0


@pytest.mark.django_db
def test_phone_attribute_defaults_to_none(supplier):
    supplier_contact = models.SupplierContact.objects.create(
        supplier=supplier, name="New Contact"
    )
    assert supplier_contact.phone is None


@pytest.mark.django_db
def test_has_notes_attribute(supplier_contact):
    assert isinstance(supplier_contact.notes, str)
    assert len(supplier_contact.notes) > 0


@pytest.mark.django_db
def test_notes_attribute_defaults_to_none(supplier):
    supplier_contact = models.SupplierContact.objects.create(
        supplier=supplier, name="New Contact"
    )
    assert supplier_contact.notes is None


@pytest.mark.django_db
def test_has_created_at_attribute(supplier_contact):
    assert isinstance(supplier_contact.created_at, dt.datetime)


@pytest.mark.django_db
def test_has_modified_at_attribute(supplier_contact):
    assert isinstance(supplier_contact.modified_at, dt.datetime)


@pytest.mark.django_db
def test_cannot_be_created_without_any_details(supplier):
    with pytest.raises(exceptions.ValidationError):
        models.SupplierContact(supplier=supplier).save()


@pytest.mark.django_db
def test_str_method(supplier_contact_factory):
    supplier_contact = supplier_contact_factory(
        supplier__name="New Supplier", name="Bill Bob"
    )
    assert str(supplier_contact) == "Bill Bob - New Supplier"


@pytest.mark.django_db
def test_str_method_with_empty_name(supplier_contact_factory):
    supplier_contact = supplier_contact_factory(supplier__name="New Supplier", name="")
    assert str(supplier_contact) == "New Supplier"


@pytest.mark.django_db
def test_get_absolute_url_method(supplier_contact):
    assert isinstance(supplier_contact.get_absolute_url(), str)
    assert len(supplier_contact.get_absolute_url()) > 0
