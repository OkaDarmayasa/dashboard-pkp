import streamlit as st
from db import *
from auth import login
from custom_pages import indikator, tlhp 
import pandas as pd
import plotly.express as px
import json
import time
from datetime import datetime
import plotly.graph_objects as go

# Set page config with title and icon if desired
st.set_page_config(
    page_title="Dashboard Tau Kawan",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": None,
        "Get help": None,
        "Report a bug": None
    }
)

# ─────────────────────── CUSTOM CSS ────────────────────────
# This CSS will set the background color of the entire app to a dark blue
# st.markdown(
#     """
#     <style>
#     /* Main background: light gray */
#     html, body, [data-testid="stAppViewContainer"],
#     .stApp, .block-container, [data-testid="stHeader"] {
#         background-color: #D1D5DB !important;
#         color: #111827 !important;  /* Dark text */
#     }

#     /* Sidebar: dark blue */
#     [data-testid="stSidebar"] {
#         background-color: #023047 !important;
#         color: white !important;
#     }

#     /* Sidebar text */
#     [data-testid="stSidebar"] * {
#         color: white !important;
#     }

#     /* Fix labels and general text in main area */
#     .block-container label,
#     .block-container h1, .block-container h2, .block-container h3,
#     .block-container h4, .block-container h5, .block-container h6,
#     .block-container p, .block-container div {
#         color: #111827 !important;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )

# # ─── DATABASE INIT ─────────────────────────────────────────
# file_path = "Ready to Prisma.xlsx"
# seed_indikators_from_excel(file_path)

# ─── AUTHENTICATION ────────────────────────────────────────
if 'user' not in st.session_state:
    login()
    st.stop()

user = st.session_state.user

# Function to draw full-width sidebar buttons
def sidebar_nav_button(label, page_name):
    if st.button(label, use_container_width=True):
        st.session_state.selected_page = page_name

# ─── SIDEBAR ───────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        # Centered image using columns
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.image("assets/logo.png", width=100)  # Set desired width here

        # Centered title
        st.markdown(
            """
            <div style='text-align: center; font-size: 20px; font-weight: bold; margin-top: 0px;'>
                Dashboard Tau Kawan
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")

        # Initialize session state for page selection
        if "selected_page" not in st.session_state:
            st.session_state.selected_page = "Dashboard"

        # Menu buttons
        sidebar_nav_button("🏠  Dashboard", "Dashboard")
        sidebar_nav_button("📊  21 Indikator", "21 Indikator")
        sidebar_nav_button("📁  TLHP", "TLHP")

        st.markdown("---")

        # Logout button
        if st.button("🚪 Logout"):
            st.session_state.pop("user")
            st.rerun()

def format_capaian(value):
    try:
        val = float(value)
        if 0 <= val <= 1:
            return f"{val * 100:.0f}%" 
        else:
            return f"{val:.0f}" if val.is_integer() else str(val)
    except:
        return str(value)
    
# ─── USER VIEW ─────────────────────────────────────────────
def user_view():
    sidebar()
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
    sidebar()
    st.header("Dashboard Tau Kawan")

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
        "Sangat Baik": "#6FFFE9",     # Green
        "Baik": "#2BB7DA",            # Light Green
        "Cukup": "#4682B4",           # Orange
        "Kurang": "#2F4F4F",          # Dark Orange
        "Sangat Kurang": "#5C4FC8",   # Red
    }

    # Generate pie chart
    fig_kategori_pie = px.pie(
        kategori_counts,
        names="Kategori",
        values="Jumlah",
        title="Proporsi Indikator Berdasarkan Kategori",
        hole=0.4
    )

    # Apply styling and colors
    fig_kategori_pie.update_traces(
        textinfo="label+percent",
        textposition="outside",
        marker=dict(colors=[custom_colors.get(k, "#cccccc") for k in kategori_counts["Kategori"]]),
        hoverinfo="label+percent+value",
        showlegend=True
    )

    # Layout tweaks
    fig_kategori_pie.update_layout(
        annotations=[dict(text='Kategori', x=0.5, y=0.5, font_size=16, showarrow=False)],
        showlegend=True,
        margin=dict(t=40, b=40, l=0, r=0),
        font=dict(size=16)
    )

    # Display in Streamlit
    st.plotly_chart(fig_kategori_pie, use_container_width=True)
# ─── ENTRY POINT ───────────────────────────────────────────

if user["is_admin"]:
    admin_view()
else:
    user_view()