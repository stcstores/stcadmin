# Generated by Django 3.0 on 2019-12-12 15:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("print_audit", "0004_auto_20191212_1517")]

    operations = [
        migrations.RemoveField(model_name="userfeedback", name="feedback_type"),
        migrations.RemoveField(model_name="userfeedback", name="user"),
        migrations.DeleteModel(name="Feedback"),
        migrations.DeleteModel(name="UserFeedback"),
    ]