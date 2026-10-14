import os
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns

st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")

BLUE, GREY, ORANGE = "#1f6fb2", "#b8bfc7", "#e8833a"
sns.set_theme(style="whitegrid")
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False,
                     "axes.titleweight": "bold", "axes.titlesize": 12})

BASE = os.path.dirname(os.path.abspath(__file__))
WEATHER_ORDER = ["Cerah", "Berkabut/Berawan", "Hujan/Salju Ringan", "Hujan/Salju Lebat"]
SEASON_ORDER = ["Semi", "Panas", "Gugur", "Dingin"]
TEMP_ORDER = ["Dingin (<10°C)", "Sejuk (10-20°C)", "Hangat (20-30°C)", "Panas (>30°C)"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]


@st.cache_data
def load_data():
    hour = pd.read_csv(os.path.join(BASE, "main_data.csv"), parse_dates=["dteday"])
    day = pd.read_csv(os.path.join(BASE, "day_data.csv"), parse_dates=["dteday"])
    return hour, day


hour_df, day_df = load_data()

# ---------------- Sidebar (filter) ----------------
st.sidebar.header("Filter Data")
min_d, max_d = day_df["dteday"].min().date(), day_df["dteday"].max().date()
date_range = st.sidebar.date_input("Rentang tanggal", (min_d, max_d), min_value=min_d, max_value=max_d)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
else:
    start, end = pd.to_datetime(min_d), pd.to_datetime(max_d)

season_sel = st.sidebar.selectbox("Musim", ["Semua Musim"] + SEASON_ORDER)
weather_sel = st.sidebar.selectbox("Kondisi cuaca", ["Semua Cuaca"] + WEATHER_ORDER[:3])
st.sidebar.caption("Sumber: Capital Bikeshare, Washington D.C. (2011–2012)")


def apply(df):
    m = df["dteday"].between(start, end)
    if season_sel != "Semua Musim":
        m &= df["season_lbl"] == season_sel
    if weather_sel != "Semua Cuaca":
        m &= df["weather_lbl"] == weather_sel
    return df[m]


hour_f, day_f = apply(hour_df), apply(day_df)

# ---------------- Header ----------------
st.title("Dashboard Analisis Bike Sharing")
st.markdown("Pola penyewaan sepeda berdasarkan **jam**, **cuaca/musim/suhu**, dan **pertumbuhan tahunan**.")

if day_f.empty:
    st.warning("Tidak ada data untuk filter yang dipilih. Ubah filter di sidebar.")
    st.stop()

# ---------------- KPI ----------------
total = int(day_f["cnt"].sum())
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total penyewaan", f"{total:,}")
c2.metric("Rata-rata per hari", f"{day_f['cnt'].mean():,.0f}")
c3.metric("Pengguna registered", f"{day_f['registered'].sum() / total:.0%}")
c4.metric("Pengguna casual", f"{day_f['casual'].sum() / total:.0%}")

tab1, tab2, tab3, tab4 = st.tabs(["Pola Jam", "Cuaca, Musim & Suhu", "Pertumbuhan", "Analisis Lanjutan"])

