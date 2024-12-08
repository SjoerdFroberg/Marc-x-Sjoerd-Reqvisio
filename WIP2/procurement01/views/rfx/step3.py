from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, redirect, render

from ...forms import GeneralQuestionForm
from ...models import RFX, GeneralQuestion


@login_required
def create_rfx_step3(request, rfx_id):
    rfx = get_object_or_404(RFX, id=rfx_id)

    if GeneralQuestion.objects.filter(rfx=rfx):
        extra_forms = 0
    else:
        extra_forms = 1

    GeneralQuestionFormSet = modelformset_factory(
        GeneralQuestion, form=GeneralQuestionForm, extra=extra_forms, can_delete=True
    )

    if request.method == "POST":
        with transaction.atomic():
            general_questions_formset = GeneralQuestionFormSet(
                request.POST, queryset=GeneralQuestion.objects.filter(rfx=rfx)
            )

            if general_questions_formset.is_valid():
                general_questions = general_questions_formset.save(commit=False)
                for question in general_questions:
                    question.rfx = rfx
                    question.save()

                for deleted_question in general_questions_formset.deleted_objects:
                    deleted_question.delete()

            navigation_destination = request.POST.get("navigation_destination")
            return redirect(f"create_rfx_{navigation_destination}", rfx_id=rfx.id)

    else:
        general_questions_formset = GeneralQuestionFormSet(
            queryset=GeneralQuestion.objects.filter(rfx=rfx)
        )

        context = {
            "rfx": rfx,
            "general_questions_formset": general_questions_formset,
            "step": "step3",
        }

        return render(request, "procurement01/create_rfx_step3.html", context)
