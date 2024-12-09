from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from ...forms import RFXBasicForm
from ...models import RFX, Project, RFXFile


@login_required
def create_rfx_step1(request, rfx_id=None):
    user_company = request.user.company

    if rfx_id:
        rfx = get_object_or_404(RFX, id=rfx_id)
        existing_files = rfx.files.all()
    else:
        rfx = None
        existing_files = None

    project_id = request.GET.get("project_id")
    initial_data = {"company": user_company}

    if project_id:
        try:
            initial_project = Project.objects.get(
                id=project_id, company=request.user.company
            )
            initial_data["project"] = initial_project
        except Project.DoesNotExist:
            pass

    if request.method == "POST":
        with transaction.atomic():
            if rfx:
                form = RFXBasicForm(
                    request.POST,
                    request.FILES,
                    instance=rfx,
                    user=request.user,
                    initial=initial_data,
                )
            else:
                form = RFXBasicForm(
                    request.POST, request.FILES, user=request.user, initial=initial_data
                )

            if form.is_valid():
                rfx = form.save(commit=False)
                rfx.company = user_company
                rfx.save()

                files_to_delete = request.POST.getlist("delete_files")
                if files_to_delete:
                    RFXFile.objects.filter(id__in=files_to_delete, rfx=rfx).delete()

                for file in request.FILES.getlist("new_files"):
                    RFXFile.objects.create(rfx=rfx, file=file)

                return redirect("create_rfx_step2", rfx_id=rfx.id)
    else:
        if rfx:
            form = RFXBasicForm(instance=rfx, user=request.user, initial=initial_data)
            existing_files = rfx.files.all()
        else:
            form = RFXBasicForm(user=request.user, initial=initial_data)
            existing_files = None

    return render(
        request,
        "procurement01/create_rfx_step1.html",
        {
            "form": form,
            "existing_files": existing_files,
            "rfx": rfx,
        },
    )
