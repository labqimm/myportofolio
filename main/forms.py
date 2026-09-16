from django.forms import ModelForm, TextInput, Textarea, URLInput, NumberInput, CheckboxInput
from main.models import Project

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ["title", "description", "tech_stack", "year", "repo_url", "is_featured"]
        labels = {
            "title": "Nama Proyek",
            "description": "Deskripsi Proyek",
            "tech_stack": "Teknologi yang Digunakan",
            "year": "Tahun",
            "repo_url": "URL Repository",
            "is_featured": "Proyek Unggulan?",
        }
        widgets = {
            "title": TextInput(attrs={"placeholder": "Portfolio Website", "maxlength": 120}),
            "description": Textarea(attrs={"placeholder": "Ceritakan proyekmu", "rows": 3}),
            "tech_stack": TextInput(attrs={"placeholder": "Django, Python, HTML, CSS"}),
            "year": NumberInput(attrs={"placeholder": "2026"}),
            "repo_url": URLInput(attrs={"placeholder": "https://github.com/labqimm/..."}),
            "is_featured": CheckboxInput(),
        }