from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput, Textarea, URLInput, NumberInput, CheckboxInput
from django.utils.html import strip_tags
from main.models import Education, Project



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

    # clean_<field> dijalankan otomatis saat form.is_valid(); nilai kembaliannya yang disimpan.
    # Lapisan pertahanan kedua terhadap XSS: buang tag HTML sejak data masuk.
    def clean_title(self):
        title = strip_tags(self.cleaned_data["title"]).strip()
        if not title:
            raise ValidationError("Nama proyek tidak boleh hanya berisi tag HTML.")
        return title

    def clean_tech_stack(self):
        return strip_tags(self.cleaned_data["tech_stack"]).strip()

    def clean_description(self):
        return strip_tags(self.cleaned_data["description"]).strip()


class EducationForm(ModelForm):
    class Meta:
        model = Education
        fields = ["institution", "level", "major", "start_year", "end_year"]
        labels = {
            "institution": "Nama Institusi",
            "level": "Jenjang",
            "major": "Jurusan / Program Studi",
            "start_year": "Tahun Masuk",
            "end_year": "Tahun Lulus (kosongkan jika masih berjalan)",
        }
        widgets = {
            "institution": TextInput(attrs={"placeholder": "Universitas Indonesia", "maxlength": 150}),
            "major": TextInput(attrs={"placeholder": "S1 Ilmu Komputer"}),
            "start_year": NumberInput(attrs={"placeholder": "2025"}),
            "end_year": NumberInput(attrs={"placeholder": "2029"}),
        }

    def clean(self):
        """Tahun lulus tidak boleh lebih kecil dari tahun masuk."""
        cleaned_data = super().clean()
        start_year = cleaned_data.get("start_year")
        end_year = cleaned_data.get("end_year")
        if start_year and end_year and end_year < start_year:
            self.add_error("end_year", "Tahun lulus tidak boleh sebelum tahun masuk.")
        return cleaned_data
