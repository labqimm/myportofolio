from django.contrib import admin
from main.models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'year', 'is_featured')
    list_filter = ('is_featured',)
    search_fields = ('title', 'tech_stack')