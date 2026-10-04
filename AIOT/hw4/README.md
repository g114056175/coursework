# AIOT HW4 - RAG Q&A System

## Project Summary & Process
本次作業是基於蔡炎龍教授的「檢索增強生成(RAG)的原理及實作」影片課程與Colab實作範例完成。我們使用Gemini API作為大型語言模型(LLM)，並透過以下步驟將PDF資料處理為RAG檢索向量檔案：首先，使用`pypdf`工具提取PDF文本內容；接著，利用`RecursiveCharacterTextSplitter`將文本分割成適當的文本塊；最後，運用`HuggingFaceEmbeddings`模型（`all-MiniLM-L6-v2`）生成文本嵌入向量，並建立`FAISS`向量資料庫。本專案旨在Streamlit平台上展示RAG技術的實際應用效果，同時深入探討其優勢、劣勢與在當前LLM發展趨勢下的必要性。

---

## Project Description
This is a Retrieval-Augmented Generation (RAG) question-answering system built with Streamlit, LangChain, and the Google Gemini API. It allows users to ask questions about specific document content through an interactive chat interface.

This project not only supports real-time PDF document uploads as a knowledge base but also automatically loads pre-processed local knowledge bases stored in the `RAG_file` directory. This gives the system the dual capabilities of dynamic knowledge expansion and having a foundational knowledge base.

To demonstrate the value of RAG technology, the system will chat directly with the Gemini model when no RAG document source is selected. In this mode, the model may "hallucinate" due to a lack of specific domain knowledge. When a document source is selected, the model will provide precise answers based on the document's content.

Furthermore, the system features conversational memory, enabling it to understand context and engage in coherent, multi-turn dialogues in both RAG and non-RAG modes.

## Features

-   **Interactive Chat Interface**: Provides an intuitive UI for asking questions and receiving answers.
-   **PDF Document Upload**: Users can upload their own PDF files, which the system automatically processes into a searchable vector database.
-   **Automatic Loading of Local Knowledge Base**: On startup, the application automatically scans and loads all pre-processed FAISS indexes from the `RAG_file` directory to serve as a default knowledge base.
-   **Multiple Knowledge Source Selection**: Users can freely select which documents (both uploaded and default) to use as context for the current response via checkboxes in the sidebar.
-   **Conversational Memory**: In both pure chat and RAG modes, the model remembers previous conversations, allowing for context-aware follow-up questions.
-   **Vector Database Download**: Users can package and download the processed vector database (FAISS index) as a `.zip` file for future direct use.
-   **Model and API Key Configuration**: The Google API Key can be entered directly in the UI, and the system is configured to use the `gemini-2.0-flash-lite` model.

## Live Demo

You can interact with the application deployed on Streamlit Cloud via the following link:

[https://aiothw4-884u3yufyrjytbb2fya242.streamlit.app/](https://aiothw4-884u3yufyrjytbb2fya242.streamlit.app/)

### DEMO1: `"說明根據 國立中興大學學生獎懲辦法 第三條 學生有下列各條情形之一者，予以記嘉獎 的行為有哪些?"`
![DEMO1 Screenshot](DEMO1.png)
![DEMO1 Screenshot](DEMO1_1.png)

### DEMO2: `"根據RAG資料 簡單說明What are the symptoms of Mitral Valve Prolapse ?"`
![DEMO2 Screenshot](DEMO2.png)
![DEMO2 Screenshot](DEMO2_1.png)

## References

-   **Instructional Video**: [檢索增強生成(RAG)的原理及實作](https://www.youtube.com/watch?v=jF80Y8_BvEA&list=PL-eaXJVCzwbsXqWvQncPuuCg3wASAWWfO&index=7)
-   **RAG Implementation Reference**: [【Demo06a】RAG01_打造向量資料庫.ipynb](https://github.com/yenlung/AI-Demo/blob/master/%E3%80%90Demo06a%E3%80%91RAG01_%E6%89%93%E9%80%A0%E5%90%91%E9%87%8F%E8%B3%87%E6%96%99%E5%BA%AB.ipynb)

## Local Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/g114056175/AIOT_hw4.git
    cd AIOT_hw4
    ```

2.  **Install required packages**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Streamlit application**:
    ```bash
    streamlit run main.py
    ```
    The application will open in your browser. You can paste your Google API Key into the input box in the sidebar to get started.

---

## Discussion: The Relevance of RAG in the Era of Powerful LLMs

As Large Language Models (LLMs) become increasingly powerful, with capabilities like native web search and massive context windows (e.g., a hypothetical `gemini-3-pro-preview`), a valid question arises: is Retrieval-Augmented Generation (RAG) still necessary?

For this project, a smaller, older model (`gemini-2.0-flash-lite`) was intentionally used to clearly demonstrate the classic benefits of RAG. As observed during personal testing, when a top-tier model is used to query public information (like the regulations of a public university), the difference in performance with and without RAG can seem minimal. This is because the frontier model's vast training data often already includes the information, or it can find it through its own internal knowledge mechanisms.

However, this observation does not diminish the value of RAG. Instead, it highlights where RAG provides its most critical advantages:

1.  **Handling Private & Proprietary Data**: The most significant advantage of RAG is its ability to work with data that is not on the public internet. For any business or individual, the ability to query internal documents, confidential research, personal notes, or customer data without exposing that data to a third-party model vendor for training is paramount. RAG allows the model to use this data for inference on-the-fly without absorbing it.

2.  **Ensuring Data Freshness**: An LLM's knowledge is static and ends at its last training date. RAG provides a live, real-time channel to the most current information. For applications in fields like news, finance, or scientific research, this is non-negotiable.

3.  **Source Verification & Trust**: When a powerful LLM provides an answer, it often acts as a "black box," making it difficult to verify the source of its information. RAG, by its nature, first retrieves specific chunks of text. This allows the system to cite its sources, giving users the ability to fact-check the response and building trust in the application.

4.  **Cost-Effectiveness and Scalability**: Continuously fine-tuning an LLM on new or changing data is computationally expensive and time-consuming. RAG offers a much cheaper and faster alternative. Updating a vector database is a trivial operation compared to retraining a multi-billion parameter model.

5.  **Reducing Hallucinations**: By grounding the LLM's response in a specific, provided context, RAG drastically reduces the model's tendency to "hallucinate" or invent facts. It constrains the model to the retrieved information, leading to more factual and reliable outputs.

In conclusion, while the raw power of modern LLMs is impressive, RAG is not becoming obsolete. Instead, its role is shifting from a general-purpose enhancement to an essential tool for enterprise-grade, data-sensitive, and high-reliability applications. The vectorization and retrieval process remains a core pillar for building truly intelligent and trustworthy AI systems.
