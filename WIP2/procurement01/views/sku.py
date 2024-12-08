import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ..forms import SKUForm
from ..models import SKU


@login_required
def sku_list_view(request):
    user_company = request.user.company
    skus = SKU.objects.filter(company=user_company)
    return render(request, "procurement01/sku_list.html", {"skus": skus})


@login_required
def sku_detail_view(request, sku_id):
    sku = get_object_or_404(SKU, id=sku_id)
    return render(request, "procurement01/sku_detail.html", {"sku": sku})


@login_required
def sku_create_view(request):
    if not request.user.is_procurer:
        return render(request, "procurement01/access_denied.html")

    company = request.user.company

    if request.method == "POST":
        form = SKUForm(request.POST, company=company)
        if form.is_valid():
            sku = form.save(commit=False)
            sku.company = company
            sku.save()
            return redirect("sku_list")
    else:
        form = SKUForm(company=company)

    return render(request, "procurement01/sku_form.html", {"form": form})


@login_required
def search_skus(request):
    query = request.GET.get("query", "")
    company = request.user.company

    if query:
        skus = SKU.objects.filter(company=company, name__icontains=query)
        sku_data = [
            {"id": sku.id, "name": sku.name, "sku_code": sku.sku_code} for sku in skus
        ]
    else:
        sku_data = []

    return JsonResponse(sku_data, safe=False)


@login_required
@csrf_exempt
@require_POST
def create_sku(request):
    try:
        user = request.user
        if not user.is_procurer:
            return JsonResponse(
                {"success": False, "error": "Only procurers can create SKUs."},
                status=403,
            )

        data = json.loads(request.body.decode("utf-8"))
        sku_name = data.get("name", "").strip()

        if not sku_name:
            return JsonResponse(
                {"success": False, "error": "SKU name cannot be empty."}, status=400
            )

        company = user.company
        if SKU.objects.filter(name=sku_name, company=company).exists():
            return JsonResponse(
                {"success": False, "error": "SKU with this name already exists."},
                status=400,
            )

        new_sku = SKU.objects.create(
            name=sku_name, company=company, sku_code=f"{sku_name.upper()}-{company.id}"
        )

        return JsonResponse(
            {"success": True, "sku_id": new_sku.id, "sku_name": new_sku.name}
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
