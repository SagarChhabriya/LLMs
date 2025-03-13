import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF for reading PDFs
import os
import time  # For streaming effect
import re  # For splitting text into sentences
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

# ✅ Gemini Response Generator with Sentence-by-Sentence Streaming


def get_gemini_response(prompt):
    """Generate response using Gemini AI and return it sentence by sentence for simulated streaming."""
    # model = genai.GenerativeModel("gemini-1.5-pro-latest")  # Use "gemini-1.5-flash-latest" for speed
    # Use "gemini-1.5-flash-latest" for speed
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    # No streaming support, so we simulate it
    response = model.generate_content(prompt)

    response_text = response.text if response and response.text else "Sorry, I couldn't generate a response."

    # Split response into sentences
    # Splits on .!? but keeps them
    sentences = re.split(r'(?<=[.!?]) +', response_text)

    for sentence in sentences:
        yield sentence.strip()  # Yield one sentence at a time


# ✅ Streamlit UI
st.title("RAG-Based-Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question based on your PDFs!"}]

if prompt := st.chat_input("Your question"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display previous messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Generate response using Gemini with sentence-by-sentence streaming
    with st.chat_message("assistant"):
        response_placeholder = st.empty()  # Placeholder for dynamic updates
        full_response = ""

        for sentence in get_gemini_response(prompt):
            full_response += sentence + " "
            response_placeholder.write(full_response)  # Update dynamically
            time.sleep(0.5)  # Pause for effect

        # Store the final response in chat history
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response})
