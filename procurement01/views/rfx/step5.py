import json
from collections import OrderedDict

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, redirect, render

from ...forms import GeneralQuestionForm, RFXBasicForm
from ...models import RFX, SKU, GeneralQuestion, RFX_SKUs, RFXFile, SKUSpecificQuestion


@login_required
def create_rfx_step5(request, rfx_id):
    rfx = get_object_or_404(RFX, id=rfx_id)
    GeneralQuestionFormSet = modelformset_factory(
        GeneralQuestion, form=GeneralQuestionForm, extra=0, can_delete=True
    )

    if request.method == "POST":
        with transaction.atomic():
            rfx_form = RFXBasicForm(request.POST, instance=rfx)
            general_questions_formset = GeneralQuestionFormSet(
                request.POST, queryset=GeneralQuestion.objects.filter(rfx=rfx)
            )

            if rfx_form.is_valid() and general_questions_formset.is_valid():
                rfx = rfx_form.save()

                files_to_delete = request.POST.getlist("delete_files")
                if files_to_delete:
                    RFXFile.objects.filter(id__in=files_to_delete, rfx=rfx).delete()

                for file in request.FILES.getlist("new_files"):
                    RFXFile.objects.create(rfx=rfx, file=file)

                general_questions = general_questions_formset.save(commit=False)
                for question in general_questions:
                    question.rfx = rfx
                    question.save()

                for deleted_question in general_questions_formset.deleted_objects:
                    deleted_question.delete()

                existing_sku_ids = set(
                    RFX_SKUs.objects.filter(rfx=rfx).values_list("sku_id", flat=True)
                )

                sku_ids = request.POST.getlist("skus[]")
                submitted_sku_ids = set(int(sku_id) for sku_id in sku_ids)

                skus_to_remove = existing_sku_ids - submitted_sku_ids
                RFX_SKUs.objects.filter(rfx=rfx, sku_id__in=skus_to_remove).delete()

                extra_columns_data = request.POST.get("extra_columns_data")
                extra_columns_json = (
                    json.loads(extra_columns_data) if extra_columns_data else []
                )

                for sku_data in extra_columns_json:
                    sku_id = sku_data["sku_id"]
                    sku = get_object_or_404(SKU, id=sku_id)
                    rfx_sku, _ = RFX_SKUs.objects.get_or_create(rfx=rfx, sku=sku)
                    data_ordered = OrderedDict(sku_data["data"])
                    rfx_sku.set_specification_data(OrderedDict(data_ordered))

                SKUSpecificQuestion.objects.filter(rfx=rfx).delete()

                sku_specific_data = request.POST.get("sku_specific_data")
                sku_specific_json = (
                    json.loads(sku_specific_data) if sku_specific_data else []
                )

                for question_data in sku_specific_json:
                    SKUSpecificQuestion.objects.create(
                        rfx=rfx,
                        question=question_data["question"],
                        question_type=question_data["question_type"],
                    )

                navigation_destination = request.POST.get("navigation_destination")
                if navigation_destination == "step4":
                    return redirect(
                        f"create_rfx_{navigation_destination}", rfx_id=rfx.id
                    )
                else:
                    return redirect("invite_suppliers", rfx_id=rfx.id)

    else:
        rfx_form = RFXBasicForm(instance=rfx)
        existing_files = rfx.files.all()
        general_questions_formset = GeneralQuestionFormSet(
            queryset=GeneralQuestion.objects.filter(rfx=rfx)
        )

        rfx_skus = RFX_SKUs.objects.filter(rfx=rfx)
        processed_skus = []
        extra_columns = []

        for rfx_sku in rfx_skus:
            specification_data = rfx_sku.get_specification_data()
            if not extra_columns and specification_data:
                extra_columns = list(specification_data.keys())
            processed_skus.append(
                {
                    "sku_id": rfx_sku.sku.id,
                    "sku_name": rfx_sku.sku.name,
                    "extra_data": specification_data,
                }
            )

        sku_specific_questions = SKUSpecificQuestion.objects.filter(rfx=rfx)

        context = {
            "rfx": rfx,
            "rfx_form": rfx_form,
            "existing_files": existing_files,
            "general_questions_formset": general_questions_formset,
            "extra_columns": extra_columns,
            "processed_skus": processed_skus,
            "sku_specific_questions": sku_specific_questions,
        }

        return render(request, "procurement01/create_rfx_step5.html", context)
