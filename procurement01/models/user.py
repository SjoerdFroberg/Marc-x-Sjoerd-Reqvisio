from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    company = models.ForeignKey("Company", on_delete=models.CASCADE, null=True)

    @property
    def is_procurer(self):
        return self.company.company_type == "Procurer"

    @property
    def is_supplier(self):
        return self.company.company_type == "Supplier"

    def __str__(self):
        return self.username
