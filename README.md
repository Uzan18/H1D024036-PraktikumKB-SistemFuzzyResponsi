# CardioFuzzy - Sistem Inferensi Fuzzy Mamdani

Ini adalah project praktikum Sistem Pakar untuk membuat aplikasi berbasis Logika Fuzzy (Metode Mamdani). Sistem ini berfungsi untuk memprediksi tingkat risiko penyakit jantung berdasarkan tiga parameter klinis, yaitu: Tekanan Darah, Kadar Kolesterol, dan Usia.

Project ini dibuat menggunakan **Python** (dengan bantuan library `scikit-fuzzy` untuk perhitungan matematikanya) dan **Flask** sebagai backend/API-nya. Bagian tampilannya (frontend) dibuat responsif menggunakan **Tailwind CSS**. Semuanya sudah di-setting agar gampang di-deploy secara *serverless* menggunakan **Vercel**.

## Cara Kerja Sistem

Secara sederhana, sistem ini bekerja melalui tiga tahapan utama logika fuzzy mamdani:

1. **Fuzzifikasi**: Sistem menerima input angka pasti (*crisp input*) dari form web (misal tekanan darah 120, usia 45). Lalu, nilai ini dipetakan ke dalam himpunan fuzzy (misal: "Muda", "Paruh Baya", "Tua") menggunakan fungsi keanggotaan trapesium (*trapmf*). Saya pakai fungsi trapesium karena parameter medis biasanya punya rentang konstan yang tegas di bagian puncaknya (lebih akurat daripada segitiga biasa).
2. **Inferensi Rule Base**: Nilai fuzzy yang didapat tadi dicocokkan dengan 18 aturan (*rule*) logika yang sudah ditetapkan di sistem. (Contoh aturan: *JIKA Tekanan Darah Normal DAN Kolesterol Cukup Tinggi DAN Usia Paruh Baya, MAKA Risiko Sedang*).
3. **Defuzzifikasi**: Hasil penggabungan dari seluruh aturan yang cocok akan diubah kembali menjadi nilai persentase risiko (0-100%) menggunakan metode **Centroid** (mengambil titik berat/tengah dari area kurva hasil). Nilai inilah yang akhirnya ditampilkan di layar.

## Struktur Direktori

Agar kompatibel dengan Vercel, foldernya sengaja diatur seperti ini:
- `api/index.py` : File utama backend Flask dan semua hitung-hitungan logic fuzzy-nya ada di sini.
- `templates/index.html` : Tampilan utama web. Di dalamnya sudah disematkan script JS untuk interaksi animasi dan Fetch API ke backend.
- `requirements.txt` : Daftar library Python yang dipakai.
- `vercel.json` : Konfigurasi routing supaya server Vercel tahu ini adalah aplikasi Flask serverless.

## Cara Menjalankan di Lokal (Localhost)

Kalau mau coba run atau ubah kode di laptop sendiri, caranya gampang banget:

1. Pastikan sudah install Python. 
2. Install library yang dibutuhkan lewat terminal:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalanin server Flask-nya:
   ```bash
   python api/index.py
   ```
4. Buka web browser, lalu akses ke `http://127.0.0.1:5005`.

> **Catatan Khusus Pengguna Python 3.12 ke atas**: 
> Di versi Python terbaru, modul `imp` bawaan sudah dihapus secara permanen, padahal library `scikit-fuzzy` masih membutuhkannya secara internal. Makanya, di bagian paling atas file `api/index.py` saya sudah menambahkan beberapa baris kode khusus (*monkey-patch*) untuk mengakali modul `imp` tersebut biar aplikasinya tetap bisa jalan mulus tanpa error `ModuleNotFoundError`.

## Cara Deploy ke Vercel

1. Push atau upload seluruh isi folder project ini ke repository GitHub kamu.
2. Login ke Vercel, lalu klik **Add New Project**.
3. Import repository GitHub tadi.
4. Langsung klik **Deploy**. Nggak perlu ubah setting apa-apa lagi karena file `vercel.json` sudah ngatur rute aplikasinya.
