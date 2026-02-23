import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"

def signup_page():
    st.title("📝 Library Sign-Up")

    # Input fields
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up"):
        if not name or not email or not password:
            st.warning("All fields are required!")
            return

        if password != confirm_password:
            st.warning("Passwords do not match!")
            return

        # Call backend API to create user
        response = requests.post(
            f"{BASE_URL}/auth/signup",
            json={
                "name": name,
                "email": email,
                "password": password
            }
        )

        if response.status_code == 201:
            st.success("Account created successfully! Please log in.")
        else:
            try:
                st.error(response.json().get("detail", "Failed to create account"))
            except:
                st.error("Failed to create account. Please try again.")

