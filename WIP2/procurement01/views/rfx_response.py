import json
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone

from ..models import (
    RFX,
    GeneralQuestion,
    GeneralQuestionResponse,
    RFX_SKUs,
    RFXInvitation,
    SKUSpecificQuestion,
    SKUSpecificQuestionResponse,
    SupplierResponse,
)


def supplier_rfx_response(request, token):
    invitation = get_object_or_404(RFXInvitation, token=token)

    if invitation.expires_at and timezone.now() > invitation.expires_at:
        return render(request, "procurement01/expired_invitation.html")

    if invitation.responded_at:
        return render(request, "procurement01/already_responded.html")

    rfx = invitation.rfx
    general_questions = GeneralQuestion.objects.filter(rfx=rfx)
    sku_specific_questions = SKUSpecificQuestion.objects.filter(rfx=rfx)
    rfx_skus = RFX_SKUs.objects.filter(rfx=rfx)

    procurer_name = rfx.company.name
    if procurer_name == "REBUY":
        first_rfx_sku = rfx_skus.first()
        has_oem_column = False
        if first_rfx_sku:
            spec_data = first_rfx_sku.get_specification_data()
            extra_columns = list(spec_data.keys()) if spec_data else []
            if "OEM" in extra_columns:
                has_oem_column = True

        if has_oem_column:
            served_oems = invitation.supplier.oems.all()
            rfx_skus = rfx_skus.filter(sku__oem__in=served_oems)

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

    for question in general_questions:
        if question.question_type in ["Single-select", "Multi-select"]:
            question.options_list = [
                option.strip() for option in question.multiple_choice_options.split(",")
            ]

    for sku_question in sku_specific_questions:
        if sku_question.question_type in ["Single-select", "Multi-select"]:
            sku_question.options_list = [
                option.strip()
                for option in sku_question.multiple_choice_options.split(",")
            ]

    if request.method == "POST":
        try:
            with transaction.atomic():
                supplier_response = SupplierResponse.objects.create(
                    rfx=rfx, supplier=invitation.supplier, is_finalized=True
                )

                # Process general question responses
                for question in general_questions:
                    field_name = f"general_{question.id}"
                    file = request.FILES.get(field_name)

                    answer_text = None
                    answer_choice = None
                    if question.question_type == "text":
                        answer_text = request.POST.get(field_name)
                    elif question.question_type == "Single-select":
                        answer_choice = request.POST.get(field_name)
                    elif question.question_type == "Multi-select":
                        selected_options = request.POST.getlist(field_name)
                        answer_choice = ",".join(selected_options)

                    GeneralQuestionResponse.objects.create(
                        response=supplier_response,
                        question=question,
                        invitation=invitation,
                        answer_text=answer_text,
                        answer_choice=answer_choice,
                        answer_file=(
                            file if question.question_type == "File upload" else None
                        ),
                    )

                # Process SKU-specific question responses
                for sku in processed_skus:
                    for sku_question in sku_specific_questions:
                        field_name = f'sku_{sku["sku_id"]}_{sku_question.id}'
                        file = request.FILES.get(field_name)
                        answer = request.POST.get(field_name)

                        response_data = {
                            "response": supplier_response,
                            "rfx_sku": RFX_SKUs.objects.get(
                                rfx=rfx, sku__id=sku["sku_id"]
                            ),
                            "question": sku_question,
                            "answer_text": None,
                            "answer_number": None,
                            "answer_file": None,
                            "answer_date": None,
                            "answer_choice": None,
                        }

                        if sku_question.question_type == "text":
                            response_data["answer_text"] = answer
                        elif sku_question.question_type == "number":
                            try:
                                response_data["answer_number"] = (
                                    Decimal(answer) if answer else None
                                )
                            except InvalidOperation:
                                pass
                        elif sku_question.question_type == "date":
                            try:
                                response_data["answer_date"] = (
                                    datetime.strptime(answer, "%Y-%m-%d").date()
                                    if answer
                                    else None
                                )
                            except ValueError:
                                pass
                        elif sku_question.question_type == "file":
                            response_data["answer_file"] = file
                        elif sku_question.question_type == "Single-select":
                            response_data["answer_choice"] = answer
                        elif sku_question.question_type == "Multi-select":
                            selected_options = request.POST.getlist(field_name)
                            response_data["answer_choice"] = ",".join(selected_options)

                        SKUSpecificQuestionResponse.objects.create(**response_data)

                invitation.responded_at = timezone.now()
                invitation.is_accepted = True
                invitation.save()

                return redirect("supplier_thank_you")

        except Exception as e:
            return render(request, "procurement01/error.html", {"message": str(e)})

    return render(
        request,
        "procurement01/supplier_rfx_response.html",
        {
            "rfx": rfx,
            "invitation": invitation,
            "general_questions": general_questions,
            "sku_specific_questions": sku_specific_questions,
            "extra_columns": extra_columns,
            "processed_skus": processed_skus,
        },
    )