# ---------------- Tab 1 ----------------
with tab1:
    st.subheader("Pertanyaan 1: Pada jam berapa rata-rata penyewaan sepeda per jam mencapai puncak tertinggi pada hari kerja dibandingkan akhir pekan/libur selama periode 2011–2012?")
    hourly = hour_f.groupby(["day_type", "hr"])["cnt"].mean().reset_index()
    if hourly.empty:
        st.info("Data per jam kosong untuk filter ini.")
    else:
        fig, ax = plt.subplots(figsize=(7.5, 3.6))
        colors = {"Hari Kerja": BLUE, "Akhir Pekan/Libur": ORANGE}
        for t, g in hourly.groupby("day_type"):
            ax.plot(g["hr"], g["cnt"], color=colors[t], lw=2.5, marker="o", ms=4, label=t)
            top = g.loc[g["cnt"].idxmax()]
            ax.annotate(f"{int(top['hr']):02d}:00 · {top['cnt']:.0f}", (top["hr"], top["cnt"]),
                        textcoords="offset points", xytext=(0, 9), ha="center",
                        color=colors[t], fontweight="bold", fontsize=9)
        ax.set_xticks(range(0, 24, 2)); ax.set_xticklabels([f"{h:02d}" for h in range(0, 24, 2)])
        ax.set_xlabel("Jam dalam sehari"); ax.set_ylabel("Rata-rata penyewaan per jam")
        ax.set_ylim(0, hourly["cnt"].max() * 1.2)
        ax.legend(frameon=False, loc="upper left")
        ax.set_title("Rata-rata penyewaan per jam", loc="left")
        st.pyplot(fig, use_container_width=False)

        col_a, col_b = st.columns(2)
        with col_a:
            seg = hour_f.groupby(["day_type", "time_segment"], observed=True)["cnt"].mean().unstack(0)
            seg = seg.reindex([x for x in hour_df["time_segment"].unique() if x in seg.index])
            order = ["Dini Hari (00-05)", "Pagi (06-09)", "Siang (10-15)", "Sore (16-19)", "Malam (20-23)"]
            seg = seg.reindex([o for o in order if o in seg.index]).round(0)
            st.markdown("**Rata-rata penyewaan per jam menurut segmen waktu**")
            st.dataframe(seg.astype(int))
        with col_b:
            share = hour_f.groupby("day_type")[["casual", "registered"]].sum()
            share["Casual (%)"] = (share["casual"] / share.sum(axis=1) * 100).round(1)
            st.markdown("**Porsi pengguna casual**")
            st.dataframe(share[["Casual (%)"]])

    st.info("**Insight:** hari kerja punya dua puncak komuter (±08:00 dan ±17:00), sedangkan akhir pekan/libur "
            "satu puncak lebar di siang hari dengan porsi pengguna *casual* jauh lebih besar. "
            "**Aksi:** redistribusi sepeda sebelum jam sibuk dan perawatan pada 00:00–05:00.")

# ---------------- Tab 2 ----------------
with tab2:
    st.subheader("Pertanyaan 2: Berapa persen penurunan rata-rata penyewaan harian saat cuaca hujan/salju ringan dibandingkan cuaca cerah selama periode 2011–2012?")
    w = day_f.groupby("weather_lbl")["cnt"].mean().reindex(WEATHER_ORDER[:3]).dropna()
    s = day_f.groupby("season_lbl")["cnt"].mean().reindex(SEASON_ORDER).dropna()
    t = day_f.groupby("temp_category", observed=True)["cnt"].mean().reindex(TEMP_ORDER).dropna()

    fig, axes = plt.subplots(1, 3, figsize=(11, 3.6), sharey=True)
    for ax, ser, title in zip(axes, [w, s, t], ["Kondisi cuaca", "Musim", "Kategori suhu"]):
        cols = [ORANGE if v == ser.max() else GREY for v in ser]
        bars = ax.bar([str(i).replace(" (", "\n(").replace("/", "/\n") if title == "Kondisi cuaca" else str(i).replace(" (", "\n(") for i in ser.index], ser.values, color=cols)
        for b, v in zip(bars, ser.values):
            ax.text(b.get_x() + b.get_width() / 2, v + ser.max() * 0.015, f"{v:,.0f}", ha="center", fontsize=9, fontweight="bold")
        ax.set_title(title, loc="left"); ax.tick_params(axis="x", labelsize=8.5)
        ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    axes[0].set_ylabel("Rata-rata penyewaan harian")
    plt.tight_layout()
    st.pyplot(fig, use_container_width=False)

    if "Cerah" in w.index and "Hujan/Salju Ringan" in w.index:
        drop = (w["Hujan/Salju Ringan"] / w["Cerah"] - 1) * 100
        st.metric("Penurunan saat hujan/salju ringan vs cerah", f"{drop:.0f}%")

    fig2, ax2 = plt.subplots(figsize=(6, 3.6))
    cmap = {"Cerah": BLUE, "Berkabut/Berawan": GREY, "Hujan/Salju Ringan": ORANGE}
    for lbl, g in day_f.groupby("weather_lbl"):
        ax2.scatter(g["temp_c"], g["cnt"], s=22, alpha=.65, color=cmap.get(lbl, "black"), label=lbl)
    if len(day_f) > 2:
        z = np.polyfit(day_f["temp_c"], day_f["cnt"], 1)
        xs = np.linspace(day_f["temp_c"].min(), day_f["temp_c"].max(), 50)
        ax2.plot(xs, np.polyval(z, xs), "k--", lw=1.4)
        ax2.text(0.03, 0.95, f"r = {day_f['temp_c'].corr(day_f['cnt']):.2f}", transform=ax2.transAxes, fontweight="bold")
    ax2.set_xlabel("Suhu (°C)"); ax2.set_ylabel("Penyewaan harian"); ax2.legend(frameon=False, loc="lower right")
    ax2.set_title("Suhu vs penyewaan harian", loc="left")
    st.pyplot(fig2, use_container_width=False)

    st.info("**Insight:** cuaca hujan/salju ringan menurunkan penyewaan ±63%; musim gugur dan suhu 20–30°C tertinggi. "
            "**Aksi:** sesuaikan jumlah armada dengan prakiraan cuaca dan siapkan kapasitas ekstra untuk musim gugur.")

