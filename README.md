# Laporan Proyek Korean Drama Recommendation - Sirly Ziadatul Mustafidah

## Project Overview

Di era digital saat ini, drama Korea menjadi salah satu hiburan yang sangat populer di berbagai kalangan, mulai dari anak-anak, remaja, hingga dewasa. Banyaknya judul drama Korea yang terus bertambah setiap tahun, seperti pada tahun 2017 hingga 2019 yang mencapai lebih dari 300 judul, membuat penonton memiliki banyak pilihan. Namun, keterbatasan waktu membuat penonton kesulitan menentukan drama mana yang sesuai dengan preferensi mereka.

Sistem rekomendasi bertujuan untuk memberikan pengalaman personalisasi yang lebih baik bagi pengguna sehingga mereka dapat lebih mudah menemukan drama Korea yang sesuai dengan minat mereka. Rekomendasi yang dihasilkan juga harus disesuaikan dengan kesamaan pada alur cerita, genre, serta rating dan preferensi pengguna lain yang memiliki kesamaan selera, sehingga hasil rekomendasi menjadi lebih relevan dan bermanfaat.

Proyek ini bertujuan untuk membangun sistem rekomendasi drama Korea menggunakan pendekatan *content-based filtering* dan *collaborative filtering* untuk memberikan top-N rekomendasi kepada pengguna berdasarkan preferensi atau riwayat mereka.

Referensi:
[1] W. Kristianto, D. E. Herwindiati, and J. Hendryli, "Sistem rekomendasi drama Korea menggunakan metode user-based collaborative filtering," *Jurnal Ilmu Komputer dan Sistem Informasi*, vol. 9, no. 1, pp. 1-6, 2021, Universitas Tarumanagara. doi: 10.24912/jiksi.v9i1.12668.
[2] J. Safitri, V. Atina, and N. A. Sudibyo, "Rancang bangun sistem rekomendasi pemilihan drama korea dengan metode content-based filtering," *INFOTECH: Jurnal Informatika & Teknologi*, vol. 5, no. 2, pp. 175–189, 2024. doi: 10.37373/infotech.v5i2.1235.


## Business Understanding

### Problem Statements
1. Bagaimana cara merekomendasikan drama Korea yang relevan berdasarkan kesamaan konten?
2. Bagaimana memanfaatkan data interaksi pengguna untuk menghasilkan rekomendasi personal?

### Goals
1. Mengembangkan sistem rekomendasi berbasis genre untuk menyarankan drama serupa.
2. Mengembangkan sistem rekomendasi berbasis kolaboratif dari interaksi pengguna rating untuk memberikan rekomendasi personal.

### Solution Approach
- **Content-Based Filtering**: Menggunakan fitur genre untuk menghitung kemiripan antar drama.
- **Collaborative Filtering**: Menggunakan algoritma seperti Matrix Factorization untuk mempelajari pola preferensi pengguna.

