from django.contrib import admin
from main.models import Education, Experience, Project


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'started_at', 'ended_at')
    list_filter = ('category',)
    search_fields = ('title', 'description')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'year', 'is_featured')
    list_filter = ('is_featured',)
    search_fields = ('title', 'tech_stack')


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('institution', 'level', 'start_year', 'end_year')
    list_filter = ('level',)
    search_fields = ('institution', 'major')