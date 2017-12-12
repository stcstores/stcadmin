from django.db import models
from django.utils.timezone import now


class FiledManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(time_filed__isnull=False)


class UnFiledManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(time_filed__isnull=True)


class SpringManifest(models.Model):

    class Meta:
        ordering = ['-time_filed', '-time_created']

    TRACKED = 'T'
    UNTRACKED = 'U'
    MANIFEST_TYPE_CHOICES = ((TRACKED, 'Tracked'), (UNTRACKED, 'Untracked'))

    UNFILED = 'unfiled'
    IN_PROGRESS = 'in_progress'
    FILED = 'filed'
    STATUS_CHOICES = (
        (UNFILED, 'Unfiled'), (IN_PROGRESS, 'In Progress'), (FILED, 'Filed'))

    manifest_type = models.CharField(
        max_length=1, choices=MANIFEST_TYPE_CHOICES)
    time_created = models.DateTimeField(default=now)
    time_filed = models.DateTimeField(blank=True, null=True)
    manifest_file = models.FileField(
        upload_to='manifests', blank=True, null=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=UNFILED)

    objects = models.Manager()
    filed = FiledManager()
    unfiled = UnFiledManager()

    def __str__(self):
        manifest_type = dict(self.MANIFEST_TYPE_CHOICES)[self.manifest_type]
        if self.time_filed is None:
            time = 'Unfiled'
        else:
            time = self.time_filed.strftime('%Y-%m-%d')
        return '{}_{}_{}'.format(
            self.id, manifest_type, time)

    def file_manifest(self):
        self.time_filed = now()
        self.save()
