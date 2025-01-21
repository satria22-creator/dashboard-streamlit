import streamlit as st
import pandas as pd
import altair as alt

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tema Altair
alt.themes.enable("dark")

# Mengimpor Data
DATA_PATH = 'Data/day.csv'
try:
    day_df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    st.error(f"File tidak ditemukan: {DATA_PATH}")
    st.stop()

# Pemetaan angka ke nama musim
season_mapping = {1: 'Musim Semi', 2: 'Musim Panas', 3: 'Musim Gugur', 4: 'Musim Dingin'}
day_df['season'] = day_df['season'].map(season_mapping)

# Pemetaan angka ke deskripsi kondisi cuaca
weathersit_mapping = {
    1: 'Cerah, Sedikit berawan, Sebagian berawan',
    2: 'Kabut + Berawan, Kabut + Awan Pecah, Kabut + Sedikit berawan, Kabut',
    3: 'Salju ringan, Hujan ringan + Petir + Awan tersebar',
    4: 'Hujan deras + Es + Petir + Kabut, Salju + Kabut'
}
day_df['weathersit'] = day_df['weathersit'].map(weathersit_mapping)

# Tambahkan kolom tahun
day_df['year'] = pd.to_datetime(day_df['dteday']).dt.year

# Sidebar untuk filter
with st.sidebar:
    st.title("Bike 🚲 Sharing Dashboard")
    st.sidebar.header('Filter Data')

    # Filter untuk tahun
    selected_year = st.sidebar.selectbox(
        'Pilih Tahun:',
        options=['Semua'] + list(day_df['year'].unique()),
        index=0
    )

    # Filter untuk musim
    selected_season = st.sidebar.selectbox(
        'Pilih Musim:',
        options=['Semua'] + list(day_df['season'].unique()),
        index=0
    )

    # Filter untuk hari kerja
    selected_workingday = st.sidebar.selectbox(
        'Pilih Hari Kerja (0 = Libur, 1 = Hari Kerja):',
        options=['Semua'] + list(day_df['workingday'].unique()),
        index=0
    )

    # Filter untuk kondisi cuaca
    selected_weathersit = st.sidebar.selectbox(
        'Pilih Kondisi Cuaca:',
        options=['Semua'] + list(day_df['weathersit'].unique()),
        index=0
    )

# Terapkan filter ke dataframe
filtered_df = day_df.copy()
if selected_year != 'Semua':
    filtered_df = filtered_df[filtered_df['year'] == selected_year]
if selected_season != 'Semua':
    filtered_df = filtered_df[filtered_df['season'] == selected_season]
if selected_workingday != 'Semua':
    filtered_df = filtered_df[filtered_df['workingday'] == selected_workingday]
if selected_weathersit != 'Semua':
    filtered_df = filtered_df[filtered_df['weathersit'] == selected_weathersit]

# Membagi tampilan menjadi dua baris
row1, row2 = st.columns(2)

# Kartu total penyewa
with row1:
    st.subheader("Total Penyewa Sepeda")
    col1, col2 = st.columns(2)

    # Total Casual
    total_casual_2011 = day_df[day_df['year'] == 2011]['casual'].sum()
    total_casual_2012 = day_df[day_df['year'] == 2012]['casual'].sum()
    total_casual = filtered_df['casual'].sum()

    # Hitung perubahan casual
    casual_change = total_casual_2012 - total_casual_2011
    casual_arrow = "→"
    casual_color = "off"

    if selected_year == 'Semua':
        casual_arrow = "→"
        casual_color = "off"
    elif casual_change > 0:
        casual_arrow = "↗"
        casual_color = "normal"
    elif casual_change < 0:
        casual_arrow = "↘"
        casual_color = "inverse"

    col1.metric(
        label="Casual",
        value=f"{total_casual:,.0f}",
        delta=f"{casual_arrow}",
        delta_color=casual_color
    )

    # Total Registered
    total_registered_2011 = day_df[day_df['year'] == 2011]['registered'].sum()
    total_registered_2012 = day_df[day_df['year'] == 2012]['registered'].sum()
    total_registered = filtered_df['registered'].sum()

    # Hitung perubahan registered
    registered_change = total_registered_2012 - total_registered_2011
    registered_arrow = "→"
    registered_color = "off"

    if selected_year == 'Semua':
        registered_arrow = "→"
        registered_color = "off"
    elif registered_change > 0:
        registered_arrow = "↗"
        registered_color = "normal"
    elif registered_change < 0:
        registered_arrow = "↘"
        registered_color = "inverse"

    col2.metric(
        label="Registered",
        value=f"{total_registered:,.0f}",
        delta=f"{registered_arrow}",
        delta_color=registered_color
    )

# Kolom 1: Histogram Hari Kerja
with row2:
    st.subheader("Total Pengguna Berdasarkan Hari Kerja")

    # Data histogram hari kerja
    users_workingday = (
        filtered_df[['workingday', 'casual', 'registered']]
        .melt(id_vars='workingday', var_name='Tipe Pengguna', value_name='Total Pengguna')
    )

    workingday_chart = (
        alt.Chart(users_workingday)
        .mark_bar()
        .encode(
            x=alt.X('workingday:O', title='Hari Kerja (0 = Libur, 1 = Hari Kerja)', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('sum(Total Pengguna):Q', title='Total Pengguna'),
            color=alt.Color('Tipe Pengguna:N', legend=alt.Legend(title='Tipe Pengguna'))
        )
        .properties(width=400, height=300)
    )
    st.altair_chart(workingday_chart, use_container_width=True)

# Histogram musim
st.subheader("Total Pengguna Berdasarkan Musim")
users_season = (
    filtered_df[['season', 'casual', 'registered']]
    .melt(id_vars='season', var_name='Tipe Pengguna', value_name='Total Pengguna')
)

season_chart = (
    alt.Chart(users_season)
    .mark_bar()
    .encode(
        x=alt.X('season:O', title='Musim', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('sum(Total Pengguna):Q', title='Total Pengguna'),
        color=alt.Color('Tipe Pengguna:N', legend=alt.Legend(title='Tipe Pengguna'))
    )
    .properties(width=400, height=300)
)
st.altair_chart(season_chart, use_container_width=True)

# Histogram kondisi cuaca
st.subheader("Total Pengguna Berdasarkan Kondisi Cuaca")
users_weather = (
    filtered_df[['weathersit', 'casual', 'registered']]
    .melt(id_vars='weathersit', var_name='Tipe Pengguna', value_name='Total Pengguna')
)

weather_chart = (
    alt.Chart(users_weather)
    .mark_bar()
    .encode(
        x=alt.X('weathersit:O', title='Kondisi Cuaca', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('sum(Total Pengguna):Q', title='Total Pengguna'),
        color=alt.Color('Tipe Pengguna:N', legend=alt.Legend(title='Tipe Pengguna'))
    )
    .properties(width=400, height=300)
)
st.altair_chart(weather_chart, use_container_width=True)
