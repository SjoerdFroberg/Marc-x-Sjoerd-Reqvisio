import json
from collections import OrderedDict

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from ...models import RFX, SKU, RFX_SKUs, SKUSpecificQuestion


@login_required
def create_rfx_step4(request, rfx_id):
    rfx = get_object_or_404(RFX, id=rfx_id)

    if request.method == "POST":
        with transaction.atomic():
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
            return redirect(f"create_rfx_{navigation_destination}", rfx_id=rfx.id)
    else:
        rfx_skus = RFX_SKUs.objects.filter(rfx=rfx)
        processed_skus = []
        extra_columns = []

        for rfx_sku in rfx_skus:
            extra_data = rfx_sku.get_specification_data()
            if not extra_columns and extra_data:
                extra_columns = list(extra_data.keys())
            processed_skus.append(
                {
                    "sku_id": rfx_sku.sku.id,
                    "sku_name": rfx_sku.sku.name,
                    "extra_data": extra_data,
                }
            )

        sku_specific_questions = SKUSpecificQuestion.objects.filter(rfx=rfx)

        context = {
            "rfx": rfx,
            "extra_columns": extra_columns,
            "processed_skus": processed_skus,
            "sku_specific_questions": sku_specific_questions,
            "step": "step4",
        }

        return render(request, "procurement01/create_rfx_step4.html", context)


@login_required
def create_rfx_step4a(request, rfx_id):
    rfx = get_object_or_404(RFX, id=rfx_id)
    rfx_skus = RFX_SKUs.objects.filter(rfx=rfx)
    processed_skus = []
    extra_columns = []

    for rfx_sku in rfx_skus:
        extra_data = rfx_sku.get_extra_data()
        if not extra_columns:
            extra_columns = list(extra_data.keys())
        processed_skus.append(
            {
                "sku_id": rfx_sku.id,
                "sku_name": rfx_sku.sku.name,
                "extra_data": extra_data,
            }
        )

    if request.method == "POST":
        sku_specific_data = request.POST.get("sku_specific_data")
        questions_data = json.loads(sku_specific_data) if sku_specific_data else []

        SKUSpecificQuestion.objects.filter(rfx=rfx).delete()

        for question_data in questions_data:
            SKUSpecificQuestion.objects.create(
                rfx=rfx,
                question=question_data["question"],
                question_type=question_data["question_type"],
            )

        return redirect("create_rfx_step5", rfx_id=rfx.id)

    context = {
        "rfx": rfx,
        "extra_columns": extra_columns,
        "processed_skus": processed_skus,
        "question_types": SKUSpecificQuestion.QUESTION_TYPES,
    }
    return render(request, "procurement01/create_rfx_step4.html", context)