def supplier_thank_you(request):
    rfx_title = request.session.get("rfx_title", "the RFX")
    if "rfx_title" in request.session:
        del request.session["rfx_title"]
    return render(
        request, "procurement01/supplier_thank_you.html", {"rfx_title": rfx_title}
    )


@login_required
def general_question_table_view(request, rfx_id):
    rfx = get_object_or_404(RFX, id=rfx_id)
    general_questions = GeneralQuestion.objects.filter(rfx=rfx)
    supplier_responses = SupplierResponse.objects.filter(rfx=rfx)
    response_data = {}

    for response in supplier_responses:
        for gq_response in response.general_responses.all():
            question_id = gq_response.question.id
            supplier_id = response.supplier.id
            if question_id not in response_data:
                response_data[question_id] = {}
            response_data[question_id][supplier_id] = gq_response

    context = {
        "rfx": rfx,
        "general_questions": general_questions,
        "supplier_responses": supplier_responses,
        "response_data": response_data,
        "multi_choice_types": ["Single-select", "Multi-select"],
    }

    return render(request, "procurement01/general_question_table.html", context)


@login_required
def sku_specific_question_responses_analysis(request, rfx_id):
    rfx = get_object_or_404(RFX, id=rfx_id)
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
    supplier_responses = SupplierResponse.objects.filter(rfx=rfx)
    sku_question_responses = SKUSpecificQuestionResponse.objects.filter(
        response__in=supplier_responses
    )

    response_lookup = {}
    for response in sku_question_responses:
        key = f"{response.response.supplier.id}_{response.rfx_sku.sku.id}_{response.question.id}"
        response_lookup[key] = {
            "text": response.answer_text,
            "number": response.answer_number,
            "file": response.answer_file.url if response.answer_file else None,
            "date": response.answer_date,
            "choice": response.answer_choice,
        }

    selected_question_ids = request.GET.getlist("question_ids[]")
    if "question_ids[]" not in request.GET:
        selected_question_ids = [str(q.id) for q in sku_specific_questions]
    else:
        selected_question_ids = [qid for qid in selected_question_ids if qid]

    selected_questions = sku_specific_questions.filter(id__in=selected_question_ids)

    sku_specific_questions_data = [
        {
            "value": str(question.id),
            "label": question.question.replace('"', '\\"').replace('\\\\"', '"'),
            "selected": str(question.id) in selected_question_ids,
        }
        for question in sku_specific_questions
    ]

    context = {
        "rfx": rfx,
        "processed_skus": processed_skus,
        "extra_columns": extra_columns,
        "sku_specific_questions": sku_specific_questions,
        "selected_questions": selected_questions,
        "selected_question_ids": selected_question_ids,
        "supplier_responses": supplier_responses,
        "response_lookup": response_lookup,
        "multi_choice_types": ["Single-select", "Multi-select"],
        "sku_specific_questions_json": json.dumps(
            sku_specific_questions_data, cls=DjangoJSONEncoder
        ),
    }

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        table_html = render_to_string(
            "procurement01/sku_specific_question_table.html", context, request=request
        )
        return JsonResponse({"table_html": table_html})

    return render(
        request,
        "procurement01/sku_specific_question_responses_analysis.html",
        context,
    )
