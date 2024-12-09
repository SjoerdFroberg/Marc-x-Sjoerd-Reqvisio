from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from ..models import RFX, Company, RFXInvitation


def send_invitation_email(invitation):
    subject = f"Invitation to respond to RFX: {invitation.rfx.title}"
    invitation_link = settings.SITE_URL + reverse(
        "supplier_rfx_response", args=[invitation.token]
    )
    message = f"""
    Dear {invitation.supplier.name},

    You have been invited to respond to the RFX titled "{invitation.rfx.title}".

    Please click the link below to view the RFX and submit your response:

    {invitation_link}

    Best regards,
    {invitation.rfx.title}
    """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [invitation.supplier.email],
        fail_silently=False,
    )


@login_required
def invite_suppliers(request, rfx_id):
    rfx = get_object_or_404(RFX, id=rfx_id)

    if not request.user.is_procurer:
        return render(request, "procurement01/access_denied.html")

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

    procurer_company = request.user.company
    suppliers = Company.objects.filter(
        procurer=procurer_company, company_type="Supplier"
    )
    return render(
        request,
        "procurement01/invite_suppliers.html",
        {"rfx": rfx, "suppliers": suppliers},
    )
