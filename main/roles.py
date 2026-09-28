"""Aturan peran (role) portofolio yang dipakai bersama oleh views dan template.

Empat peran pada Tugas 4:
- Pengunjung (belum login): hanya membaca.
- Pengguna biasa: membaca + memberi/membatalkan star.
- Editor (anggota grup "Editor"): hak pengguna biasa + mengubah data.
- Pemilik (superuser): membuat, mengubah, dan menghapus data.
"""

EDITOR_GROUP_NAME = "Editor"


def is_editor(user):
    """True kalau akun sudah login dan tergabung di grup Editor (diatur lewat Django Admin)."""
    return user.is_authenticated and user.groups.filter(name=EDITOR_GROUP_NAME).exists()


def can_edit(user):
    """Boleh mengubah data: pemilik portofolio atau editor."""
    return user.is_superuser or is_editor(user)
