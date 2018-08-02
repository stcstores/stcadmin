"""Manifest model."""

from django.db import models
from django.utils import timezone
from django.utils.timezone import now

from .manifest_type_model import ManifestType


class FiledManager(models.Manager):
    """Manager for manifests that have been filed."""

    def get_queryset(self):
        """Return queryset of filed manifests."""
        return super().get_queryset().filter(status=self.model.FILED)


class UnFiledManager(models.Manager):
    """Manager for manifests that are still unfiled."""

    def get_queryset(self):
        """Return queryset of unfiled manifests."""
        return super().get_queryset().exclude(status=self.model.FILED)


class Manifest(models.Model):
    """Model for manifests."""

    UNFILED = "unfiled"
    IN_PROGRESS = "in_progress"
    FILED = "filed"
    FAILED = "failed"
    STATUS_CHOICES = (
        (UNFILED, "Unfiled"),
        (IN_PROGRESS, "In Progress"),
        (FILED, "Filed"),
        (FAILED, "Failed"),
    )

    manifest_type = models.ForeignKey(
        ManifestType, on_delete=models.SET_NULL, null=True, blank=True
    )
    time_created = models.DateTimeField(default=now)
    time_filed = models.DateTimeField(blank=True, null=True)
    manifest_file = models.FileField(upload_to="manifests", blank=True, null=True)
    item_advice_file = models.FileField(upload_to="item_advice", blank=True, null=True)
    docket_file = models.FileField(upload_to="docket", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=FILED)
    errors = models.TextField(blank=True, null=True)

    objects = models.Manager()
    filed = FiledManager()
    unfiled = UnFiledManager()

    class Meta:
        """Meta class for Manifest."""

        verbose_name = "Manifest"
        verbose_name_plural = "Manifests"
        ordering = ["-time_filed", "-time_created"]

    def __str__(self):
        manifest_type = self.manifest_type
        if self.time_filed is None:
            time = "Unfiled"
        else:
            time = self.time_filed.strftime("%Y-%m-%d")
        return "{}_{}_{}".format(self.id, manifest_type, time)

    def file_manifest(self):
        """Set time_filed to current time."""
        self.time_filed = now()
        self.save()

    def get_error_list(self):
        """Return list of errors."""
        if self.errors:
            return self.errors.split("\n")

    def tracked_count(self):
        """Return number of orders on manifest using Secured Mail Tracked."""
        return self.manifestorder_set.filter(service="SMIT").count()

    def untracked_count(self):
        """Return number of orders on manifest using Secured Mail Untracked."""
        return self.manifestorder_set.filter(service="SMIU").count()


class ManifestUpdate(models.Model):
    """Records of manifest updates."""

    class Meta:
        """Meta class for Manifest."""

        verbose_name = "Manifest Update"
        verbose_name_plural = "Manifest Updates"
        ordering = ["-started"]

    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    FAILED = "failed"

    STATUS_CHOICES = (
        (IN_PROGRESS, "In Progress"),
        (COMPLETE, "Complete"),
        (FAILED, "Failed"),
    )

    started = models.DateTimeField(auto_now_add=True)
    finished = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=IN_PROGRESS
    )

    def __str__(self):
        return self.started.strftime("%d-%m-%Y %H:%M:%S")

    def complete(self):
        """Mark update as complete."""
        self.status = self.COMPLETE
        self.finished = timezone.now()
        self.save()

    def fail(self):
        """Mark update as failed."""
        self.status = self.FAILED
        self.finished = None
        self.save()
