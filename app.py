import streamlit as st
from db import *
from auth import login
import pandas as pd
import plotly.express as px
import time

st.set_page_config(layout="wide")

# Initialize DB if not already
init_db()

# Login logic
if 'user' not in st.session_state:
    login()
    st.stop()

user = st.session_state.user
st.title(f"Selamat Datang, {user['username']}!")

# Sidebar styling
st.markdown("""
    <style>
    div[data-testid="stSidebar"] > div:first-child {
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    .sidebar-section {
        margin-bottom: 20px;
    }
    hr {
        margin-top: 10px;
        margin-bottom: 10px;
        border: none;
        border-top: 1px solid #ccc;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar content
with st.sidebar:
    st.markdown("### 👤 User Info", unsafe_allow_html=True)
    st.markdown(f"<div class='sidebar-section'>"
                f"<strong>Username:</strong> {user['username']}<br>"
                f"<strong>Unit:</strong> {user['unit']}<br>"
                f"{'<strong>Role:</strong> Admin' if user['is_admin'] else ''}"
                f"</div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Logout at the bottom
    logout_placeholder = st.empty()
    with logout_placeholder.container():
        st.button("🚪 Logout", on_click=lambda: st.session_state.pop('user', None))

# Stage validity thresholds
stage_limits = {
    "Perencanaan": 7,
    "Pelaksanaan": 21,
    "Pelaporan": 28,
    "Selesai": None  # Always valid
}

# Add validity column to DataFrame
def get_stage_validity(stage, start_date_str):
    if stage == "Selesai":
        return "✅ Valid"
    start_date = pd.to_datetime(start_date_str)
    days_elapsed = (datetime.now() - start_date).days
    if days_elapsed > stage_limits[stage]:
        return "⚠️ Expired"
    return "✅ Valid"


# User View
def user_view():
    st.header("📌 Tambah PKP Baru")

    # Handle success flag before widget is created
    if "job_success" not in st.session_state:
        st.session_state.job_success = False

    if st.session_state.job_success:
        st.session_state.job_name = ""
        st.session_state.job_success = False
        time.sleep(3)
        st.rerun()

    # Text input
    job_name = st.text_input("PKP", key="job_name")

    if st.button("Tambah PKP") and job_name.strip() != "":
        add_job(user['id'], job_name.strip())
        st.session_state.job_success = True
        st.success("PKP Berhasil Ditambahkan!")
        time.sleep(3)
        st.rerun()

    st.header("📊 PKP Saya")
    user_jobs = get_user_jobs(user['id'])
    df = pd.DataFrame(user_jobs, columns=["ID", "UserID", "Job", "Stage", "Start Date"])
    # Ensure date formatting
    df["Start Date"] = pd.to_datetime(df["Start Date"]).dt.strftime("%Y-%m-%d")
    # Format Validity
    df["Validitas"] = df.apply(lambda row: get_stage_validity(row["Stage"], row["Start Date"]), axis=1)
    
    # Stage options and badge styles
    stage_options = ["Perencanaan", "Pelaksanaan", "Pelaporan", "Selesai"]
    stage_colors = {
        "Perencanaan": "#f0ad4e",
        "Pelaksanaan": "#0275d8",
        "Pelaporan": "#5cb85c",
        "Selesai": "#6c757d"
    }

    # Render table in an expander
    with st.expander("📋 PKP Table with Actions", expanded=True):
        st.markdown("### Daftar PKP")
        
        # Table headers
        header = st.columns([1, 3, 2, 2, 2, 4, 2])  # e.g. No, PKP, Tanggal, Tahap, Validitas, Ubah, Delete
        header_labels = ["No", "PKP", "Tanggal", "Tahap", "Validitas", "Ubah Status", "Delete"]
        for col, label in zip(header, header_labels):
            col.markdown(f"**{label}**")

        # Render each row with columns and controls
        for i, row in df.reset_index(drop=True).iterrows():
            cols = st.columns([1, 3, 2, 2, 2, 4, 2])

            cols[0].markdown(f"{i + 1}")
            cols[1].markdown(row["Job"])
            cols[2].markdown(row["Start Date"])

            # Stage badge
            stage = row["Stage"]
            stage_html = f"<span style='background-color:{stage_colors[stage]}; color:white; padding:4px 10px; border-radius:4px;'>{stage}</span>"
            cols[3].markdown(stage_html, unsafe_allow_html=True)

            # Validity
            validity_color = "#28a745" if "Valid" in row["Validitas"] else "#dc3545"
            cols[4].markdown(
                f"<span style='background-color:{validity_color}; color:white; padding:4px 10px; border-radius:4px;'>{row['Validitas']}</span>",
                unsafe_allow_html=True
            )

            with cols[5]:
                new_stage = st.selectbox(
                    label="Change Stage",
                    options=stage_options,
                    index=stage_options.index(stage),
                    key=f"dropdown_{row['ID']}",
                    label_visibility="collapsed"
                )

                if new_stage != stage:
                    if st.button("🔄 Update", key=f"update_{row['ID']}"):
                        update_job_stage(row["ID"], new_stage)
                        st.rerun()
                else:
                    st.markdown("<span style='color:gray;'>No changes</span>", unsafe_allow_html=True)

            with cols[6]:
                delete_key = f"confirm_delete_{row['ID']}"
                if st.session_state.get(delete_key):
                    if st.button("✅ Ya", key=f"yes_delete_{row['ID']}"):
                        delete_job(row["ID"])
                        st.session_state.pop(delete_key, None)
                        st.rerun()
                    if st.button("❌ Batal", key=f"cancel_delete_{row['ID']}"):
                        st.session_state[delete_key] = False
                else:
                    if st.button("🗑️", key=f"delete_{row['ID']}"):
                        st.session_state[delete_key] = True


def admin_view():
    from datetime import datetime

    st.header("📋 All Jobs Overview")

    # Fetch all jobs
    jobs = get_all_jobs()
    df = pd.DataFrame(jobs, columns=["ID", "Username", "Unit", "Job", "Stage", "Start Date"])

    # Ensure Start Date is datetime
    df["Start Date"] = pd.to_datetime(df["Start Date"])

    # Stage duration limits in days
    stage_limits = {
        "Perencanaan": 7,
        "Pelaksanaan": 21,
        "Pelaporan": 28,
        "Selesai": None  # always valid
    }

    def get_stage_validity(stage, start_date):
        if stage == "Selesai":
            return "✅ Valid"
        if stage not in stage_limits:
            return "❓ Unknown"
        days_elapsed = (datetime.now() - start_date).days
        return "✅ Valid" if days_elapsed <= stage_limits[stage] else "⚠️ Expired"

    # Add Validitas column
    df["Validitas"] = df.apply(lambda row: get_stage_validity(row["Stage"], row["Start Date"]), axis=1)

    # Format Start Date for display
    df["Start Date"] = df["Start Date"].dt.strftime("%Y-%m-%d")

    # Stage options and colors
    stage_options = ["Perencanaan", "Pelaksanaan", "Pelaporan", "Selesai"]
    stage_colors = {
        "Perencanaan": "#f0ad4e",
        "Pelaksanaan": "#0275d8",
        "Pelaporan": "#5cb85c",
        "Selesai": "#6c757d"
    }

    # Filters
    with st.expander("🔍 Filter Jobs", expanded=True):
        unit_filter = st.multiselect("Filter by Unit", options=df["Unit"].unique())
        user_filter = st.multiselect("Filter by User", options=df["Username"].unique())
        date_range = st.date_input("Filter by Date", [])
        validity_filter = st.selectbox("Filter by Validity", options=["All", "Valid", "Expired"])

        if unit_filter:
            df = df[df["Unit"].isin(unit_filter)]
        if user_filter:
            df = df[df["Username"].isin(user_filter)]
        if len(date_range) == 2:
            df = df[
                (pd.to_datetime(df["Start Date"], format='ISO8601') >= pd.to_datetime(date_range[0])) &
                (pd.to_datetime(df["Start Date"], format='ISO8601') <= pd.to_datetime(date_range[1]))
            ]
        if validity_filter != "All":
            if validity_filter == "Valid":
                df = df[df["Validitas"].str.contains("Valid")]
            else:
                df = df[~df["Validitas"].str.contains("Valid")]

    # Show filtered result in interactive table
    with st.expander("📋 Job Table with Admin Actions", expanded=True):
        st.markdown("### Semua PKP")

        # Table headers
        header = st.columns([1, 2, 2, 3, 2, 3, 2, 3])
        labels = ["No", "Username", "Unit", "PKP", "Tanggal", "Tahap", "Validitas", "Ubah Status"]
        for col, label in zip(header, labels):
            col.markdown(f"**{label}**")

        for i, row in df.reset_index(drop=True).iterrows():
            cols = st.columns([1, 2, 2, 3, 2, 3, 2, 3])

            cols[0].markdown(f"{i + 1}")
            cols[1].markdown(row["Username"])
            cols[2].markdown(row["Unit"])
            cols[3].markdown(row["Job"])
            cols[4].markdown(row["Start Date"])

            # Stage badge
            stage = row["Stage"]
            stage_html = f"<span style='background-color:{stage_colors[stage]}; color:white; padding:4px 10px; border-radius:4px;'>{stage}</span>"
            cols[5].markdown(stage_html, unsafe_allow_html=True)

            # Validity badge
            validity_color = "#28a745" if "Valid" in row["Validitas"] else "#dc3545"
            cols[6].markdown(
                f"<span style='background-color:{validity_color}; color:white; padding:4px 10px; border-radius:4px;'>{row['Validitas']}</span>",
                unsafe_allow_html=True
            )

            # Dropdown to update stage
            with cols[7]:
                new_stage = st.selectbox(
                    label="Ubah Status",
                    options=stage_options,
                    index=stage_options.index(stage),
                    key=f"admin_dropdown_{row['ID']}",
                    label_visibility="collapsed"
                )

                if new_stage != stage:
                    if st.button("🔄 Update", key=f"admin_update_{row['ID']}"):
                        update_job_stage(row["ID"], new_stage)
                        st.rerun()
                else:
                    st.markdown("<div style='margin-top: -10px; color: gray;'>No changes</div>", unsafe_allow_html=True)

    # Stage Distribution Chart (Improved UI)
    st.header("📈 Distribusi Tahapan PKP")

    stage_counts = df["Stage"].value_counts().reset_index()
    stage_counts.columns = ["Stage", "Count"]

    stage_color_map = {
        "Perencanaan": "#f0ad4e",
        "Pelaksanaan": "#0275d8",
        "Pelaporan": "#5cb85c",
        "Selesai": "#6c757d"
    }
    stage_counts["Color"] = stage_counts["Stage"].map(stage_color_map)

    fig1 = px.bar(
        stage_counts,
        x="Count",
        y="Stage",
        orientation="h",
        color="Stage",
        color_discrete_map=stage_color_map,
        title="Distribusi PKP Berdasarkan Tahap",
    )

    fig1.update_layout(
        font=dict(
            family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Helvetica Neue", sans-serif',
            size=20,
            color="#333"
        ),
        yaxis_title="Tahap",
        xaxis_title="Jumlah PKP",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(l=40, r=20, t=40, b=40),
    )

    st.plotly_chart(fig1, use_container_width=True)

    # Valid vs Expired Chart
    validity_summary = df["Validitas"].apply(lambda v: "Valid" if "Valid" in v else "Expired").value_counts().reset_index()
    validity_summary.columns = ["Status", "Count"]

    color_map_validity = {
        "Valid": "#28a745",
        "Expired": "#dc3545"
    }

    fig2 = px.pie(
        validity_summary,
        names="Status",
        values="Count",
        color="Status",
        color_discrete_map=color_map_validity,
        title="Status Validitas PKP (Valid vs Expired)",
        hole=0.4  # donut style
    )

    fig2.update_layout(
        font=dict(
            family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Helvetica Neue", sans-serif',
            size=18,
            color="#333"
        ),
        showlegend=True,
        margin=dict(l=40, r=20, t=40, b=40),
    )

    st.plotly_chart(fig2, use_container_width=True)
# User View
if not user["is_admin"]:
    user_view()

# Admin View
else: 
    admin_view()

