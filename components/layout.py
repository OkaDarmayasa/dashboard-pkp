# layout.py

import streamlit as st

def sidebar(current_page):
    with st.sidebar:
        __, col2, __ = st.columns([1, 1, 1])
        with col2:
            st.image("assets/logo.png", width=100)

        st.markdown(
            """
            <div style='text-align: center; font-size: 20px; font-weight: bold; margin-top: 0px;'>
                Dashboard Tau Kawan
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")

        # Use unique keys to prevent Streamlit conflicts
        if st.button("🏠  Dashboard", use_container_width=True, key="sidebar_dashboard_btn"):
            current_page = "Dashboard"
        if st.button("📊  21 Indikator", use_container_width=True, key="sidebar_21indikator_btn"):
            current_page = "21 Indikator"
        if st.button("📁  TLHP", use_container_width=True, key="sidebar_tlhp_btn"):
            current_page = "TLHP"

        st.markdown("---")

        if st.button("🚪 Logout", key="sidebar_logout_btn"):
            st.session_state.pop("user", None)
            st.rerun()

    return current_page


def under_construction():
    st.title("🚧 Under Construction")
    st.write("This page is currently under construction. Please check back later.")


def display_page(current_page, is_admin):
    if current_page == "Dashboard":
        under_construction()
    elif current_page == "21 Indikator":
        from custom_pages.indikator import admin_view, user_view
        if is_admin:
            admin_view()
        else:
            user_view()
    elif current_page == "TLHP":
        under_construction()
    else:
        st.error("❌ Page not found.")


# Optional helper for dynamic nav
def sidebar_nav_button(label, page_name):
    if st.button(label, use_container_width=True, key=f"sidebar_nav_btn_{page_name}"):
        st.session_state.selected_page = page_name
