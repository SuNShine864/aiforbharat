import os
import uuid
import json
import requests
import re
import json


def extract_json(text):

    match = re.search(r'\{.*\}', text, re.DOTALL)

    if not match:
        return None

    json_text = match.group(0)

    try:
        return json.loads(json_text)

    except Exception as e:

        print("JSON extraction failed:", e)

        return None
from dotenv import load_dotenv

from pinecone import Pinecone

from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings
)

load_dotenv()

# =========================
# CONFIG
# =========================

PINECONE_API_KEY = os.getenv(
    "PINECONE_API_KEY"
)

PINECONE_INDEX_NAME = os.getenv(
    "PINECONE_INDEX_NAME"
)

NVIDIA_API_KEY = os.getenv(
    "NVIDIA_API_KEY"
)

MODEL_NAME = os.getenv(
    "MODEL_NAME"
)

NVIDIA_URL = (
    "https://integrate.api.nvidia.com/v1/chat/completions"
)

# =========================
# GOOGLE EMBEDDINGS
# =========================

embeddings = GoogleGenerativeAIEmbeddings(

    model="gemini-embedding-001",

    google_api_key=os.getenv(
        "GEMINI_API_KEY"
    )
)

# =========================
# PINECONE
# =========================

pc = Pinecone(
    api_key=PINECONE_API_KEY
)

index = pc.Index(
    PINECONE_INDEX_NAME
)

# =========================
# EMBEDDING FUNCTION
# =========================

def get_embedding(text: str):

    return embeddings.embed_query(text)

# =========================
# INDEX BIDDER CHUNKS
# =========================

def index_bidder_chunks(
    bidder_id,
    blocks
):

    vectors = []

    for block in blocks:

        text = block.get(
            "text",
            ""
        ).strip()

        if not text:
            continue

        embedding = get_embedding(text)

        vectors.append({

            "id": str(uuid.uuid4()),

            "values": embedding,

            "metadata": {

                "bidder_id": bidder_id,

                "text": text,

                "page": block.get("page"),

                "filename": block.get(
                    "filename"
                ),

                "source_type": block.get(
                    "source_type"
                )
            }
        })

    if vectors:

        index.upsert(vectors=vectors)

    print(
        f"Indexed {len(vectors)} chunks"
    )

# =========================
# RETRIEVE CHUNKS
# =========================

def retrieve_relevant_chunks(

    bidder_id,

    criterion_text,

    top_k=5
):

    query_embedding = get_embedding(
        criterion_text
    )

    results = index.query(

        vector=query_embedding,

        top_k=top_k,

        include_metadata=True,

        filter={
            "bidder_id": {
                "$eq": bidder_id
            }
        }
    )

    return [

        match["metadata"]

        for match in results["matches"]
    ]

# =========================
# NVIDIA EVALUATION
# =========================

def evaluate_criterion(

    criterion,

    retrieved_chunks
):

    context = "\n\n".join([

        f"""
FILE: {c['filename']}
PAGE: {c['page']}

{c['text']}
"""

        for c in retrieved_chunks
    ])

    prompt = f"""
You are an expert procurement evaluator.

Criterion:
{criterion['description']}

Category:
{criterion.get('category', 'general')}

Relevant Evidence:
{context}

Return ONLY valid JSON:

{{
  "criterion_id": "{criterion['id']}",
  "category": "{criterion.get('category', 'general')}",
  "verdict": "ELIGIBLE | NOT_ELIGIBLE | MANUAL_REVIEW",
  "value": "...",
  "reason": "...",
  "documentRef": "...",
  "page": ...
}}
Do not give any extra information or any extra line, give only and only json response, do not write anything else, 
strictly json response 
Return ONLY valid JSON.
Do not include explanations.
Do not include markdown.
Do not include extra text.
"""

    response = requests.post(

        NVIDIA_URL,

        headers={

            "Authorization": f"Bearer {NVIDIA_API_KEY}",

            "Content-Type": "application/json"
        },

        json={

            "model": MODEL_NAME,

            "messages": [

                {
                    "role": "system",

                    "content": (
                        "Return only valid JSON."
                    )
                },

                {
                    "role": "user",

                    "content": prompt
                }
            ],

            "temperature": 0,

            "max_tokens": 1024
        }
    )

    data = response.json()

    raw = data["choices"][0]["message"]["content"]

    raw = raw.replace("```json", "")
    raw = raw.replace("```", "")
    raw = raw.strip()

    print("\nRAW LLM RESPONSE:\n")
    print(raw)

    try:
        parsed = extract_json(raw)

        if parsed:
            return parsed

        return {
        "criterion_id": criterion.get("criterion_id"),
        "verdict": "MANUAL_REVIEW",
        "reason": "Could not parse AI response",
        "raw_output": raw
        }

    except Exception as e:

        print("\nJSON PARSE ERROR:\n", e)

    return {
        "status": "Manual Review",
        "reason": "Invalid AI response",
        "raw_output": raw
    }

# =========================
# FULL RAG PIPELINE
# =========================

def run_rag_evaluation(

    bidder_id,

    criteria
):

    results = []

    for criterion in criteria:

        print(
            f"Evaluating {criterion['id']}"
        )

        chunks = retrieve_relevant_chunks(

            bidder_id,

            criterion["description"],

            top_k=5
        )

        result = evaluate_criterion(

            criterion,

            chunks
        )

        results.append(result)

    return results