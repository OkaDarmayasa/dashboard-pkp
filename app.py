import streamlit as st
from db import *
from auth import login
import pandas as pd
import plotly.express as px

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


# User View
if not user["is_admin"]:
    st.header("📌 Tambah PKP Baru")

    # Text input tied to session_state
    if "job_name" not in st.session_state:
        st.session_state.job_name = ""

    job_name = st.text_input("PKP", key="job_name")

    if st.button("Tambah PKP") and job_name.strip() != "":
        add_job(user['id'], job_name.strip())
        st.success("PKP Berhasil Ditambahkan!")

        # Clear the input and refresh the page
        st.session_state.job_name = ""
        st.rerun()

    st.header("📊 PKP Saya")
    user_jobs = get_user_jobs(user['id'])
    df = pd.DataFrame(user_jobs, columns=["ID", "UserID", "Job", "Stage", "Start Date"])
    # Ensure date formatting
    df["Start Date"] = pd.to_datetime(df["Start Date"]).dt.strftime("%Y-%m-%d")

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
        header = st.columns([1, 3, 2, 2, 4])  # Adjust width ratios
        header_labels = ["No", "PKP", "Tanggal", "Tahap", "Action"]
        for col, label in zip(header, header_labels):
            col.markdown(f"**{label}**")

        # Render each row with columns and controls
        for i, row in df.reset_index(drop=True).iterrows():
            cols = st.columns([1, 3, 2, 2, 4])

            # Column 1: Row number starting from 1
            cols[0].markdown(f"{i + 1}")

            # Column 2: Job Name
            cols[1].markdown(row["Job"])

            # Column 3: Start Date
            cols[2].markdown(row["Start Date"])

            # Column 4: Stage with badge color
            stage = row["Stage"]
            stage_html = f"<span style='background-color:{stage_colors[stage]}; color:white; padding:4px 10px; border-radius:4px;'>{stage}</span>"
            cols[3].markdown(stage_html, unsafe_allow_html=True)

            # Column 5: Dropdown and Update button
            with cols[4]:
                new_stage = st.selectbox(
                    label="Change Stage",
                    options=stage_options,
                    index=stage_options.index(stage),
                    key=f"dropdown_{row['ID']}",
                    label_visibility="collapsed"  # hides the label space
                )

                if new_stage != stage:
                    if st.button("🔄 Update", key=f"update_{row['ID']}"):
                        update_job_stage(row["ID"], new_stage)
                        st.rerun()
                else:
                    cols[4].markdown("<span style='color:gray;'>No changes</span>", unsafe_allow_html=True)

# Admin View
else:
    st.header("📋 All Jobs Overview")
    jobs = get_all_jobs()
    df = pd.DataFrame(jobs, columns=["ID", "Username", "Unit", "Job", "Stage", "Start Date"])

    with st.expander("🔍 Filter Jobs"):
        unit_filter = st.multiselect("Filter by Unit", options=df["Unit"].unique())
        user_filter = st.multiselect("Filter by User", options=df["Username"].unique())
        date_range = st.date_input("Filter by Date", [])

        if unit_filter:
            df = df[df["Unit"].isin(unit_filter)]
        if user_filter:
            df = df[df["Username"].isin(user_filter)]
        if len(date_range) == 2:
            df = df[(df["Start Date"] >= pd.to_datetime(date_range[0]).isoformat()) & 
                    (df["Start Date"] <= pd.to_datetime(date_range[1]).isoformat())]

    st.dataframe(df)

    st.header("📈 Stage Distribution")
    stage_counts = df["Stage"].value_counts().reset_index()
    stage_counts.columns = ["Stage", "Count"]
    fig = px.pie(stage_counts, names="Stage", values="Count", title="Job Stages Overview")
    st.plotly_chart(fig)
