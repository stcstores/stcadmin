from django.db import models
from django.utils.timezone import now


class FiledManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(status=self.model.FILED)


class UnFiledManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().exclude(status=self.model.FILED)


class SpringManifest(models.Model):

    class Meta:
        ordering = ['-time_filed', '-time_created']

    TRACKED = 'T'
    UNTRACKED = 'U'
    MANIFEST_TYPE_CHOICES = ((TRACKED, 'Tracked'), (UNTRACKED, 'Untracked'))

    UNFILED = 'unfiled'
    IN_PROGRESS = 'in_progress'
    FILED = 'filed'
    FAILED = 'failed'
    STATUS_CHOICES = (
        (UNFILED, 'Unfiled'), (IN_PROGRESS, 'In Progress'), (FILED, 'Filed'),
        (FAILED, 'Failed'))

    manifest_type = models.CharField(
        max_length=1, choices=MANIFEST_TYPE_CHOICES)
    time_created = models.DateTimeField(default=now)
    time_filed = models.DateTimeField(blank=True, null=True)
    manifest_file = models.FileField(
        upload_to='manifests', blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=FILED)
    errors = models.TextField(blank=True, null=True)

    objects = models.Manager()
    filed = FiledManager()
    unfiled = UnFiledManager()

    def __str__(self):
        manifest_type = dict(self.MANIFEST_TYPE_CHOICES)[self.manifest_type]
        if self.time_filed is None:
            time = 'Unfiled'
        else:
            time = self.time_filed.strftime('%Y-%m-%d')
        return '{}_{}_{}'.format(self.id, manifest_type, time)

    def file_manifest(self):
        self.time_filed = now()
        self.save()

    def get_error_list(self):
        if self.errors:
            return self.errors.split('\n')
