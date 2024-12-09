from django import forms

from ..models import (
    GeneralQuestion,
    GeneralQuestionResponse,
    SKUSpecificQuestion,
    SKUSpecificQuestionResponse,
)


class GeneralQuestionForm(forms.ModelForm):
    class Meta:
        model = GeneralQuestion
        fields = ["question_text", "question_type", "multiple_choice_options"]
        widgets = {
            "question_text": forms.TextInput(attrs={"class": "form-control"}),
            "question_type": forms.Select(
                attrs={"class": "form-control question-type-select"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        question_type = cleaned_data.get("question_type")
        multiple_choice_options = cleaned_data.get("multiple_choice_options")

        if (
            question_type in ["Single-select", "Multi-select"]
            and not multiple_choice_options
        ):
            self.add_error(
                "multiple_choice_options",
                "This field is required for single or multi-select questions.",
            )

        return cleaned_data


class SKUSpecificQuestionForm(forms.ModelForm):
    class Meta:
        model = SKUSpecificQuestion
        fields = ["question", "question_type"]
        labels = {"question": "Question", "question_type": "Question Type"}
        widgets = {
            "question": forms.TextInput(
                attrs={"placeholder": "Enter question text", "class": "form-control"}
            ),
            "question_type": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super(SKUSpecificQuestionForm, self).__init__(*args, **kwargs)
        # Customize the question_type choices display
        self.fields["question_type"].choices = SKUSpecificQuestion.QUESTION_TYPES


class GeneralQuestionResponseForm(forms.ModelForm):
    class Meta:
        model = GeneralQuestionResponse
        fields = [
            "answer_text",
            "answer_choice",
            "answer_number",
            "answer_date",
            "answer_file",
        ]

    def __init__(self, *args, **kwargs):
        question = kwargs.pop(
            "question", None
        )  # Expecting the question instance to be passed in
        super().__init__(*args, **kwargs)

        # Customize the form fields based on question type
        if question:
            self.fields["answer_text"].widget = forms.HiddenInput()
            self.fields["answer_choice"].widget = forms.HiddenInput()
            self.fields["answer_number"].widget = forms.HiddenInput()
            self.fields["answer_date"].widget = forms.HiddenInput()
            self.fields["answer_file"].widget = forms.HiddenInput()

            if question.question_type == "text":
                self.fields["answer_text"].widget = forms.Textarea(
                    attrs={"placeholder": "Enter your answer here"}
                )
                self.fields["answer_text"].required = True
            elif question.question_type in ["Single-select", "Multi-select"]:
                choices = [
                    (option, option)
                    for option in question.multiple_choice_options.split(",")
                ]
                if question.question_type == "Single-select":
                    self.fields["answer_choice"] = forms.ChoiceField(
                        choices=choices, widget=forms.RadioSelect
                    )
                else:
                    self.fields["answer_choice"] = forms.MultipleChoiceField(
                        choices=choices, widget=forms.CheckboxSelectMultiple
                    )
                self.fields["answer_choice"].required = True
            elif question.question_type == "number":
                self.fields["answer_number"].widget = forms.NumberInput(
                    attrs={"placeholder": "Enter a number"}
                )
                self.fields["answer_number"].required = True
            elif question.question_type == "date":
                self.fields["answer_date"].widget = forms.DateInput(
                    attrs={"type": "date"}
                )
                self.fields["answer_date"].required = True
            elif question.question_type == "file":
                self.fields["answer_file"].widget = forms.FileInput()
                self.fields["answer_file"].required = True


class SKUSpecificQuestionResponseForm(forms.ModelForm):
    class Meta:
        model = SKUSpecificQuestionResponse
        fields = ["answer_text", "answer_number", "answer_file", "answer_date"]

    def __init__(self, *args, **kwargs):
        question = kwargs.pop(
            "question", None
        )  # Expecting the question instance to be passed in
        super().__init__(*args, **kwargs)

        # Customize the form fields based on question type
        if question:
            self.fields["answer_text"].widget = forms.HiddenInput()
            self.fields["answer_number"].widget = forms.HiddenInput()
            self.fields["answer_date"].widget = forms.HiddenInput()
            self.fields["answer_file"].widget = forms.HiddenInput()

            if question.question_type == "text":
                self.fields["answer_text"].widget = forms.Textarea(
                    attrs={"placeholder": "Enter your answer here"}
                )
                self.fields["answer_text"].required = True
            elif question.question_type == "number":
                self.fields["answer_number"].widget = forms.NumberInput(
                    attrs={"placeholder": "Enter a number"}
                )
                self.fields["answer_number"].required = True
            elif question.question_type == "date":
                self.fields["answer_date"].widget = forms.DateInput(
                    attrs={"type": "date"}
                )
                self.fields["answer_date"].required = True
            elif question.question_type == "file":
                self.fields["answer_file"].widget = forms.FileInput()
                self.fields["answer_file"].required = True
