# Generated by Django 2.0.7 on 2018-07-31 12:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('stock_check', '0001_initial'), ('stock_check', '0002_auto_20180104_1154'), ('stock_check', '0003_auto_20180104_1203'), ('stock_check', '0004_auto_20180124_1053'), ('stock_check', '0005_auto_20180514_0933'), ('stock_check', '0006_auto_20180529_1010')]

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bay_id', models.PositiveIntegerField(db_index=True, unique=True, verbose_name='Bay ID')),
                ('name', models.CharField(max_length=50)),
                ('warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stock_check.Warehouse')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('range_id', models.PositiveIntegerField(blank=True, null=True, verbose_name='Range ID')),
                ('product_id', models.PositiveIntegerField(blank=True, db_index=True, null=True, unique=True, verbose_name='Product ID')),
                ('sku', models.CharField(db_index=True, max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductBayStock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock_level', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('bay', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stock_check.Bay')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stock_check.Product')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='productbaystock',
            unique_together=set(),
        ),
        migrations.CreateModel(
            name='ProductBay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock_level', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('bay', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stock_check.Bay')),
            ],
        ),
        migrations.RemoveField(
            model_name='productbaystock',
            name='bay',
        ),
        migrations.RemoveField(
            model_name='productbaystock',
            name='product',
        ),
        migrations.AddField(
            model_name='product',
            name='bays',
            field=models.ManyToManyField(through='stock_check.ProductBay', to='stock_check.Bay'),
        ),
        migrations.DeleteModel(
            name='ProductBayStock',
        ),
        migrations.AddField(
            model_name='productbay',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stock_check.Product'),
        ),
        migrations.AlterField(
            model_name='bay',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterModelOptions(
            name='bay',
            options={'ordering': ('name',), 'verbose_name': 'Bay', 'verbose_name_plural': 'Bays'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'verbose_name': 'Product', 'verbose_name_plural': 'Products'},
        ),
        migrations.AlterModelOptions(
            name='productbay',
            options={'verbose_name': 'Product Bay', 'verbose_name_plural': 'Product Bays'},
        ),
        migrations.RemoveField(
            model_name='bay',
            name='warehouse',
        ),
        migrations.AlterField(
            model_name='product',
            name='bays',
            field=models.ManyToManyField(through='stock_check.ProductBay', to='inventory.Bay'),
        ),
        migrations.AlterField(
            model_name='productbay',
            name='bay',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.Bay'),
        ),
        migrations.DeleteModel(
            name='Bay',
        ),
    ]
