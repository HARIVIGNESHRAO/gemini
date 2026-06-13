import streamlit as st
import os
import google.genai as genai
from google.genai import types

st.set_page_config(page_title="Gemini Chat App", page_icon="💬", layout="centered")
st.title("💬 Gemini AI Chat")

# --- 1. SET UP THE GEMINI API CLIENT ---
# Streamlit reads this from your "Advanced Settings -> Secrets" on the dashboard
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.info("💡 Please add your GEMINI_API_KEY to continue.", icon="🔑")
    api_key = st.sidebar.text_input("Gemini API Key", type="password")
    if not api_key:
        st.stop()

# Initialize the official Google GenAI Client
@st.cache_resource
def get_genai_client(key: str):
    return genai.Client(api_key=key)

client = get_genai_client(api_key)

# --- 2. INITIALIZE IN-MEMORY CHAT HISTORY ---
# This acts as your temporary database directly inside the browser session
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. RENDER THE EXISTING CONVERSATION ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 4. HANDLE NEW MESSAGES ---
if user_input := st.chat_input("What is on your mind?"):
    # Immediately show what the user typed
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Save user message to our session state list
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Convert the session history into the precise format the new SDK expects
    contents = []
    for msg in st.session_state.messages:
        sdk_role = "user" if msg["role"] == "user" else "model"
        contents.append(
            types.Content(
                role=sdk_role,
                parts=[types.Part.from_text(text=msg["content"])]
            )
        )

    # Stream or generate assistant response directly from the cloud client
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents
                )
                reply_text = response.text
                st.markdown(reply_text)
                
                # Save assistant reply to session state
                st.session_state.messages.append({"role": "assistant", "content": reply_text})
                
            except Exception as e:
                st.error(f"Gemini API Error: {str(e)}")