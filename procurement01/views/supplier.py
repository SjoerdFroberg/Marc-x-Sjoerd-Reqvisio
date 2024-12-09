from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from ..forms import SupplierForm
from ..models import Company


@login_required
def supplier_list_view(request):
    if request.user.is_procurer:
        procurer_company = request.user.company
        suppliers = Company.objects.filter(procurer=procurer_company)
        return render(
            request, "procurement01/supplier_list.html", {"suppliers": suppliers}
        )
    else:
        return render(request, "procurement01/access_denied.html")


@login_required
def create_supplier_view(request):
    if not request.user.is_procurer:
        return render(request, "procurement01/access_denied.html")

    procurer_company = request.user.company

    if request.method == "POST":
        form = SupplierForm(request.POST, procurer=procurer_company)
        if form.is_valid():
            form.save(procurer=procurer_company)
            return redirect("supplier_list")
    else:
        form = SupplierForm(procurer=procurer_company)

    return render(request, "procurement01/supplier_form.html", {"form": form})
