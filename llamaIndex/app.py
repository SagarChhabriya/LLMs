import streamlit as st
import google.generativeai as genai
import os
from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.embeddings.google import GeminiEmbedding

# ✅ Configure Gemini Embeddings (Use `GeminiEmbedding`, not `GoogleGenerativeAIEmbedding`)
Settings.embed_model = GeminiEmbedding(model_name="models/embedding-001")

# ✅ Load API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", st.secrets["GEMINI_API_KEY"])
genai.configure(api_key=GEMINI_API_KEY)

# ✅ Load Data and Create Index


@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner("Loading and indexing documents..."):
        reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
        docs = reader.load_data()
        index = VectorStoreIndex.from_documents(docs)
        return index


index = load_data()

# ✅ Gemini Response Generator


def get_gemini_response(prompt):
    # Use "gemini-1.5-flash-latest" for speed
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    # model = genai.GenerativeModel("gemini-1.5-flash-latest")
    response = model.generate_content(prompt)
    return response.text if response else "Sorry, I couldn't generate a response."


# ✅ Streamlit UI
st.title("Chat with Documents 🤖📚 (Gemini-Powered)")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question!"}]

if prompt := st.chat_input("Your question"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display previous messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Generate response using Gemini
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_gemini_response(prompt)
            st.write(response)
            st.session_state.messages.append(
                {"role": "assistant", "content": response})
