"""Celery tasks for the FNAC app."""

from celery import shared_task

from fnac import models


@shared_task
def create_missing_information_export():
    """Create a new missing information export."""
    models.MissingInformationExport.objects.create_export()
