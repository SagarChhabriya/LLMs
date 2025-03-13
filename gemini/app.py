import streamlit as st
import google.generativeai as genai
import time
import os


# --- Must be the first Streamlit command ---
st.set_page_config(page_title="Gemini AI Bot", page_icon="🤖", layout="wide")

# --- Custom Styling (Grey Theme & Centered Chat) ---
st.markdown(
    """
    <style>
        /* Remove extra padding/margin from Streamlit's default layout */
        .block-container { padding-top: 60px !important; }

        /* Fixed Title Styling */
        .app-title {
            position: fixed;
            top: 10px;
            left: 20px;
            font-size: 24px;
            font-weight: bold;
            color: white;
            background-color: #1e1e1e;
            padding: 10px 15px;
            border-radius: 8px;
            z-index: 1000;
        }

        /* Centered Chat Container */
        .chat-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-top: 60px;
        }

        /* Chat Messages */
        .chat-message {
            border-radius: 10px;
            padding: 12px 16px;
            margin: 8px 0;
            max-width: 60%;
            word-wrap: break-word;
            font-family: Arial, sans-serif;
            text-align: left;
        }

        /* Different Styles for User and Assistant Messages */
        .user {
            background-color: #2b2b2b;
            color: white;
            align-self: flex-end;
        }
        .assistant {
            background-color: #444;
            color: white;
            align-self: flex-start;
        }
        
        /* Typing Animation */
        .typing { animation: blink 1s infinite; }
        @keyframes blink { 0% { opacity: 0.2; } 50% { opacity: 1; } 100% { opacity: 0.2; } }

        /* Hide Default Streamlit Header */
        header {visibility: hidden;}

        /* Background Color */
        .stApp { background-color: #1e1e1e; }

    </style>
    """,
    unsafe_allow_html=True,
)

# --- Configure API Key ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # for github actions
    # genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

except KeyError:
    st.sidebar.error("⚠️ API key not found! Please check your secrets.")
    st.stop()

# --- Fixed Title (Always Visible) ---
st.markdown("<div class='app-title'>🤖 Gemini AI Bot</div>",
            unsafe_allow_html=True)

# --- Expandable Sidebar ---
with st.sidebar.expander("⚙️ Settings", expanded=False):
    MODEL_NAME = st.selectbox(
        "Select Model",
        ["gemini-1.5-flash-latest"],
        # ["gemini-1.5-flash-latest", "gemini-1.5-pro-latest"],
        index=0,
    )
    st.write("📝 Choose a model for your chatbot.")
    st.markdown("---")
    st.write("💡 **Tip:** Gemini 1.5 Flash is faster but Pro is more powerful.")

# --- Initialize Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Previous Messages (Centered) ---
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

for message in st.session_state.messages:
    role_class = "user" if message["role"] == "user" else "assistant"
    avatar = "🧑‍💻" if message["role"] == "user" else "🤖"
    st.markdown(
        f"<div class='chat-message {role_class}'> {avatar} {message['content']} </div>",
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)

# --- User Input ---
if prompt := st.chat_input("Type your message..."):
    # Display user message instantly (Centered)
    st.markdown(
        f"<div class='chat-message user'> 🧑‍💻 {prompt} </div>", unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)

        # Typing animation effect
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            animated_response = ""
            for letter in response.text:
                animated_response += letter
                message_placeholder.markdown(
                    f"<div class='chat-message assistant'>🤖 {animated_response}</div>", unsafe_allow_html=True
                )
                time.sleep(0.02)  # Typing speed effect

        # Append assistant response to session
        st.session_state.messages.append(
            {"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"❌ Error: {e}")
