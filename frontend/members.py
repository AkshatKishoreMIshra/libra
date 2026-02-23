import streamlit as st

BASE_URL = "http://127.0.0.1:8000"

def members_page():
    if not st.session_state.logged_in:
        st.warning("Please login first.")
        return

    if st.session_state.role != "admin":
        st.error("Admin access required")
        return

    st.subheader("📋 Membership Plans")

    # Fetch existing memberships
    response = st.session_state.session.get(f"{BASE_URL}/memberships/")
    if response.status_code == 200:
        memberships = response.json()["memberships"]
        st.dataframe(memberships)
    else:
        st.error("Failed to fetch memberships")

    st.divider()
    st.subheader("➕ Add New Membership")
    name = st.text_input("Membership Name")
    duration = st.number_input("Duration (Days)", min_value=1)
    max_books = st.number_input("Max Books Allowed", min_value=1)
    fine = st.number_input("Fine Per Day (₹)", min_value=0)

    if st.button("Create Membership"):
        response = st.session_state.session.post(
            f"{BASE_URL}/memberships/",
            params={
                "name": name,
                "duration_days": duration,
                "max_books_allowed": max_books,
                "fine_per_day": fine
            }
        )
        if response.status_code == 200:
            st.success("Membership created successfully!")
            st.rerun()
        else:
            st.error(response.text)

    st.divider()
    st.subheader("✏️ Update Membership")
    membership_id = st.number_input("Membership ID", min_value=1)
    new_name = st.text_input("New Name")
    new_duration = st.number_input("New Duration (Days)", min_value=1)
    new_max_books = st.number_input("New Max Books Allowed", min_value=1)
    new_fine = st.number_input("New Fine Per Day", min_value=0)

    if st.button("Update Membership"):
        response = st.session_state.session.put(
            f"{BASE_URL}/memberships/{membership_id}",
            params={
                "name": new_name,
                "duration_days": new_duration,
                "max_books_allowed": new_max_books,
                "fine_per_day": new_fine
            }
        )
        if response.status_code == 200:
            st.success("Membership updated successfully!")
            st.rerun()
        else:
            st.error(response.text)
