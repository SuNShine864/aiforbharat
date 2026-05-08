import os
from pinecone import Pinecone
from openai import OpenAI
import json

client = OpenAI(
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1"
)
# =========================
# CONFIG
# =========================

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = "aiforbharatintegrated"

pc = Pinecone(api_key=PINECONE_API_KEY)

index = pc.Index(PINECONE_INDEX)


# =========================
# UPSERT TEXT DIRECTLY
# (Integrated Embeddings)
# =========================
def run_llm(criterion, context_blocks):

    context_text = "\n\n".join([
        f"{b['text']} (file: {b['filename']}, page: {b['page']})"
        for b in context_blocks
    ])

    prompt = f"""
You are a strict JSON generator.

Criterion:
{criterion['description']}

Context:
{context_text}

Return ONLY valid JSON:

{{
  "criterion_id": "{criterion['id']}",
  "description": "{criterion['description']}",
  "matched": true,
  "value_found": "...",
  "document_reference": "...",
  "page": ...,
  "confidence": "high"
}}
"""

    response = client.chat.completions.create(
        model=os.getenv("NVIDIA_API_MODEL"),
        messages=[
            {
                "role": "system",
                "content": "Return only valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content
def parse_bids(flat_blocks, criteria):

    print("FLATTENING BLOCKS")

    flattened_blocks = []

    for file_data in flat_blocks:

        filename = file_data.get("filename")

        chunk_list = file_data.get("text", [])

        for chunk in chunk_list:

            chunk["filename"] = filename

            flattened_blocks.append(chunk)

    print("INDEXING BLOCKS")

    index_blocks(flattened_blocks)

    print("PROCESSING CRITERIA")

    results = []

    for criterion in criteria:

        print(f"Processing {criterion['id']}")

        relevant_blocks = retrieve_relevant_blocks(
            criterion["description"]
        )

        llm_output = run_llm(
            criterion,
            relevant_blocks
        )

        try:
            parsed = json.loads(llm_output)

        except Exception as e:

            print("JSON PARSE ERROR:", e)

            parsed = {
                "criterion_id": criterion["id"],
                "matched": False,
                "confidence": "low"
            }

        results.append(parsed)

    return results
def index_blocks(blocks):

    records = []

    for i, block in enumerate(blocks):

        text = block.get("text", "").strip()

        if not text:
            continue

        records.append({
            "_id": f"chunk-{i}",
            "chunk_text": text,

            # metadata
            "filename": block.get("filename"),
            "page": block.get("page"),
            "source_type": block.get("source_type")
        })

    if records:
        index.upsert_records(
            namespace="bidder-documents",
            records=records
        )

    print(f"Indexed {len(records)} records")


# =========================
# RETRIEVE RELEVANT BLOCKS
# =========================

def retrieve_relevant_blocks(query, top_k=5):

    results = index.search(
        namespace="bidder-documents",

        query={
            "top_k": top_k,
            "inputs": {
                "text": query
            }
        },

        fields=[
            "chunk_text",
            "filename",
            "page",
            "source_type"
        ]
    )

    matches = []

    for match in results["result"]["hits"]:

        matches.append({
            "text": match["fields"].get("chunk_text"),
            "filename": match["fields"].get("filename"),
            "page": match["fields"].get("page"),
            "source_type": match["fields"].get("source_type")
        })

    return matches