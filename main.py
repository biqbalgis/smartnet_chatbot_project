import streamlit as st
import pandas as pd
import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from components.chat import answer_user_query

# ─── Basic Config & Styles ──────────────────────────────
st.set_page_config(page_title="SmartNet Support Bot", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff;
        color: #000000;
    }
    .chat-box {
        max-height: 500px;
        overflow-y: auto;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 10px;
        background-color: #f9f9f9;
        margin-bottom: 1rem;
    }
    .chat-input {
        position: fixed;
        bottom: 2rem;
        left: 5%;
        width: 90%;
    }
    </style>
""", unsafe_allow_html=True)

# ─── Dummy Users (Username:Password) ────────────────────
users = {
    "admin": "admin123",
    "user": "user123"
}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.role = ""

if not st.session_state.authenticated:
    st.title("🔐 SmartNet Support Bot Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state.authenticated = True
            st.session_state.role = "admin" if username == "admin" else "user"
            st.rerun()
        else:
            st.error("Invalid credentials")
    st.stop()

# ─── Panel Selector ─────────────────────────────────────
role = st.session_state.role
page = st.sidebar.radio("Select Panel", ["User Panel", "Admin Panel"] if role == "admin" else ["User Panel"])

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ─── USER PANEL ─────────────────────────────────────────
if page == "User Panel":
    st.title(" SmartNet Support Bot - User Panel")
    st.markdown("Ask about internet issues, Wi-Fi problems, or billing questions.")

    # Chat History
    with st.container():
        st.markdown('<div class="chat-box">', unsafe_allow_html=True)
        for turn in st.session_state.chat_history:
            st.markdown(f"** You:** {turn['user']}")
            st.markdown(f"** Bot:** {turn['bot']}")
        st.markdown('</div>', unsafe_allow_html=True)

    # Chat Input at Bottom
    with st.container():
        st.markdown('<div class="chat-input">', unsafe_allow_html=True)
        with st.form(key="user_input_form", clear_on_submit=True):
            user_query = st.text_input("Type your issue:")
            submitted = st.form_submit_button("Send")
        st.markdown('</div>', unsafe_allow_html=True)

    if submitted and user_query:
        with st.spinner("Getting help..."):
            reply = answer_user_query(user_query, st.session_state.chat_history)
            st.session_state.chat_history.append({"user": user_query, "bot": reply})

    if st.button("🔁 Clear Chat"):
        st.session_state.chat_history = []

# ─── ADMIN PANEL ────────────────────────────────────────
elif page == "Admin Panel":
    st.title(" Admin Panel - SmartNet Support Bot")
    st.markdown("### Complaint Logs")

    log_file = "data/complaints.csv"
    if os.path.exists(log_file):
        df = pd.read_csv(log_file)
        st.dataframe(df)
    else:
        st.warning("No complaints found.")

    st.markdown("\n---\n")
    st.info("Future features: search logs, assign tickets, export data")

