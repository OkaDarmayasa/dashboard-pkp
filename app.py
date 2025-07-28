import streamlit as st
from db import *
from auth import login
import pandas as pd
import plotly.express as px
import json
import time
from datetime import datetime

st.set_page_config(layout="wide")

# Initialize DB
file_path = "Ready to Prisma.xlsx"
seed_indikators_from_excel(file_path)

def format_capaian(value):
    try:
        val = float(value)
        if 0 <= val <= 1:
            return f"{val * 100:.0f}%"   # turn 0.87 → 87%
        else:
            return f"{val:.0f}" if val.is_integer() else str(val)
    except:
        return str(value)

# Authentication
if 'user' not in st.session_state:
    login()
    st.stop()

user = st.session_state.user
st.title(f"Selamat Datang, {user['username']}!")

# ─── SIDEBAR ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 👤 User Info")
    st.markdown(f"**Username:** {user['username']}")
    st.markdown(f"**Unit:** {user['unit']}")
    if user["is_admin"]:
        st.markdown("**Role:** Admin")

    st.markdown("---")
    if st.button("🚪 Logout"):
        st.session_state.pop("user")
        st.rerun()

# ─── USER VIEW ─────────────────────────────────────────────

def user_view():
    st.header("📌 Tambah Indikator Baru")

    if "indikator_success" not in st.session_state:
        st.session_state.indikator_success = False

    if st.session_state.indikator_success:
        st.success("Indikator berhasil ditambahkan!")
        time.sleep(2)
        st.session_state.indikator_success = False
        st.rerun()

    with st.form("indikator_form"):
        name = st.text_input("Nama Indikator")
        #type_ = st.selectbox("Tipe", options=["range", "categorical", "kelas", "custom"])
        capaian = st.text_input("Capaian")
        kategori = st.text_input("Kategori")
        nilai = st.text_area("Nilai (JSON Array)", value="[100, 80, 60, 40, 0]")
        #kriteria = st.text_area("Kriteria (JSON Object)", value='{"thresholds": [90, 75, 60]}')
        year = st.number_input("Tahun", min_value=2000, max_value=2100, value=2025)
        bukti = st.text_input("Bukti")

        submitted = st.form_submit_button("Tambah")
        if submitted:
            try:
                parsed_nilai = json.loads(nilai)
                #parsed_kriteria = json.loads(kriteria)
                add_indikator(name, capaian, kategori, parsed_nilai, year, bukti)
                st.session_state.indikator_success = True
                st.rerun()
            except json.JSONDecodeError:
                st.error("Format JSON untuk nilai atau kriteria tidak valid.")

    st.header("📊 Daftar Indikator")
    data = get_all_indikators()
    if data:
        df = pd.DataFrame(data, columns=[
            "Name", "Capaian", "Kategori", "Nilai", "Year", "Bukti"
        ])
        df.index = df.index + 1
        df["Capaian"] = df["Capaian"].apply(format_capaian)
        df["Nilai"] = df["Nilai"].apply(lambda x: json.loads(x)[0] if isinstance(x, str) else x)
        search_query = st.text_input("🔍 Search", "")
        if search_query:
            df = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
        st.dataframe(df)
    else:
        st.info("Belum ada indikator.")

# ─── ADMIN VIEW ────────────────────────────────────────────
def admin_view():
    st.header("📋 Semua Indikator")

    data = get_all_indikators()
    if not data:
        st.info("Belum ada data indikator.")
        return

    df = pd.DataFrame(data, columns=[
        "Name", "Capaian", "Kategori", "Nilai", "Year", "Bukti"
    ])
    df.index = df.index + 1
    df["Capaian"] = df["Capaian"].apply(format_capaian)
    df["Nilai"] = df["Nilai"].apply(lambda x: json.loads(x)[0] if isinstance(x, str) else x)
    # ── Filter Section ──
    with st.expander("🔍 Filter Indikator", expanded=True):
        selected_years = st.multiselect("Filter Tahun", sorted(df["Year"].unique()))
        selected_kategori = st.multiselect("Filter Kategori", sorted(df["Kategori"].unique()))

        if selected_years:
            df = df[df["Year"].isin(selected_years)]
        if selected_kategori:
            df = df[df["Kategori"].isin(selected_kategori)]


    # ── Data Table ──
    with st.expander("📋 Tabel Indikator", expanded=True):
        search_query = st.text_input("🔍 Search", "")
        if search_query:
            df = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]

        st.dataframe(df)

    # ── Charts ──
    st.header("📊 Visualisasi Indikator")

    # Pie chart: jumlah indikator per kategori
    kategori_counts = df["Kategori"].value_counts().reset_index()
    kategori_counts.columns = ["Kategori", "Jumlah"]

    # Custom color mapping
    custom_colors = {
        "Sangat Baik": "#2ca02c",     # Green
        "Baik": "#98df8a",            # Light Green
        "Cukup": "#ffbb78",           # Orange
        "Kurang": "#ff7f0e",          # Dark Orange
        "Sangat Kurang": "#d62728",   # Red
    }

    # Generate pie chart
    fig_kategori_pie = px.pie(
        kategori_counts,
        names="Kategori",
        values="Jumlah",
        title="Proporsi Indikator Berdasarkan Kategori",
        hole=0.4
    )

    # Apply manual colors based on kategori
    fig_kategori_pie.update_traces(marker=dict(colors=[custom_colors.get(k, "#cccccc") for k in kategori_counts["Kategori"]]))

    st.plotly_chart(fig_kategori_pie, use_container_width=True)

# ─── ENTRY POINT ───────────────────────────────────────────

if user["is_admin"]:
    admin_view()
else:
    user_view()