from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from ...models import RFX


@login_required
def rfx_list_view(request):
    user = request.user
    company = user.company

    if company.company_type == "Procurer":
        rfxs = RFX.objects.filter(company=company)
    else:
        rfxs = RFX.objects.none()

    return render(request, "procurement01/rfx_list.html", {"rfxs": rfxs})


@login_required
def rfx_detail(request, rfx_id):
    rfx = get_object_or_404(RFX, id=rfx_id)
    invitations_sent = rfx.invitations.count()
    responses_received = rfx.responses.filter(is_finalized=True).count()

    context = {
        "rfx": rfx,
        "invitations_sent": invitations_sent,
        "responses_received": responses_received,
    }

    return render(request, "procurement01/rfx_detail.html", context)
