from django.db import models


class SupplierResponse(models.Model):
    """A model to store a supplier's overall response to an RFX."""

    rfx = models.ForeignKey("RFX", on_delete=models.CASCADE, related_name="responses")
    supplier = models.ForeignKey("Company", on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_finalized = models.BooleanField(default=False)

    def __str__(self):
        return f"Response to {self.rfx.title} by {self.supplier.name}"


class GeneralQuestionResponse(models.Model):
    """Stores each response to a general question within an RFX."""

    response = models.ForeignKey(
        SupplierResponse, on_delete=models.CASCADE, related_name="general_responses"
    )
    question = models.ForeignKey("GeneralQuestion", on_delete=models.CASCADE)
    invitation = models.ForeignKey("RFXInvitation", on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True, null=True)
    answer_choice = models.TextField(blank=True, null=True)
    answer_number = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    answer_date = models.DateField(blank=True, null=True)
    answer_file = models.FileField(upload_to="responses/files/", blank=True, null=True)

    def __str__(self):
        return f"Response to General Question '{self.question}' by {self.response.supplier.name}"


class SKUSpecificQuestionResponse(models.Model):
    response = models.ForeignKey(
        SupplierResponse,
        on_delete=models.CASCADE,
        related_name="sku_question_responses",
    )
    rfx_sku = models.ForeignKey("RFX_SKUs", on_delete=models.CASCADE)
    question = models.ForeignKey("SKUSpecificQuestion", on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True, null=True)
    answer_number = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    answer_file = models.FileField(upload_to="responses/files/", blank=True, null=True)
    answer_date = models.DateField(blank=True, null=True)
    answer_choice = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Response to SKU Question '{self.question}' for SKU '{self.rfx_sku.sku.name}' by {self.response.supplier.name}"
