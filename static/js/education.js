/**
 * Tugas 6 — Bagian Education di halaman utama, sekarang memakai API DRF di /api/v1/education/.
 *
 * Alur besarnya:
 * 1. Halaman dimuat -> fetchEducations() mengambil JSON dari GET /api/v1/education/?q=...
 * 2. Pengguna mengetik di kotak cari -> debounce 300 ms -> fetchEducations(kata kunci).
 * 3. Pemilik menambah data  -> POST   /api/v1/education/            (201 / 400 / 403)
 * 4. Editor/pemilik mengubah -> PATCH  /api/v1/education/<id>/       (200 / 400 / 403)
 * 5. Pemilik menghapus      -> DELETE /api/v1/education/<id>/       (204 / 403)
 * 6. User login memberi star -> POST   /api/v1/education/<id>/star/  (200 / 403)
 * Setelah setiap aksi berhasil, daftar dimuat ulang tanpa me-reload halaman.
 *
 * Fungsi getCookie, escapeHtml, dan formatApiErrors berasal dari static/js/utils.js,
 * sedangkan showToast berasal dari static/js/toast.js.
 */
(function () {
    // IIFE supaya variabel di file ini tidak bentrok dengan skrip halaman lain.

    const section = document.getElementById('education');
    if (!section) return; // bukan halaman utama

    // ---------- Konfigurasi dari atribut data-* di index.html ----------
    const LIST_URL = section.dataset.listUrl;        // /api/v1/education/
    const DETAIL_URL = section.dataset.detailUrl;    // /api/v1/education/0/
    const STAR_URL = section.dataset.starUrl;        // /api/v1/education/0/star/
    const LOGIN_URL = section.dataset.loginUrl;
    const IS_AUTHENTICATED = section.dataset.isAuthenticated === 'true';
    const CAN_EDIT = section.dataset.canEdit === 'true';
    const IS_OWNER = section.dataset.isOwner === 'true';
    const SEARCH_DEBOUNCE_DELAY = 300;
    const EDUCATION_FIELDS = ['institution', 'level', 'major', 'start_year', 'end_year'];

    // ---------- Elemen DOM ----------
    const loadingState = document.getElementById('education-loading');
    const errorState = document.getElementById('education-error');
    const emptyState = document.getElementById('education-empty');
    const emptyMessage = document.getElementById('education-empty-message');
    const timeline = document.getElementById('education-timeline');
    const retryButton = document.getElementById('education-retry');
    const searchForm = document.getElementById('education-search-form');
    const searchInput = document.getElementById('education-search-input');
    // Elemen di bawah hanya dirender untuk peran tertentu -> bisa null
    const addForm = document.getElementById('education-form');                 // pemilik
    const editModal = document.getElementById('edit-education-modal');         // editor & pemilik
    const editForm = document.getElementById('edit-education-form');           // editor & pemilik
    const deleteModal = document.getElementById('delete-education-modal');     // pemilik
    const confirmDeleteButton = document.getElementById('confirm-delete-education');

    // Data terakhir dari API, disimpan per id supaya modal edit bisa diisi data lama
    const educationById = new Map();
    let searchDebounceTimer;
    let abortController;
    let pendingDeleteId = null;

    /** Mengganti id dummy 0 pada URL dari Django dengan id asli. */
    function buildUrl(templateUrl, id) {
        return templateUrl.replace('/0/', `/${id}/`);
    }

    function currentQuery() {
        return searchInput.value.trim();
    }

    /** Menampilkan satu kondisi (loading/error/empty/timeline) dan menyembunyikan sisanya. */
    function showState({ loading = false, error = false, empty = false, list = false }) {
        loadingState.classList.toggle('hide', !loading);
        errorState.classList.toggle('hide', !error);
        emptyState.classList.toggle('hide', !empty);
        timeline.classList.toggle('hide', !list);
    }

    /**
     * Satu fungsi untuk semua request yang MENGUBAH data (POST/PUT/PATCH/DELETE).
     * - Header X-CSRFToken wajib, karena API memakai SessionAuthentication.
     * - Kalau status bukan 2xx, lempar Error berisi pesan dari DRF (400/403/404).
     */
    async function sendWriteRequest(url, method, payload) {
        const response = await fetch(url, {
            method,
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: payload === undefined ? undefined : JSON.stringify(payload),
        });
        if (response.status === 204) return null; // DELETE berhasil: body kosong, jangan .json()
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(formatApiErrors(data, response.status));
        return data;
    }

    /** Mengambil nilai field model dari sebuah form lalu mengubahnya menjadi objek JSON. */
    function formToPayload(form) {
        const formData = new FormData(form);
        // Pilih field secara eksplisit -> csrfmiddlewaretoken tidak ikut terkirim
        const payload = Object.fromEntries(EDUCATION_FIELDS.map(name => [name, formData.get(name)]));
        // Input angka yang kosong dikirim sebagai null (bukan "") supaya diterima IntegerField
        payload.end_year = payload.end_year === '' ? null : payload.end_year;
        return payload;
    }

    /**
     * Membuat satu item timeline dari objek JSON DRF (data langsung di objek: edu.id, edu.institution).
     * SEMUA teks dari server melewati escapeHtml sebelum masuk ke innerHTML (anti-XSS).
     */
    function buildTimelineItem(edu) {
        const article = document.createElement('article');
        article.className = 'timeline-item';
        const id = escapeHtml(edu.id);

        const endYearHtml = edu.is_ongoing
            ? 'sekarang'
            : `<time datetime="${escapeHtml(edu.end_year)}">${escapeHtml(edu.end_year)}</time>`;
        const majorHtml = edu.major ? ` &middot; ${escapeHtml(edu.major)}` : '';
        const starTitle = edu.star_count > 0
            ? `Dibintangi oleh ${escapeHtml(edu.starred_by_names)}`
            : 'Jadilah yang pertama memberi star';

        // Pengunjung tanpa login: tombol star diganti tautan login
        const starHtml = IS_AUTHENTICATED
            ? `<button type="button" class="button button-small button-star${edu.is_starred ? ' is-starred' : ''}"
                    data-action="star" data-id="${id}" title="${starTitle}">
                    <span aria-hidden="true">&#9733;</span>
                    ${edu.is_starred ? 'Unstar' : 'Star'}
                    <span class="star-count">${escapeHtml(edu.star_count)}</span>
               </button>`
            : `<a href="${escapeHtml(LOGIN_URL)}" class="button button-small button-star" title="Login untuk memberi star">
                    <span aria-hidden="true">&#9733;</span> Login untuk star
                    <span class="star-count">${escapeHtml(edu.star_count)}</span>
               </a>`;

        // Tombol hanya disembunyikan di sini; pemeriksaan hak akses yang sebenarnya ada di permission class
        const editHtml = CAN_EDIT
            ? `<button type="button" class="button button-secondary button-small"
                    data-action="edit" data-id="${id}">Edit</button>`
            : '';
        const deleteHtml = IS_OWNER
            ? `<button type="button" class="button button-danger button-small"
                    data-action="delete" data-id="${id}">Hapus</button>`
            : '';

        article.innerHTML = `
            <span class="timeline-dot${edu.is_ongoing ? ' timeline-dot-active' : ''}"></span>
            <p class="timeline-period">
                <time datetime="${escapeHtml(edu.start_year)}">${escapeHtml(edu.start_year)}</time> &mdash; ${endYearHtml}
            </p>
            <h3 class="timeline-institution">${escapeHtml(edu.institution)}</h3>
            <p class="timeline-detail">${escapeHtml(edu.level_display)}${majorHtml}</p>
            <div class="timeline-actions">
                ${starHtml}
                ${editHtml}
                ${deleteHtml}
            </div>
        `;
        return article;
    }

    // ---------- GET daftar pendidikan (+ pencarian ?q=) ----------
    async function fetchEducations(query = '') {
        // Batalkan request lama supaya hasil pencarian lama tidak menimpa yang baru
        if (abortController) abortController.abort();
        abortController = new AbortController();

        showState({ loading: true });
        try {
            const url = new URL(LIST_URL, window.location.origin);
            if (query) url.searchParams.set('q', query);
            const response = await fetch(url, {
                headers: { 'Accept': 'application/json' },
                signal: abortController.signal,
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const educations = await response.json();
            educationById.clear();
            educations.forEach(edu => educationById.set(String(edu.id), edu));

            if (educations.length === 0) {
                emptyMessage.textContent = query
                    ? `Tidak ada riwayat pendidikan yang cocok dengan "${query}".` // textContent -> aman
                    : 'Belum ada riwayat pendidikan yang ditambahkan.';
                showState({ empty: true });
                return;
            }
            timeline.replaceChildren(...educations.map(buildTimelineItem));
            showState({ list: true });
        } catch (error) {
            if (error.name === 'AbortError') return; // dibatalkan sengaja, bukan error
            console.error('Gagal memuat education:', error);
            showState({ error: true });
        }
    }

    // ---------- Pencarian dengan debouncing ----------
    searchInput.addEventListener('input', () => {
        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = setTimeout(() => fetchEducations(currentQuery()), SEARCH_DEBOUNCE_DELAY);
    });
    searchForm.addEventListener('submit', (event) => {
        event.preventDefault(); // jangan reload halaman
        clearTimeout(searchDebounceTimer);
        fetchEducations(currentQuery());
    });
    retryButton.addEventListener('click', () => fetchEducations(currentQuery()));

    // ---------- Tambah (POST) — hanya pemilik ----------
    async function addEducation(event) {
        event.preventDefault();
        const submitButton = addForm.querySelector('button[type="submit"]');
        submitButton.disabled = true; // cegah klik ganda -> data tersimpan dua kali
        try {
            await sendWriteRequest(LIST_URL, 'POST', formToPayload(addForm));
            addForm.reset();
            document.getElementById('add-education-modal').hidePopover();
            showToast('Berhasil', 'Riwayat pendidikan berhasil ditambahkan.', 'success');
            await fetchEducations(currentQuery());
        } catch (error) {
            showToast('Gagal menambahkan pendidikan', error.message, 'error');
        } finally {
            submitButton.disabled = false;
        }
    }
    if (addForm) addForm.addEventListener('submit', addEducation);

    // ---------- Ubah (PATCH) — editor & pemilik ----------
    function openEditModal(id) {
        const edu = educationById.get(String(id));
        if (!edu || !editForm) return;
        editForm.dataset.id = id;
        // Isi form dengan data lama. .value pada input aman dari XSS (tidak di-parse sebagai HTML).
        EDUCATION_FIELDS.forEach(name => {
            editForm.elements[name].value = edu[name] ?? '';
        });
        editModal.showPopover();
    }

    async function updateEducation(event) {
        event.preventDefault();
        const submitButton = editForm.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        try {
            // PATCH = hanya field yang dikirim yang diubah (di sini semua field form dikirim)
            await sendWriteRequest(buildUrl(DETAIL_URL, editForm.dataset.id), 'PATCH', formToPayload(editForm));
            editModal.hidePopover();
            showToast('Berhasil', 'Riwayat pendidikan berhasil diperbarui.', 'success');
            await fetchEducations(currentQuery());
        } catch (error) {
            showToast('Gagal memperbarui pendidikan', error.message, 'error');
        } finally {
            submitButton.disabled = false;
        }
    }
    if (editForm) editForm.addEventListener('submit', updateEducation);

    // ---------- Hapus (DELETE) — hanya pemilik ----------
    function openDeleteModal(id) {
        const edu = educationById.get(String(id));
        if (!edu || !deleteModal) return;
        pendingDeleteId = id;
        // textContent -> nama institusi tampil sebagai teks biasa
        document.getElementById('delete-education-name').textContent = edu.institution;
        deleteModal.showPopover();
    }

    async function deleteEducation() {
        if (pendingDeleteId === null) return;
        confirmDeleteButton.disabled = true;
        try {
            await sendWriteRequest(buildUrl(DETAIL_URL, pendingDeleteId), 'DELETE');
            deleteModal.hidePopover();
            showToast('Berhasil', 'Riwayat pendidikan dihapus.', 'success');
            await fetchEducations(currentQuery());
        } catch (error) {
            showToast('Gagal menghapus pendidikan', error.message, 'error');
        } finally {
            confirmDeleteButton.disabled = false;
            pendingDeleteId = null;
        }
    }
    if (confirmDeleteButton) confirmDeleteButton.addEventListener('click', deleteEducation);

    // ---------- Star (POST) — semua akun yang login ----------
    async function toggleStar(button) {
        button.disabled = true; // star = toggle, klik ganda akan membatalkan dirinya sendiri
        try {
            const result = await sendWriteRequest(buildUrl(STAR_URL, button.dataset.id), 'POST');
            showToast('Berhasil', result.is_starred ? 'Star diberikan.' : 'Star dibatalkan.', 'success');
            await fetchEducations(currentQuery());
        } catch (error) {
            showToast('Gagal memperbarui star', error.message, 'error');
            button.disabled = false;
        }
    }

    // ---------- Event delegation: satu listener untuk semua tombol di timeline ----------
    // Tombol dibuat ulang setiap kali data dimuat, jadi listener dipasang di induknya.
    timeline.addEventListener('click', (event) => {
        const button = event.target.closest('button[data-action]');
        if (!button || button.disabled) return;
        const { action, id } = button.dataset;
        if (action === 'star') toggleStar(button);
        else if (action === 'edit') openEditModal(id);
        else if (action === 'delete') openDeleteModal(id);
    });

    // ---------- Mulai ----------
    fetchEducations();
})();