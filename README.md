Nama : Muhammad Iqbal
NPM : 2506657075
Kelas : PBP C

[LOG] latihan branch 1

[TUGAS 1]
1. Saya pakai beberapa elemen semantik seperti header, nav, main, section, dan footer supaya struktur halamannya jelas, bagian mana yang navigasi, bagian mana isi utama, bagian mana yang footer dibanding  pakai div semua. 

2. Tantangan yang saya rasakan adalah menentukan urutan tampilan waktu pindah dari desktop ke HP. Di desktop, foto dan teks bisa disandingkan jadi dua kolom, tapi di layar kecil semuanya harus ditumpuk jadi satu kolom, 

3. Karena websitenya masih murni HTML/CSS, semua isi (bio, foto, dll) harus saya tulis manual di file HTML kalau mau update sesuatu, saya harus edit kode dan upload ulang nggak bisa diubah langsung dari halaman itu sendiri.

AI DISCLOSURE
> Tools Yang Digunakan : Claude (Antrophic)

> Bagian Yang Dibantu AI:
AI membantu saya dalam menulis kode di bagian style.css dan index.html, AI membantu saya membuat section education selain itu AI nya juga mengajari saya cara branching agar commit nya terlihat rapih dan professional sehingga sesuai dengan ketentuan git commit pada tugas.

> Strategi Prompting:
Saya menjelaskan dulu konteks untuk mengerjakan tugas ini dengan memberikan referensi dan arahan desain serta konteks berupa file yang digunakan agar AI paham sepenuhnya apa mau saya dan saya bisa merealisasikan keinginan saya.

>Bagian yang Saya Kerjakan Sendiri:
Kontribusi saya ada pada ide saya untuk membuat section education, dimana section education lazim dalam web portofolio serta saya memberikan data dan ide untuk bagaimana design web saya sendiri.

>Evaluasi terhadap hasil AI:
Menurut saya AI sudah memberikan hasil yang sangat memuaskan bahkan melampaui batasan saya, oleh karena itu saya tidak setuju dengan usulan AI yang terlalu advanced dalam level saya sehingga saya meminta untuk dikerjakan sesuai dengan kemampuan saya agar saya bisa belajar sendiri.

>Log Percakapan:  https://claude.ai/share/76622cb9-754d-4495-85e5-5583a65306af
[TUGAS 1]

[TUGAS 2]
1. Saat buka halaman portofolio misal /projects/, django akan memproses permintaan tersebut melalui beberapa tahap.Pertama request ke urls.py proyek, untuk ditentukan aplikasi mana yang akan menangani url tersebut lalu diteruskan ke urls.py aplikasi.Di main/urls.py django mencari URL yang cocok lalu menjalakan view untuk mengatur logika halaman , jika butuh data view akan mengambil dari model.Model berhubungan dengan database dan menyimpan data ,lalu data tersebut diberikan oleh view kepada template melalui context.terakhir template mengatur bagaimana data ditampilkan dalam HTML. Django mengirimkan ke browser untuk dilihat pengguna 
Alurnya 
>Browser → urls.py proyek → urls.py aplikasi → View → Model → View → Template → Browser

2. Data disimpan di model agar gampang terhubung dengan database, jadi bisa diubah tidak secara langsung di html tapi melalui database.Jika data di tulis langsung / di hard code , setiap kali mengubah harus mengedit file html sehingga tidak praktis

3. Perbedaan makemigrations dan migrate adalah makemigrations membuat file migrasi berdasarkan perubahan model kalau migrate digunakan untuk mengirim/menerapkan file tersebut ke database

AI Disclosure:

Tools yang digunakan: Claude (Antrophic)

Bagian yang dibantu AI: 
AI membantu saya memahami konteks tugas dan mengarahkan hal yang harus saya lakukan serta memberikan kode untuk di tulis di dalam file. serta membantu mengarahkan saya untuk menjawab refleksi nomor pertama 

Strategi Prompting:
Saya memberikan file agar AI memahami konteks dalam mengerjakan tugas tugasnya lalu saya memberi tugas spesifik agar AI paham keinignan saya dan saya memberikan feedback dari proses yang sudah disarankan oleh AI

Bagian yang saya kerjakan Sendiri:
Saya mengubah file yang diarahkan dan melakukan makemigrate dan migration untuk template 

