# -*- coding: utf-8 -*-
"""Proyek Akhir: Membuat Model Sistem Rekomendasi.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ghhNBHV-6IxAe-fTeGS-f0t4rb6YgkzA

# Proyek Akhir: Membuat Model Sistem Rekomendasi

# Import Libarary
"""

import pandas as pd
import numpy as np
import ast
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns

from tabulate import tabulate
from pathlib import Path
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import mean_squared_error, mean_absolute_error
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.callbacks import ReduceLROnPlateau

"""# Data Understanding"""

kdrama_df = pd.read_csv('https://raw.githubusercontent.com/sirly82/kdrama-recommendation/refs/heads/main/dataset/korean_drama.csv')
reviews_df = pd.read_csv('https://raw.githubusercontent.com/sirly82/kdrama-recommendation/refs/heads/main/dataset/reviews.csv')
genres_df = pd.read_csv('https://raw.githubusercontent.com/sirly82/kdrama-recommendation/refs/heads/main/scraping-data/kdrama_genres_platforms.csv')

"""# Load Dataset"""

kdrama_df.head()

reviews_df.head()

genres_df.head()

print('Jumlah data korean drama: ', len(kdrama_df.kdrama_id.unique()))
print('Jumlah data reviews korean drama: ', len(reviews_df.user_id.unique()))
print('Jumlah data genres korean drama: ', len(genres_df))

"""# Univariate Exploratory Data Analysis

## kdrama dataset
"""

kdrama_df.info()

print('Banyak data: ', len(kdrama_df.kdrama_id.unique()))
print('Judul Drama Korea: ', kdrama_df.drama_name.unique())

"""## reviews dataset"""

reviews_df.info()

reviews_df.describe()

"""## genres dataset"""

genres_df.info()

print('Banyak data: ', len(genres_df.title.unique()))
print('Genre Drama: ', genres_df.genres.unique())

print('Platforms Drama: ', genres_df.where_to_watch.unique())

"""Visualisasi Genre Paling Populer"""

genres_all = genres_df['genres'].dropna().str.split(', ')
all_genres_flat = [genre for sublist in genres_all for genre in sublist]

genre_counts = pd.Series(all_genres_flat).value_counts()
top_genres = genre_counts.head(10)

plt.figure(figsize=(10,6))
sns.barplot(x=top_genres.values, y=top_genres.index, palette="viridis")
plt.title('Top 10 Most Popular K-Drama Genres')
plt.xlabel('Number of Dramas')
plt.ylabel('Genre')
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

"""Visualisasi Plarform paling Populer

Visualisasi Genre paling banyak
"""

platform_all = genres_df['where_to_watch'].dropna().str.split(', ')
all_platform_flat = [platform for sublist in platform_all for platform in sublist]

platform_counts = pd.Series(all_platform_flat).value_counts()
top_platform = platform_counts.head(10)

plt.figure(figsize=(10,6))
sns.barplot(x=top_platform.values, y=top_platform.index, palette="viridis")
plt.title('Top 10 Most Popular Platforms')
plt.xlabel('Number of Dramas')
plt.ylabel('Platform')
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

"""# Data Preprocessing

## Mapping reviews_df
"""

# Membuat mapping drama_name ke drama_id
mapping = dict(zip(kdrama_df['drama_name'].str.lower().str.strip(), kdrama_df['kdrama_id']))

# Membersihkan judul di reviews_df agar konsisten
reviews_df['title_clean'] = reviews_df['title'].str.lower().str.strip()

# Menambahkan kolom kdrama_id berdasarkan judul drama
reviews_df['kdrama_id'] = reviews_df['title_clean'].map(mapping)

# Cek Missing Judul ketika mapping
missing = reviews_df[reviews_df['kdrama_id'].isnull()]['title'].unique()
print("Judul drama yang tidak ditemukan di kdrama_df:", missing)

cols = reviews_df.columns.tolist()
cols.remove('kdrama_id')
cols.remove('title_clean')

# Cari index kolom 'title'
idx = cols.index('title')
cols.insert(idx, 'kdrama_id')