# ---------------- Tab 3 ----------------
with tab3:
    st.subheader("Pertanyaan 3: Berapa persen pertumbuhan total penyewaan sepeda tahun 2012 dibandingkan tahun 2011 (Year-over-Year)?")
    monthly = day_f.pivot_table(index="mnth", columns="year", values="cnt", aggfunc="sum").reindex(range(1, 13))
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    if 2011 in monthly: ax.plot(MONTHS, monthly[2011], color=GREY, lw=2.5, marker="o", label="2011")
    if 2012 in monthly: ax.plot(MONTHS, monthly[2012], color=BLUE, lw=2.5, marker="o", label="2012")
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{x/1000:.0f} rb"))
    ax.set_ylabel("Total penyewaan per bulan"); ax.set_ylim(0); ax.legend(frameon=False)
    ax.set_title("Total penyewaan bulanan", loc="left")
    st.pyplot(fig, use_container_width=False)

    if {2011, 2012}.issubset(monthly.columns) and monthly[[2011, 2012]].notna().all(axis=None):
        yoy = (monthly[2012] / monthly[2011] - 1) * 100
        tot = day_f.groupby("year")["cnt"].sum()
        a, b = st.columns(2)
        a.metric("Pertumbuhan total 2012 vs 2011", f"{(tot[2012] / tot[2011] - 1) * 100:.1f}%")
        b.metric("Bulan puncak 2012", MONTHS[int(monthly[2012].idxmax()) - 1])
        fig, ax = plt.subplots(figsize=(7.5, 3))
        ax.bar(MONTHS, yoy, color=[ORANGE if v == yoy.min() else BLUE for v in yoy])
        for i, v in enumerate(yoy): ax.text(i, v + 3, f"{v:.0f}%", ha="center", fontsize=8.5)
        ax.set_ylabel("YoY (%)"); ax.set_title("Pertumbuhan YoY per bulan", loc="left")
        st.pyplot(fig, use_container_width=False)
    else:
        st.info("Pilih rentang tanggal yang mencakup 2011 dan 2012 (dan bulan yang sama) untuk melihat pertumbuhan YoY.")

    st.info("**Insight:** penyewaan 2012 tumbuh ±65% dari 2011 dan pola musimannya sama (puncak di pertengahan tahun). "
            "**Aksi:** tambah armada/dok sebelum Mei, jadwalkan perawatan besar saat Desember–Februari.")

# ---------------- Tab 4 ----------------
with tab4:
    st.subheader("Analisis lanjutan: binning suhu × tingkat permintaan harian")
    st.markdown("Hari dikelompokkan menjadi permintaan **Rendah/Sedang/Tinggi** (binning kuantil, `pd.qcut`) dan suhu "
                "dibagi 4 kategori (`pd.cut`). Heatmap menunjukkan peluang sebuah hari berpermintaan **Tinggi**.")
    d = day_f[day_f["weather_lbl"].isin(WEATHER_ORDER[:3])].assign(high=lambda x: (x["demand_level"] == "Tinggi").astype(int))
    heat = (d.pivot_table(index="weather_lbl", columns="temp_category", values="high", aggfunc="mean", observed=True)
              .mul(100).reindex(index=WEATHER_ORDER[:3], columns=TEMP_ORDER))
    fig, ax = plt.subplots(figsize=(6.5, 3))
    sns.heatmap(heat, annot=True, fmt=".0f", cmap="Blues", linewidths=.5, ax=ax,
                cbar_kws={"label": "% hari berpermintaan Tinggi"}, annot_kws={"fontweight": "bold"})
    ax.set_xlabel(""); ax.set_ylabel("")
    st.pyplot(fig, use_container_width=False)
    st.caption("Sel kosong = tidak ada hari pada kombinasi tersebut dalam filter terpilih. "
               "Kombinasi dengan jumlah hari sedikit (mis. cuaca hujan) sebaiknya dibaca hati-hati.")

st.caption("Dibuat dengan Streamlit · Data: Capital Bikeshare 2011–2012 (Fanaee-T & Gama, 2013)")
