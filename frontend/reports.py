import streamlit as st

BASE_URL = "http://127.0.0.1:8000"

def reports_page():
    if not st.session_state.logged_in:
        st.warning("Please login first.")
        return

    if st.session_state.role != "admin":
        st.error("Admin access required")
        return

    report_type = st.selectbox(
        "Select Report",
        ["Active Issues", "Overdue Books", "Fine Summary", "Book Summary", "User Activity"]
    )

    st.divider()

    if report_type == "Active Issues":
        response = st.session_state.session.get(f"{BASE_URL}/reports/active-issues")
        if response.status_code == 200:
            data = response.json()["active_issues"]
            st.dataframe(data)
        else:
            st.error(f"Failed to fetch report: {response.status_code}")

    elif report_type == "Overdue Books":
        response = st.session_state.session.get(f"{BASE_URL}/reports/overdue")
        if response.status_code == 200:
            data = response.json()["overdue_books"]
            st.dataframe(data)
        else:
            st.error(f"Failed to fetch report: {response.status_code}")

    elif report_type == "Fine Summary":
        response = st.session_state.session.get(f"{BASE_URL}/reports/fine-summary")
        if response.status_code == 200:
            total = response.json()["total_fines_collected"]
            st.metric("Total Fines Collected (₹)", total)
        else:
            st.error(f"Failed to fetch report: {response.status_code}")

    elif report_type == "Book Summary":
        response = st.session_state.session.get(f"{BASE_URL}/reports/book-summary")
        if response.status_code == 200:
            data = response.json()["books"]
            st.dataframe(data)
        else:
            st.error(f"Failed to fetch report: {response.status_code}")

    elif report_type == "User Activity":
        response = st.session_state.session.get(f"{BASE_URL}/reports/user-activity")
        if response.status_code == 200:
            data = response.json()["user_activity"]
            st.dataframe(data)
        else:
            st.error(f"Failed to fetch report: {response.status_code}")
