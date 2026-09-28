import datetime

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from main.forms import EducationForm, ProjectForm
from main.models import Education, Experience, Project
from main.roles import can_edit

def show_main(request):
    # .get() dengan nilai default supaya tidak KeyError kalau cookie belum ada
    last_login = request.COOKIES.get("last_login", "Belum ada sesi login / Cookie tidak ditemukan")
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
        "last_login": last_login,
    }
    return render(request, "index.html", context)


# ---------- Autentikasi (Tutorial 04) ----------

def register(request):
    """Menampilkan form daftar akun; akun baru disimpan dengan password yang sudah di-hash."""
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": "Muhammad Iqbal",
        "form": form,
    }
    return render(request, "register.html", context)


def login_user(request):
    """Memeriksa username & password, lalu mencatat pengguna ke session."""
    form = AuthenticationForm(request, data=request.POST or None)
    # ?next= diisi otomatis oleh @login_required (mis. /login/?next=/projects/add/)
    next_url = request.POST.get("next") or request.GET.get("next", "")

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)

        # Hanya ikuti next kalau alamatnya masih di website ini (mencegah open redirect)
        if not url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
        ):
            next_url = reverse("main:show_main")

        # Simpan waktu login terakhir di cookie browser (Tutorial 04 Bagian 2)
        response = redirect(next_url)
        response.set_cookie("last_login", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return response

    context = {
        "name": "Muhammad Iqbal",
        "form": form,
        "next": next_url,
    }
    return render(request, "login.html", context)


def logout_user(request):
    """Menghapus session pengguna; akunnya tetap ada di database."""
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie("last_login")
    return response


def show_experience(request):
    context = {
        "name": "Muhammad Iqbal",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)


@login_required(login_url="/login/")
def create_project(request):
    # Hanya pemilik portofolio (superuser) yang boleh menambah proyek -> selain itu 403
    if not request.user.is_superuser:
        raise PermissionDenied

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
    # use_natural_foreign_keys: starred_by tampil sebagai username, bukan id internal database
    projects_json = serializers.serialize("json", projects, use_natural_foreign_keys=True)
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


@login_required(login_url="/login/")
def delete_project(request, project_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        project.delete()
        messages.success(request, "Project berhasil dihapus!")
    return redirect("main:project_list")

# Tanpa cek is_superuser: semua akun yang sudah login boleh memberi star
@login_required(login_url="/login/")
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        # Kalau akun ini sudah pernah memberi star, batalkan star-nya. Kalau belum, tambahkan.
        if project.starred_by.filter(pk=request.user.pk).exists():
            project.starred_by.remove(request.user)
        else:
            project.starred_by.add(request.user)

    return redirect("main:project_list")

# ---------- Experience (JSON) ----------

def get_experience_json(request):
    """Mengembalikan seluruh data Experience dalam format JSON."""
    experience_json = serializers.serialize("json", Experience.objects.all())
    return HttpResponse(experience_json, content_type="application/json")


# ---------- Education (CRUD + JSON) ----------

def get_education_json(request):
    """Mengembalikan seluruh data Education dalam format JSON."""
    # Natural key: starred_by berisi username, bukan id internal user
    education_json = serializers.serialize(
        "json", Education.objects.all(), use_natural_foreign_keys=True
    )
    return HttpResponse(education_json, content_type="application/json")


def get_educations_from_json(request):
    """Mengambil JSON dari get_education_json lalu mengubahnya kembali menjadi objek Education."""
    json_response = get_education_json(request)
    educations = serializers.deserialize("json", json_response.content.decode("utf-8"))
    return [e.object for e in educations]


@login_required(login_url="/login/")
def create_education(request):
    # Membuat data baru hanya untuk pemilik portofolio
    if not request.user.is_superuser:
        raise PermissionDenied

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


@login_required(login_url="/login/")
def update_education(request, education_id):
    # Mengubah data boleh untuk pemilik dan editor
    if not can_edit(request.user):
        raise PermissionDenied

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


@login_required(login_url="/login/")
def delete_education(request, education_id):
    # Menghapus data hanya untuk pemilik portofolio (editor tidak boleh)
    if not request.user.is_superuser:
        raise PermissionDenied

    education = get_object_or_404(Education, pk=education_id)
    if request.method == "POST":
        education.delete()
        messages.success(request, "Riwayat pendidikan berhasil dihapus!")
    return redirect("main:show_main")


# Semua akun yang sudah login boleh memberi star (maksimal satu star per akun)
@login_required(login_url="/login/")
def toggle_education_star(request, education_id):
    education = get_object_or_404(Education, pk=education_id)

    if request.method == "POST":
        if education.starred_by.filter(pk=request.user.pk).exists():
            education.starred_by.remove(request.user)
        else:
            education.starred_by.add(request.user)

    # Kembali ke bagian Education di halaman utama
    return redirect(reverse("main:show_main") + "#education")
