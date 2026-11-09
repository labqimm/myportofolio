from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Education, Project


class ProjectSerializer(serializers.ModelSerializer):
    # Field hasil perhitungan: tidak ada di tabel, jadi otomatis read-only
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id", "title", "description", "tech_stack",
            "year", "repo_url", "is_featured",
            "star_count", "is_starred", "starred_by_names",
        ]
        read_only_fields = ["id"]

                # Pesan bawaan DRF berbahasa Inggris; diganti supaya toast di halaman mudah dipahami
        extra_kwargs = {
            "institution": {"error_messages": {
                "blank": "Nama institusi wajib diisi.", "required": "Nama institusi wajib diisi.",
            }},
            "level": {"error_messages": {"invalid_choice": "Jenjang \"{input}\" tidak tersedia."}},
            "start_year": {"error_messages": {
                "invalid": "Tahun masuk harus berupa angka.", "required": "Tahun masuk wajib diisi.",
                "null": "Tahun masuk wajib diisi.",
            }},
            "end_year": {"error_messages": {"invalid": "Tahun lulus harus berupa angka."}},
        }

    # validate_<field> = padanan clean_<field> di ProjectForm (serializer TIDAK menjalankan form)
    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Nama proyek tidak boleh kosong atau hanya berisi tag HTML.")
        return value

    def validate_description(self, value):
        return strip_tags(value).strip()

    def validate_tech_stack(self, value):
        return strip_tags(value).strip()

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

    def get_starred_by_names(self, obj):
        # Hanya username, bukan id/email user
        return ", ".join(user.username for user in obj.starred_by.all())


class EducationSerializer(serializers.ModelSerializer):
    """Serializer untuk bagian pilihan tugas (Education) - dipakai di Implementasi Peran Editor."""

    level_display = serializers.CharField(source="get_level_display", read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Education
        fields = [
            "id", "institution", "level", "level_display", "major",
            "start_year", "end_year", "is_ongoing",
            "star_count", "is_starred", "starred_by_names",
        ]
        read_only_fields = ["id"]

    def validate_institution(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Nama institusi tidak boleh kosong atau hanya berisi tag HTML.")
        return value

    def validate_major(self, value):
        return strip_tags(value).strip()

    def validate(self, attrs):
        # Padanan EducationForm.clean(): cek dua field sekaligus.
        # Saat PATCH, field yang tidak dikirim diambil dari data lama (self.instance).
        start_year = attrs.get("start_year", getattr(self.instance, "start_year", None))
        end_year = attrs.get("end_year", getattr(self.instance, "end_year", None))
        if start_year and end_year and end_year < start_year:
            raise serializers.ValidationError({"end_year": "Tahun lulus tidak boleh sebelum tahun masuk."})
        return attrs

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())


class EducationQuerySerializer(serializers.Serializer):
    """Fitur ekstra Tugas 6: memvalidasi parameter query endpoint daftar Education.

    Contoh: /api/v1/education/?q=indonesia&level=s1&ordering=-start_year
    Nilai yang tidak dikenal (mis. level=s9) ditolak dengan 400, sama seperti input POST.
    """

    ORDERING_CHOICES = [
        ("-start_year", "Terbaru"),
        ("start_year", "Terlama"),
        ("institution", "Nama A-Z"),
        ("-institution", "Nama Z-A"),
    ]

    q = serializers.CharField(required=False, allow_blank=True, default="")
    level = serializers.ChoiceField(
        choices=Education.LEVEL_CHOICES, required=False, allow_blank=True, default="",
        error_messages={"invalid_choice": "Jenjang \"{input}\" tidak tersedia."},
    )
    ordering = serializers.ChoiceField(
        choices=ORDERING_CHOICES, required=False, allow_blank=True, default="-start_year",
        error_messages={"invalid_choice": "Urutan \"{input}\" tidak tersedia."},
    )