from django import forms

from ..models import OEM, Company


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["name", "email", "oems"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter Supplier Name"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Enter Supplier Email"}
            ),
            "oems": forms.SelectMultiple(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        procurer = kwargs.pop("procurer", None)
        super().__init__(*args, **kwargs)
        if procurer:
            self.fields["oems"].queryset = OEM.objects.filter(procurer=procurer)

    def save(self, procurer, *args, **kwargs):
        supplier = super().save(commit=False)
        supplier.company_type = "Supplier"
        supplier.procurer = procurer
        supplier.save()
        self.save_m2m()
        return supplier

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            raise forms.ValidationError("Email is required for suppliers.")
        return email
