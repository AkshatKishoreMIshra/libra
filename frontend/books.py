import streamlit as st

BASE_URL = "http://127.0.0.1:8000"

def books_page():
    if not st.session_state.logged_in:
        st.warning("Please login first.")
        return

    if st.session_state.role != "admin":
        st.error("Admin access required")
        return

    # ---------------------------
    # 1️⃣ Add New Book
    # ---------------------------
    st.subheader("📚 Add New Book")

    title = st.text_input("Title", key="add_title")
    author = st.text_input("Author", key="add_author")
    category = st.text_input("Category", key="add_category")
    copies = st.number_input("Total Copies", min_value=1, key="add_copies")

    if st.button("Add Book"):
        response = st.session_state.session.post(
            f"{BASE_URL}/books/",
            json={
                "title": title,
                "author": author,
                "category": category,
                "total_copies": copies
            }
        )
        if response.status_code in [200,201]:
            st.success("Book added successfully")
            st.rerun()
        else:
            st.error(f"Failed to add book: {response.text}")

    st.divider()

    # ---------------------------
    # 2️⃣ Update Book
    # ---------------------------
    st.subheader("✏️ Update Existing Book")

    book_id = st.number_input("Book ID to Update", min_value=1, key="update_id")
    new_title = st.text_input("New Title", key="update_title")
    new_author = st.text_input("New Author", key="update_author")
    new_category = st.text_input("New Category", key="update_category")
    new_copies = st.number_input("New Total Copies", min_value=1, key="update_copies")

    if st.button("Update Book"):
        response = st.session_state.session.put(
            f"{BASE_URL}/books/{book_id}",
            json={
                "title": new_title,
                "author": new_author,
                "category": new_category,
                "total_copies": new_copies
            }
        )
        if response.status_code == 200:
            st.success("Book updated successfully")
            st.rerun()
        else:
            st.error(f"Failed to update book: {response.text}")

    st.divider()

    # ---------------------------
    # 3️⃣ View All Books
    # ---------------------------
    st.subheader("📖 All Books")

    response = st.session_state.session.get(f"{BASE_URL}/books/")
    if response.status_code == 200:
        books = response.json()  # directly use the list

        for book in books:
            st.write(f"{book['id']}: {book['title']}")
    else:
        st.error(f"Failed to fetch books: {response.text}")

    st.divider()

    # ---------------------------
    # 4️⃣ Search Books
    # ---------------------------
    st.subheader("🔍 Search Books")

    search_query = st.text_input("Search by Title, Author, or Category", key="search_query")
    if st.button("Search"):
        if search_query.strip() == "":
            st.warning("Enter a search query first")
        else:
            response = st.session_state.session.get(
                f"{BASE_URL}/books/search",
                params={"query": search_query}
            )
            if response.status_code == 200:
                results = response.json()
                st.dataframe(results)
            else:
                st.error(f"Failed to search books: {response.text}")

    st.divider()

    # ---------------------------
    # 5️⃣ Check Book Availability
    # ---------------------------
    st.subheader("✅ Check Book Availability")

    check_id = st.number_input("Book ID to Check", min_value=1, key="check_id")
    if st.button("Check Availability"):
        response = st.session_state.session.get(f"{BASE_URL}/books/{check_id}/availability")
        if response.status_code == 200:
            data = response.json()
            st.write(f"Available Copies: {data['available_copies']}")
            st.write(f"Is Available: {'Yes' if data['is_available'] else 'No'}")
        else:
            st.error(f"Failed to check availability: {response.text}")