# Reorder dataframe dengan urutan kolom baru
reviews_df = reviews_df[cols]

reviews_df.head()

"""## Mapping genres_df"""

# Membersihkan kdrama_name di genres_df agar konsisten
genres_df['kdrama_name_clean'] = genres_df['title'].str.lower().str.strip()

# Menambahkan kolom kdrama_id berdasarkan judul drama
genres_df['kdrama_id'] = genres_df['kdrama_name_clean'].map(mapping)

# Cek Missing Judul ketika mapping
missing = genres_df[genres_df['kdrama_id'].isnull()]['title'].unique()
print("Judul drama yang tidak ditemukan di kdrama_df:", missing)

cols = genres_df.columns.tolist()
cols.remove('kdrama_id')
cols.remove('kdrama_name_clean')

idx = cols.index('title')
cols.insert(idx, 'kdrama_id')

# Reorder dataframe dengan urutan kolom baru
genres_df = genres_df[cols]

genres_df

"""## Mengetahui Korean Drama Info"""

kdrama_df.info()

kdrama_info_df = kdrama_df[['kdrama_id', 'drama_name', 'year', 'tot_eps']]
kdrama_info_df

"""## Mengetahui Genre"""

kdrama_genre_df = pd.merge(kdrama_df[['kdrama_id', 'drama_name']], genres_df[['kdrama_id', 'genres']], on='kdrama_id', how='left')
kdrama_genre_df

missing_genres = kdrama_genre_df[kdrama_genre_df['genres'].isna()]['drama_name'].unique()
print("Judul drama yang tidak ada genre:", missing_genres)

print("Jumlah kdrama tanpa genre:", len(missing_genres))

"""## Mengetahui Platforms Drama"""

kdrama_platform_df = pd.merge(
    kdrama_df[['kdrama_id', 'drama_name', 'org_net']],
    genres_df[['kdrama_id', 'where_to_watch']].rename(columns={'where_to_watch': 'platform'}),
    on='kdrama_id',
    how='left'
)

kdrama_platform_df['platform'] = kdrama_platform_df['platform'].fillna(kdrama_platform_df['org_net'])
kdrama_platform_df.drop(columns=['org_net'], inplace=True)

kdrama_platform_df

missing_ott = kdrama_platform_df[kdrama_platform_df['platform'].isna()]['drama_name'].unique()
print("Jumlah kdrama tanpa platform:", len(missing_ott))

"""## Menggabung Data dengan fitur Judul Kdrama, Genre, dan Original Network"""

all_kdrama_rate_df = reviews_df[['user_id', 'kdrama_id', 'story_score', 'rewatch_value_score', 'overall_score']]
all_kdrama_rate_df.head()

all_kdrama_info_df = pd.merge(all_kdrama_rate_df, kdrama_info_df[['kdrama_id', 'drama_name', 'year', 'tot_eps']], on='kdrama_id', how='left')
all_kdrama_info_df.head()

all_kdrama_name_df = pd.merge(all_kdrama_info_df, kdrama_genre_df[['kdrama_id', 'genres']], on='kdrama_id', how='left')
all_kdrama_name_df.head()

all_kdrama_df = pd.merge(all_kdrama_name_df, kdrama_platform_df[['kdrama_id', 'platform']], on='kdrama_id', how='left')
all_kdrama_df.head()

"""# Data Preparation

## Mengatasi Missing Value
"""

all_kdrama_clean_df = all_kdrama_df.copy()

all_kdrama_clean_df.isnull().sum()

"""Membersihkan missing value pada column genres dengan menghapusnya"""

all_kdrama_clean_df = all_kdrama_clean_df.dropna(subset=['genres'])

"""Mengisi data Nan pada coloum org_net dengan Not Available"""

all_kdrama_clean_df['platform'] = all_kdrama_clean_df['platform'].fillna('Not Available')

"""Cek Kembali Missing Value"""

all_kdrama_clean_df.isna().sum()

"""## Finishing"""

