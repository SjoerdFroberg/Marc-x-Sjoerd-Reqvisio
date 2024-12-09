import csv
import json
from collections import OrderedDict
from io import TextIOWrapper

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import RebuyUploadForm
from ..models import RFX, SKU, Company, RFX_SKUs, RFXInvitation, SKUSpecificQuestion
from .invitation import send_invitation_email


@login_required
def quick_quote_rebuy_initial_create(request):
    user_company = request.user.company

    with transaction.atomic():
        rfx = RFX.objects.create(
            title="Temporary Title",
            description="Quick quote for REBUY parts",
            company=user_company,
        )
        rfx.title = f"REBUY Quotation for Parts {rfx.id}"
        rfx.save()

        sku_specific_questions = [
            {"question": "All-In Price / Unit", "question_type": "number"},
            {"question": "Quantity Offered", "question_type": "number"},
            {"question": "Lead Time in Days", "question_type": "number"},
        ]
        for question in sku_specific_questions:
            SKUSpecificQuestion.objects.get_or_create(
                rfx=rfx,
                question=question["question"],
                question_type=question["question_type"],
            )

    return redirect("quick_quote_rebuy", rfx_id=rfx.id)


@login_required
def quick_quote_rebuy(request, rfx_id):
    rfx = RFX.objects.get(id=rfx_id, company=request.user.company)
    user_company = request.user.company
    preloaded_sku_questions = SKUSpecificQuestion.objects.filter(rfx=rfx)
    processed_skus = []

    rfx_skus = RFX_SKUs.objects.filter(rfx=rfx)
    if rfx_skus:
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
    else:
        extra_columns = ["OEM", "SKU Code", "Quantity Required", "Maximum Lead Time"]

    upload_form = RebuyUploadForm()

    if request.method == "POST" and request.POST.get("action") == "upload_file":
        upload_form = RebuyUploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            file = upload_form.cleaned_data["file"]
            processed_skus, warnings = parse_rebuy_csv(
                file=file, company=user_company, encoding=request.encoding or "utf-8"
            )

            with transaction.atomic():
                for sku_info in processed_skus:
                    if not sku_info.get("invalid"):
                        db_sku = sku_info["db_sku"]
                        rfx_sku, created = RFX_SKUs.objects.get_or_create(
                            rfx=rfx, sku=db_sku
                        )
                        data = {
                            "OEM": sku_info["OEM"],
                            "SKU Code": sku_info["SKU Code"],
                            "Quantity Required": sku_info["Quantity Required"],
                            "Maximum Lead Time": sku_info["Maximum Lead Time"],
                        }
                        rfx_sku.set_specification_data(data)

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

            return render(
                request,
                "procurement01/quick_quote_rebuy.html",
                {
                    "rfx": rfx,
                    "extra_columns": extra_columns,
                    "processed_skus": processed_skus,
                    "sku_specific_questions": preloaded_sku_questions,
                    "upload_form": upload_form,
                    "warnings": warnings,
                },
            )

    elif request.method == "POST" and request.POST.get("action") == "save_changes":
        with transaction.atomic():
            rfx.title = request.POST.get("title", rfx.title)
            rfx.save()

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

            if navigation_destination == "quick_quote_rebuy_invite_suppliers":
                return redirect("quick_quote_rebuy_invite_suppliers", rfx_id=rfx.id)
            elif navigation_destination == "quick_quote_rebuy_invite_suppliers_auto":
                rfx_skus = RFX_SKUs.objects.filter(rfx=rfx)
                oem_ids = rfx_skus.values_list("sku__oem", flat=True).distinct()
                oem_ids = [o for o in oem_ids if o is not None]

                suppliers = Company.objects.filter(
                    company_type="Supplier",
                    procurer=request.user.company,
                    oems__in=oem_ids,
                ).distinct()

                for supplier in suppliers:
                    invitation, created = RFXInvitation.objects.get_or_create(
                        rfx=rfx, supplier=supplier
                    )
                    if created:
                        send_invitation_email(invitation)

                return redirect("rfx_list")
            else:
                return redirect("quick_quote_rebuy", rfx_id=rfx.id)

    return render(
        request,
        "procurement01/quick_quote_rebuy.html",
        {
            "rfx": rfx,
            "extra_columns": extra_columns,
            "processed_skus": processed_skus,
            "sku_specific_questions": preloaded_sku_questions,
            "upload_form": upload_form,
        },
    )


@login_required
def quick_quote_rebuy_invite_suppliers(request, rfx_id):
    rfx = get_object_or_404(RFX, id=rfx_id, company=request.user.company)

    if not request.user.is_procurer:
        return render(request, "procurement01/access_denied.html")

    rfx_skus = RFX_SKUs.objects.filter(rfx=rfx)
    oem_ids = rfx_skus.values_list("sku__oem", flat=True).distinct()
    oem_ids = [o for o in oem_ids if o is not None]

    suppliers = Company.objects.filter(
        company_type="Supplier", procurer=request.user.company, oems__in=oem_ids
    ).distinct()

    if request.method == "POST":
        supplier_ids = request.POST.getlist("suppliers")
        for supplier_id in supplier_ids:
            supplier = Company.objects.get(id=supplier_id)
            invitation, created = RFXInvitation.objects.get_or_create(
                rfx=rfx, supplier=supplier
            )
            if created:
                send_invitation_email(invitation)
        return redirect("rfx_list")

    return render(
        request,
        "procurement01/quick_quote_rebuy_invite_suppliers.html",
        {"rfx": rfx, "suppliers": suppliers},
    )


def parse_rebuy_csv(file, company, encoding="utf-8"):
    f = TextIOWrapper(file.file, encoding=encoding, errors="replace")
    reader = csv.DictReader(f)

    required_columns = ["SKU Name", "Quantity Required", "Maximum Lead Time"]
    for col in required_columns:
        if col not in reader.fieldnames:
            raise ValueError(f"Missing column '{col}' in CSV.")

    processed_skus = []
    warnings = []

    for line_num, row in enumerate(reader, start=2):
        sku_name = row.get("SKU Name", "").strip()
        quantity_required = row.get("Quantity Required", "").strip()
        max_lead_time = row.get("Maximum Lead Time", "").strip()

        try:
            db_sku = SKU.objects.get(name__iexact=sku_name, company=company)
            oem_name = db_sku.oem.name if db_sku.oem else ""
            sku_code = db_sku.sku_code
            invalid = False
        except SKU.DoesNotExist:
            db_sku = None
            oem_name = ""
            sku_code = ""
            invalid = True
            warnings.append(f"Line {line_num}: SKU '{sku_name}' not found in database.")

        processed_skus.append(
            {
                "SKU Name": sku_name,
                "OEM": oem_name,
                "SKU Code": sku_code,
                "Quantity Required": quantity_required,
                "Maximum Lead Time": max_lead_time,
                "db_sku": db_sku,
                "invalid": invalid,
            }
        )

    return processed_skus, warnings
