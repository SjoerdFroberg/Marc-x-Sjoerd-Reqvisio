from django.contrib.auth.models import AbstractUser
import json 
from django.db import models




    

class Company(models.Model):
    COMPANY_TYPES = [
        ('Procurer', 'Procurer'),
        ('Supplier', 'Supplier'),
    ]
    name = models.CharField(max_length=100)
    company_type = models.CharField(max_length=10, choices=COMPANY_TYPES)
    procurer = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='suppliers')

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

    def __str__(self):
        return self.name 
    

class RFP_SKUs(models.Model):
    rfp = models.ForeignKey('RFP', on_delete=models.CASCADE)
    sku = models.ForeignKey('SKU', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    extra_data = models.TextField(null=True, blank=True)  # Use TextField to store JSON data

    def set_extra_data(self, data):
        """Serialize Python dictionary to JSON string and save in extra_data"""
        self.extra_data = json.dumps(data)

    def get_extra_data(self):
        """Deserialize JSON string from extra_data into Python dictionary"""
        if self.extra_data:
            return json.loads(self.extra_data)
        return {}



class RFP(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank = True)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return self.title

    @property
    def skus(self):
        return self.rfp_skus_set.all()  # This will return all related SKUs through the RFP_SKUs table


class RFPFile(models.Model):
    rfp = models.ForeignKey(RFP, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='rfp_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rfp.title} - {self.file.name}"


class GeneralQuestion(models.Model):
    QUESTION_TYPES = [
        ('text', 'Text'),
        ('Single-select', 'Single-select'),
        ('Multi-select', 'Multi-select'),
        ('File upload', 'File upload')
    ]

    rfp = models.ForeignKey(RFP, related_name='general_questions', on_delete=models.CASCADE)
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
    ]

    rfp = models.ForeignKey('RFP', on_delete=models.CASCADE, related_name='sku_specific_questions')
    question = models.CharField(max_length=255)
    question_type = models.CharField(max_length=50, choices=QUESTION_TYPES)

    def __str__(self):
        return f"{self.question} ({self.get_question_type_display()})"
