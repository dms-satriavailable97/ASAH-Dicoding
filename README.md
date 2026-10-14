# Proyek Analisis Data: Bike Sharing Dataset 🚲

Analisis data penyewaan sepeda Capital Bikeshare (Washington D.C., 2011–2012) beserta dashboard interaktif Streamlit.

## Pertanyaan Bisnis
1. Pada jam berapa rata-rata penyewaan sepeda per jam mencapai puncak tertinggi pada hari kerja dibandingkan akhir pekan/libur selama periode 2011–2012?
2. Berapa persen penurunan rata-rata penyewaan harian saat cuaca hujan/salju ringan dibandingkan cuaca cerah selama periode 2011–2012?
3. Berapa persen pertumbuhan total penyewaan sepeda tahun 2012 dibandingkan tahun 2011 (Year-over-Year)?

## Struktur Direktori
```
submission
├── dashboard
│   ├── main_data.csv      # data per jam yang sudah dibersihkan
│   ├── day_data.csv       # data harian yang sudah dibersihkan
│   └── dashboard.py
├── data
│   ├── day.csv
│   └── hour.csv
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## Setup Environment

### Menggunakan Anaconda
```
conda create --name main-ds python=3.11
conda activate main-ds
pip install -r requirements.txt
```

### Menggunakan Shell/Terminal
```
cd submission
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Menjalankan Dashboard
```
cd submission/dashboard
streamlit run dashboard.py
```
Dashboard akan terbuka di `http://localhost:8501`. Gunakan sidebar untuk memfilter rentang tanggal, musim, dan kondisi cuaca.

## Menjalankan Ulang Notebook
Jalankan `notebook.ipynb` dari folder `submission` (agar path `data/` dan `dashboard/` terbaca). Notebook akan membuat ulang `dashboard/main_data.csv` dan `dashboard/day_data.csv`.

## Sumber Data
Fanaee-T, H. & Gama, J. (2013). *Event labeling combining ensemble detectors and background knowledge*. Progress in Artificial Intelligence. doi:10.1007/s13748-013-0040-3
