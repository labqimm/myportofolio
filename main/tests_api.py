from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Education, Project


class ProjectAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.visitor = User.objects.create_user(username="visitor", password="test-password")
        self.project = Project.objects.create(
            title="Portfolio", description="My website", tech_stack="Django", year=2026,
        )
        self.list_url = reverse("api:project-list")
        self.detail_url = reverse("api:project-detail", args=[self.project.id])
        self.star_url = reverse("api:project-star", args=[self.project.id])
        self.payload = {
            "title": "New project", "description": "A useful app", "tech_stack": "Python",
            "year": 2026, "repo_url": "https://example.com/", "is_featured": False,
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], self.project.id)
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("fields", response.data[0])
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"title": "PORT"})
        self.assertEqual(len(response.data), 1)
        response = self.client.get(self.list_url, {"title": "not-found"})
        self.assertEqual(response.data, [])

    def test_missing_project(self):
        url = reverse("api:project-detail", args=[999999])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Project.objects.count(), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Portfolio")

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(pk=response.data["id"]).exists())

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"repo_url": "javascript:alert(1)"}, "repo_url"),
            ({"year": "bukan-angka"}, "year"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)
        self.assertEqual(Project.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.description, "My website")
        response = self.client.put(self.detail_url, {"title": "Incomplete"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True,
            "starred_by_names": "forged", "starred_by": [self.visitor.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])

    def test_staff_and_editor_cannot_manage_tutorial_projects(self):
        self.visitor.is_staff = True
        self.visitor.save()
        # Grup Editor sudah dibuat migrasi 0005 -> get_or_create, bukan create (bisa IntegrityError)
        editor_group, _ = Group.objects.get_or_create(name="Editor")
        self.visitor.groups.add(editor_group)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(self.list_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password="test-password")
        # The Browsable API form renders a real CSRF token into the response.
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class EducationAPITest(APITestCase):
    """Tugas 6: API Education untuk keempat peran (pengunjung, pengguna biasa, Editor, pemilik)."""

    password = "test-password"

    def setUp(self):
        self.owner = User.objects.create_superuser(username="owner", password=self.password)
        self.user = User.objects.create_user(username="visitor", password=self.password)
        self.editor = User.objects.create_user(username="editor", password=self.password)
        # Grup "Editor" sudah dibuat migrasi 0005 (database test ikut menjalankan migrasi),
        # jadi pakai get_or_create; Group.objects.create akan gagal karena nama grup unik.
        editor_group, _ = Group.objects.get_or_create(name="Editor")
        self.editor.groups.add(editor_group)

        self.education = Education.objects.create(
            institution="Universitas Indonesia", level="s1", major="Ilmu Komputer", start_year=2025,
        )
        self.list_url = reverse("api:education-list")
        self.detail_url = reverse("api:education-detail", args=[self.education.id])
        self.star_url = reverse("api:education-star", args=[self.education.id])
        self.payload = {
            "institution": "SMA Negeri 8", "level": "sma", "major": "IPA",
            "start_year": 2022, "end_year": 2025,
        }

    def assert_education_unchanged(self):
        """Memeriksa isi database, bukan hanya status HTTP."""
        self.assertEqual(Education.objects.count(), 1)
        self.education.refresh_from_db()
        self.assertEqual(self.education.institution, "Universitas Indonesia")
        self.assertEqual(self.education.major, "Ilmu Komputer")

    # ---------- Membaca ----------

    def test_everyone_can_read_list_and_detail(self):
        for user in (None, self.user, self.editor, self.owner):
            self.client.force_authenticate(user=user)
            response = self.client.get(self.list_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data[0]["institution"], "Universitas Indonesia")
            self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_response_fields_and_no_sensitive_data(self):
        self.education.starred_by.add(self.user)
        data = self.client.get(self.detail_url).data
        self.assertEqual(data["star_count"], 1)
        self.assertEqual(data["starred_by_names"], "visitor")
        self.assertEqual(data["level_display"], "S1")
        self.assertTrue(data["is_ongoing"])
        for sensitive in ("starred_by", "email", "password"):
            self.assertNotIn(sensitive, data)

    def test_search_with_query_param(self):
        Education.objects.create(institution="SMA Negeri 11 Bekasi", level="sma", major="IPA", start_year=2022)
        by_institution = [e["institution"] for e in self.client.get(self.list_url, {"q": "bekasi"}).data]
        by_major = [e["institution"] for e in self.client.get(self.list_url, {"q": "KOMPUTER"}).data]
        self.assertEqual(by_institution, ["SMA Negeri 11 Bekasi"])
        self.assertEqual(by_major, ["Universitas Indonesia"])
        self.assertEqual(self.client.get(self.list_url, {"q": "tidak-ada"}).data, [])

        # ---------- Fitur ekstra: filter jenjang & urutan ----------

    def test_filter_by_level_and_ordering(self):
        Education.objects.create(institution="SMA Negeri 11 Bekasi", level="sma", start_year=2022)
        Education.objects.create(institution="Akademi Contoh", level="s1", start_year=2019)
        names = lambda params: [e["institution"] for e in self.client.get(self.list_url, params).data]

        self.assertEqual(names({"level": "sma"}), ["SMA Negeri 11 Bekasi"])
        self.assertEqual(names({"level": "s1"}), ["Universitas Indonesia", "Akademi Contoh"])  # default terbaru
        self.assertEqual(names({"level": "s1", "ordering": "start_year"}), ["Akademi Contoh", "Universitas Indonesia"])
        self.assertEqual(
            names({"ordering": "institution"}),
            ["Akademi Contoh", "SMA Negeri 11 Bekasi", "Universitas Indonesia"],
        )
        self.assertEqual(names({"q": "contoh", "level": "s1"}), ["Akademi Contoh"])
        self.assertEqual(names({"level": "s2"}), [])

    def test_invalid_filter_returns_400(self):
        for params, field in [({"level": "s9"}, "level"), ({"ordering": "password"}, "ordering")]:
            response = self.client.get(self.list_url, params)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)

    def test_main_page_renders_filter_controls(self):
        response = self.client.get(reverse("main:show_main"))
        self.assertContains(response, 'id="education-level-filter"')
        self.assertContains(response, '<option value="sma">SMA/SMK</option>', html=True)
        self.assertContains(response, '<option value="-start_year">Terbaru</option>', html=True)
        
    def test_missing_education_returns_404(self):
        url = reverse("api:education-detail", args=[999999])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_404_NOT_FOUND)

    # ---------- Hak akses menulis ----------

    def test_guest_and_regular_user_cannot_write(self):
        for user in (None, self.user):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"major": "X"}, format="json").status_code, 403)
            self.assertEqual(self.client.put(self.detail_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assert_education_unchanged()

    def test_editor_can_patch_and_put(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.patch(self.detail_url, {"major": "Sistem Informasi"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.education.refresh_from_db()
        self.assertEqual(self.education.major, "Sistem Informasi")
        self.assertEqual(self.education.institution, "Universitas Indonesia")  # PATCH: field lain tetap

        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.education.refresh_from_db()
        self.assertEqual(self.education.institution, "SMA Negeri 8")
        self.assertEqual(Education.objects.count(), 1)  # diubah, bukan ditambah

    def test_editor_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)
        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assert_education_unchanged()

    def test_owner_can_create_update_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Education.objects.filter(pk=response.data["id"], institution="SMA Negeri 8").exists())

        response = self.client.patch(self.detail_url, {"end_year": 2029}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.education.refresh_from_db()
        self.assertEqual(self.education.end_year, 2029)

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Education.objects.filter(pk=self.education.id).exists())

    # ---------- Validasi ----------

    def test_invalid_input_returns_400(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"institution": "   "}, "institution"),
            ({"institution": "<b></b>"}, "institution"),
            ({"level": "s9"}, "level"),
            ({"start_year": "bukan-angka"}, "start_year"),
            ({"end_year": 2020}, "end_year"),  # sebelum start_year 2022
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, changes)
            self.assertIn(field, response.data)
        self.assertEqual(Education.objects.count(), 1)

    def test_patch_end_year_checks_existing_start_year(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.patch(self.detail_url, {"end_year": 2000}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.education.refresh_from_db()
        self.assertIsNone(self.education.end_year)

    def test_html_tags_are_stripped(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "institution": "<script>alert(1)</script>SMA 8", "major": "<b>IPA</b>",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Education.objects.get(pk=response.data["id"])
        self.assertEqual(created.institution, "alert(1)SMA 8")
        self.assertEqual(created.major, "IPA")

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True,
            "starred_by_names": "forged", "starred_by": [self.user.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(Education.objects.get(pk=response.data["id"]).starred_by.exists())

    # ---------- Star ----------

    def test_guest_cannot_star(self):
        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.education.starred_by.count(), 0)

    def test_star_toggles_for_request_user_only(self):
        self.client.force_authenticate(user=self.user)
        # Field "user" di body diabaikan: pemberi star selalu request.user
        response = self.client.post(self.star_url, {"user": self.owner.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        self.assertEqual(list(self.education.starred_by.all()), [self.user])

        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(self.education.starred_by.count(), 0)

    def test_star_only_allows_post(self):
        self.client.force_authenticate(user=self.user)
        self.assertEqual(self.client.get(self.star_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # ---------- CSRF (wajib memakai .login(), bukan force_authenticate) ----------

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password=self.password))
        self.assertEqual(client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(client.delete(self.detail_url).status_code, 403)
        self.assertEqual(client.post(self.star_url).status_code, 403)
        self.assert_education_unchanged()
        self.assertEqual(self.education.starred_by.count(), 0)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="editor", password=self.password)
        # Halaman utama memuat {% csrf_token %} -> cookie csrftoken dibuat, sama seperti di browser
        client.get(reverse("main:show_main"))
        token = client.cookies["csrftoken"].value
        response = client.patch(
            self.detail_url, {"major": "Sistem Informasi"}, format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.education.refresh_from_db()
        self.assertEqual(self.education.major, "Sistem Informasi")