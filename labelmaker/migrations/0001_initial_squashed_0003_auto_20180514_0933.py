# Generated by Django 2.0.7 on 2018-07-31 12:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('labelmaker', '0001_initial'), ('labelmaker', '0002_auto_20161013_1149'), ('labelmaker', '0003_auto_20180514_0933')]

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SizeChart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='SizeChartSize',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort', models.PositiveSmallIntegerField(default=0)),
                ('name', models.CharField(blank=True, default=None, max_length=300, null=True)),
                ('uk_size', models.CharField(max_length=200, verbose_name='UK Size')),
                ('eu_size', models.CharField(max_length=200, verbose_name='EUR Size')),
                ('us_size', models.CharField(max_length=200, verbose_name='USA Size')),
                ('au_size', models.CharField(max_length=200, verbose_name='AUS Size')),
                ('size_chart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='labelmaker.SizeChart')),
            ],
            options={
                'ordering': ('sort',),
                'verbose_name': 'Size Chart Size',
                'verbose_name_plural': 'Size Chart Sizes',
            },
        ),
        migrations.AlterModelOptions(
            name='sizechart',
            options={'ordering': ('name',), 'verbose_name': 'Size Chart', 'verbose_name_plural': 'Size Charts'},
        ),
    ]