"""Celery tasks for the ITD app."""

from celery import shared_task

from itd import models


@shared_task
def close_manifest(manifest_id):
    """Close an ITD manifest and generate a manifest file from current orders."""
    models.ITDManifest.objects.close_manifest(manifest_id)
