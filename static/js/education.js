/**
 * Tugas 5 — Interaktivitas bagian Education di halaman utama.
 *
 * Alur besarnya:
 * 1. Halaman dimuat -> fetchEducations() mengambil JSON dari /api/education/.
 * 2. Pengguna mengetik di kotak cari -> debounce 300 ms -> fetchEducations(kata kunci).
 * 3. Pemilik mengisi modal -> addEducation() mengirim POST (AJAX) -> toast -> daftar dimuat ulang.
 *
 * Fungsi getCookie, escapeHtml, dan formatServerErrors berasal dari static/js/utils.js,
 * sedangkan showToast berasal dari static/js/toast.js.
 */
(function () {
    // IIFE (fungsi yang langsung dipanggil) supaya variabel di file ini tidak bentrok
    // dengan variabel di skrip lain, mis. searchInput milik halaman Projects.

    const section = document.getElementById('education');
    if (!section) return; // bukan halaman utama, tidak ada yang perlu dikerjakan

    // ---------- Konfigurasi dari atribut data-* di index.html ----------
    const API_URL = section.dataset.apiUrl;
    const CREATE_URL = section.dataset.createUrl;
    const CAN_EDIT = section.dataset.canEdit === 'true';
    const IS_OWNER = section.dataset.isOwner === 'true';
    const SEARCH_DEBOUNCE_DELAY = 300; // ms setelah ketikan terakhir
    // Token dari {% csrf_token %} di section, dipakai untuk form star yang dibuat JavaScript
    const CSRF_INPUT = section.querySelector('input[name="csrfmiddlewaretoken"]');
    const CSRF_TOKEN = CSRF_INPUT ? CSRF_INPUT.value : '';

    // ---------- Elemen DOM ----------
    const loadingState = document.getElementById('education-loading');
    const errorState = document.getElementById('education-error');
    const emptyState = document.getElementById('education-empty');
    const emptyMessage = document.getElementById('education-empty-message');
    const timeline = document.getElementById('education-timeline');
    const retryButton = document.getElementById('education-retry');
    const searchForm = document.getElementById('education-search-form');
    const searchInput = document.getElementById('education-search-input');
    // Dua elemen di bawah hanya ada untuk pemilik -> bisa null untuk peran lain
    const educationForm = document.getElementById('education-form');
    const deleteModal = document.getElementById('delete-education-modal');

    let searchDebounceTimer;
    let abortController;

    /** Mengganti id dummy 0 pada URL dari Django dengan id asli. */
    function buildUrl(templateUrl, id) {
        return templateUrl.replace('/0/', `/${id}/`);
    }

    /** Menampilkan satu kondisi (loading/error/empty/timeline) dan menyembunyikan sisanya. */
    function showState({ loading = false, error = false, empty = false, list = false }) {
        loadingState.classList.toggle('hide', !loading);
        errorState.classList.toggle('hide', !error);
        emptyState.classList.toggle('hide', !empty);
        timeline.classList.toggle('hide', !list);
    }

    /**
     * Membuat satu item timeline dari objek JSON.
     * SEMUA teks dari server melewati escapeHtml sebelum masuk ke innerHTML (anti-XSS).
     */
    function buildTimelineItem(item) {
        const edu = item.fields;
        const id = item.pk;

        const article = document.createElement('article');
        article.className = 'timeline-item';

        const endYearHtml = edu.is_ongoing
            ? 'sekarang'
            : `<time datetime="${escapeHtml(edu.end_year)}">${escapeHtml(edu.end_year)}</time>`;
        const majorHtml = edu.major ? ` &middot; ${escapeHtml(edu.major)}` : '';

        const starTitle = edu.star_count > 0
            ? `Dibintangi oleh ${escapeHtml(edu.starred_by_names)}`
            : 'Jadilah yang pertama memberi star';

        // Tombol hanya disembunyikan di sini; pengecekan hak akses yang sebenarnya ada di views.py
        const editHtml = CAN_EDIT
            ? `<a href="${buildUrl(section.dataset.editUrl, id)}" class="button button-secondary button-small">Edit</a>`
            : '';
        const deleteHtml = IS_OWNER
            ? `<button type="button" class="button button-danger button-small js-delete-education"
                    popovertarget="delete-education-modal"
                    data-id="${id}" data-name="${escapeHtml(edu.institution)}">Hapus</button>`
            : '';

        article.innerHTML = `
            <span class="timeline-dot${edu.is_ongoing ? ' timeline-dot-active' : ''}"></span>
            <p class="timeline-period">
                <time datetime="${escapeHtml(edu.start_year)}">${escapeHtml(edu.start_year)}</time> &mdash; ${endYearHtml}
            </p>
            <h3 class="timeline-institution">${escapeHtml(edu.institution)}</h3>
            <p class="timeline-detail">${escapeHtml(edu.level_display)}${majorHtml}</p>
            <div class="timeline-actions">
                <form method="post" action="${buildUrl(section.dataset.starUrl, id)}" class="star-form">
                    <input type="hidden" name="csrfmiddlewaretoken" value="${escapeHtml(CSRF_TOKEN)}">
                    <button type="submit" class="button button-small button-star${edu.is_starred ? ' is-starred' : ''}"
                        title="${starTitle}">
                        <span aria-hidden="true">&#9733;</span>
                        ${edu.is_starred ? 'Unstar' : 'Star'}
                        <span class="star-count">${escapeHtml(edu.star_count)}</span>
                    </button>
                </form>
                ${editHtml}
                ${deleteHtml}
            </div>
        `;
        return article;
    }

    /** Mengambil data pendidikan dari API (opsional dengan kata kunci) lalu menampilkannya. */
    async function fetchEducations(query = '') {
        // Batalkan request lama supaya hasil pencarian lama tidak menimpa hasil yang baru
        if (abortController) abortController.abort();
        abortController = new AbortController();

        showState({ loading: true });
        try {
            const url = query ? `${API_URL}?q=${encodeURIComponent(query)}` : API_URL;
            const response = await fetch(url, {
                headers: { 'Accept': 'application/json' },
                signal: abortController.signal,
            });
            // fetch tidak melempar error untuk status 4xx/5xx, jadi dicek manual
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const educations = await response.json();
            if (educations.length === 0) {
                emptyMessage.textContent = query
                    ? `Tidak ada riwayat pendidikan yang cocok dengan "${query}".` // textContent -> aman
                    : 'Belum ada riwayat pendidikan yang ditambahkan.';
                showState({ empty: true });
                return;
            }

            timeline.innerHTML = '';
            educations.forEach(item => timeline.appendChild(buildTimelineItem(item)));
            showState({ list: true });
        } catch (error) {
            if (error.name === 'AbortError') return; // dibatalkan sengaja, bukan error
            console.error('Gagal memuat education:', error);
            showState({ error: true });
        }
    }

    function currentQuery() {
        return searchInput.value.trim();
    }

    // ---------- Pencarian dengan debouncing ----------
    searchInput.addEventListener('input', () => {
        // Setiap ketikan me-reset timer, jadi request baru dikirim setelah pengguna berhenti mengetik
        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = setTimeout(() => fetchEducations(currentQuery()), SEARCH_DEBOUNCE_DELAY);
    });

    searchForm.addEventListener('submit', (event) => {
        event.preventDefault(); // jangan reload halaman
        clearTimeout(searchDebounceTimer);
        fetchEducations(currentQuery());
    });

    retryButton.addEventListener('click', () => fetchEducations(currentQuery()));

    // ---------- Tambah pendidikan lewat modal + AJAX (hanya pemilik) ----------
    async function addEducation(event) {
        event.preventDefault();
        const submitButton = educationForm.querySelector('button[type="submit"]');
        submitButton.disabled = true; // cegah klik ganda -> data tersimpan dua kali

        try {
            const response = await fetch(CREATE_URL, {
                method: 'POST',
                // Token CSRF dikirim lewat header; FormData juga sudah membawa csrfmiddlewaretoken
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
                body: new FormData(educationForm),
            });
            // Kalau balasan bukan JSON (mis. halaman error), pakai objek kosong
            const result = await response.json().catch(() => ({}));

            if (response.status === 201) {
                educationForm.reset();
                document.getElementById('add-education-modal').hidePopover();
                showToast('Berhasil', result.message || 'Riwayat pendidikan ditambahkan.', 'success');
                fetchEducations(currentQuery()); // perbarui daftar tanpa reload halaman
            } else {
                // 400 = data tidak valid, 403 = tidak punya hak akses
                showToast('Gagal menambahkan pendidikan', formatServerErrors(result, response.status), 'error');
            }
        } catch (error) {
            console.error('Gagal menambah education:', error);
            showToast('Gagal menambahkan pendidikan', 'Tidak dapat terhubung ke server. Coba lagi.', 'error');
        } finally {
            submitButton.disabled = false;
        }
    }

    // Elemen hanya ada untuk pemilik: cek dulu supaya skrip tidak error di peran lain
    if (educationForm) {
        educationForm.addEventListener('submit', addEducation);
    }

    // ---------- Modal hapus bersama (hanya pemilik) ----------
    if (deleteModal) {
        // Event delegation: satu listener di timeline untuk semua tombol Hapus,
        // karena tombolnya dibuat ulang setiap kali data dimuat.
        timeline.addEventListener('click', (event) => {
            const button = event.target.closest('.js-delete-education');
            if (!button) return;
            // dataset otomatis meng-unescape &lt; dll., lalu textContent menampilkannya sebagai teks biasa
            document.getElementById('delete-education-name').textContent = button.dataset.name;
            document.getElementById('delete-education-form').action =
                buildUrl(section.dataset.deleteUrl, button.dataset.id);
        });
    }

    // ---------- Mulai ----------
    fetchEducations();
})();