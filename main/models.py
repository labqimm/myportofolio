import uuid
from django.db import models

class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ('internship', 'Internship'),
        ('research', 'Research'),
        ('volunteer', 'Volunteer'),
        ('part-time', 'Part-Time'),
        ('full-time', 'Full-Time'),
        ('freelance', 'Freelance'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='full-time')
    thumbnail = models.URLField(blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title

    @property
    def is_ongoing(self):
        return self.ended_at is None

class Project(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField()
    tech_stack = models.CharField(max_length=200)
    year = models.PositiveIntegerField()
    repo_url = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-year', 'title']

    def __str__(self):
        return self.title


class Education(models.Model):
    """Satu riwayat pendidikan yang tampil di timeline halaman utama."""

    LEVEL_CHOICES = [
        ('sd', 'SD'),
        ('smp', 'SMP'),
        ('sma', 'SMA/SMK'),
        ('d3', 'D3'),
        ('s1', 'S1'),
        ('s2', 'S2'),
    ]

    institution = models.CharField(max_length=150)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='s1')
    major = models.CharField(max_length=100, blank=True)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_year']

    def __str__(self):
        return self.institution

    @property
    def is_ongoing(self):
        """Pendidikan dianggap masih berjalan kalau tahun selesai belum diisi."""
        return self.end_year is None