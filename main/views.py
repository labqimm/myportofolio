from django.shortcuts import render
from main.models import Experience

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