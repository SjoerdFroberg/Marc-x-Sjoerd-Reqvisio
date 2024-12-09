from django import forms

from ..models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description"]

    def save(self, commit=True, company=None):
        project = super().save(commit=False)
        if company:
            project.company = company
        if commit:
            project.save()
        return project