fix_kdrama_df = all_kdrama_clean_df.copy()
fix_kdrama_df.head()

"""# **Model Development dengan Content-based Filtering**

## Filter Data yang Dibutuhkan

Mengambil data kdrama_id, drama_name, genres, dan platform
"""

content_filter_df = fix_kdrama_df[['kdrama_id', 'drama_name', 'year', 'genres', 'platform', 'tot_eps']].copy()
content_filter_df

"""Cek duplikasi data"""

dup_count = content_filter_df['kdrama_id'].duplicated().sum()
print('Jumlah data duplikat:', dup_count)

"""Menghapus duplikasi data"""

content_filter_df = content_filter_df.drop_duplicates(subset='kdrama_id').copy()

"""## Text Normalization for Genres and Platforms

Karena tiap genre dan platform memiliki banyak values, maka perlu displit terlebih dahulu untuk dijadikan bentuk list
"""

content_filter_df['genres'] = content_filter_df['genres'].str.split(',')
content_filter_df['platform'] = content_filter_df['platform'].str.split(',')

"""Merapikan spasi setelah split"""

content_filter_df['genres'] = content_filter_df['genres'].apply(
    lambda x: [i.strip() for i in x] if isinstance(x, list) else x
)

content_filter_df['platform'] = content_filter_df['platform'].apply(
    lambda x: [i.strip() for i in x] if isinstance(x, list) else x
)

"""Cek hasil split"""

print(content_filter_df['platform'].iloc[5])

content_filter_df

"""## Label Encoding

Melakukan label encoding untuk setiap genre dan platform pada dataset
"""

mlb_genre = MultiLabelBinarizer()
genre_encoded = mlb_genre.fit_transform(content_filter_df['genres'])

"""Cek hasil encode dari genre"""

genre_encoded

"""## Cosine Similiarity

Menghitung cosine similiarity untuk genre
"""

genre_similarity = cosine_similarity(genre_encoded)

print(genre_similarity)

genre_sim_df = pd.DataFrame(genre_similarity, index=content_filter_df['drama_name'], columns=content_filter_df['drama_name'])
print('Shape:', genre_sim_df.shape)

genre_sim_df.sample(10, axis=0).sample(5, axis=1)

"""Menggabungkan hasil encode genre dan platform

## Mendapatkan Rekomendasi
"""

def genre_recommendations(drama_title, similarity_matrix, drama_info, top_k=5):
    """
    Rekomendasi drama berdasarkan kemiripan genre.

    Parameter:
    -----------
    drama_title : str
        Judul drama yang dijadikan acuan rekomendasi.
    similarity_matrix : pd.DataFrame
        Matriks kemiripan antar drama (index dan kolom adalah judul drama).
    drama_info : pd.DataFrame
        Dataframe yang berisi informasi drama (minimal kolom 'drama_name' dan info lain).
    top_k : int, default 5
        Jumlah rekomendasi yang diinginkan.

    Return:
    -----------
    pd.DataFrame
        Dataframe drama rekomendasi dengan informasi yang relevan.
    """

    if drama_title not in similarity_matrix.columns:
        raise ValueError(f"Drama '{drama_title}' tidak ditemukan di similarity matrix.")

    # Ambil similarity scores drama yang ditentukan
    sim_scores = similarity_matrix[drama_title]

    # Ambil top_k+1 terbesar (salah satunya pasti drama itu sendiri)
    closest = sim_scores.nlargest(top_k+1).index.drop(drama_title, errors='ignore')[:top_k]

    # Filter drama_info yang termasuk dalam rekomendasi
    recommendations = drama_info[drama_info['drama_name'].isin(closest)].reset_index(drop=True)

    return recommendations

drama_name_key = 'The Devil Judge'
drama_total = 10

drama_name_key = input('Masukkan Nama Drama: ')
drama_total = int(input('Masukkan Jumlah Rekomendasi Drama: '))

content_filter_df[content_filter_df['drama_name'].eq(drama_name_key)]

genre_recommendations(drama_name_key, genre_sim_df, content_filter_df, top_k=drama_total)

