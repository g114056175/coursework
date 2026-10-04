# OpenSpec Change Proposal: RAG Q&A System with Streamlit

## 1. Feature Description

This proposal outlines the plan to build a web-based Question-Answering (Q&A) application using a Retrieval-Augmented Generation (RAG) architecture. The application will be built with Python and deployed using Streamlit.

The system will be able to answer questions based on a knowledge base provided by documents. It will support both user-uploaded PDF files and pre-loaded knowledge bases found in the `./RAG_file` directory.

The application will use the Gemini API for its Large Language Model (LLM) capabilities. A key feature will be its conversational memory, allowing for follow-up questions and context-aware interactions in both RAG and non-RAG chat modes.

## 2. Files to be Created / Modified

### New Files:

- **`main.py`**: The main entry point for the Streamlit application, containing UI logic and orchestrating the backend calls.
- **`helpers.py`**: A helper script containing the core RAG logic (document processing, vector store creation, conversational chain setup).
- **`README.md`**: The main project README file, describing the project, its features, and setup instructions.
- **`requirements.txt`**: A text file listing all necessary Python dependencies.
- **`Conversation.md`**: A log of the development process and key decisions.

### Modified Files:

- This is a new feature, so no existing project files will be modified.

## 3. Implementation Plan (Reflecting Final Architecture)

The implementation was broken down into the following key areas:

### a. `requirements.txt`

This file contains the following key packages to ensure a stable environment:

```
streamlit
langchain
google-generativeai
pypdf
faiss-cpu
langchain-google-genai
sentence-transformers
nest-asyncio
```

### b. `README.md`

The README was structured to provide a comprehensive overview:
- **Project Title & User Summary Placeholder**
- **Project Description:** Explains the RAG system, its dual-mode (RAG vs. non-RAG) functionality, and its support for both uploaded and pre-loaded knowledge bases.
- **Features:** A detailed list including the interactive UI, PDF uploads, automatic loading of default RAGs, source selection, **conversational memory**, and vector store downloading.
- **Demo Link:** A link to the deployed Streamlit application.
- **References:** Links to the source materials provided by the user.
- **Local Setup:** Instructions on how to clone, install dependencies, and run the application locally.

### c. Core Logic & Architecture (`main.py` and `helpers.py`)

The application was built with a clear separation of concerns between the UI (`main.py`) and the backend logic (`helpers.py`).

**Phase 1: RAG Core Logic (`helpers.py`)**

1.  **Document Processing:**
    - Uses `PyPDF` to load and extract text from PDF documents.
    - Uses `RecursiveCharacterTextSplitter` to break the text into manageable chunks.

2.  **Vector Store Creation:**
    - **Key Decision**: Due to Google API key permission issues with the embedding service, the project switched from `GoogleGenerativeAIEmbeddings` to `HuggingFaceEmbeddings` (using the `all-MiniLM-L6-v2` model via the `sentence-transformers` library). This allows for robust, local embedding generation on the server.
    - Uses `FAISS` to create an in-memory vector store from the embeddings.

3.  **Conversational Answer Generation:**
    - **Key Decision**: To enable conversational memory, the stateless `load_qa_chain` was replaced with `ConversationalRetrievalChain`.
    - This chain takes the user's question and the previous chat history to first generate a standalone question, then retrieves relevant documents, and finally generates a context-aware answer.
    - The function was made **synchronous** to ensure stability within the Streamlit environment, avoiding issues with nested asyncio event loops.

**Phase 2: Streamlit UI & Orchestration (`main.py`)**

1.  **UI Layout:**
    - The main area is dedicated to the chat interface.
    - A sidebar (`st.sidebar`) contains all user controls.

2.  **Sidebar Controls:**
    - **API Key:** A `st.text_input` (password type) for the Gemini API Key, placed at the top for easy access.
    - **File Uploader:** `st.file_uploader` for uploading new PDF documents.
    - **Default RAG Loading:** On startup, the app automatically scans the `./RAG_file` directory and loads any existing FAISS indexes.
    - **RAG Source Management:**
        - All available knowledge sources (uploaded and default) are listed with a `st.checkbox` each.
        - Users can select which sources to use for the RAG query.
        - A two-step "Prepare Download" -> "Download" button pair is provided for each source, allowing users to save the processed vector store.

3.  **Dual-Mode Chat Logic:**
    - The application checks if any RAG sources are selected.
    - **If NO sources are selected (Non-RAG Mode):**
        - It engages in a direct, conversational chat with the Gemini model.
        - The full chat history (as a list of `HumanMessage` and `AIMessage` objects) is passed to the `llm.invoke` method on each turn to provide memory.
    - **If sources ARE selected (RAG Mode):**
        - It calls the `helpers.generate_answer` function.
        - It passes the current question and the chat history (excluding the latest question) to the `ConversationalRetrievalChain`.

4.  **Stability:**
    - **`nest_asyncio.apply()`** is called at the very top of the script to patch the asyncio event loop, preventing potential conflicts.
    - All core LLM and chain calls were ultimately made synchronous (`.invoke` instead of `.ainvoke`) to prevent the application from hanging, which was a recurring issue during development.

## 4. Final Outcome

The project successfully implements a stable, feature-rich, and conversational RAG application. It effectively demonstrates the difference between a generic LLM response and a context-aware RAG response. The final architecture is robust, handling dependencies, API limitations, and Streamlit's execution model correctly.
