# Generated by Django 2.0.7 on 2018-08-01 11:48

from django.db import migrations


class Migration(migrations.Migration):
    def rename_spring_group(apps, schema_editor):
        Group = apps.get_model('auth', 'Group')
        for group in Group.objects.filter(name='spring').all():
            group.name = 'manifests'
            group.save()

    def revert_rename_spring_group(apps, schema_editor):
        Group = apps.get_model('auth', 'Group')
        for group in Group.objects.filter(name='manifests').all():
            group.name = 'spring'
            group.save()

    dependencies = [
        ('spring_manifest', '0054_remove_destination_zone'),
    ]

    operations = [
        migrations.RunPython(rename_spring_group, revert_rename_spring_group)
    ]
