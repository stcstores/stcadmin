"""Model Admin for the Hardware app."""

from django.contrib import admin

from . import models


@admin.register(models.OperatingSystem)
class OperatingSystemAdmin(admin.ModelAdmin):
    """Model admin for the OperatingSystem model."""

    fields = ["name"]


@admin.register(models.OperatingSystemInstall)
class OperatingSystemInstallAdmin(admin.ModelAdmin):
    """Model admin for the OperatingSystemInstall model."""

    fields = (
        "operating_system",
        "operating_system_version",
        "bus_width",
        "installation_date",
        "os_key",
    )
    list_display = (
        "__str__",
        "operating_system",
        "operating_system_version",
        "bus_width",
        "installation_date",
    )


@admin.register(models.CpuSocket)
class CpuSocketAdmin(admin.ModelAdmin):
    """Model admin for the CpuSocket model."""

    fields = ("name", "manufacturer")
    list_display = ("__str__", "name", "manufacturer")
    list_editable = ("name", "manufacturer")


@admin.register(models.Cpu)
class CpuAdmin(admin.ModelAdmin):
    """Model admin for the Cpu model."""

    fields = ("manufacturer", "model", "clock_speed", "year", "generation", "socket")
    list_display = (
        "__str__",
        "manufacturer",
        "model",
        "clock_speed",
        "year",
        "generation",
        "socket",
    )
    list_editable = (
        "manufacturer",
        "model",
        "clock_speed",
        "year",
        "generation",
        "socket",
    )
    list_filter = ("manufacturer", "socket", "generation")
    search_fields = (
        "manufacturer",
        "model",
        "socket__name",
        "generation",
    )


@admin.register(models.Gpu)
class GpuAdmin(admin.ModelAdmin):
    """Model admin for the Gpu model."""

    fields = (
        "manufacturer",
        "model",
        "clock_speed",
        "year",
        "vga",
        "dvi",
        "hdmi",
        "display_port",
    )
    list_display = (
        "__str__",
        "manufacturer",
        "model",
        "clock_speed",
        "year",
        "vga",
        "dvi",
        "hdmi",
        "display_port",
    )
    list_editable = (
        "manufacturer",
        "model",
        "clock_speed",
        "year",
        "vga",
        "dvi",
        "hdmi",
        "display_port",
    )
    list_filter = ("manufacturer",)
    search_fields = ("manufacturer", "model")


@admin.register(models.Motherboard)
class MotherboardAdmin(admin.ModelAdmin):
    """Model admin for the Motherboard model."""

    fields = (
        "manufacturer",
        "model",
        "socket",
        "chipset",
        "vga",
        "dvi",
        "hdmi",
        "display_port",
    )
    list_display = (
        "__str__",
        "manufacturer",
        "model",
        "socket",
        "chipset",
        "vga",
        "dvi",
        "hdmi",
        "display_port",
    )
    list_editable = (
        "manufacturer",
        "model",
        "socket",
        "chipset",
        "vga",
        "dvi",
        "hdmi",
        "display_port",
    )
    search_fields = (
        "manufacturer",
        "model",
        "socket__name",
        "chipset",
    )
    search_fields = ("manufacturer", "model", "socket__name")


@admin.register(models.HardwareUse)
class HardwareUserAdmin(admin.ModelAdmin):
    """Model admin for the HardwareUse model."""

    fields = ("name", "location", "primary_user", "primary_use")
    list_display = ("__str__", "name", "location", "primary_user", "primary_use")
    list_editable = ("name", "location", "primary_user", "primary_use")
    search_fields = ("name", "location", "primary_user")


@admin.register(models.StorageLocation)
class StorageLocationAdmin(admin.ModelAdmin):
    """Model admin for the storage location model."""

    fields = ("name",)
    list_display = ("__str__", "name")
    list_editable = ("name",)
    search_fields = ("name",)


@admin.register(models.Computer)
class ComputerAdmin(admin.ModelAdmin):
    """Model admin for the Computer model."""

    fields = (
        "name",
        "computer_type",
        "network_name",
        "status",
        "operating_system",
        "motherboard",
        "cpu",
        "ram_gb",
        "gpu",
        "use",
        "storage_location",
        "notes",
    )
    list_display = (
        "__str__",
        "name",
        "computer_type",
        "network_name",
        "status",
        "operating_system",
        "motherboard",
        "cpu",
        "ram_gb",
        "gpu",
        "use",
        "storage_location",
        "notes",
        "added",
    )
    list_editable = ("status", "use")
    list_filter = ("computer_type", "status")
    search_fields = (
        "name",
        "network_name",
        "storage_location",
        "use__location",
        "use__primary_user",
    )


@admin.register(models.Printer)
class PrinterAdmin(admin.ModelAdmin):
    """Model admin for the Printer model."""

    fields = ("name", "manufacturer", "model", "printer_type", "status", "use", "notes")
    list_display = (
        "name",
        "manufacturer",
        "model",
        "printer_type",
        "status",
        "use",
        "storage_location",
        "notes",
    )
    list_editable = ("status", "use", "storage_location")
    list_filter = ("manufacturer", "printer_type", "status", "storage_location")
    search_fields = (
        "name",
        "manufacturer",
        "model",
        "use__location",
        "use__primary_user",
    )


@admin.register(models.Name)
class NameAdmin(admin.ModelAdmin):
    """Model admin for the Name model."""

    fields = ("name", "is_available")
    list_display = ("network_safe", "name", "is_available")
    list_editable = ("name", "is_available")
    list_filter = ("is_available",)
    search_fields = ("name",)


@admin.register(models.ComputerMaintainanceJob)
class ComputerMaintainanceJobAdmin(admin.ModelAdmin):
    """Model admin for the ComputerMaintainanceJob model."""

    fields = ("completed_at", "computer", "cleaned", "os_reinstalled", "notes")
    list_display = (
        "__str__",
        "completed_at",
        "computer",
        "cleaned",
        "os_reinstalled",
        "notes",
    )
    search_fields = (
        "computer__name",
        "computer__network_name",
        "computer__user__primary_user",
    )
    date_hierarchy = "completed_at"
