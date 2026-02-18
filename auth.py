"""Authentication helpers for the Streamlit app."""

import bcrypt
import streamlit as st
from supabase_client import supabase


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def authenticate(username: str, password: str) -> dict | None:
    """Return user row if credentials are valid, else None."""
    response = (
        supabase.table("users")
        .select("id, username, password_hash")
        .eq("username", username)
        .limit(1)
        .execute()
    )
    if not response.data:
        return None
    user = response.data[0]
    if verify_password(password, user["password_hash"]):
        return {"id": user["id"], "username": user["username"]}
    return None


def login_page():
    """Render login form. Returns True if user is authenticated."""
    if st.session_state.get("user"):
        return True

    st.title("finlive – Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")

    if submitted:
        if not username or not password:
            st.error("Enter both username and password.")
            return False
        user = authenticate(username, password)
        if user:
            st.session_state["user"] = user
            st.rerun()
        else:
            st.error("Invalid username or password.")
    return False


def logout_button():
    """Render a logout button in the sidebar."""
    user = st.session_state.get("user", {})
    st.sidebar.markdown(f"Logged in as **{user.get('username', '')}**")
    if st.sidebar.button("Log out"):
        st.session_state.pop("user", None)
        st.rerun()


def get_current_user_id() -> int:
    """Return the logged-in user's id."""
    return st.session_state["user"]["id"]