def platform_filter_recommendations(drama_title, platform_choice, drama_info, similarity_matrix, top_k=drama_total):
    """
    Cari rekomendasi genre dulu, lalu filter hasil rekomendasi itu berdasarkan platform_choice.

    Param:
    - drama_title: str, judul drama input
    - platform_choice: str, platform yang ingin difilter (misal 'VIU')
    - drama_info: DataFrame, info drama dengan kolom 'drama_name', 'platform', dll.
    - similarity_matrix: matrix similarity genre (dipakai di genre_recommendations)
    - top_k: int, jumlah rekomendasi

    Return:
    - DataFrame rekomendasi drama sesuai genre dan platform
    """

    # Dapatkan rekomendasi berdasarkan genre
    genre_recs = genre_recommendations(drama_title, similarity_matrix, drama_info, top_k=drama_total)

    # Filter berdasarkan platform
    filtered_recs = genre_recs[genre_recs['platform'].apply(lambda x: platform_choice in x)]

    # Ambil maksimal top_k setelah filter platform
    filtered_recs = filtered_recs.head(top_k)

    if filtered_recs.empty:
        return f"Tidak ada rekomendasi drama di platform '{platform_choice}' berdasarkan genre drama '{drama_title}'."

    return filtered_recs.reset_index(drop=True)

platform_key = 'Viki'

platform_key = input('Masukkan Platform: ')

platform_rekom = platform_filter_recommendations(drama_name_key, platform_key, content_filter_df, genre_sim_df)
platform_rekom

"""# **Model Development dengan Collaborative Filtering**"""

collaborative_filter_df = fix_kdrama_df[['user_id', 'kdrama_id', 'story_score', 'rewatch_value_score', 'overall_score']].copy()
collaborative_filter_df

coll_kdrama_filter_df = pd.merge(kdrama_info_df, kdrama_genre_df[['kdrama_id', 'genres']], on='kdrama_id', how='left')
coll_kdrama_filter_df = coll_kdrama_filter_df.dropna(subset=['genres'])
coll_kdrama_filter_df

"""## user_id

Mengubah user_id menjadi list tanpa nilai yang sama
"""

user_ids = collaborative_filter_df['user_id'].unique().tolist()
print('List user id: ', user_ids)

"""Melakukan encoding user_id atau mengubah bentuk string dari user_id menjadi angka"""

user_to_user_encoded = {x: i for i, x in enumerate(user_ids)}
print('encoded user_id : ', user_to_user_encoded)

"""Melakukan encoding angka ke user_id atau mengubah kembali dari bentuk angka ke id asli"""

user_encoded_to_user = {i: x for i, x in enumerate(user_ids)}
print('encoded angka ke userID: ', user_encoded_to_user)

"""Mapping user_id ke dataframe user"""

collaborative_filter_df['user'] = collaborative_filter_df['user_id'].map(user_to_user_encoded)

"""Mengetahui jumlah user"""

num_users = len(user_to_user_encoded)
print(num_users)

"""## kdrama_id

Mengubah kdrama_ids menjadi list tanpa nilai yang sama
"""

kdrama_ids = collaborative_filter_df['kdrama_id'].unique().tolist()
print('List drama id: ', kdrama_ids)

"""Melakukan encoding kdrama_ids atau mengubah bentuk string dari kdrama_id menjadi angka"""

kdrama_to_kdrama_encoded = {x: i for i, x in enumerate(kdrama_ids)}
print('encoded angka ke kdrama_id: ', kdrama_to_kdrama_encoded)

"""Melakukan encoding angka ke kdrama_ids atau mengubah kembali dari bentuk angka ke id asli"""

kdrama_encoded_to_kdrama = {i: x for i, x in enumerate(kdrama_ids)}
print('encoded angka ke kdrama_id: ', kdrama_encoded_to_kdrama)

"""Mapping kdrama_id ke dataframe kdrama"""

collaborative_filter_df['kdrama'] = collaborative_filter_df['kdrama_id'].map(kdrama_to_kdrama_encoded)

