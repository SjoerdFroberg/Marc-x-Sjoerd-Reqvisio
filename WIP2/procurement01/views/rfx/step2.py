import json
from collections import OrderedDict

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from ...forms import SKUSearchForm
from ...models import RFX, SKU, RFX_SKUs


@login_required
def create_rfx_step2(request, rfx_id):
    rfx = get_object_or_404(RFX, id=rfx_id)

    if request.method == "POST":
        with transaction.atomic():
            existing_sku_ids = set(
                RFX_SKUs.objects.filter(rfx=rfx).values_list("sku_id", flat=True)
            )

            sku_ids = request.POST.getlist("skus[]")
            submitted_sku_ids = set(int(sku_id) for sku_id in sku_ids)

            skus_to_remove = existing_sku_ids - submitted_sku_ids
            if skus_to_remove:
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
                    "extra_columns": extra_columns,
                }
            )

        context = {
            "rfx": rfx,
            "sku_search_form": SKUSearchForm(),
            "processed_skus": processed_skus,
            "extra_columns": extra_columns,
            "step": "step2",
            "current_step": 2,
        }

        return render(request, "procurement01/create_rfx_step2.html", context)


@login_required
def create_rfx_step2a(request, rfx_id):
    rfx = get_object_or_404(RFX, id=rfx_id)

    if request.method == "POST":
        sku_ids = request.POST.getlist("skus[]")
        extra_columns_data = request.POST.get("extra_columns_data")
        extra_columns_json = (
            json.loads(extra_columns_data) if extra_columns_data else []
        )

        for sku_data in extra_columns_json:
            sku_id = sku_data["sku_id"]
            sku = get_object_or_404(SKU, id=sku_id)
            rfx_sku = RFX_SKUs.objects.create(rfx=rfx, sku=sku)
            data_ordered = OrderedDict(sku_data["data"])
            rfx_sku.set_extra_data(data_ordered)
            rfx_sku.save()

        return redirect("create_rfx_step3", rfx_id=rfx.id)

    return render(
        request,
        "procurement01/create_rfx_step2a.html",
        {
            "rfx": rfx,
            "sku_search_form": SKUSearchForm(),
        },
    )
