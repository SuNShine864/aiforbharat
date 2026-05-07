# AI-Powered Tender Evaluation System

## Overview

An AI-powered tender evaluation platform that automates bidder document analysis, eligibility verification, and criteria-based evaluation using Retrieval-Augmented Generation (RAG), vector search, and Large Language Models.

The system allows users to:

* Upload tender documents and bidder submissions
* Extract eligibility criteria automatically
* Parse PDF and scanned documents
* Store embeddings in Pinecone
* Evaluate bidders against tender requirements
* Generate eligibility decisions
* Support manual review workflows

# Project Architecture


Frontend (html,css,js)
        ↓
Backend API (Python)
        ↓
AI Service (FastAPI + RAG Pipeline)
        ↓
Pinecone Vector Database
        ↓
NVIDIA LLM APIs / Gemini APIs

---

# Tech Stack

## Frontend

Current Version:

* HTML
* CSS
* JavaScript
* Modular JS architecture
* Fetch

Planned Upgrade:

* React.js
* Vite
* Tailwind CSS

## Backend

* FastAPI
* Python
* MongoDB
* Pydantic Schemas
* Modular Service Architecture
* File Upload Handling

## AI Service

* FastAPI
* Python
* LangChain
* Pinecone
* NVIDIA APIs
* Gemini API
* OCR + PDF Extraction


# Features

## Tender Processing

* Upload tender documents
* Extract evaluation criteria automatically
* Store criteria in structured JSON format

## Bidder Evaluation

* Upload bidder PDFs/documents
* Extract and chunk text
* Generate embeddings
* Store vectors in Pinecone
* Retrieve relevant chunks using RAG
* Evaluate each criterion using LLMs

## Evaluation Status

* Eligible
* Not Eligible
* Manual Review

## AI Capabilities

* Semantic document search
* Criteria extraction
* Eligibility reasoning
* Natural language evaluation summaries

# Folder Structure

project-root/
│
├── frontend/
│   ├── js/
│   │   ├── api.js
│   │   ├── audit.js
│   │   ├── bidder.js
│   │   ├── evaluation.js
│   │   ├── tender.js
│   │   └── ui.js
│   ├── index.html
│   ├── script.js
│   ├── style.css
│   └── README.md
│
├── backend/
│   ├── database/
│   │   └── mongo.py
│   ├── models/
│   │   ├── bidder.py
│   │   ├── result.py
│   │   └── tender.py
│   ├── routes/
│   │   ├── bidder.py
│   │   └── tender.py
│   ├── schemas/
│   │   ├── bidder_schema.py
│   │   ├── result_schema.py
│   │   └── tender_schema.py
│   ├── services/
│   │   ├── bidder_service.py
│   │   └── tender_service.py
│   ├── uploads/
│   │   ├── bidders/
│   │   └── tenders/
│   ├── utils/
│   │   └── file_handler.py
│   ├── main.py
│   └── requirements.txt
│
├── ai_service/
│   ├── evaluators/
│   │   └── verdict_engine.py
│   ├── extractors/
│   │   ├── criteria_extractor.py
│   │   └── document_extractor.py
│   ├── data/
│   └── requirements.txt
│   |__ rag_pipeline.py
└── README.md

# Environment Variables

Create a `.env` file in the required services.

## AI Service `.env`

NVIDIA_API_KEY=your_nvidia_api_key
MODEL_NAME=your_model_name
GEMINI_API_KEY=your_gemini_api_key
MONGO_URI=your_mongodb_uri

NVIDIA_EMBEDDING_KEY=your_embedding_key
NVIDIA_EMBEDDING_MODEL=your_embedding_model

PINECONE_INDEX_NAME=your_pinecone_index
PINECONE_API_KEY=your_pinecone_api_key

# Installation

## 1. Clone Repository

git clone <your-github-repo-url>
cd <project-folder>

# Frontend Setup

Since the current frontend is built using HTML, CSS, and JavaScript:

You can directly run it using:

* VS Code Live Server Extension
  OR
* Any static web server

Frontend typically runs on:

http://127.0.0.1:5500

Future frontend migration planned:

* React.js
* Vite
* Tailwind CSS

# Backend Setup

cd backend
pip install -r requirements.txt
uvicorn main:app --reload

Backend runs on:

http://localhost:8000

# AI Service Setup

The AI service handles:

- Criteria extraction
- Document parsing
- Embedding generation
- RAG pipeline
- Eligibility evaluation
- Verdict generation

## Create Virtual Environment


cd ai_service
python -m venv venv


### Activate Environment

#### Windows

venv\Scripts\activate


#### Linux/Mac

source venv/bin/activate

## Install Dependencies

pip install -r requirements.txt

## Run AI Service

uvicorn main:app --reload

AI service typically runs on:

http://localhost:8001


# API Workflow

## Tender Upload

1. Upload tender document
2. Extract criteria using LLM
3. Save structured criteria JSON

## Bid Evaluation

1. Upload bidder documents
2. Extract document text
3. Generate embeddings
4. Store vectors in Pinecone
5. Retrieve relevant chunks
6. Evaluate criteria
7. Return eligibility status


# Future Improvements

- Multi-user authentication
- Role-based access control
- Dashboard analytics
- Real-time evaluation progress
- Fine-tuned legal models
- Support for DOCX and Excel files


# Screenshots

Add screenshots here:

- Tender Upload Page
  <img width="1919" height="909" alt="image" src="https://github.com/user-attachments/assets/8cc375ac-6c19-4829-bd7e-385e28c57d23" />
- Bidder Portal
  <img width="1919" height="914" alt="image" src="https://github.com/user-attachments/assets/ce4e7a88-0538-48e8-a2e3-c08267092c82" />
- Bidder Submission
  <img width="1919" height="919" alt="image" src="https://github.com/user-attachments/assets/894e7fbc-0183-41f6-8d90-821b29d86fbc" />
- Bid Evaluation Page
  <img width="1917" height="895" alt="image" src="https://github.com/user-attachments/assets/73b8b0c0-08b6-4567-9d36-c3d5f6553200" />
- See Report of Each Bid
  <img width="1919" height="915" alt="image" src="https://github.com/user-attachments/assets/7ce837f0-2a5b-42b9-9e98-ba7665cb96cb" />

# Contributors

- Bhawya Wadhwa
- Suraj Raj
- Aniket Kumar Sharma

# License

This project is for educational and research purposes.

```
