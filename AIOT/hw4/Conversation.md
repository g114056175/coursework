# Conversation Log

This document logs the key interactions and decisions made during the project setup.

## Initial Setup

- User confirmed the working directory and initial file structure.
- User asked about Gemini CLI's support for "openspec". I confirmed that it does, in several ways (integration, generation, documentation).
- User pointed out that I missed two directories (`.gemini` and `openspec`) in the initial directory listing. I acknowledged the mistake and confirmed I could see them.

## OpenSpec Workflow

- User was presented with the "Next steps" from the OpenSpec tool.
- User chose to first have the existing `.ipynb` files explained rather than starting the OpenSpec workflow.
- I provided a detailed summary of the three notebooks:
    - `【Demo06】用_RAG_打造心靈處方籤機器人.ipynb`: A complete, end-to-end RAG chatbot demo using OpenAI.
    - `【Demo06a】RAG01_打造向量資料庫.ipynb`: A script focused on creating a vector database from custom documents using HuggingFace embeddings.
    - `【Demo06b】RAG02_打造_RAG_系統.ipynb`: A script focused on building the application layer, loading a pre-built vector DB, and creating a Gradio chat interface using Groq for the LLM.

## Project Scoping & Git Integration

- User asked for a good dataset recommendation for a class project demo. I suggested using a board game rulebook like "Codenames" and outlined the steps.
- User requested to connect the project to their GitHub repository: `https://github.com/g114056175/AIOT_hw4.git`.
- I performed the following git operations:
    - `git init`
    - `git remote add origin ...`
    - Configured git user name and email based on user's input.
    - `git add .`
    - `git commit -m "Initial commit"`
    - `git push -u origin master`
- The project is now successfully linked to the user's GitHub.

## New Task: RAG System with Streamlit

User has requested to start the OpenSpec planning for a new feature:

- **Goal:** Build a RAG-based Q&A system deployed on Streamlit.
- **Files to create:** `main.py`, `README.md`, `requirements.txt`, `Conversation.md`.
- **Core Logic:**
    - Use `"國立中興大學學生獎懲辦法.pdf"` as the initial knowledge base.
    - Use the Gemini API for the LLM.
    - Forbid web search.
- **Streamlit UI Features:**
    - A chat interface (question/answer).
    - A file uploader to allow users to provide their own documents for the RAG system.

---

## Development and Debugging Journey

This section summarizes the iterative process of building and refining the Streamlit application.

### 1. Initial Implementation & Core Logic
- Created the initial file structure: `main.py` for the Streamlit UI, `helpers.py` for backend logic (PDF processing, vector store creation), and `requirements.txt` for dependencies.
- Implemented the basic RAG pipeline using LangChain and the Gemini API.

### 2. Embedding Model & API Key Issues
- **Problem**: The Google-provided embedding model failed due to API key permission issues. The user's key was valid for the Gemini chat model but not for the embedding service.
- **Solution**: Switched the embedding model to a Hugging Face `sentence-transformers` model (`all-MiniLM-L6-v2`). This model runs locally on the Streamlit server instance, successfully bypassing the API key issue.

### 3. Dependency and Environment Stabilization
- **Problem**: The application failed to deploy on Streamlit Cloud due to version conflicts, primarily between `pydantic`, `langchain`, and `streamlit`.
- **Solution**: After several attempts, specific working versions of `langchain`, `langchain-core`, `langchain-community`, and `langchain-google-genai` were pinned in `requirements.txt` to create a stable environment.

### 4. Asynchronous Code & Performance Debugging
- **Problem**: The application frequently got stuck on the "Thinking..." screen, indicating that the LLM call was not returning. This was the most persistent issue throughout the development process.
- **Initial Attempts**: The first hypothesis was that Streamlit's event loop was conflicting with Python's `asyncio`. `nest_asyncio` was installed and applied at the top of `main.py` to patch this.
- **Root Cause Discovery**: The user clarified that the hanging occurred even when no RAG documents were selected, pointing to a fundamental problem in the direct LLM call, not the RAG chain.
- **Solution**: The unstable `asyncio.run(llm.ainvoke(...))` pattern was replaced with a direct, synchronous call (`llm.invoke(...)`). This proved to be much more stable within the Streamlit execution model and resolved the hanging issue.

### 5. UI/UX Iteration based on User Feedback
- **Feature - Default Knowledge Base**: Implemented logic to automatically find and load pre-existing FAISS vector stores from the `./RAG_file` directory on startup.
- **Feature - Download**: Added a feature to download processed vector stores as `.zip` files. This was refined from an unstable on-the-fly zipping method to a more robust two-step "Prepare" -> "Download" process.
- **UI Refactoring & Reversion**:
    1. A complex UI was briefly implemented where clicking a file would switch the main panel to a "details view".
    2. Based on user feedback ("回滾到原本的方法"), this complex UI was completely removed.
    3. The final UI was reverted to a simpler, more intuitive sidebar layout containing both the checkboxes for RAG source selection and the download buttons.
- **API Key Input**: Changed from using Streamlit Secrets to a visible `st.text_input` in the sidebar with a default key, as per the user's specific request for this temporary project.

### 6. Implementing Conversational Memory
- **Requirement**: The user requested that the chatbot should remember the context of the current conversation for follow-up questions.
- **Solution**:
    - **Non-RAG Mode**: The logic was updated to pass the entire list of `HumanMessage` and `AIMessage` objects from the session state to the LLM on each turn.
    - **RAG Mode**: The `helpers.py` function was significantly refactored from the stateless `load_qa_chain` to use the `ConversationalRetrievalChain`, which is specifically designed to manage chat history when performing retrieval.

### 7. Final Bug Fixes
- **`SyntaxError`**: Corrected a critical syntax error in `main.py` that was caused by a previous faulty `replace` operation which had duplicated a large block of code at the end of the file.
- **`NameError`**: After a refactoring, a `NameError` on `nest_asyncio` appeared. This was fixed by ensuring `import nest_asyncio` and `nest_asyncio.apply()` were correctly placed at the very top of `main.py`.

### 8. Prompt & Model Tuning
- Throughout the process, the Gemini model was changed several times (`gemini-2.5-flash-image`, `gemini-2.5-flash`, `gemini-2.0-flash-lite`) based on user requests.
- The prompt was updated to explicitly request that all responses be in **Traditional Chinese**.
