# 1. Configure app secrets

# 2. Install dependencies
# 2.1. Local development
# 2.2. Cloud development
# 3. Build the app
# 3.1. Import libraries

from llama_index.core import VectorStoreIndex, ServiceContext, Document
from llama_index.llms.openai import OpenAI  # Updated import
from llama_index.core.readers import SimpleDirectoryReader
import streamlit as st
import openai
from llama_index.core import Settings


# 3.2. Initialize message history
openai.api_key = st.secrets.OPENAI_API_KEY
st.header("Chat with the Streamlit docs 💬 📚")

if "messages" not in st.session_state.keys():  # Initialize the chat message history
    st.session_state.messages = [
        {"role": "assistant",
            "content": "Ask me a question about Streamlit's open-source Python library!"}
    ]

# 3.3. Load and index data


@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the Streamlit docs – hang tight! This should take 1-2 minutes."):
        reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
        docs = reader.load_data()

        # Set default LLM settings
        Settings.llm = OpenAI(
            model="gpt-3.5-turbo", temperature=0.5, system_prompt="You are an expert...")
        # Create the index without service_context
        index = VectorStoreIndex.from_documents(docs)
        return index


index = load_data()


# 3.4. Create the chat engine
chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

# 3.5. Prompt for user input and display message history
# Prompt for user input and save to chat history
if prompt := st.chat_input("Your question"):
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages:  # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])


# 3.6. Pass query to chat engine and display response

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            # Add response to message history
            st.session_state.messages.append(message)

# 4. Deploy the app!
