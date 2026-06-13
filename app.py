import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_BASE = os.getenv("API_BASE", "http://localhost:8000")

st.set_page_config(page_title="AI Chat", layout="wide")
st.title("🤖 Mini AI Chat App - Gemini")

# Sidebar
st.sidebar.header("💬 Chat Threads")

def get_threads():
    try:
        return requests.get(f"{API_BASE}/threads/").json()
    except:
        return []

# New Chat Button
if st.sidebar.button("➕ New Chat", use_container_width=True):
    requests.post(f"{API_BASE}/threads/")
    st.rerun()

# List existing threads
threads = get_threads()
for thread in threads:
    if st.sidebar.button(
        thread.get("title", f"Chat {thread['id']}"), 
        key=f"t_{thread['id']}",
        use_container_width=True
    ):
        st.session_state.current_thread = thread['id']
        st.rerun()

# Main Chat Area
current_thread = st.session_state.get("current_thread")

if current_thread:
    try:
        msgs = requests.get(f"{API_BASE}/threads/{current_thread}/messages").json()
    except:
        msgs = []

    for msg in msgs:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Type your message..."):
        with st.spinner("🤔 Gemini is thinking..."):
            try:
                requests.post(f"{API_BASE}/chat", 
                            json={"thread_id": current_thread, "message": prompt})
            except:
                st.error("Backend not running!")
        st.rerun()
else:
    st.info("👈 Click **New Chat** or select a thread from the sidebar to start chatting")
    st.caption("Powered by Google Gemini 1.5 Flash (Free)")