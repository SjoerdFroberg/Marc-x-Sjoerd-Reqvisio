from collections import OrderedDict

from django.db import models


class RFX(models.Model):
    project = models.ForeignKey(
        "Project", on_delete=models.CASCADE, related_name="rfxs", null=True
    )
    company = models.ForeignKey(
        "Company", on_delete=models.CASCADE, related_name="rfxs"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def skus(self):
        return self.rfx_skus_set.all()


class RFXFile(models.Model):
    rfx = models.ForeignKey(RFX, related_name="files", on_delete=models.CASCADE)
    file = models.FileField(upload_to="rfx_files/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rfx.title} - {self.file.name}"


class RFX_SKUs(models.Model):
    rfx = models.ForeignKey("RFX", on_delete=models.CASCADE)
    sku = models.ForeignKey("SKU", on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def set_specification_data(self, data):
        self.specification_data.all().delete()
        for key, value in data.items():
            RFX_SKUSpecificationData.objects.create(rfx_sku=self, key=key, value=value)

    def get_specification_data(self):
        data = OrderedDict()
        for spec in self.specification_data.all():
            data[spec.key] = spec.value
        return data


class RFX_SKUSpecificationData(models.Model):
    rfx_sku = models.ForeignKey(
        "RFX_SKUs", on_delete=models.CASCADE, related_name="specification_data"
    )
    key = models.CharField(max_length=255)
    value = models.TextField()
