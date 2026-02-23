import streamlit as st
import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def transactions_page():
    if not st.session_state.logged_in:
        st.warning("Please login first.")
        return

    user_role = st.session_state.role
    st.subheader("📚 Transactions")

    # --------------------------
    # 1️⃣ User: Request a Book
    # --------------------------
    if user_role != "admin":
        st.subheader("Request a Book")
        book_id = st.number_input("Book ID", min_value=1, step=1)
        if st.button("Request Book", key="request_book"):
            resp = st.session_state.session.post(f"{BASE_URL}/transactions/request/{book_id}")
            if resp.status_code == 200:
                st.success("Book request submitted successfully")
            else:
                try:
                    st.error(resp.json().get("detail", "Failed to request book"))
                except:
                    st.error("Failed to request book")

    # --------------------------
    # 2️⃣ User: My Active Books
    # --------------------------
    st.subheader("📖 My Active Books")
    try:
        resp = st.session_state.session.get(f"{BASE_URL}/transactions/my-books")
        if resp.status_code == 200:
            my_books = resp.json().get("my_books", [])
            if my_books:
                for book in my_books:
                    issue_date = datetime.fromisoformat(book["issue_date"]).strftime("%Y-%m-%d")
                    due_date = datetime.fromisoformat(book["due_date"]).strftime("%Y-%m-%d")
                    st.write(f"Transaction ID: {book['id']} | Title: {book['title']} | Issue: {issue_date} | Due: {due_date}")
            else:
                st.info("No active books")
        else:
            st.error("Failed to fetch active books")
    except:
        st.error("Error fetching active books")

    # --------------------------
    # 3️⃣ User: Return Book
    # --------------------------
    st.subheader("Return a Book")
    transaction_id = st.number_input("Transaction ID", min_value=1, step=1, key="return_id")
    if st.button("Return Book", key="return_book"):
        resp = st.session_state.session.post(f"{BASE_URL}/transactions/return/{transaction_id}")
        if resp.status_code == 200:
            data = resp.json()
            st.success(f"Book returned successfully! Fine: ₹{data.get('fine', 0)}")
        else:
            try:
                st.error(resp.json().get("detail", "Failed to return book"))
            except:
                st.error("Failed to return book")

    # --------------------------
    # 4️⃣ Admin Only: Issue Book Directly
    # --------------------------
    if user_role == "admin":
        st.subheader("Issue Book (Admin)")
        user_id = st.number_input("User ID", min_value=1, step=1, key="issue_user")
        book_id_admin = st.number_input("Book ID", min_value=1, step=1, key="issue_book")
        if st.button("Issue Book", key="issue_book_btn"):
            resp = st.session_state.session.post(f"{BASE_URL}/transactions/issue", params={"user_id": user_id, "book_id": book_id_admin})
            if resp.status_code == 200:
                st.success("Book issued successfully")
            else:
                try:
                    st.error(resp.json().get("detail", "Failed to issue book"))
                except:
                    st.error("Failed to issue book")

        # --------------------------
        # 5️⃣ Admin Only: View All Transactions
        # --------------------------
        st.subheader("All Transactions (Admin)")
        try:
            resp = st.session_state.session.get(f"{BASE_URL}/transactions")
            if resp.status_code == 200:
                transactions = resp.json().get("transactions", [])
                if transactions:
                    for t in transactions:
                        issue_date = datetime.fromisoformat(t["issue_date"]).strftime("%Y-%m-%d") if t["issue_date"] else "-"
                        due_date = datetime.fromisoformat(t["due_date"]).strftime("%Y-%m-%d") if t["due_date"] else "-"
                        return_date = datetime.fromisoformat(t["return_date"]).strftime("%Y-%m-%d") if t["return_date"] else "-"
                        st.write(f"ID: {t['id']} | User: {t['user_name']} | Book: {t['book_title']} | Issue: {issue_date} | Due: {due_date} | Return: {return_date} | Status: {t['status']}")
                else:
                    st.info("No transactions found")
            else:
                st.warning("Failed to fetch transactions")
        except:
            st.error("Error fetching transactions")

        # --------------------------
        # 6️⃣ Admin Only: Pending Requests
        # --------------------------
        st.subheader("Pending Book Requests")
        try:
            resp = st.session_state.session.get(f"{BASE_URL}/transactions/requests")
            if resp.status_code == 200:
                requests_data = resp.json().get("requests", [])
                if requests_data:
                    for req in requests_data:
                        st.write(f"Request ID: {req['id']} | User: {req['user_name']} ({req['user_email']}) | Book: {req['book_title']} | Status: {req['status']}")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"Approve {req['id']}", key=f"approve_{req['id']}"):
                                approve_resp = st.session_state.session.post(f"{BASE_URL}/transactions/approve/{req['id']}")
                                if approve_resp.status_code == 200:
                                    st.success(f"Request {req['id']} approved and book issued")
                                    st.rerun()
                                else:
                                    st.error("Failed to approve request")
                        with col2:
                            if st.button(f"Reject {req['id']}", key=f"reject_{req['id']}"):
                                reject_resp = st.session_state.session.post(f"{BASE_URL}/transactions/reject/{req['id']}")
                                if reject_resp.status_code == 200:
                                    st.success(f"Request {req['id']} rejected")
                                    st.rerun()
                                else:
                                    st.error("Failed to reject request")
                else:
                    st.info("No pending requests")
            else:
                st.warning("Failed to fetch pending requests")
        except:
            st.error("Error fetching pending requests")