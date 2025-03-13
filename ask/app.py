import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF for reading PDFs
import os
from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.embeddings.google import GeminiEmbedding

# ✅ Configure Gemini Embeddings
Settings.embed_model = GeminiEmbedding(model_name="models/embedding-001")

# ✅ Load API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", st.secrets["GEMINI_API_KEY"])
genai.configure(api_key=GEMINI_API_KEY)


# ✅ Extract text from PDFs
def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file using PyMuPDF."""
    doc = fitz.open(pdf_path)
    text = f"Document: {os.path.basename(pdf_path)}\n\n"
    for page in doc:
        text += page.get_text("text") + "\n"
    return text


# ✅ Load Data and Create Index
@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner("Loading and indexing documents..."):
        docs = []
        data_dir = "./data"  # Directory containing PDF files

        # Read all PDF files in the directory
        for filename in os.listdir(data_dir):
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(data_dir, filename)
                text = extract_text_from_pdf(pdf_path)
                doc = Document(text=text)
                docs.append(doc)

        # Create an index from extracted documents
        index = VectorStoreIndex.from_documents(docs)
        return index


index = load_data()


# ✅ Gemini Response Generator
def get_gemini_response(prompt):
    """Generate response using Gemini AI."""
    model = genai.GenerativeModel("gemini-1.5-pro-latest")  # Use "gemini-1.5-flash-latest" for speed
    response = model.generate_content(prompt)
    return response.text if response else "Sorry, I couldn't generate a response."


# ✅ Streamlit UI
st.title("Chat with Your PDFs 🤖📚 (Gemini-Powered)")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Ask me a question based on your PDFs!"}]

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
            st.session_state.messages.append({"role": "assistant", "content": response})
