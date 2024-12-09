from django.db import models


class OEM(models.Model):
    name = models.CharField(max_length=100, unique=True)
    procurer = models.ForeignKey(
        "Company",
        on_delete=models.CASCADE,
        related_name="procurer_oems",
        limit_choices_to={"company_type": "Procurer"},
    )

    def __str__(self):
        return f"{self.name} (Procurer: {self.procurer.name})"


class Company(models.Model):
    COMPANY_TYPES = [
        ("Procurer", "Procurer"),
        ("Supplier", "Supplier"),
    ]
    name = models.CharField(max_length=100)
    company_type = models.CharField(max_length=10, choices=COMPANY_TYPES)
    procurer = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="suppliers",
    )
    email = models.EmailField(max_length=254, blank=True, null=True)
    oems = models.ManyToManyField("OEM", blank=True, related_name="suppliers")

    def __str__(self):
        return self.name
