from django.db import models


class SKU(models.Model):
    name = models.CharField(max_length=100)
    sku_code = models.CharField(max_length=50, unique=True)
    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    image_url = models.URLField(blank=True, null=True)
    oem = models.ForeignKey("OEM", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name
