# 📘 Product Requirements Document (PRD)

## 📌 Project Name
HR Onboarding Knowledge Assistant

## 🧩 Overview
The HR Onboarding Knowledge Assistant is an AI-powered chat tool designed to help new employees quickly find answers to HR-related questions. It replaces time-consuming HR onboarding sessions with an intelligent assistant that can reference internal policy documents and provide instant, accurate, and contextual responses.

---

## 🎯 Goals & Objectives

- Reduce repetitive HR inquiries during onboarding
- Improve employee experience with instant, self-serve answers
- Ensure HR responses are consistent, accurate, and up-to-date
- Free up HR teams from basic policy explanations

---

## 🧑‍💼 Target Users

- **New Hires** – employees during their onboarding phase
- **HR Teams** – as admin users for document upload and system monitoring
- **People Managers** – for answering employee-related policy questions

---

## 💡 Key Features

### ✅ Core Functionality

- **Document Upload**  
  Upload multi-format documents: PDF, DOCX, TXT

- **Text Extraction & Chunking**  
  Extract HR content using intelligent chunking (headings, sections)

- **Vector Embeddings with Metadata**  
  Store content in a vector database with filters like category, source, and page

- **Chat Interface**  
  Natural language queries with response generation

- **Policy Citations**  
  Responses include links or references to the original document chunks

- **Query Categorization**  
  Automatically categorize questions (e.g., Leave, Benefits, Conduct)

### 🛠 Admin Tools

- Upload, remove, and manage HR documents
- Monitor query logs and categories
- Force refresh vector index after upload

---

## 📚 Example Queries

- “How many vacation days do I get as a new employee?”
- “What's the process for requesting parental leave?”
- “Can I work remotely and what are the guidelines?”
- “How do I enroll in health insurance?”
- “What are the rules around workplace conduct?”

---

## ⚙️ Technical Requirements

### 🚀 Backend

- **Document Ingestion**
  - PDF: `PyMuPDF`
  - DOCX: `python-docx`
  - TXT: native string parsing

- **Text Chunking Strategy**
  - Chunk by headings, section titles
  - Overlapping windows for context

- **Vector Embedding & Storage**
  - Embedding: OpenAI
  - Vector DB: Pinecone

- **Retrieval Pipeline**
  - RAG (Retrieval-Augmented Generation)
  - Filterable by category, document type

- **Response Generation**
  - LLM-generated with reference annotations
  - Uses retrieved chunks as strict context

### 🖥️ Frontend

- **Chat UI**
  - Next.js
  - Query input and threaded answers with citations

- **Admin Dashboard**
  - Upload/manage documents
  - View and categorize queries
  - Rebuild index

---

## 🧪 Success Metrics

- 📉 Reduction in HR tickets related to onboarding
- ⏱️ Average response time per query
- 📈 Employee satisfaction score (post-onboarding)
- 🔍 Accuracy of responses (human-reviewed audit)
- 🧠 % of questions answered without fallback to HR team