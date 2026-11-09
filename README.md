# myportofolio — Portofolio Pribadi Muhammad Iqbal

| | |
|---|---|
| **Nama** | Muhammad Iqbal |
| **NPM** | 2506657075 |
| **Kelas** | PBP C |
| **Deploy** | https://muhammad-iqbal517-myportofolio.pws.cs.ui.ac.id |

Website portofolio pribadi berbasis Django dengan tema komik: profil, riwayat pendidikan (Education), pengalaman (Experience), dan proyek (Projects). Proyek ini dikembangkan bertahap setiap minggu pada mata kuliah Pemrograman Berbasis Platform (PBP) Fasilkom UI.

## Daftar Isi

1. [Fitur](#fitur)
2. [Teknologi](#teknologi)
3. [Cara Menjalankan (Lokal)](#cara-menjalankan-lokal)
4. [Peran & Hak Akses](#peran--hak-akses)
5. [Endpoint API](#endpoint-api)
6. [Testing](#testing)
7. [Progres Mingguan](#progres-mingguan)
8. [Pertanyaan Reflektif & AI Disclosure](#pertanyaan-reflektif--ai-disclosure)

## Fitur

- **Profil** dengan cookie "sesi terakhir login".
- **Education**: daftar timeline, pencarian, filter jenjang, urutan, tambah, edit, hapus, dan star, semuanya lewat REST API tanpa reload halaman.
- **Projects**: daftar, pencarian, tambah, hapus, dan star lewat REST API.
- **Experience**: halaman pengalaman dari database.
- **Autentikasi**: register, login (dengan `?next=`), logout.
- **Empat peran**: pengunjung, pengguna biasa, Editor, dan pemilik portofolio.
- **Keamanan**: CSRF token di setiap request yang mengubah data, escaping teks sebelum masuk `innerHTML`, `strip_tags` di form dan serializer, halaman 403/404 khusus.
- **Contacts** (Tutorial 6): latihan HTMX.

## Teknologi

Python · Django 5.2 · Django REST Framework 3.18 · SQLite (lokal) / PostgreSQL (PWS) · WhiteNoise · JavaScript (Fetch API, Popover API) · HTML/CSS

## Cara Menjalankan (Lokal)

```bash
git clone https://github.com/labqimm/myportofolio.git
cd myportofolio
python -m venv env
env\Scripts\activate            # Windows (macOS/Linux: source env/bin/activate)
pip install -r requirements.txt
python manage.py migrate         # sekaligus membuat grup "Editor" (migrasi 0005)
python manage.py createsuperuser # akun pemilik portofolio
python manage.py runserver
```

| Halaman | URL |
|---|---|
| Halaman utama + Education | http://127.0.0.1:8000/ |
| Projects | http://127.0.0.1:8000/projects/ |
| Browsable API | http://127.0.0.1:8000/api/v1/education/ dan http://127.0.0.1:8000/api/v1/projects/ |
| Django Admin (atur grup Editor) | http://127.0.0.1:8000/admin/ |

Untuk memberi peran Editor, buka Django Admin → Users → pilih akun → tambahkan ke grup **Editor**.

## Peran & Hak Akses

| Peran | Baca | Star | Ubah (PUT/PATCH) | Tambah & Hapus |
|---|:-:|:-:|:-:|:-:|
| Pengunjung (belum login) | ✅ | ❌ | ❌ | ❌ |
| Pengguna biasa | ✅ | ✅ | ❌ | ❌ |
| Editor (grup "Editor") | ✅ | ✅ | ✅ Education | ❌ |
| Pemilik (superuser) | ✅ | ✅ | ✅ | ✅ |

Hak akses diperiksa di server (permission class DRF dan pengecekan di view), bukan hanya dengan menyembunyikan tombol.

## Endpoint API

Semua endpoint memakai `SessionAuthentication`. Request yang mengubah data wajib membawa header `X-CSRFToken`.

| Endpoint | Method | Hak akses | Status |
|---|---|---|---|
| `/api/v1/education/` | GET | semua orang | 200, 400 (filter tidak valid) |
| `/api/v1/education/` | POST | pemilik | 201, 400, 403 |
| `/api/v1/education/<id>/` | GET | semua orang | 200, 404 |
| `/api/v1/education/<id>/` | PUT, PATCH | Editor & pemilik | 200, 400, 403, 404 |
| `/api/v1/education/<id>/` | DELETE | pemilik | 204, 403, 404 |
| `/api/v1/education/<id>/star/` | POST | semua akun yang login | 200, 403, 404 |
| `/api/v1/projects/` dan turunannya | sama seperti di atas | menulis hanya untuk pemilik | (Tutorial 07) |

Parameter query untuk `GET /api/v1/education/`:

| Parameter | Contoh | Keterangan |
|---|---|---|
| `q` | `?q=indonesia` | cari di nama institusi atau jurusan |
| `level` | `?level=s1` | `sd`, `smp`, `sma`, `d3`, `s1`, `s2` |
| `ordering` | `?ordering=-start_year` | `-start_year` (terbaru, default), `start_year`, `institution`, `-institution` |

Nilai `level`/`ordering` yang tidak dikenal dibalas **400**.

## Testing

```bash
python manage.py test main
```

Test mencakup view & template (`main/tests.py`) dan API (`main/tests_api.py`): setiap peran, isi database pada test penolakan, validasi, star, filter, serta CSRF dengan `APIClient(enforce_csrf_checks=True)` + `.login()`.

## Progres Mingguan

| Minggu | Topik | Yang ditambahkan |
|---|---|---|
| Tutorial 1 / Tugas 1 | HTML, CSS, deploy | Setup proyek Django, halaman profil, section Education (statis), deploy ke PWS |
| Tutorial 2 / Tugas 2 | Model, view, template | Model `Project`, admin, halaman Projects, `base.html`, unit test pertama |
| Tutorial 3 / Tugas 3 | Form & data delivery | Model + `ModelForm` Education, CRUD Education, endpoint JSON, modal hapus |
| Tutorial 4 / Tugas 4 | Autentikasi & otorisasi | Register/login/logout, cookie `last_login`, star, peran Editor, halaman 403 |
| Tutorial 5 / Tugas 5 | AJAX & keamanan | Fetch API, toast, pencarian dengan debounce, modal tambah via AJAX, CSRF header, anti-XSS |
| Tutorial 6 | HTMX | Aplikasi latihan `contacts`; tampilan diperbarui dengan tema komik |
| Tutorial 7 / Tugas 6 | Django REST Framework | API `/api/v1/` untuk Projects & Education (serializer, permission class, `@api_view`), halaman memakai API, test `APITestCase`, plus fitur ekstra filter jenjang & urutan |

## Pertanyaan Reflektif & AI Disclosure

### Tugas 1

1. Saya pakai beberapa elemen semantik seperti header, nav, main, section, dan footer supaya struktur halamannya jelas, bagian mana yang navigasi, bagian mana isi utama, bagian mana yang footer dibanding  pakai div semua. 

2. Tantangan yang saya rasakan adalah menentukan urutan tampilan waktu pindah dari desktop ke HP. Di desktop, foto dan teks bisa disandingkan jadi dua kolom, tapi di layar kecil semuanya harus ditumpuk jadi satu kolom, 

3. Karena websitenya masih murni HTML/CSS, semua isi (bio, foto, dll) harus saya tulis manual di file HTML kalau mau update sesuatu, saya harus edit kode dan upload ulang nggak bisa diubah langsung dari halaman itu sendiri.

AI DISCLOSURE
> Tools Yang Digunakan : Claude (Anthropic)

> Bagian Yang Dibantu AI:
AI membantu saya dalam menulis kode di bagian style.css dan index.html, AI membantu saya membuat section education selain itu AI nya juga mengajari saya cara branching agar commit nya terlihat rapih dan professional sehingga sesuai dengan ketentuan git commit pada tugas.

> Strategi Prompting:
Saya menjelaskan dulu konteks untuk mengerjakan tugas ini dengan memberikan referensi dan arahan desain serta konteks berupa file yang digunakan agar AI paham sepenuhnya apa mau saya dan saya bisa merealisasikan keinginan saya.

>Bagian yang Saya Kerjakan Sendiri:
Kontribusi saya ada pada ide saya untuk membuat section education, dimana section education lazim dalam web portofolio serta saya memberikan data dan ide untuk bagaimana design web saya sendiri.

>Evaluasi terhadap hasil AI:
Menurut saya AI sudah memberikan hasil yang sangat memuaskan bahkan melampaui batasan saya, oleh karena itu saya tidak setuju dengan usulan AI yang terlalu advanced dalam level saya sehingga saya meminta untuk dikerjakan sesuai dengan kemampuan saya agar saya bisa belajar sendiri.

>Log Percakapan:  https://claude.ai/share/76622cb9-754d-4495-85e5-5583a65306af

### Tugas 2

1. Saat buka halaman portofolio misal /projects/, django akan memproses permintaan tersebut melalui beberapa tahap.Pertama request ke urls.py proyek, untuk ditentukan aplikasi mana yang akan menangani url tersebut lalu diteruskan ke urls.py aplikasi.Di main/urls.py django mencari URL yang cocok lalu menjalakan view untuk mengatur logika halaman , jika butuh data view akan mengambil dari model.Model berhubungan dengan database dan menyimpan data ,lalu data tersebut diberikan oleh view kepada template melalui context.terakhir template mengatur bagaimana data ditampilkan dalam HTML. Django mengirimkan ke browser untuk dilihat pengguna 
Alurnya 
>Browser → urls.py proyek → urls.py aplikasi → View → Model → View → Template → Browser

2. Data disimpan di model agar gampang terhubung dengan database, jadi bisa diubah tidak secara langsung di html tapi melalui database.Jika data di tulis langsung / di hard code , setiap kali mengubah harus mengedit file html sehingga tidak praktis

3. Perbedaan makemigrations dan migrate adalah makemigrations membuat file migrasi berdasarkan perubahan model kalau migrate digunakan untuk mengirim/menerapkan file tersebut ke database

AI Disclosure:

Tools yang digunakan: Claude (Anthropic)

Bagian yang dibantu AI: 
AI membantu saya memahami konteks tugas dan mengarahkan hal yang harus saya lakukan serta memberikan kode untuk di tulis di dalam file. serta membantu mengarahkan saya untuk menjawab refleksi nomor pertama 

Strategi Prompting:
Saya memberikan file agar AI memahami konteks dalam mengerjakan tugas tugasnya lalu saya memberi tugas spesifik agar AI paham keinignan saya dan saya memberikan feedback dari proses yang sudah disarankan oleh AI

Bagian yang saya kerjakan Sendiri:
Saya mengubah file yang diarahkan dan melakukan makemigrate dan migration untuk template 

Link Chat AI: https://claude.ai/share/c5aa6d61-2e5a-4b1a-953b-c421088fcf75

### Tugas 3

1. ModelForm dipakai karena form dibuat otomatis dari model, sehingga field, tipe input, dan validasinya (misalnya angka wajib angka, panjang maksimal teks) langsung mengikuti model. Kalau form HTML dibuat manual, kita harus menulis setiap input dan mengecek datanya satu per satu, dan kalau model berubah, form juga harus diubah manual. Dengan ModelForm, data yang sudah valid cukup disimpan dengan form.save(), bahkan untuk update cukup menambahkan instance=. {% csrf_token %} wajib ditambahkan untuk mencegah serangan CSRF (Cross-Site Request Forgery), yaitu ketika website lain diam-diam mengirim request POST ke website kita atas nama pengguna. Token ini berupa kode acak yang hanya diketahui halaman kita, sehingga Django menolak request POST yang tidak membawa token yang benar.

2. JSON lebih disukai karena formatnya lebih ringkas dan mudah dibaca manusia, ukuran datanya lebih kecil daripada XML yang harus membuka dan menutup tag untuk setiap data, dan strukturnya (objek dan array) sama dengan objek di JavaScript sehingga bisa langsung dipakai di browser tanpa parsing yang rumit. Hampir semua bahasa pemrograman dan API modern juga sudah mendukung JSON secara bawaan.

3. Saat membuka /api/education/, request masuk ke urls.py lalu diteruskan ke view get_education_json. View mengambil data dari database lewat Education.objects.all() (hasilnya berupa objek Python), lalu serializers.serialize("json", ...) mengubahnya menjadi teks JSON, dan hasilnya dikirim dengan HttpResponse ber-content_type application/json. Serialization diperlukan karena objek model Django hanya dimengerti oleh Python dan tidak bisa langsung dikirim lewat internet; data harus diubah dulu menjadi teks dengan format standar agar bisa dibaca aplikasi lain (browser, aplikasi mobile, dll). Di halaman utama prosesnya dibalik: JSON dideserialisasi kembali menjadi objek Education lalu ditampilkan di template.

AI Disclosure:

Tools yang digunakan: Claude (Anthropic)

Bagian yang dibantu AI: AI membantu membuat model dan ModelForm Education, view create/update/delete/JSON, template form dan modal hapus, refactor experience.html, unit test, serta draft jawaban pertanyaan reflektif.

Strategi Prompting: Saya memberikan file soal dan seluruh file proyek terbaru (termasuk link commit GitHub) agar AI memahami kode Tutorial 03 saya, lalu meminta AI bertanya dulu jika ada konteks yang kurang sebelum mengerjakan.

Bagian yang saya kerjakan sendiri: Memilih bagian Education, menjalankan migrasi, mengisi ulang data pendidikan lewat form, mengecek hasilnya di browser, dan melakukan commit bertahap.

LINK CHAT AI: https://claude.ai/share/11e0fbad-a6c4-4a0a-8f8e-9172425a265a

### Tugas 4

AI Disclosure:

Tools yang digunakan: Claude (Anthropic)

Bagian yang dibantu AI: AI membantu menerapkan Tutorial 04 (register, login, logout, cookie last_login, otorisasi Projects, star), peran Editor dan star untuk Education, unit test, perbaikan kecil dari tugas sebelumnya.

Strategi Prompting: Saya memberikan PDF Tutorial 1–4 dan Tugas 2–4 serta repo GitHub terbaru, lalu meminta AI mengerjakan langkah demi langkah sambil menjelaskan, memisahkan commit Tutorial 04 dan Tugas 4, dan bertanya dulu jika konteks kode kurang.

Bagian yang saya kerjakan sendiri:Membuat superuser, memasukkan akun ke editor, test secara manual fitur di browser , deploy pws. 

LINK CHAT AI: https://claude.ai/artifact/B3xMx5cb4UBkZnJ5Jk1aAQ

### Tugas 5

1. Debouncing adalah teknik menunda eksekusi suatu fungsi sampai pengguna berhenti memicu event selama jeda tertentu. Di halaman Education, setiap ketikan me-reset timer 300 ms, jadi request ke /api/education/?q=... baru dikirim setelah pengguna berhenti mengetik. Tanpa debouncing, mengetik "indonesia" mengirim 9 request sekaligus: server terbebani, kuota internet boros, dan hasil pencarian bisa datang tidak berurutan sehingga hasil lama menimpa hasil baru. Untuk kasus terakhir saya juga memakai AbortController untuk membatalkan request lama.

2. fetch() tidak langsung mengembalikan data, melainkan Promise (janji bahwa hasilnya akan ada nanti), karena request ke server butuh waktu. await membuat fungsi async menunggu Promise itu selesai lalu memberikan hasilnya (objek Response). Setelah itu response.json() juga perlu di-await karena membaca isi balasan juga asinkron. Tanpa await, variabel hanya berisi Promise yang belum selesai: response.ok bernilai undefined, response.json() tidak bisa dipakai sebagaimana mestinya, dan kode di bawahnya berjalan duluan sebelum data datang, sehingga data tidak tampil atau muncul error. await tidak membekukan seluruh halaman; hanya fungsi async itu yang menunggu.

3. XSS (Cross-Site Scripting) adalah serangan ketika penyerang menyisipkan kode (misalnya <img src="x" onerror="alert('XSS!')">) ke dalam data, lalu kode itu ikut dijalankan di browser orang lain yang membuka halaman tersebut. Akibatnya bisa berupa pencurian cookie/session atau aksi atas nama korban. Template Django otomatis meng-escape {{ variabel }}, sehingga karakter < > diubah menjadi teks biasa. Sebaliknya, data yang disisipkan JavaScript lewat innerHTML tidak di-escape otomatis; browser menganggap string tersebut sebagai HTML lalu menjalankannya. Karena itu saya meng-escape setiap nilai dengan escapeHtml/textContent di sisi klien dan membersihkan input dengan strip_tags di clean_institution/clean_major di sisi server (dua lapis pertahanan).

AI Disclosure:

Tools yang digunakan: Claude (Anthropic)

Bagian yang dibantu AI: AI membaca repo GitHub saya, lalu membantu memindahkan getCookie/escapeHtml ke static/js/utils.js, membuat endpoint JSON Education manual (star + pencarian), view create_education_ajax (201/400/403), modal tambah dan modal hapus bersama, static/js/education.js (fetch, debounce, toast, escape), clean_<field> dengan strip_tags, penyesuaian 4 test lama dan 8 test baru, setup guide README

Strategi Prompting: Saya memberikan PDF Tugas 5 dan meminta AI mengerjakan langkah demi langkah dengan kode yang saya salin manual, menjelaskan alurnya, memperbaiki kekurangan tugas sebelumnya, dan bertanya jika konteks kurang.

Bagian yang saya kerjakan sendiri:Saya menjalan runserver untuk melihat berjalnkan atau tidak, melakukan testing serta membuat commit dan branching yang rapih


LINK CHAT AI: https://claude.ai/share/68257ee7-a08a-449d-b71c-62a9e1462b04

### Tugas 6

1. REST (Representational State Transfer) adalah gaya arsitektur untuk membangun API: setiap data dianggap sebagai *resource* yang punya alamat (URL) sendiri, misalnya `/api/v1/education/` (kumpulan) dan `/api/v1/education/3/` (satu data), lalu aksi terhadap resource itu ditentukan oleh **method HTTP**: GET membaca, POST membuat, PUT/PATCH mengubah, DELETE menghapus. Server juga harus membalas dengan **status HTTP** yang bermakna (201 dibuat, 204 dihapus, 400 input salah, 403 tidak diizinkan, 404 tidak ditemukan) dan bersifat *stateless* (setiap request membawa informasi yang dibutuhkan, misalnya cookie session dan token CSRF). Jadi mengembalikan JSON saja belum cukup: endpoint Tugas 5 seperti `/api/education/` memang membalas JSON, tetapi menambah data lewat URL berbentuk kata kerja (`/education/add-ajax/`), menghapus lewat POST ke `/delete/`, dan formatnya dirakit manual. Itu "API yang membalas JSON", bukan API RESTful.
   **PUT** mengganti seluruh data, sehingga semua field wajib dikirim; field wajib yang tidak dikirim ditolak 400. Cocok dipakai saat form edit mengirim semua field, misalnya mengganti seluruh isi satu riwayat pendidikan. **PATCH** hanya mengubah field yang dikirim, field lain tetap. Cocok untuk perubahan sebagian, misalnya Editor hanya mengoreksi jurusan dengan `{"major": "Sistem Informasi"}`, atau mengisi tahun lulus saja.

2. Serializer adalah "penerjemah dua arah" antara objek model Django dan JSON. Arah keluar: `EducationSerializer(education).data` mengubah objek menjadi dict/JSON dengan field yang ditulis eksplisit, termasuk field hasil perhitungan yang read-only (`star_count`, `is_starred`, `starred_by_names`, `level_display`). Arah masuk: `EducationSerializer(data=request.data)` memvalidasi input (tipe angka, pilihan jenjang, `validate_institution` dengan `strip_tags`, `validate()` untuk tahun lulus ≥ tahun masuk), lalu `save()` membuat atau mengubah objek. Dibanding merakit dictionary manual dengan `JsonResponse` di Tutorial 05, keuntungannya: (a) satu definisi dipakai untuk output dan input, jadi format list, detail, dan star selalu sama; (b) validasi otomatis dari model plus validasi tambahan, dengan pesan error per field yang langsung dikirim sebagai 400; (c) field yang tidak ada di `fields` atau yang read-only tidak bisa diubah klien, sehingga data sensitif seperti email/password tidak bocor dan `star_count` tidak bisa dipalsukan; (d) `partial=True` langsung mendukung PATCH; (e) kode view menjadi pendek dan tidak perlu menulis ulang loop serta `get_json_data()` di setiap view.

3. Autentikasi menjawab "siapa kamu?": DRF memakai `SessionAuthentication` untuk membaca cookie session dari login Django, lalu mengisi `request.user`. Otorisasi menjawab "kamu boleh melakukan apa?": dijalankan oleh permission class setelah autentikasi. Di proyek ini `IsPortfolioOwnerOrEditorOrReadOnly` mengizinkan GET untuk semua orang, PUT/PATCH untuk Editor dan pemilik, serta POST/DELETE hanya untuk pemilik, sedangkan `IsAuthenticated` dipakai di endpoint star. Hak akses harus dicek di server karena menyembunyikan tombol di template hanya mengubah tampilan. Siapa pun tetap bisa mengirim request langsung lewat console browser (`fetch('/api/v1/education/1/', {method: 'DELETE'})`), Postman, atau curl tanpa melihat tombolnya. Saya sudah membuktikannya: akun Editor yang memanggil DELETE lewat console tetap mendapat 403 dan datanya tidak terhapus. Server adalah satu-satunya tempat yang tidak bisa diubah pengguna.

4. Dengan `SessionAuthentication`, browser otomatis mengirim cookie session ke website kita di setiap request, termasuk request yang dipicu website lain (misalnya form tersembunyi di situs jahat yang mengirim POST ke `/api/v1/education/1/` saat korban sedang login). Tanpa pemeriksaan tambahan, server akan menganggap request itu sah karena cookienya valid; inilah serangan CSRF. Karena itu DRF tetap mewajibkan token CSRF untuk method yang mengubah data (POST/PUT/PATCH/DELETE) jika user terautentikasi lewat session. Token dibaca dari cookie `csrftoken` dengan `getCookie()` lalu dikirim di header `X-CSRFToken`. Situs lain tidak bisa membaca cookie itu, jadi tidak bisa mengirim token yang benar. `force_authenticate` di test langsung menempelkan user ke request dan **melewati** `SessionAuthentication` sepenuhnya, termasuk pemeriksaan CSRF di dalamnya, sehingga test seperti itu akan lulus meskipun tokennya tidak ada. Untuk membuktikan perlindungan CSRF, test harus memakai `APIClient(enforce_csrf_checks=True)` dan `.login()` sehingga request benar-benar lewat session. Di `test_session_write_without_csrf_is_rejected`, POST/DELETE/star tanpa token mendapat 403 dan isi database tidak berubah, sedangkan `test_session_write_with_csrf_succeeds` membuktikan PATCH dengan header `X-CSRFToken` berhasil.

**Fitur ekstra (di luar instruksi)**

- **Filter jenjang & urutan lewat API**: `?level=s1&ordering=-start_year`, divalidasi `EducationQuerySerializer` (nilai tidak dikenal → 400), dengan dropdown di halaman dan jumlah hasil.
- **Error validasi per field**: pesan 400 dari serializer tampil tepat di bawah input yang salah di modal tambah/edit (selain toast), input pertama yang salah langsung difokuskan, dan pesannya hilang saat mulai diperbaiki.
- **Star tanpa memuat ulang daftar**: kartu yang diklik langsung diganti dengan data terbaru dari balasan API.
- Pesan error API berbahasa Indonesia, modal konfirmasi hapus, dan tautan "Login untuk star" untuk pengunjung.

**AI Disclosure**

- **Tools:** Claude (Anthropic) di Claude Cowork, dengan akses baca ke folder proyek.
- **Bagian yang dibantu AI:** mengubah `static/js/education.js` agar memakai API `/api/v1/education/` (GET + pencarian, POST, PATCH lewat modal edit baru, DELETE, star); menambah `formatApiErrors` di `utils.js`; membuat `education_edit_modal.html` dan memperbarui modal hapus; pesan error berbahasa Indonesia di `EducationSerializer`; docstring dan pesan 403 `IsPortfolioOwnerOrEditorOrReadOnly`; fitur ekstra (`EducationQuerySerializer` untuk filter & urutan, error per field di modal, star tanpa memuat ulang daftar); test API Education per peran; penyusunan ulang README; draf jawaban reflektif.
- **Strategi prompting:** memberikan PDF Tugas 6 dan akses ke folder proyek, meminta AI mengerjakan langkah demi langkah dengan kode yang saya salin manual sambil menjelaskan alurnya, memperbaiki kekurangan tutorial/tugas sebelumnya, dan bertanya dulu jika konteks kurang. Setelah fitur wajib selesai, saya meminta fitur ekstra yang tetap berkaitan dengan materi DRF.
- **Keterbatasan AI & perbaikan manual:**
  - Soal menyarankan `Group.objects.create(name="Editor")` di `setUp()`, tetapi di proyek saya grup itu sudah dibuat migrasi `0005_create_editor_group`, sehingga `create` akan gagal (`IntegrityError`, nama grup unik). Test memakai `get_or_create`. Saran yang benar untuk proyek pada umumnya belum tentu benar untuk proyek saya, jadi tetap harus dicek terhadap kode sendiri.
  - Saat menyalin langkah modal edit, saya salah menempel blok `{% if can_edit %}...{% endif %}` di dalam header sehingga `{% endif %}` milik tombol "+ Tambah Pendidikan" tertimpa. Akibatnya 10 test gagal dengan `TemplateSyntaxError` ("Invalid block tag ... endblock"). Error ditelusuri dari traceback, lalu `{% endif %}` dikembalikan dan blok modal edit cukup ada sekali di bagian bawah template. Dari sini saya belajar bahwa tag template Django harus berpasangan seperti kurung.
  - Panduan AI disusun dari salinan kode, bukan langsung di laptop saya, jadi setiap langkah saya verifikasi sendiri dengan `python manage.py test main` (akhirnya 92 test lulus) sebelum commit.
- **Bagian yang saya kerjakan sendiri:** menyalin dan menyesuaikan kode secara manual, menjalankan test di setiap langkah, menemukan dan memperbaiki kesalahan template di atas, mencoba fitur di browser, dan membuat commit bertahap di branch `tugas-6-drf-education`. deploy pws
- **Link chat AI:** https://claude.ai/cowork/cse_01ND8s63E1TJ6NE9X49KnkWT