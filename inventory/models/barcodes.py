from django.db import models


class Barcode(models.Model):
    barcode = models.CharField(max_length=13, unique=True)
    used = models.BooleanField(default=False)

    def mark_used(self):
        self.used = True
        self.save()


def get_barcode():
    barcode = Barcode.objects.filter(used=False).all()[0]
    barcode.used = True
    barcode.save()
    return barcode.barcode
