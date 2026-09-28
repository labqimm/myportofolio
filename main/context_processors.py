from main.roles import can_edit, is_editor


def roles(request):
    """Menyediakan is_editor dan can_edit ke semua template tanpa dikirim manual dari tiap view."""
    return {
        "is_editor": is_editor(request.user),
        "can_edit": can_edit(request.user),
    }