collaborative_filter_df

"""Mengetahui jumlah kdrama"""

num_kdrama = len(kdrama_to_kdrama_encoded)
print(num_kdrama)

"""## overall_score

Mengubah nilai overall_score menjadi nilai float
"""

collaborative_filter_df['overall_score'] = collaborative_filter_df['overall_score'].values.astype(np.float32)

"""Mengetahui nilai minimum overall_score"""

min_overall_score = min(collaborative_filter_df['overall_score'])

"""Mengetahui nilai maksimum overall_score"""

max_overall_score = max(collaborative_filter_df['overall_score'])

print('Min Rating: {}, Max Rating: {}'.format(
    min_overall_score, max_overall_score
))

"""## Membagi Data untuk Training dan Validasi

Mengacak dataset
"""

collaborative_filter_df = collaborative_filter_df.sample(frac=1, random_state=42)
collaborative_filter_df

"""Selanjutnya, kita bagi data train dan validasi dengan komposisi 80:20. Namun sebelumnya, kita perlu memetakan (mapping) data user dan resto menjadi satu value terlebih dahulu. Lalu, buatlah rating dalam skala 0 sampai 1 agar mudah dalam melakukan proses training.

Membuat variabel x untuk mencocokkan data user dan resto menjadi satu value
"""

x = collaborative_filter_df[['user', 'kdrama']].values

"""Membuat variabel y untuk membuat overall_score dari hasil dengan min max scaling sehingga score berada di range 0 - 1"""

y = collaborative_filter_df['overall_score'].apply(lambda x: (x - min_overall_score) / (max_overall_score - min_overall_score)).values

"""Membagi menjadi 80% data train dan 20% data validasi"""

train_indices = int(0.8 * collaborative_filter_df.shape[0])
x_train, x_val, y_train, y_val = (
    x[:train_indices],
    x[train_indices:],
    y[:train_indices],
    y[train_indices:]
)

print(x, y)

"""## Proses Training

Pada tahap ini, model menghitung skor kecocokan antara pengguna dan korean drama dengan teknik embedding. Pertama, kita melakukan proses embedding terhadap data user dan kdrama. Selanjutnya, lakukan operasi perkalian dot product antara embedding user dan kdrama. Selain itu, kita juga dapat menambahkan bias untuk setiap user dan kdrama. Skor kecocokan ditetapkan dalam skala [0,1] dengan fungsi aktivasi sigmoid.
"""

class RecommenderNet(tf.keras.Model):

  # Insialisasi fungsi
  def __init__(self, num_users, num_kdrama, embedding_size, **kwargs):
    super(RecommenderNet, self).__init__(**kwargs)
    self.num_users = num_users
    self.num_kdrama = num_kdrama
    self.embedding_size = embedding_size
    self.user_embedding = layers.Embedding( # layer embedding user
        num_users,
        embedding_size,
        embeddings_initializer = 'he_normal',
        embeddings_regularizer = keras.regularizers.l2(1e-6)
    )
    self.user_bias = layers.Embedding(num_users, 1) # layer embedding user bias
    self.kdrama_embedding = layers.Embedding( # layer embeddings kdrama
        num_kdrama,
        embedding_size,
        embeddings_initializer = 'he_normal',
        embeddings_regularizer = keras.regularizers.l2(1e-6)
    )
    self.kdrama_bias = layers.Embedding(num_kdrama, 1) # layer embedding kdrama bias
    self.dense = layers.Dense(1, activation='sigmoid')

  def call(self, inputs):
    user_vector = self.user_embedding(inputs[:,0]) # memanggil layer embedding 1
    user_bias = self.user_bias(inputs[:, 0]) # memanggil layer embedding 2
    kdrama_vector = self.kdrama_embedding(inputs[:, 1]) # memanggil layer embedding 3
    kdrama_bias = self.kdrama_bias(inputs[:, 1]) # memanggil layer embedding 4

    # dot_user_kdrama = tf.tensordot(user_vector, kdrama_vector, 2)
    dot_user_kdrama = tf.reduce_sum(user_vector * kdrama_vector, axis=1, keepdims=True)

    x = dot_user_kdrama + user_bias + kdrama_bias
    x = self.dense(x)

    return tf.nn.sigmoid(x) # activation sigmoid

