import streamlit as st
import nest_asyncio
import os
from dotenv import load_dotenv

# Apply the patch for asyncio right at the start
nest_asyncio.apply()
# Load environment variables from .env file for local development
load_dotenv()


import helpers
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import asyncio
import shutil
from langchain.vectorstores import FAISS
import io
import zipfile

def get_zip_file_bytes(vector_store, filename):
    TEMP_DIR = "./temp_download"
    save_path = os.path.join(TEMP_DIR, filename.replace(" ", "_") + "_faiss_index")
    
    if os.path.exists(save_path):
        shutil.rmtree(save_path)
    
    vector_store.save_local(save_path)
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zip_file:
        for root, _, files in os.walk(save_path):
            for file in files:
                zip_file.write(os.path.join(root, file), 
                               os.path.relpath(os.path.join(root, file), save_path))
    
    shutil.rmtree(TEMP_DIR) # Clean up after zipping
    return zip_buffer.getvalue()

st.set_page_config(page_title="RAG Q&A with Gemini", layout="wide")
st.title("📄 RAG-based Q&A with Gemini")

# --- Session State Initialization ---
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "vector_stores" not in st.session_state:
    st.session_state.vector_stores = {}
if "selected_sources_dict" not in st.session_state:
    st.session_state.selected_sources_dict = {}

# --- Load Default RAG Indexes on Startup ---
DEFAULT_RAG_ROOT = "./RAG_file"
if "default_loaded" not in st.session_state:
    if os.path.exists(DEFAULT_RAG_ROOT) and os.path.isdir(DEFAULT_RAG_ROOT):
        try:
            with st.spinner("Loading default RAG sources..."):
                embeddings = helpers.get_hf_embeddings()
                for item in sorted(os.listdir(DEFAULT_RAG_ROOT), reverse=True):
                    item_path = os.path.join(DEFAULT_RAG_ROOT, item)
                    # Check if it's a directory and not already loaded
                    if os.path.isdir(item_path) and f"{item} (Default)" not in st.session_state.vector_stores:
                        default_vs = FAISS.load_local(item_path, embeddings, allow_dangerous_deserialization=True)
                        st.session_state.vector_stores[f"{item} (Default)"] = default_vs
            if st.session_state.vector_stores:
                st.toast("Default RAG sources loaded successfully!")
        except Exception as e:
            st.error(f"Failed to load default RAG sources: {e}")
    st.session_state.default_loaded = True

