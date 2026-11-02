from rest_framework.permissions import BasePermission, SAFE_METHODS

from main.roles import is_editor


class IsPortfolioOwnerOrReadOnly(BasePermission):
    """Semua orang boleh membaca; hanya pemilik (superuser) yang boleh menulis."""

    message = "Only the portfolio owner can change projects."

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_superuser
        )


class IsPortfolioOwnerOrEditorOrReadOnly(BasePermission):
    """Untuk bagian pilihan tugas (Education): Editor boleh PUT/PATCH, pemilik boleh semuanya."""

    message = "Only the portfolio owner or an editor can change this data."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        # is_editor dari main/roles.py (Tugas 4) = cek grup "Editor"
        return request.method in ("PUT", "PATCH") and is_editor(request.user)