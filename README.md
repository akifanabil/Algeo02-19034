# Tugas Besar 2 Aljabar Linier dan Geometri
Proyek tugas besar ke-2 mata kuliah IF2123 Aljabar Linier dan Geometri, membuat *search engine* menggunakan *cosine similarity*. Dokumen-dokumen diambil dari https://www.alodokter.com.
## Daftar Isi
- [Informasi Kelompok](#informasi-kelompok)
- [Screenshot](#screenshot)
- [Setup](#setup)
## Informasi Kelompok
1. Nama kelompok: duabelaslimalima
2. Kelas: K-03
3. Anggota:
    - 13519034 Ruhiyah Faradishi Widiaputri
    - 13519063 Melita
    - 13519179 Akifa Nabil Ufairah
## Screenshot
![Screenshot Search Engine](screenshot.png?raw=true "Screenshot Search Engine")
## Setup
1. Install `python3` dari https://www.python.org/downloads/
2. Install *library-library* berikut dengan mengetikkan *command* pada terminal jika belum tersedia:
    1. Flask `pip install flask`
    2. BeautifulSoup4 `pip install beautifulsoup4`
    3. Sastrawi `pip install Sastrawi`
    4. Pandas `pip install pandas`
    5. Numpy `pip install numpy`
    6. Scipy `pip install scipy`
    7. Requests `python -m pip install requests`
3. Terdapat dua mode dari pencarian:
    1. *Web scraping*, yaitu mengambil artikel dari situs alodokter. Jika akan menggunakan mode ini, pastikan perangkat Anda tersambung dengan internet, lalu jalankan `index.py`
    2. File .txt. Jika akan menggunakan mode ini, jalankan `index2.py`  
 (PENTING: Jalankan file dari *directory* Algeo! Pada terminal, gunakan: `python src/index2.py` untuk index2.)
 ![Contoh menjalankan program](screenshot3.png?raw=true "Contoh menjalankan program")
4. Buka alamat website yang dituliskan (`http://127.0.0.1:5000/` atau `localhost:5000`) menggunakan *browser* seperti Mozilla Firefox, Google Chrome, Microsoft Edge, dll.
![Contoh alamat website](screenshot2.png?raw=true "Contoh alamat website")
5. Jika menggunakan mode *file* .txt, *upload file* yang ingin digunakan pada halaman *Uploader*. *Link* menuju halaman terdapat di bagian bawah halaman utama *website*. Setelah meng-*upload*, lakukan *restart* `index2.py` agar *file* ter-*update*.
