from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from main.forms import ProjectForm
from main.models import Experience, Project


def show_main(request):
    context = {
        "name": "Muhammad Iqbal",
        "npm": "2506657075",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "CS student at Universitas Indonesia for longer than planned, "
            "now a familiar (and slightly dreaded) face among Fasilkom "
            "students as a teaching assistant across several courses."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Muhammad Iqbal",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)


def create_project(request):
    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:project_list")
    context = {
        "page_title": "Tambah Project",
        "form": form,
    }
    return render(request, "project_form.html", context)


def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()
    if title_query:
        projects = projects.filter(title__icontains=title_query)
    projects_json = serializers.serialize("json", projects)
    return HttpResponse(projects_json, content_type="application/json")


def project_list(request):
    json_response = get_projects_json(request)
    projects = serializers.deserialize("json", json_response.content.decode("utf-8"))
    projects = [p.object for p in projects]
    title_query = request.GET.get("title", "").strip()
    context = {
        "page_title": "Projects",
        "projects": projects,
        "title_query": title_query,
    }
    return render(request, "project_list.html", context)


def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        project.delete()
        messages.success(request, "Project berhasil dihapus!")
    return redirect("main:project_list")