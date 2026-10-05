/**
 * Fungsi bantu yang dipakai bersama oleh beberapa halaman (Projects & Education).
 * Dimuat di <head> base.html supaya sudah siap sebelum skrip halaman berjalan.
 */

/**
 * Membaca nilai cookie berdasarkan namanya (dipakai untuk mengambil token CSRF).
 * @param {string} name nama cookie, mis. 'csrftoken'
 * @returns {string|null} nilai cookie, atau null kalau tidak ada
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Mengubah karakter khusus HTML menjadi entity supaya tampil sebagai teks biasa (anti-XSS).
 * Wajib dipakai untuk setiap nilai yang disisipkan lewat innerHTML.
 * @param {*} value nilai apa pun (null/undefined jadi string kosong)
 * @returns {string} teks yang aman disisipkan ke HTML
 */
function escapeHtml(value) {
    return String(value ?? '')
        .replaceAll('&', '&amp;')   // & harus pertama, supaya entity di bawah tidak ter-escape dua kali
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}

/**
 * Mengubah objek error dari form.errors.get_json_data() menjadi satu kalimat.
 * Contoh input: { start_year: [{ message: "Wajib diisi." }] }
 * @param {object} result isi JSON balasan server
 * @param {number} status kode status HTTP (untuk pesan cadangan)
 * @returns {string}
 */
function formatServerErrors(result, status) {
    if (result && result.errors) {
        return Object.values(result.errors).flat().map(error => error.message).join(' ');
    }
    return (result && result.message) || `Terjadi kesalahan (status ${status}).`;
}