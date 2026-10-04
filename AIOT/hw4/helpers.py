import os
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain # Reverted import
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate # Reverted import
import io # Added import for io

def process_text_from_pdfs(pdf_docs):
    """
    Extracts and concatenates text from a list of uploaded PDF files.
    Args:
        pdf_docs (list): A list of uploaded file objects from Streamlit.
    Returns:
        str: A single string containing all the extracted text.
    """
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(io.BytesIO(pdf.read())) # Modified line
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

def get_text_chunks(text):
    """
    Splits a long text into smaller, manageable chunks.
    Args:
        text (str): The input text.
    Returns:
        list: A list of text chunks.
    """
    if not text or not isinstance(text, str): # Add check for empty or non-string input
        print("Warning: Input text for get_text_chunks is empty or not a string. Returning empty list.")
        return []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(text)
    return chunks

def get_hf_embeddings():
    """Initializes and returns the HuggingFace embedding model."""
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def create_vector_store(text_chunks):
    """
    Creates and returns a FAISS vector store from text chunks using a HuggingFace model.
    Args:
        text_chunks (list): A list of text chunks.
    Returns:
        FAISS: A FAISS vector store object, or None if input is empty.
    """
    if not text_chunks:
        print("Warning: Text chunks are empty. Cannot create vector store.")
        return None
    embeddings = get_hf_embeddings()
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    return vector_store

def generate_answer(user_question, vector_stores, api_key): # Removed chat_history
    """
    Generates an answer based on the user's question and selected vector stores.
    This is a synchronous function.
    Args:
        user_question (str): The user's question.
        vector_stores (dict): A dictionary of available vector stores.
        api_key (str): The Google Gemini API key.
    Returns:
        str: The generated answer.
    """
    if not vector_stores:
        return "Please upload and select at least one document to ask questions."

    # Initialize the model
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        temperature=0.3,
        google_api_key=api_key,
        convert_system_message_to_human=True,
        request_timeout=60
    )

    # --- Retrieve relevant documents from all selected vector stores ---
    all_docs = []
    for store in vector_stores.values():
        all_docs.extend(store.similarity_search(user_question)) # Use user_question directly

    if not all_docs:
        return "No relevant information found in the selected documents for your question."

    # A more basic and versatile prompt template, asking for Traditional Chinese
    prompt_template = """
    Answer the user's question based ONLY on the following context. If the answer is not found in the context, state that you cannot find the answer in the provided documents.
    Please respond in Traditional Chinese.

    Context:
    {context}

    Question:
    {question}

    Answer:
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt) # Reverted to stuff chain

    response = chain.run(input_documents=all_docs, question=user_question) # Use chain.run
    return response