# 🧠 RAG Chat System (Nepali Constitution QA)

A **Retrieval-Augmented Generation (RAG)** system built with **Google Gemini**, **FastAPI**, **Streamlit**, and **Qdrant**.
This project enables users to ask questions related to the **Nepali Constitution**, retrieve relevant context from stored documents, and get accurate AI-generated answers.

---

## 📖 Overview

This RAG system focuses on question–answering over the **Nepali Constitution**.
Documents are preprocessed, chunked, and stored with metadata in a **Qdrant vector database**.
When a user asks a question, the system retrieves the most relevant chunks and uses **Google Gemini** to generate a contextual answer.

---

## ✨ Features

* 🔍 **Retrieval-Augmented Generation (RAG)** pipeline using Qdrant and Gemini.
* 🧩 **Chunk-based document storage** with metadata for efficient retrieval.
* 🤖 **Gemini Function Calling** — the LLM automatically triggers the retriever tool when needed.
* 💾 **Chat history storage** in MongoDB.
* 📂 **Document upload** and embedding generation using `models/embedding-001`.
* ⚡ **FastAPI backend** serving the RAG API.
* 🖥️ **Streamlit frontend** for an interactive chat interface.

---

## 🏗️ Architecture

```
 ┌──────────────────────────────────────────────────────────┐
 │                       Streamlit UI                       │
 │  - User chat interface                                   │
 │  - Sends questions to backend                            │
 └──────────────────────────────────────────────────────────┘
                 │
                 ▼
 ┌──────────────────────────────────────────────────────────┐
 │                        FastAPI Backend                   │
 │  - Handles chat requests                                 │
 │  - Calls Gemini for reasoning + function calling          │
 │  - Retrieves relevant chunks via retriever function       │
 │  - Stores chat history in MongoDB                         │
 └──────────────────────────────────────────────────────────┘
                 │
                 ▼
 ┌──────────────────────────────────────────────────────────┐
 │                   Qdrant Vector Database                 │
 │  - Stores document embeddings and metadata               │
 │  - Provides top-k retrieval for queries                  │
 └──────────────────────────────────────────────────────────┘
                 │
                 ▼
 ┌──────────────────────────────────────────────────────────┐
 │                       MongoDB                            │
 │  - Stores chat history and user context                  │
 └──────────────────────────────────────────────────────────┘
```

---

## ⚙️ Setup Guide (Local)

### 1️⃣ Clone the repository

```bash
git clone https://github.com/shisir1729/RAG_chat_system.git
cd RAG_chat_system
```

### 2️⃣ Install dependencies

```bash
uv add <packages>
```

### 3️⃣ Configure environment

Edit the connection details in `configuration.py`:

```python
QDRANT_URL = "your_qdrant_url"
MONGO_URI = "your_mongodb_connection_string"
```

### 4️⃣ Start the backend

```bash
 uv run uvicorn main:app --reload
```

### 5️⃣ Run the frontend

```bash
 uvx streamlit run streamlit_learning.py
```

Now open the Streamlit app (default: `http://localhost:8501`) and start chatting!

---

## 🗂️ Folder Structure

```
RAG_chat_system/
├── main.py                 # Core FastAPI backend
├── configuration.py        # Qdrant and MongoDB configurations
├── streamlit_learning.py   # Streamlit frontend
├── pyproject.toml          # Python dependencies
└── README.md               # Project documentation
```

---

## 📚 How It Works

1. Documents are chunked and stored with embeddings in Qdrant.
2. When a user sends a query, Gemini uses **function calling** to invoke the `retriever_text()` function.
3. The retriever searches Qdrant for relevant chunks.
4. Gemini integrates the retrieved context to generate a precise answer.
5. Chat history is saved to MongoDB for future context.

---

## 🧩 Tech Stack

| Component       | Technology             |
| --------------- | ---------------------- |
| LLM             | Google Gemini          |
| Embeddings      | `models/embedding-001` |
| Backend         | FastAPI                |
| Frontend        | Streamlit              |
| Vector Database | Qdrant                 |
| Database        | MongoDB                |




---

## 👨‍💻 Author

**Shisir Adhikari**

> RAG Chat System for Nepali Constitution Q&A
> [GitHub: shisir1729](https://github.com/shisir1729)

---
