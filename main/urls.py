from django.urls import path
from main.views import (
    show_main, show_experience, project_list,
    create_project, get_projects_json, delete_project,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("projects/", project_list, name="project_list"),
    path("projects/add/", create_project, name="create_project"),
    path("api/projects/", get_projects_json, name="get_projects_json"),
    path("projects/<int:project_id>/delete/", delete_project, name="delete_project"),
]