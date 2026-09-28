from django.urls import path
from main.views import (
    show_main, show_experience, project_list,
    create_project, get_projects_json, delete_project,
    create_education, update_education, delete_education,
    get_education_json, get_experience_json,
    register, login_user, logout_user, toggle_star,
    toggle_education_star,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),

    # Autentikasi
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),

    # Projects
    path("projects/", project_list, name="project_list"),
    path("projects/add/", create_project, name="create_project"),
    path("projects/<int:project_id>/delete/", delete_project, name="delete_project"),
    path("projects/<int:project_id>/star/", toggle_star, name="toggle_star"),

    # Education
    path("education/add/", create_education, name="create_education"),
    path("education/<int:education_id>/edit/", update_education, name="update_education"),
    path("education/<int:education_id>/delete/", delete_education, name="delete_education"),
    path("education/<int:education_id>/star/", toggle_education_star, name="toggle_education_star"),

    # JSON API
    path("api/projects/", get_projects_json, name="get_projects_json"),
    path("api/education/", get_education_json, name="get_education_json"),
    path("api/experience/", get_experience_json, name="get_experience_json"),
]
