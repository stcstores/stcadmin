# Generated by Django 3.1.11 on 2021-05-25 13:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CpuSocket",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50, unique=True)),
                (
                    "manufacturer",
                    models.CharField(
                        choices=[("Intel", "Intel"), ("AMD", "AMD")], max_length=50
                    ),
                ),
            ],
            options={
                "verbose_name": "CPU Socket",
                "verbose_name_plural": "CPU Sockets",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="HardwareUse",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200, unique=True)),
                ("location", models.CharField(max_length=200)),
                ("primary_user", models.CharField(blank=True, max_length=200)),
                ("primary_use", models.TextField(blank=True)),
            ],
            options={
                "verbose_name": "Hardware Use",
                "verbose_name_plural": "Hardware Uses",
            },
        ),
        migrations.CreateModel(
            name="Name",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50, unique=True)),
                ("is_available", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Name",
                "verbose_name_plural": "Names",
                "ordering": ["-is_available", "name"],
            },
        ),
        migrations.CreateModel(
            name="OperatingSystem",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
            ],
            options={
                "verbose_name": "Operating System",
                "verbose_name_plural": "Operating Systems",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="StorageLocation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200, unique=True)),
            ],
            options={
                "verbose_name": "Stoarage Location",
                "verbose_name_plural": "Storage Locations",
            },
        ),
        migrations.CreateModel(
            name="Printer",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                ("manufacturer", models.CharField(max_length=50)),
                ("model", models.CharField(max_length=50)),
                (
                    "printer_type",
                    models.CharField(
                        choices=[
                            ("laser", "Laser"),
                            ("inkjet", "Inkjet"),
                            ("thermal", "Thermal"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("in_use", "In Use"),
                            ("stored", "Stored"),
                            ("obsolete", "Obsolete"),
                            ("binned", "Binned"),
                        ],
                        max_length=50,
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                ("added", models.DateField(auto_now_add=True)),
                (
                    "storage_location",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="hardware.storagelocation",
                    ),
                ),
                (
                    "use",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="hardware.hardwareuse",
                    ),
                ),
            ],
            options={
                "verbose_name": "Printer",
                "verbose_name_plural": "Printers",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="OperatingSystemInstall",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("operating_system_version", models.CharField(max_length=50)),
                (
                    "bus_width",
                    models.CharField(
                        choices=[("64", "64 Bit"), ("32", "32 Bit")], max_length=50
                    ),
                ),
                ("installation_date", models.DateField()),
                ("os_key", models.CharField(blank=True, max_length=255)),
                (
                    "operating_system",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="hardware.operatingsystem",
                    ),
                ),
            ],
            options={
                "verbose_name": "Operating System Install",
                "verbose_name_plural": "Operating System Installs",
            },
        ),
        migrations.CreateModel(
            name="Motherboard",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("manufacturer", models.CharField(max_length=50)),
                ("model", models.CharField(max_length=50)),
                ("chipset", models.CharField(max_length=50)),
                ("vga", models.SmallIntegerField(default=0)),
                ("dvi", models.SmallIntegerField(default=0)),
                ("hdmi", models.SmallIntegerField(default=0)),
                ("display_port", models.SmallIntegerField(default=0)),
                (
                    "socket",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="hardware.cpusocket",
                    ),
                ),
            ],
            options={
                "verbose_name": "Motherboard",
                "verbose_name_plural": "Motherboards",
                "ordering": ["manufacturer", "model"],
                "unique_together": {("manufacturer", "model")},
            },
        ),
        migrations.CreateModel(
            name="Gpu",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "manufacturer",
                    models.CharField(
                        choices=[("Intel", "Intel"), ("AMD", "AMD")], max_length=50
                    ),
                ),
                ("model", models.CharField(max_length=255)),
                ("clock_speed", models.FloatField()),
                ("year", models.SmallIntegerField()),
                ("vga", models.SmallIntegerField(default=0)),
                ("dvi", models.SmallIntegerField(default=0)),
                ("hdmi", models.SmallIntegerField(default=0)),
                ("display_port", models.SmallIntegerField(default=0)),
            ],
            options={
                "verbose_name": "GPU",
                "verbose_name_plural": "GPUs",
                "ordering": ["manufacturer", "model"],
                "unique_together": {("manufacturer", "model")},
            },
        ),
        migrations.CreateModel(
            name="Cpu",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "manufacturer",
                    models.CharField(
                        choices=[("Intel", "Intel"), ("AMD", "AMD")], max_length=50
                    ),
                ),
                ("model", models.CharField(max_length=255)),
                ("clock_speed", models.FloatField()),
                ("year", models.IntegerField()),
                ("generation", models.CharField(blank=True, max_length=50)),
                (
                    "socket",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="hardware.cpusocket",
                    ),
                ),
            ],
            options={
                "verbose_name": "CPU",
                "verbose_name_plural": "CPUs",
                "ordering": ["manufacturer", "model"],
                "unique_together": {("manufacturer", "model")},
            },
        ),
        migrations.CreateModel(
            name="Computer",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                (
                    "computer_type",
                    models.CharField(
                        choices=[
                            ("desktop", "Desktop"),
                            ("laptop", "Laptop"),
                            ("tablet", "Tablet"),
                        ],
                        max_length=50,
                    ),
                ),
                ("network_name", models.CharField(max_length=255)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("in_use", "In Use"),
                            ("stored", "Stored"),
                            ("obsolete", "Obsolete"),
                            ("binned", "Binned"),
                        ],
                        max_length=50,
                    ),
                ),
                ("ram_gb", models.SmallIntegerField()),
                ("notes", models.TextField(blank=True)),
                ("added", models.DateField(auto_now_add=True)),
                (
                    "cpu",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="hardware.cpu",
                    ),
                ),
                (
                    "gpu",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="hardware.gpu",
                    ),
                ),
                (
                    "motherboard",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="hardware.motherboard",
                    ),
                ),
                (
                    "operating_system",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="hardware.operatingsysteminstall",
                    ),
                ),
                (
                    "storage_location",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="hardware.storagelocation",
                    ),
                ),
                (
                    "use",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="hardware.hardwareuse",
                    ),
                ),
            ],
            options={
                "verbose_name": "Computer",
                "verbose_name_plural": "Computers",
                "ordering": ["name"],
            },
        ),
    ]
