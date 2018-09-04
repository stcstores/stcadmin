# Generated by Django 2.1 on 2018-08-06 15:26

from django.db import migrations, models


def mark_manifests_closed(apps, schema_editor):
    """Mark old manifests as closed."""
    Manifest = apps.get_model("spring_manifest", "Manifest")
    manifests = Manifest.objects.filter(status="filed")
    manifests.update(closed=True)


class Migration(migrations.Migration):

    dependencies = [("spring_manifest", "0005_manifestupdate")]

    operations = [
        migrations.AddField(
            model_name="manifest",
            name="closed",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="manifest",
            name="status",
            field=models.CharField(
                choices=[
                    ("unfiled", "Unfiled"),
                    ("in_progress", "In Progress"),
                    ("filed", "Filed"),
                    ("failed", "Failed"),
                ],
                default="unfiled",
                max_length=20,
            ),
        ),
        migrations.RunPython(mark_manifests_closed),
    ]