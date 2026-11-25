from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Education, Project
from main.permissions import IsPortfolioOwnerOrEditorOrReadOnly, IsPortfolioOwnerOrReadOnly
from main.serializers import EducationQuerySerializer, EducationSerializer, ProjectSerializer


# Tutorial 10: decorator @authentication_classes([SessionAuthentication]) dihapus dari
# semua view, supaya REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] di settings.py
# (TokenAuthentication lalu SessionAuthentication) berlaku. Kalau decorator lama dibiarkan,
# header "Authorization: Token <key>" dari Flutter diabaikan dan POST ditolak 403.


# ======================== AUTH (Tutorial 10) ========================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_logout(request):
    """Mencabut token milik pemanggil. Login-nya memakai obtain_auth_token bawaan DRF."""
    # request.auth berisi objek Token kalau user masuk lewat TokenAuthentication,
    # dan None kalau lewat SessionAuthentication (browser) -> tidak ada yang dihapus.
    if request.auth is not None:
        request.auth.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ======================== PROJECTS ========================

@api_view(["GET", "HEAD", "POST"])
@permission_classes([IsPortfolioOwnerOrReadOnly])
def project_list(request):
    if request.method in ("GET", "HEAD"):
        projects = Project.objects.prefetch_related("starred_by").order_by("-year", "title", "id")
        title = request.query_params.get("title", "").strip()
        if title:
            projects = projects.filter(title__icontains=title)
        serializer = ProjectSerializer(projects, many=True, context={"request": request})
        return Response(serializer.data)

    serializer = ProjectSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@permission_classes([IsPortfolioOwnerOrReadOnly])
def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.prefetch_related("starred_by"), pk=project_id,
    )
    if request.method in ("GET", "HEAD"):
        serializer = ProjectSerializer(project, context={"request": request})
        return Response(serializer.data)

    if request.method == "DELETE":
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = ProjectSerializer(
        project, data=request.data, partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def project_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.starred_by.filter(pk=request.user.pk).exists():
        project.starred_by.remove(request.user)
    else:
        project.starred_by.add(request.user)
    serializer = ProjectSerializer(project, context={"request": request})
    return Response(serializer.data)


# ============ EDUCATION (bagian pilihan tugas, peran Editor) ============

@api_view(["GET", "HEAD", "POST"])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def education_list(request):
    if request.method in ("GET", "HEAD"):
        # Parameter query divalidasi serializer juga (bukan di view) -> nilai aneh langsung 400
        params = EducationQuerySerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        filters = params.validated_data

        educations = Education.objects.prefetch_related("starred_by")
        if filters["q"]:
            educations = educations.filter(
                Q(institution__icontains=filters["q"]) | Q(major__icontains=filters["q"])
            )
        if filters["level"]:
            educations = educations.filter(level=filters["level"])
        # "id" sebagai urutan kedua supaya hasilnya stabil kalau nilainya sama
        educations = educations.order_by(filters["ordering"] or "-start_year", "id")
        serializer = EducationSerializer(educations, many=True, context={"request": request})
        return Response(serializer.data)

    serializer = EducationSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def education_detail(request, education_id):
    education = get_object_or_404(
        Education.objects.prefetch_related("starred_by"), pk=education_id,
    )
    if request.method in ("GET", "HEAD"):
        serializer = EducationSerializer(education, context={"request": request})
        return Response(serializer.data)

    if request.method == "DELETE":
        education.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = EducationSerializer(
        education, data=request.data, partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def education_star(request, education_id):
    education = get_object_or_404(Education, pk=education_id)
    if education.starred_by.filter(pk=request.user.pk).exists():
        education.starred_by.remove(request.user)
    else:
        education.starred_by.add(request.user)
    serializer = EducationSerializer(education, context={"request": request})
    return Response(serializer.data)