# --- Sidebar for Controls ---
with st.sidebar:
    st.header("API 金鑰設定")
    
    user_api_key = st.text_input(
        label="Google API 金鑰 (選填)",
        placeholder="貼上您的金鑰以覆蓋預設值",
        help="如果留空，將自動使用應用程式內建的預設金鑰。",
        type="password"
    )

    google_api_key = user_api_key or os.getenv("GOOGLE_API_KEY")
    default_key_found = os.getenv("GOOGLE_API_KEY") is not None

    # Display a single, consolidated status line
    if user_api_key:
        st.caption("🟢 您正在使用自己輸入的金鑰。")
    elif default_key_found:
        st.caption("🔵 已自動載入預設金鑰。")
    else:
        st.caption("🔴 未找到任何金鑰，請手動輸入。")
    
    st.markdown("---")
    
    st.header("RAG 文件管理")
    
    uploaded_files = st.file_uploader("上傳新的 PDF 文件", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        with st.spinner("Processing documents..."):
            for uploaded_file in uploaded_files:
                if uploaded_file.name not in st.session_state.vector_stores:
                    raw_text = helpers.process_text_from_pdfs([uploaded_file])
                    text_chunks = helpers.get_text_chunks(raw_text)
                    vector_store = helpers.create_vector_store(text_chunks)
                    if vector_store:
                        st.session_state.vector_stores[uploaded_file.name] = vector_store
                        st.success(f"Processed and indexed: {uploaded_file.name}")
                    else:
                        st.warning(f"Could not process text from: {uploaded_file.name}")

    st.subheader("Available RAG Sources")
    if not st.session_state.vector_stores:
        st.info("Upload a document or add a default RAG folder to begin.")
    else:
        # Use a dictionary to track checkbox states
        selected_sources_dict = {}
        for filename, vector_store in st.session_state.vector_stores.items():
            # Display checkbox and store its state
            is_selected = st.checkbox(filename, value=st.session_state.selected_sources_dict.get(filename, True), key=f"cb_{filename}")
            selected_sources_dict[filename] = is_selected
            
            # --- Single-Step Download Logic ---
            st.download_button(
                label="⬇️ Download",
                data=get_zip_file_bytes(vector_store, filename),
                file_name=f"{filename}_faiss_index.zip",
                mime="application/zip",
                key=f"dl_{filename}"
            )
            st.markdown("---") # Separator
        
        # Update the master dictionary of checkbox states
        st.session_state.selected_sources_dict = selected_sources_dict

# --- Main Chat Interface ---
for message in st.session_state.conversation:
    with st.chat_message(message["role"]):
        # Check for assistant messages with metadata to display the source
        if message["role"] == "assistant":
            if "is_error" in message:
                 st.error(message["content"])
            else:
                if message.get("rag_used") == False:
                    st.caption("Source: General Knowledge")
                elif message.get("rag_used") == True and "sources" in message:
                    # Format source names for readability
                    formatted_sources = [s.replace("_faiss_index (Default)", "").replace(".pdf", "") for s in message.get("sources", [])]
                    st.caption(f"Source(s): {', '.join(formatted_sources)}")
                st.markdown(message["content"])
        else: # User messages
             st.markdown(message["content"])


if user_question := st.chat_input("Ask a question..."):
    st.session_state.conversation.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    # CRITICAL: Check for API key availability *before* making any calls
    if not google_api_key:
        error_message = "API 金鑰未設定。請在左側側邊欄輸入您的 Google API 金鑰，或由應用程式管理員設定預設金鑰。"
        st.session_state.conversation.append({"role": "assistant", "content": error_message, "is_error": True})
        with st.chat_message("assistant"):
            st.error(error_message)
    else:
        # Determine which vector stores are selected for the query
        selected_stores_for_query = {
            name: store for name, store in st.session_state.vector_stores.items()
            if st.session_state.selected_sources_dict.get(name, True)
        }

        # --- Refactored Query Logic with st.status ---
        with st.chat_message("assistant"):
            rag_used = bool(selected_stores_for_query)
            status_message = "正在透過 RAG 思考..." if rag_used else "正在思考..."
            
            with st.status(status_message, expanded=False) as status:
                try:
                    if not rag_used:
                        # Fallback to direct LLM
                        st.info("未選取 RAG 文件，使用 LLM 內部知識回答。")
                        llm = ChatGoogleGenerativeAI(
                            model="gemini-2.0-flash-lite",
                            temperature=0.7,
                            google_api_key=google_api_key,
                            convert_system_message_to_human=True,
                            request_timeout=120
                        )
                        prompt_template = "Question: {question}\n\nAnswer in Traditional Chinese:"
                        prompt = PromptTemplate(template=prompt_template, input_variables=["question"])
                        llm_chain = LLMChain(prompt=prompt, llm=llm)
                        response = llm_chain.run(question=user_question)
                        source_names = []
                    else:
                        # Use RAG to generate an answer
                        response = helpers.generate_answer(
                            user_question,
                            selected_stores_for_query,
                            google_api_key
                        )
                        source_names = list(selected_stores_for_query.keys())

                    status.update(label="回答已產生！", state="complete", expanded=False)

                except Exception as e:
                    response = f"處理過程中發生錯誤： {type(e).__name__} - {e}"
                    st.error(response)
                    st.session_state.conversation.append({"role": "assistant", "content": response, "is_error": True})
                    status.update(label="處理失敗", state="error", expanded=True)
            
            # Display the final response and caption
            if "is_error" not in st.session_state.conversation[-1]:
                if not rag_used:
                    st.caption("資料來源: 通用知識")
                else:
                    formatted_sources = [s.replace("_faiss_index (Default)", "").replace(".pdf", "") for s in source_names]
                    st.caption(f"資料來源: {', '.join(formatted_sources)}")
                
                st.markdown(response)
                st.session_state.conversation.append({"role": "assistant", "content": response, "rag_used": rag_used, "sources": source_names})