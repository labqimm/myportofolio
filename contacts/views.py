from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, QueryDict
from django.views.decorators.http import require_http_methods
from .models import Contact


# Halaman utama: tampilkan semua kontak
def contact_list(request):
    contacts = Contact.objects.all()
    return render(request, "contacts/contacts_index.html", {"contacts": contacts})


# Tambah kontak -> kembalikan semua baris tabel
def contact_add(request):
    if request.method == "POST":
        Contact.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
        )
    contacts = Contact.objects.all()
    return render(request, "contacts/_contact_rows.html", {"contacts": contacts})


# Hapus kontak -> kembalikan string kosong (baris hilang)
@require_http_methods(["DELETE"])
def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    contact.delete()
    return HttpResponse("")


# Cari kontak -> kembalikan baris hasil filter
def contact_search(request):
    query = request.GET.get("q", "")
    contacts = Contact.objects.filter(name__icontains=query) if query else Contact.objects.all()
    return render(request, "contacts/_contact_rows.html", {"contacts": contacts})


# Tombol Edit -> kembalikan baris versi form
def contact_edit(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    return render(request, "contacts/_contact_edit_row.html", {"contact": contact})


# Tombol Batal -> kembalikan baris versi tampilan
def contact_row(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    return render(request, "contacts/_contact_row.html", {"contact": contact})


# Tombol Simpan -> simpan data, kembalikan baris versi tampilan
@require_http_methods(["PUT"])
def contact_update(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    data = QueryDict(request.body)
    contact.name = data.get("name", contact.name)
    contact.email = data.get("email", contact.email)
    contact.save()
    return render(request, "contacts/_contact_row.html", {"contact": contact})