## Data Understanding
Dataset yang digunakan adalah kumpulan data drama Korea dari [Kagle - Korean Drama from 2015-2023 with Actors & Reviews](https://www.kaggle.com/datasets/chanoncharuchinda/korean-drama-2015-23-actor-and-reviewmydramalist), yang terdiri dari 4 file csv dengan 1.752 drama dari MyDramaList. Dari dataset tersebut akan diambil 2 file csv yang akan dipakai dalam kasus ini yaitu file korean_drama.csv dan reviews.csv. Selain itu, dilakukan scraping dataset mandiri dari mydramalist untuk mendapatkan informasi yang belum disediakan pada dataset tersebut.

Beberapa fitur yang akan digunakan:
- `kdrama_id`: id untuk drama korea
- `user_id`: id untuk user
- `drama_name`: judul drama korea
- `year`: tahun drama tersebut tayang
- `tot_eps`: total seluruh episode drama
- `genres`: daftar genre dari drama
- `platform`: daftar platform yang menayangkan drama
- `story_score`: rating atau score yang diberikan oleh user untuk cerita dari drama tersebut
- `rewatch_value_score`: score dari user untuk menonton ulang drama
- `overall_score`: rating atau score keseluruhan yang diberikan oleh user dari cerita, music, acting, dan rewatch_value
- `user_id`, `drama_id`, `overall_score`: interaksi pengguna untuk collaborative filtering 

Variabel-variabel pada korean_drama.csv dataset adalah sebagai berikut:
- kdrama_id : kode unik untuk kdrama
- drama_name : judul kdrama
- year : tahun tayang kdrama
- director : nama director dari kdrama
- screenwriter : nama penulis script kdrama
- country : negara asal drama, karena khusus drama korea, maka country semua adalah South Korea
- type : jenis show, karena khusus drama, maka semua berisi Drama
- tot_eps : total seluruh episode kdrama
- duration : durasi per episode dari drama dalam satuan detik
- start_dt : tanggal pertama tayang kdrama
- end_dt : tanggal akhir tayang kdrama
- aired_on : hari tayang kdrama di saluran televisi atau platform
- org_net : platform yang menayangkan kdrama
- content_rt : rating dari kdrama
- synopsis : ringkasan atau cerita singkat tentang kdrama
- rank : rank kdrama dalam mydramalist berdasarkan rating
- pop : rank kdrama dalam mydramalist berdasarkan popularity atau berapa banyak yang sudah menonton drama tersebut

Variabel-variabel pada reviews.csv dataset adalah sebagai berikut:
- user_id : kode unik untuk user
- title : judul kdrama
- story_score : rating atau score yang diberikan oleh user untuk cerita dari drama tersebut
- acting_cast_score : score yang diberikan oleh user untuk akting dari para cast
- rewatch_value_score :  score dari user untuk menonton ulang drama
- overall_score : rating atau score keseluruhan yang diberikan oleh user dari cerita, music, acting, dan rewatch_value
- review_test : text review user terhadap kdrama
- ep_watched : jumlah episode yang sudah ditonton oleh user
- n_helpful : total user lain yang mengatakan bahwa review tersebut membantu

Variabel-variabel pada kdrama_genre_platforms.csv dataset adalah sebagai berikut:
- title : judul kdrama
- genres : list genre dalam kdrama
- where_to_watch : list platform yang menayangkan kdrama tersebut

### EDA (Exploratory Data Analysis)
- Distribusi rating pengguna
- Visualisasi genre paling populer
- Visualisasi platform paling populer

**Insight**:
- Genre "Romance", "Drama", dan "Comedy" paling dominan
- Platform "Viki", "Netflix", dan "Kocowa" paling banyak menayangkan drama korea
- overall_score rata-rata drama berada di kisaran 7.6 (7.0 - 8.0)

## Data Preprocessing
1. Maping reviews_df dan genres_df agar memiliki kdrama_id yang akan digunakan sebagai interaksi
2. Mengambil fitur-fitur tertentu yang akan digunakan
    - kdrama_df (`kdrama_id`, `drama_name`, `year`, `tot_eps`)
    - genre_df (`kdrama_id`, `drama_name`, `genres`, `platform`)
    - reviews_df (`user_id`, `kdrama_id`, `story_score`, `rewatch_value_score`, `overall_score`)
2. Membersihkan nilai kosong pada kolom penting (`genres`, `platform`)
    - Menghapus baris Nan untuk genres
    - Mengisi nilai Nan dengan "Not Available" untuk 'platform'

## Data Preparation [Content-Based Filtering]
1. Filter fitur yang akan digunakan, yaitu:
    - `kdrama_id`
    - `drama_name`
    - `year`
    - `genres`
    - `platform`
    - `tot_eps`
2. Cek duplikasi dan menghapus duplikasi
3. Normalisasi text untuk genre dan platform dengan menjadikan dalam bentuk list dan menghapus spasi berlebih

## Data Preparation [Collaborative-Based Filtering]
1. Filter fitur yang akan digunakan, yaitu:
    - `user_id`
    - `kdrama_id`
    - `overall_score`
    Output yang akan ditampilkan untuk rekomendasi, yaitu:
    - `drama_name`
    - `year`
    - `genres`
    - `tot_eps`
2. Mengubah user_id dan kdrama_id dalam bentuk list dan melakukan encoding
3. Mengubah nilai dari overall_score agar berbentuk float

## Modeling
Tahapan ini membahas mengenai model sisten rekomendasi yang Anda buat untuk menyelesaikan permasalahan. Sajikan top-N recommendation sebagai output.

### Modeling Content-based Filtering
1. Mengubah genre menjadi bentuk *multi-label encoding binary* untuk content-based.
2. Cek cosine similiarity berdasarkan genre
3. Mendapatkan rekomendasi drama berdasarkan kesamaan genre dan kemudian difilter berdasarkan platform yang diinginkan

### Modeling Collaborative-based Filtering
1. Normalisasi nilai overall_score dengan range (0-1)
2. Membagi data untuk training dan validation dengan perbandingan [80:20]
3. Training dengan model berbasis embedding neural network (RecommenderNet) yang dibangun menggunakan arsitektur tf.keras.Model
    Struktur Model:
    - User Embedding: merepresentasikan pengguna sebagai vektor berdimensi laten.
    - Item (K-Drama) Embedding: merepresentasikan drama sebagai vektor berdimensi laten.
    - Bias Embedding: menambahkan bias pengguna dan bias item untuk akurasi prediksi.
    - Dense Layer + Sigmoid: lapisan akhir yang menyaring hasil prediksi ke dalam rentang 0–1 (probabilitas minat pengguna terhadap drama).
4. Compile model:
    - Loss Function: MeanSquaredError
    - Optimizer: Adam dengan learning rate 0.0001
    - Metrik evaluasi: RootMeanSquaredError (RMSE)

### Kelebihan dan Kekurangan Pendekatan

- **Content-Based Filtering**
   - Kelebihan: Tidak memerlukan data pengguna lain, cocok untuk pengguna baru.
   - Kekurangan: Sulit memberi rekomendasi di luar preferensi awal (kurang eksploratif).

- **Collaborative Filtering**
   - Kelebihan: Dapat memberikan rekomendasi yang lebih bervariasi dan personal.
   - Kekurangan: Memerlukan banyak data interaksi dan tidak bekerja optimal untuk user/drama baru.

## Result

Showing recommendations for users: 55ef1033f90b39d19c265fe43109bfbe

Kdrama with high scores from user
╒═════╤════════════════════════════╤═════════╤═══════════╤════════════════════════════════════╕
│   # │ Judul                      │   Tahun │   Episode │ Genre                              │
╞═════╪════════════════════════════╪═════════╪═══════════╪════════════════════════════════════╡
│   1 │ Extraordinary Attorney Woo │    2022 │        16 │ Law, Romance, Life, Drama          │
├─────┼────────────────────────────┼─────────┼───────────┼────────────────────────────────────┤
│   2 │ To.Two                     │    2021 │         8 │ Thriller, Psychological, Youth     │
├─────┼────────────────────────────┼─────────┼───────────┼────────────────────────────────────┤
│   3 │ Back to the 2008           │    2021 │        10 │ Romance, Youth                     │
├─────┼────────────────────────────┼─────────┼───────────┼────────────────────────────────────┤
│   4 │ Zombie Detective           │    2020 │        24 │ Thriller, Mystery, Comedy, Fantasy │
├─────┼────────────────────────────┼─────────┼───────────┼────────────────────────────────────┤
│   5 │ Tong: Memories             │    2016 │        12 │ Action, Youth, Drama               │
╘═════╧════════════════════════════╧═════════╧═══════════╧════════════════════════════════════╛

Top 10 kdrama recommendation
╒═════╤════════════════════════════════╤═════════╤═══════════╤═════════════════════════════════════════╕
│   # │ Judul                          │   Tahun │   Episode │ Genre                                   │
╞═════╪════════════════════════════════╪═════════╪═══════════╪═════════════════════════════════════════╡
│   1 │ She Makes My Heart Flutter     │    2022 │         5 │ Comedy, Romance                         │
├─────┼────────────────────────────────┼─────────┼───────────┼─────────────────────────────────────────┤
│   2 │ Our Blues                      │    2022 │        20 │ Romance, Life, Drama, Melodrama         │
├─────┼────────────────────────────────┼─────────┼───────────┼─────────────────────────────────────────┤
│   3 │ Nobody Knows                   │    2020 │        16 │ Thriller, Mystery, Drama, Melodrama     │
├─────┼────────────────────────────────┼─────────┼───────────┼─────────────────────────────────────────┤
│   4 │ Children of Nobody             │    2018 │        32 │ Thriller, Mystery, Psychological, Drama │
├─────┼────────────────────────────────┼─────────┼───────────┼─────────────────────────────────────────┤
│   5 │ Life on Mars                   │    2018 │        16 │ Action, Mystery, Psychological, Comedy  │
├─────┼────────────────────────────────┼─────────┼───────────┼─────────────────────────────────────────┤
│   6 │ My Mister                      │    2018 │        16 │ Psychological, Life, Drama              │
├─────┼────────────────────────────────┼─────────┼───────────┼─────────────────────────────────────────┤
│   7 │ Good Manager                   │    2017 │        20 │ Business, Comedy, Crime, Drama          │
├─────┼────────────────────────────────┼─────────┼───────────┼─────────────────────────────────────────┤
│   8 │ The Sound of Your Heart        │    2016 │        20 │ Comedy, Life, Sitcom                    │
├─────┼────────────────────────────────┼─────────┼───────────┼─────────────────────────────────────────┤
│   9 │ D-Day                          │    2015 │        20 │ Drama, Medical                          │
├─────┼────────────────────────────────┼─────────┼───────────┼─────────────────────────────────────────┤
│  10 │ Heard It Through the Grapevine │    2015 │        30 │ Comedy, Romance, Melodrama              │
╘═════╧════════════════════════════════╧═════════╧═══════════╧═════════════════════════════════════════╛

## Evaluation
Metrik evaluasi utama yang digunakan dalam proyek ini adalah:
- Root Mean Squared Error (RMSE)
RMSE dipilih karena proyek ini merupakan problem regresi, di mana model diminta memprediksi nilai numerik kontinu. RMSE memberikan gambaran seberapa besar rata-rata kesalahan prediksi model terhadap nilai sebenarnya, dalam satuan yang sama dengan target. Semakin kecil nilai RMSE, semakin akurat prediksi model.
- Loss (Mean Squared Error - MSE)
Digunakan sebagai fungsi loss selama proses pelatihan untuk mengoptimalkan bobot model. Nilai ini juga dipantau selama pelatihan sebagai indikator konvergensi model.

Berdasarkan hasil pelatihan selama 55 epoch, diperoleh hasil sebagai berikut:
- RMSE pada data pelatihan: 0.1709
- RMSE pada data validasi: 0.2248

Nilai RMSE validasi yang cukup rendah menunjukkan bahwa model mampu memprediksi dengan baik terhadap data yang belum pernah dilihat sebelumnya. Selain itu, tidak terdapat perbedaan yang signifikan antara RMSE pelatihan dan validasi, yang berarti model tidak mengalami overfitting