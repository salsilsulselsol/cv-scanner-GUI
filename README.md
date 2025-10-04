# Scanner Dokumen GUI (OpenCV + Tkinter)

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

Aplikasi desktop buat scan dokumen dari foto. Bisa deteksi area dokumen otomatis, bisa juga diatur manual kalau hasilnya kurang pas. Dibuat sebagai proyek untuk belajar Computer Vision dari dasar.

---

### 🎬 Demo Singkat


---

### Fitur

* **Tampilan GUI:** Dibuat pakai Tkinter, jadi bisa langsung jalan di Windows, Mac, atau Linux.
* **Pilih File:** Ada tombol buat buka file explorer dan pilih gambar mana saja.
* **Deteksi Otomatis:** Program coba nebak area dokumen di gambar pakai serangkaian proses OpenCV.
* **Penyesuaian Manual:** Kalau tebakan otomatisnya salah, ada 4 titik merah yang bisa digeser-geser untuk memperbaiki area potong.
* **Tuning Parameter:** Ada slider buat mengatur parameter Canny dan Hough Transform untuk membantu deteksi otomatis.
* **Filter B&W:** Ada checkbox buat mengubah hasil scan jadi hitam-putih.
* **Simpan Hasil:** Hasil scan bisa disimpan jadi file JPG atau PNG.

---

### Dibuat Pakai:

* **Python**
* **OpenCV**
* **NumPy**
* **Pillow (PIL)**
* **Tkinter**

---

### Cara Kerja Algoritma

Proses deteksi otomatisnya berjalan lewat beberapa tahap:
1.  **Hapus Bayangan:** Mencoba meratakan pencahayaan di gambar.
2.  **Deteksi Tepi:** Mencari semua garis pinggir objek di gambar pakai Canny.
3.  **Deteksi Garis:** Dari semua tepian, mencari 4 kandidat garis lurus yang paling mungkin jadi batas dokumen pakai Hough Transform.
4.  **Hitung Sudut:** Menghitung titik potong dari 4 garis tersebut untuk dapat 4 sudut.
5.  **Koreksi Perspektif:** "Meluruskan" gambar berdasarkan 4 sudut yang sudah ditemukan atau yang sudah diatur manual.

---

### Cara Pakai

1.  **Prasyarat:** Pastikan Python 3 sudah ter-install.

2.  **Clone repositori ini:**
    ```bash
    git clone [URL_REPO_ANDA]
    cd cv-scanner-GUI
    ```

3.  **Buat dan aktifkan *virtual environment*:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

4.  **Install semua paket yang dibutuhkan:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Jalankan aplikasi:**
    ```bash
    python app.py
    ```
    Setelah itu, tinggal klik tombol-tombol yang ada di aplikasi. Alurnya cukup jelas: Pilih Gambar -> Deteksi & Sesuaikan -> Simpan.

---

### Keterbatasan

Algoritmanya masih klasik, jadi gampang bingung kalau:
* Latar belakangnya terlalu ramai.
* Kontras antara kertas dan latar belakang terlalu rendah.
* Kertasnya terlipat atau kusut parah.

Solusi buat masalah-masalah ini biasanya pakai Deep Learning, tapi itu cerita lain. Untuk sekarang, fitur tuning parameter dan penyesuaian manual sudah cukup membantu.

