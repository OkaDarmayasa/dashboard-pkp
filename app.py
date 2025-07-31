import streamlit as st
from db import *
from auth import login
from custom_pages.indikator import user_view, admin_view
from components.layout import *

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

# ─────────────────────── CUSTOM CSS FOR COLOURS ────────────────────────
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


# ─── AUTHENTICATION ────────────────────────────────────────
if 'user' not in st.session_state:
    login()
    st.stop()

user = st.session_state.user

# ─── PAGE ROUTING ──────────────────────────────────────────
if "selected_page" not in st.session_state:
    st.session_state.selected_page = "21 Indikator"

# Show sidebar and capture updated selection
st.session_state.selected_page = sidebar(st.session_state.selected_page)

# ─── DISPLAY SELECTED PAGE ─────────────────────────────────
display_page(st.session_state.selected_page, is_admin=user["is_admin"])