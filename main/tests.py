import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Education, Experience, Project


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Staff Akademi Profesi",
            description="Membantu akademik dan persiapan karir mahasiswa Fasilkom UI.",
            category="volunteer",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")
        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Staff Akademi Profesi")
        self.assertEqual(self.experience.category, "volunteer")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Volunteer")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))
        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))
        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")


class ProjectListViewTest(TestCase):
    url = reverse('main:project_list')

    def test_url_accessible_and_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'project_list.html')

    def test_existing_projects_are_rendered(self):
        Project.objects.create(
            title='Sistem Absensi Kelas',
            description='Aplikasi pencatatan kehadiran berbasis web.',
            tech_stack='Django, PostgreSQL',
            year=2026,
        )
        response = self.client.get(self.url)
        self.assertContains(response, 'Sistem Absensi Kelas')
        self.assertContains(response, 'Django, PostgreSQL')

    def test_empty_state_is_shown_when_no_projects(self):
        self.assertEqual(Project.objects.count(), 0)
        response = self.client.get(self.url)
        self.assertContains(response, 'Belum ada proyek yang ditambahkan.')


class EducationCrudTest(TestCase):
    def setUp(self):
        self.education = Education.objects.create(
            institution="Universitas Indonesia",
            level="s1",
            major="S1 Ilmu Komputer",
            start_year=2025,
        )

    def test_education_shown_on_main_page(self):
        response = self.client.get(reverse("main:show_main"))
        self.assertContains(response, "Universitas Indonesia")
        self.assertContains(response, "sekarang")

    def test_create_education(self):
        response = self.client.post(reverse("main:create_education"), {
            "institution": "SMA Negeri 11 Kota Bekasi",
            "level": "sma",
            "major": "Jurusan IPA",
            "start_year": 2022,
            "end_year": 2025,
        })
        self.assertRedirects(response, reverse("main:show_main"))
        self.assertTrue(Education.objects.filter(institution="SMA Negeri 11 Kota Bekasi").exists())

    def test_update_education(self):
        url = reverse("main:update_education", args=[self.education.id])
        # Halaman edit terisi data lama
        self.assertContains(self.client.get(url), "Universitas Indonesia")
        self.client.post(url, {
            "institution": "Universitas Indonesia",
            "level": "s1",
            "major": "S1 Sistem Informasi",
            "start_year": 2025,
            "end_year": 2029,
        })
        self.education.refresh_from_db()
        self.assertEqual(self.education.major, "S1 Sistem Informasi")
        self.assertEqual(Education.objects.count(), 1)  # diubah, bukan ditambah

    def test_end_year_before_start_year_is_rejected(self):
        response = self.client.post(reverse("main:create_education"), {
            "institution": "Tes", "level": "s1", "start_year": 2025, "end_year": 2020,
        })
        self.assertContains(response, "Tahun lulus tidak boleh sebelum tahun masuk.")

    def test_delete_education(self):
        self.client.post(reverse("main:delete_education", args=[self.education.id]))
        self.assertFalse(Education.objects.exists())

    def test_delete_with_get_does_nothing(self):
        self.client.get(reverse("main:delete_education", args=[self.education.id]))
        self.assertTrue(Education.objects.exists())

    def test_education_json(self):
        response = self.client.get(reverse("main:get_education_json"))
        self.assertEqual(response["Content-Type"], "application/json")
        data = json.loads(response.content)
        self.assertEqual(data[0]["fields"]["institution"], "Universitas Indonesia")

    def test_experience_json(self):
        response = self.client.get(reverse("main:get_experience_json"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), [])

# ---------- Tutorial 04: Autentikasi, Cookie, dan Otorisasi ----------

class AuthFlowTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="sasha", password="RahasiaKuat123")

    def test_register_creates_account_and_redirects_to_login(self):
        response = self.client.post(reverse("main:register"), {
            "username": "rian",
            "password1": "RahasiaKuat123",
            "password2": "RahasiaKuat123",
        })
        self.assertRedirects(response, reverse("main:login"))
        self.assertTrue(User.objects.filter(username="rian").exists())

    def test_register_rejects_mismatched_passwords(self):
        response = self.client.post(reverse("main:register"), {
            "username": "rian",
            "password1": "RahasiaKuat123",
            "password2": "BedaPassword123",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="rian").exists())

    def test_login_sets_session_and_last_login_cookie(self):
        response = self.client.post(reverse("main:login"), {
            "username": "sasha", "password": "RahasiaKuat123",
        })
        self.assertRedirects(response, reverse("main:show_main"))
        self.assertIn("last_login", response.cookies)
        self.assertIn("_auth_user_id", self.client.session)

    def test_wrong_password_shows_error(self):
        response = self.client.post(reverse("main:login"), {
            "username": "sasha", "password": "salah",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form-error")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_navbar_shows_username_after_login(self):
        self.client.login(username="sasha", password="RahasiaKuat123")
        response = self.client.get(reverse("main:show_main"))
        self.assertContains(response, '<span class="nav-user">sasha</span>', html=True)
        self.assertContains(response, reverse("main:logout"))

    def test_navbar_shows_login_links_for_visitor(self):
        response = self.client.get(reverse("main:show_main"))
        self.assertContains(response, reverse("main:login"))
        self.assertContains(response, reverse("main:register"))

    def test_logout_clears_session_and_cookie(self):
        self.client.login(username="sasha", password="RahasiaKuat123")
        response = self.client.get(reverse("main:logout"))
        self.assertRedirects(response, reverse("main:show_main"))
        self.assertEqual(response.cookies["last_login"].value, "")
        self.assertNotIn("_auth_user_id", self.client.session)


class ProjectAuthorizationTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(username="owner", password="RahasiaKuat123")
        self.user = User.objects.create_user(username="sasha", password="RahasiaKuat123")
        self.project = Project.objects.create(
            title="Burhan Quest", description="Game Java.", tech_stack="Java, JUnit", year=2026,
        )

    def test_visitor_is_redirected_to_login(self):
        response = self.client.get(reverse("main:create_project"))
        self.assertRedirects(response, "/login/?next=/projects/add/", fetch_redirect_response=False)

    def test_regular_user_gets_403_on_create_and_delete(self):
        self.client.login(username="sasha", password="RahasiaKuat123")
        self.assertEqual(self.client.get(reverse("main:create_project")).status_code, 403)
        response = self.client.post(reverse("main:delete_project", args=[self.project.id]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Project.objects.exists())

    def test_owner_can_create_and_delete(self):
        self.client.login(username="owner", password="RahasiaKuat123")
        self.assertEqual(self.client.get(reverse("main:create_project")).status_code, 200)
        self.client.post(reverse("main:delete_project", args=[self.project.id]))
        self.assertFalse(Project.objects.exists())

    def test_controls_hidden_for_regular_user(self):
        self.client.login(username="sasha", password="RahasiaKuat123")
        response = self.client.get(reverse("main:project_list"))
        self.assertNotContains(response, "Tambah Proyek")
        self.assertNotContains(response, "Hapus Project?")

    def test_star_toggles_once_per_user(self):
        self.client.login(username="sasha", password="RahasiaKuat123")
        url = reverse("main:toggle_star", args=[self.project.id])
        self.client.post(url)
        self.assertEqual(self.project.starred_by.count(), 1)
        self.client.post(url)  # klik kedua = unstar
        self.assertEqual(self.project.starred_by.count(), 0)

    def test_star_requires_login_and_post(self):
        url = reverse("main:toggle_star", args=[self.project.id])
        self.assertEqual(self.client.post(url).status_code, 302)
        self.client.login(username="sasha", password="RahasiaKuat123")
        self.client.get(url)  # GET tidak boleh mengubah data
        self.assertEqual(self.project.starred_by.count(), 0)

    def test_projects_api_uses_usernames_not_ids(self):
        self.project.starred_by.add(self.user)
        data = json.loads(self.client.get(reverse("main:get_projects_json")).content)
        self.assertEqual(data[0]["fields"]["starred_by"], [["sasha"]])
