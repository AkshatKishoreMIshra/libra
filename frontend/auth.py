import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"

def login_page():
    st.subheader("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        # Initialize session if not exists
        if "session" not in st.session_state:
            st.session_state.session = requests.Session()

        try:
            response = st.session_state.session.post(
                f"{BASE_URL}/auth/login",
                json={"email": email, "password": password}
            )

            # Try parsing JSON safely
            try:
                data = response.json()
            except Exception:
                st.error(f"Login failed. Server returned:\n{response.text}")
                return

            if response.status_code == 200:
                st.session_state.logged_in = True
                st.session_state.role = data.get("role", "user")
                st.success("Login successful")
                st.rerun()
            else:
                st.error(data.get("detail", "Login failed"))

        except requests.exceptions.RequestException as e:
            st.error(f"Failed to connect to server: {e}")


def logout():
    if st.sidebar.button("Logout"):
        if "session" in st.session_state:
            try:
                st.session_state.session.post(f"{BASE_URL}/auth/logout")
            except:
                pass  # ignore errors on logout
        st.session_state.logged_in = False
        st.session_state.role = None
        st.success("Logged out successfully")
        st.rerun()
