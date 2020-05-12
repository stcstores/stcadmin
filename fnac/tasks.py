"""Celery tasks for the FNAC app."""

from celery import shared_task

from fnac import models


@shared_task
def create_missing_information_export():
    """Create a new missing information export."""
    models.MissingInformationExport.objects.create_export()


@shared_task
def update_inventory():
    """Update the FNAC inventory information."""
    models.InventoryImport.objects.update_inventory()


@shared_task
def create_offer_update_export():
    """Create a new offer update export."""
    models.OfferUpdate.objects.create_export()


@shared_task
def create_new_product_export():
    """Create a new product export."""
    models.NewProductExport.objects.create_export()


@shared_task
def start_missing_information_import(import_id):
    """Import missing product information."""
    models.MissingInformationImport.objects.update_products(import_id)


@shared_task
def start_mirakl_product_import(import_id):
    """Import created product information from a Mirakl product export."""
    models.MiraklProductImport.objects.update_products(import_id)


@shared_task
def start_translation_update(update_id):
    """Create translations from a translation update."""
    models.TranslationUpdate.objects.update_translations(update_id)
