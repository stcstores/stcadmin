# Generated by Django 5.1.6 on 2025-02-13 14:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("logs", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="worklog",
            old_name="work",
            new_name="job",
        ),
    ]
