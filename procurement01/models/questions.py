from django.db import models


class GeneralQuestion(models.Model):
    QUESTION_TYPES = [
        ("text", "Text"),
        ("Single-select", "Single-select"),
        ("Multi-select", "Multi-select"),
        ("File upload", "File upload"),
    ]

    rfx = models.ForeignKey(
        "RFX", related_name="general_questions", on_delete=models.CASCADE
    )
    question_text = models.CharField(max_length=255)
    question_type = models.CharField(max_length=200, choices=QUESTION_TYPES)
    multiple_choice_options = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.question_text


class SKUSpecificQuestion(models.Model):
    QUESTION_TYPES = [
        ("text", "Text"),
        ("number", "Number"),
        ("file", "File Upload"),
        ("date", "Date"),
        ("Single-select", "Single-select"),
        ("Multi-select", "Multi-select"),
    ]

    rfx = models.ForeignKey(
        "RFX", on_delete=models.CASCADE, related_name="sku_specific_questions"
    )
    question = models.CharField(max_length=255)
    question_type = models.CharField(max_length=50, choices=QUESTION_TYPES)

    def __str__(self):
        return f"{self.question} ({self.get_question_type_display()})"
