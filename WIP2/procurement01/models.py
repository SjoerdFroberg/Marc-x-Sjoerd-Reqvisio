from django.contrib.auth.models import AbstractUser
import json 
from django.db import models
from django.utils.crypto import get_random_string
from django.utils import timezone

from collections import OrderedDict



class OEM(models.Model):
    name = models.CharField(max_length=100, unique=True)
    procurer = models.ForeignKey(
        'Company',
        on_delete=models.CASCADE,
        related_name='procurer_oems',
        limit_choices_to={'company_type': 'Procurer'}
    )  

    def __str__(self):
        return f"{self.name} (Procurer: {self.procurer.name})"



class Company(models.Model):
    COMPANY_TYPES = [
        ('Procurer', 'Procurer'),
        ('Supplier', 'Supplier'),
    ]
    name = models.CharField(max_length=100)
    company_type = models.CharField(max_length=10, choices=COMPANY_TYPES)
    procurer = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='suppliers')
    email = models.EmailField(max_length=254, blank=True, null=True)  

    oems = models.ManyToManyField('OEM', blank=True, related_name='suppliers')  


    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    
    @property
    def is_procurer(self):
        return self.company.company_type == 'Procurer'
    
    @property
    def is_supplier(self):
        return self.company.company_type == 'Supplier'

    def __str__(self):
        return self.username

class SKU(models.Model):
    name = models.CharField(max_length=100)
    sku_code = models.CharField(max_length=50, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    image_url = models.URLField(blank=True, null=True)  # Optional image URL

    oem = models.ForeignKey(OEM, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name 
    


class Project(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="projects")


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    

class RFX_SKUs(models.Model):
    rfx = models.ForeignKey('RFX', on_delete=models.CASCADE)
    sku = models.ForeignKey('SKU', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def set_specification_data(self, data):
        # Remove existing specification data
        self.specification_data.all().delete()
        # Add new specification data
        for key, value in data.items():
            RFX_SKUSpecificationData.objects.create(
                rfx_sku=self,
                key=key,
                value=value
            )

    def get_specification_data(self):
        data = OrderedDict()
        for spec in self.specification_data.all():
            data[spec.key] = spec.value
        return data

class RFX_SKUSpecificationData(models.Model):
    rfx_sku = models.ForeignKey(
        'RFX_SKUs',
        on_delete=models.CASCADE,
        related_name='specification_data'
    )
    key = models.CharField(max_length=255)
    value = models.TextField()


class RFX(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="rfxs", null = True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="rfxs")
    title = models.CharField(max_length=255)
    description = models.TextField(blank = True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return self.title

    @property
    def skus(self):
        return self.rfx_skus_set.all()  # This will return all related SKUs through the RFX_SKUs table


class RFXFile(models.Model):
    rfx = models.ForeignKey(RFX, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='rfx_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rfx.title} - {self.file.name}"


class GeneralQuestion(models.Model):
    QUESTION_TYPES = [
        ('text', 'Text'),
        ('Single-select', 'Single-select'),
        ('Multi-select', 'Multi-select'),
        ('File upload', 'File upload')
    ]

    rfx = models.ForeignKey(RFX, related_name='general_questions', on_delete=models.CASCADE)
    question_text = models.CharField(max_length=255)
    question_type = models.CharField(max_length=200, choices=QUESTION_TYPES)
    multiple_choice_options = models.TextField(blank=True, null=True)  # Store options as comma-separated values

    def __str__(self):
        return self.question_text
    

class SKUSpecificQuestion(models.Model):
    QUESTION_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('file', 'File Upload'),
        ('date', 'Date'),
        ('Single-select', 'Single-select'),
        ('Multi-select', 'Multi-select'),
    ]

    rfx = models.ForeignKey('RFX', on_delete=models.CASCADE, related_name='sku_specific_questions')
    question = models.CharField(max_length=255)
    question_type = models.CharField(max_length=50, choices=QUESTION_TYPES)

    def __str__(self):
        return f"{self.question} ({self.get_question_type_display()})"


class RFXInvitation(models.Model):
    rfx = models.ForeignKey(RFX, on_delete=models.CASCADE, related_name='invitations')
    supplier = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='rfx_invitations')
    token = models.CharField(max_length=64, unique=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    is_accepted = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = get_random_string(64)
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=7)  # Invitation expires in 7 days
        super().save(*args, **kwargs)



class SupplierResponse(models.Model):
    """A model to store a supplier's overall response to an RFX."""
    rfx = models.ForeignKey(RFX, on_delete=models.CASCADE, related_name="responses")
    supplier = models.ForeignKey(Company, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_finalized = models.BooleanField(default=False)

    def __str__(self):
        return f"Response to {self.rfx.title} by {self.supplier.name}"


class GeneralQuestionResponse(models.Model):
    """Stores each response to a general question within an RFX."""
    response = models.ForeignKey(SupplierResponse, on_delete=models.CASCADE, related_name="general_responses")
    question = models.ForeignKey(GeneralQuestion, on_delete=models.CASCADE)
    invitation = models.ForeignKey(RFXInvitation, on_delete=models.CASCADE)

    # Separate fields for different types of answers
    answer_text = models.TextField(blank=True, null=True)   # For open text responses
    answer_choice = models.TextField(blank=True, null=True)  # For single or multi-select answers
    answer_number = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # For numeric responses
    answer_date = models.DateField(blank=True, null=True)   # For date responses
    answer_file = models.FileField(upload_to='responses/files/', blank=True, null=True)  # For file uploads

    def __str__(self):
        return f"Response to General Question '{self.question}' by {self.response.supplier.name}"

class SKUSpecificQuestionResponse(models.Model):
    response = models.ForeignKey(SupplierResponse, on_delete=models.CASCADE, related_name="sku_question_responses")
    rfx_sku = models.ForeignKey(RFX_SKUs, on_delete=models.CASCADE)
    question = models.ForeignKey(SKUSpecificQuestion, on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True, null=True)
    answer_number = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    answer_file = models.FileField(upload_to='responses/files/', blank=True, null=True)
    answer_date = models.DateField(blank=True, null=True)
    answer_choice = models.TextField(blank=True, null=True)  # Add this field

    def __str__(self):
        return f"Response to SKU Question '{self.question}' for SKU '{self.rfx_sku.sku.name}' by {self.response.supplier.name}"
