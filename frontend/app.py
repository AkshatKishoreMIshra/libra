import streamlit as st
from auth import login_page, logout
from books import books_page
from members import members_page
from transactions import transactions_page
from reports import reports_page
from signup import signup_page  # import the new signup page

st.set_page_config(page_title="Library Management System", layout="wide")

st.title("📚 Library Management System")

# ----------------------
# Initialize session
# ----------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "session" not in st.session_state:
    import requests
    st.session_state.session = requests.Session()

# ----------------------
# Logout button
# ----------------------
logout()

# ----------------------
# Sidebar menu
# ----------------------
if st.session_state.logged_in:
    menu_items = ["Dashboard", "Books", "Members", "Transactions", "Reports"] if st.session_state.role == "admin" else ["Dashboard", "Transactions"]
    menu = st.sidebar.selectbox("Navigation", menu_items)
else:
    # If not logged in, allow Login or Sign-Up
    menu = st.sidebar.selectbox("Navigation", ["Login", "Sign Up"])

# ----------------------
# Render pages
# ----------------------
if menu == "Login":
    login_page()
elif menu == "Sign Up":
    signup_page()
elif menu == "Dashboard":
    st.warning("Dashboard implementation")  # keep your dashboard code here
elif menu == "Books":
    books_page()
elif menu == "Members":
    members_page()
elif menu == "Transactions":
    transactions_page()
elif menu == "Reports":
    reports_page()