model = RecommenderNet(num_users, num_kdrama, 64) # inisialisasi model

model.compile(
    loss = tf.keras.losses.MeanSquaredError(),
    optimizer = keras.optimizers.Adam(learning_rate=0.0001),
    metrics=[tf.keras.metrics.RootMeanSquaredError()]
)

early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

reduce_lr = ReduceLROnPlateau(
    monitor='val_loss', factor=0.5, patience=5,
    min_lr=1e-6, verbose=1
)

"""Memulai training"""

history = model.fit(
    x = x_train,
    y = y_train,
    batch_size = 8,
    epochs = 100,
    validation_data = (x_val, y_val),
    callbacks=[early_stop, reduce_lr]
)

"""Prediksi dari model"""

y_pred = model.predict(x_val).flatten()

# RMSE
rmse = np.sqrt(mean_squared_error(y_val, y_pred))
print(f"RMSE: {rmse:.4f}")

# MAE
mae = mean_absolute_error(y_val, y_pred)
print(f"MAE: {mae:.4f}")

"""## Visualisasi Metrik"""

plt.plot(history.history['root_mean_squared_error'])
plt.plot(history.history['val_root_mean_squared_error'])
plt.title('model_metrics')
plt.ylabel('root_mean_squared_error')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

"""## Mendapatkan Rekomendasi"""

final_kdrama_df = coll_kdrama_filter_df
score_kdrama_df = all_kdrama_rate_df.copy()

# Mengambil sample user
user_ids = score_kdrama_df.user_id.sample(1).iloc[0]
kdrama_watched_by_user = score_kdrama_df[score_kdrama_df.user_id == user_ids]

# Operator bitwise (~), bisa diketahui di sini https://docs.python.org/3/reference/expressions.html
kdrama_not_watched = final_kdrama_df[~final_kdrama_df['kdrama_id'].isin(kdrama_watched_by_user.kdrama_id.values)]['kdrama_id']
kdrama_not_watched = list(
    set(kdrama_not_watched)
    .intersection(set(kdrama_to_kdrama_encoded.keys()))
)

kdrama_not_watched = [[kdrama_to_kdrama_encoded.get(x)] for x in kdrama_not_watched]
user_encoder = user_to_user_encoded.get(user_ids)
user_kdrama_array = np.hstack(
    ([[user_encoder]] * len(kdrama_not_watched), kdrama_not_watched)
)

def print_kdrama_recommendation(df):
    if df.empty:
        print("Tidak ada rekomendasi untuk ditampilkan.")
        return

    table = []
    for i, row in enumerate(df.itertuples(), 1):
        table.append([i, row.drama_name, row.year, row.tot_eps, row.genres])

    headers = ["#", "Judul", "Tahun", "Episode", "Genre"]
    print(tabulate(table, headers=headers, tablefmt="fancy_grid"))

scores = model.predict(user_kdrama_array).flatten()

top_scores_indices = scores.argsort()[-10:][::-1]
recommended_kdrama_ids = [
    kdrama_encoded_to_kdrama.get(kdrama_not_watched[x][0]) for x in top_scores_indices
]

print('Showing recommendations for users: {}'.format(user_ids))
print('\nKdrama with high scores from user')

top_kdrama_user = (
    kdrama_watched_by_user.sort_values(
        by = 'overall_score',
        ascending=False
    )
    .head(5)
    .kdrama_id.values
)

kdrama_df_rows = final_kdrama_df[final_kdrama_df['kdrama_id'].isin(top_kdrama_user)]
print_kdrama_recommendation(kdrama_df_rows)

print('\nTop 10 kdrama recommendation')

recommended_kdrama = final_kdrama_df[final_kdrama_df['kdrama_id'].isin(recommended_kdrama_ids)]
print_kdrama_recommendation(recommended_kdrama)