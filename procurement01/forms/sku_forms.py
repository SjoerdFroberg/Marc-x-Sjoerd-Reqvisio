from django import forms

from ..models import OEM, SKU


class SKUForm(forms.ModelForm):
    class Meta:
        model = SKU
        fields = ["name", "sku_code", "image_url", "oem"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter SKU Name"}
            ),
            "sku_code": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter SKU Code"}
            ),
            "image_url": forms.URLInput(
                attrs={"class": "form-control", "placeholder": "Enter Image URL"}
            ),
            "oem": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)
        if company:
            self.fields["oem"].queryset = OEM.objects.filter(procurer=company)


class SKUSearchForm(forms.Form):
    query = forms.CharField(
        label="Search SKUs",
        max_length=100,
        widget=forms.TextInput(
            attrs={"placeholder": "Search for SKUs...", "class": "form-control"}
        ),
    )
