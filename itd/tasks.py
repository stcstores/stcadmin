"""Celery tasks for the ITD app."""

from celery import shared_task

from itd import models


@shared_task
def close_manifest(manifest_id):
    """Close an ITD manifest and generate a manifest file from current orders."""
    models.ITDManifest.objects.close_manifest(manifest_id)


@shared_task
def clear_manifest_files(manifest_id):
    """Delete manifest files from an ITD manifest."""
    manifest = models.ITDManifest.objects.get(id=manifest_id)
    manifest.clear_files()


@shared_task
def regenerate_manifest(manifest_id):
    """Regenerate an ITD manifest manifest file."""
    models.ITDManifest.objects.regenerate_manifest(manifest_id)
