import streamlit as st
import os
import google.genai as genai
from google.genai import types

st.set_page_config(page_title="Gemini Chat App", page_icon="💬", layout="centered")
st.title("💬 Gemini AI Chat")

# --- 1. HANDLE CLOUD API KEY ENVIRONMENT CONFIGURATION ---
# Checks system environment first, falls back to Streamlit Dashboard Secrets
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.info("💡 Please add your GEMINI_API_KEY to continue.", icon="🔑")
    # Sidebar credential fallback box for seamless local workstation validation
    api_key = st.sidebar.text_input("Gemini API Key", type="password")
    if not api_key:
        st.stop()

# Initialize the official Google GenAI Client wrapper securely
@st.cache_resource
def get_genai_client(key: str):
    return genai.Client(api_key=key)

client = get_genai_client(api_key)

# --- 2. INITIALIZE IN-MEMORY CHAT CONTEXT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. RENDER ON-SCREEN CONVERSATION TIMELINE ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 4. STREAM NEW INCOMING CHAT INTERACTIONS ---
if user_input := st.chat_input("What is on your mind?"):
    # Render user prompt immediately onto the screen layout canvas
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Store history map blocks locally inside session state arrays
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Pack the chronological chain using proper modern SDK object types
    contents = []
    for msg in st.session_state.messages:
        # Translate conversational markers ('user'/'assistant') to SDK indicators ('user'/'model')
        sdk_role = "user" if msg["role"] == "user" else "model"
        contents.append(
            types.Content(
                role=sdk_role,
                parts=[types.Part.from_text(text=msg["content"])]
            )
        )

    # Fetch response data payloads directly from the live endpoint container
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents
                )
                reply_text = response.text
                st.markdown(reply_text)
                
                # Append finalized model response logs into session tracking variables
                st.session_state.messages.append({"role": "assistant", "content": reply_text})
                
            except Exception as e:
                st.error(f"Gemini API Error: {str(e)}")