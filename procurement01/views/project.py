from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import ProjectForm
from ..models import RFX, Project


@login_required
def project_list_view(request):
    user_company = request.user.company
    projects = Project.objects.filter(company=user_company)
    return render(request, "procurement01/project_list.html", {"projects": projects})


@login_required
def create_project(request):
    if not request.user.company:
        return HttpResponseForbidden(
            "You must belong to a company to create a project."
        )

    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.company = request.user.company
            project.save()
            return redirect("project_detail", project_id=project.id)
    else:
        form = ProjectForm()

    return render(request, "procurement01/create_project.html", {"form": form})


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id, company=request.user.company)
    rfxs = RFX.objects.filter(project=project)
    return render(
        request, "procurement01/project_detail.html", {"project": project, "rfxs": rfxs}
    )
