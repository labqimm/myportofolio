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
    """Hak akses bagian Education (Tugas 6), sama dengan empat peran Tugas 4.

    - Pengunjung & pengguna biasa : hanya GET/HEAD/OPTIONS (SAFE_METHODS).
    - Editor (grup "Editor")      : + PUT/PATCH, tetapi tidak boleh POST/DELETE.
    - Pemilik (superuser)         : semua method.
    Star tidak memakai class ini, tetapi IsAuthenticated di view education_star.
    """

    message = "Hanya pemilik portofolio yang dapat menambah atau menghapus data; Editor hanya dapat mengubahnya."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        # is_editor dari main/roles.py (Tugas 4) = cek grup "Editor"
        return request.method in ("PUT", "PATCH") and is_editor(request.user)