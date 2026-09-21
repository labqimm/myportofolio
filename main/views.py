from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from main.forms import EducationForm, ProjectForm
from main.models import Education, Experience, Project

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
        "educations": get_educations_from_json(request),
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

# ---------- Experience (JSON) ----------

def get_experience_json(request):
    """Mengembalikan seluruh data Experience dalam format JSON."""
    experience_json = serializers.serialize("json", Experience.objects.all())
    return HttpResponse(experience_json, content_type="application/json")


# ---------- Education (CRUD + JSON) ----------

def get_education_json(request):
    """Mengembalikan seluruh data Education dalam format JSON."""
    education_json = serializers.serialize("json", Education.objects.all())
    return HttpResponse(education_json, content_type="application/json")


def get_educations_from_json(request):
    """Mengambil JSON dari get_education_json lalu mengubahnya kembali menjadi objek Education."""
    json_response = get_education_json(request)
    educations = serializers.deserialize("json", json_response.content.decode("utf-8"))
    return [e.object for e in educations]


def create_education(request):
    form = EducationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Riwayat pendidikan berhasil ditambahkan!")
        return redirect("main:show_main")
    context = {
        "page_title": "Tambah Pendidikan",
        "submit_label": "Simpan Pendidikan",
        "form": form,
    }
    return render(request, "education_form.html", context)


def update_education(request, education_id):
    # 1. Ambil data lama berdasarkan id
    education = get_object_or_404(Education, pk=education_id)
    # 2. instance=education membuat form terisi data lama, dan save() akan mengubah data itu (bukan membuat baru)
    form = EducationForm(request.POST or None, instance=education)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Riwayat pendidikan berhasil diperbarui!")
        return redirect("main:show_main")
    context = {
        "page_title": "Edit Pendidikan",
        "submit_label": "Simpan Perubahan",
        "form": form,
    }
    return render(request, "education_form.html", context)


def delete_education(request, education_id):
    education = get_object_or_404(Education, pk=education_id)
    if request.method == "POST":
        education.delete()
        messages.success(request, "Riwayat pendidikan berhasil dihapus!")
    return redirect("main:show_main")