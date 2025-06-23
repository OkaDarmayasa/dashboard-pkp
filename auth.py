import streamlit as st
from db import get_user

def login():
    with st.sidebar:
        st.write("Login")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            user = get_user(username, password)
            if user:
                st.session_state.user = {
                    "id": user[0],
                    "username": user[1],
                    "unit": user[3],
                    "is_admin": user[4]
                }
                st.rerun()
            else:
                st.sidebar.error("Invalid credentials")
