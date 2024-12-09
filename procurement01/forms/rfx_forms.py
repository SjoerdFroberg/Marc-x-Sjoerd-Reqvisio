import json

from django import forms

from ..models import RFX, SKU, Project, RFX_SKUs


class RFXBasicForm(forms.ModelForm):
    class Meta:
        model = RFX
        fields = ["title", "description", "project"]
        widgets = {
            "project": forms.Select(attrs={"class": "form-control"}),
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter RFX Title"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Enter RFX Description",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["project"].required = False
        if self.user and hasattr(self.user, "company"):
            self.fields["project"].queryset = Project.objects.filter(
                company=self.user.company
            )
        else:
            self.fields["project"].queryset = Project.objects.none()


class RFX_SKUForm(forms.ModelForm):
    quantity = forms.IntegerField(min_value=1, label="Quantity")
    target_price = forms.DecimalField(
        decimal_places=2, max_digits=10, label="Target Price"
    )
    unit_size = forms.CharField(max_length=100, label="Unit Size")

    class Meta:
        model = RFX_SKUs
        fields = ["sku", "quantity", "target_price", "unit_size"]

    def __init__(self, *args, **kwargs):
        company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)
        if company:
            self.fields["sku"].queryset = SKU.objects.filter(company=company)


class RFXForm(forms.ModelForm):
    additional_columns = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = RFX
        fields = ["title", "description"]

    def save(self, commit=True):
        instance = super().save(commit=False)
        if "additional_columns" in self.cleaned_data:
            instance.additional_columns = json.dumps(
                self.cleaned_data["additional_columns"]
            )
        if commit:
            instance.save()
        return instance


class RebuyUploadForm(forms.Form):
    file = forms.FileField(
        required=True,
        label="Upload CSV File",
        widget=forms.FileInput(attrs={"accept": ".csv"}),
    )
