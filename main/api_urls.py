from django.urls import path
from rest_framework.authtoken import views as authtoken_views

from main import api_views

app_name = "api"

urlpatterns = [
    # Autentikasi token untuk aplikasi Flutter (Tutorial 10)
    path("auth/token/", authtoken_views.obtain_auth_token, name="api_token_auth"),
    path("auth/logout/", api_views.api_logout, name="api_logout"),

    # Projects (contoh tutorial)
    path("projects/", api_views.project_list, name="project-list"),
    path("projects/<int:project_id>/", api_views.project_detail, name="project-detail"),
    path("projects/<int:project_id>/star/", api_views.project_star, name="project-star"),

    # Education (bagian pilihan tugas)
    path("education/", api_views.education_list, name="education-list"),
    path("education/<int:education_id>/", api_views.education_detail, name="education-detail"),
    path("education/<int:education_id>/star/", api_views.education_star, name="education-star"),
]