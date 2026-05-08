# import os
# import uuid
# import json
# from typing import List, Dict
# from sentence_transformers import SentenceTransformer
# from pinecone import Pinecone
# from openai import OpenAI


# # =========================
# # CONFIG
# # =========================

# PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
# PINECONE_INDEX = os.getenv("PINECONE_INDEX_NAME")

# NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

# pc = Pinecone(api_key=PINECONE_API_KEY)
# index = pc.Index(PINECONE_INDEX)

# client = OpenAI(
#     api_key=NVIDIA_API_KEY,
#     base_url="https://integrate.api.nvidia.com/v1"
# )


# # =========================
# # EMBEDDING FUNCTION
# # =========================
# embedding_model = SentenceTransformer(
#     "BAAI/bge-small-en-v1.5"
# )
# def get_embedding(text: str):
#     embedding = embedding_model.encode(text)
#     return embedding.tolist()


# # =========================
# # INDEX BLOCKS INTO PINECONE
# # =========================

# def index_blocks(blocks: List[Dict]):
#     vectors = []

#     for block in blocks:
#         text = block.get("text", "").strip()
#         if not text:
#             continue

#         embedding = get_embedding(text)

#         vectors.append({
#             "id": str(uuid.uuid4()),
#             "values": embedding,
#             "metadata": {
#                 "text": text,
#                 "filename": block.get("filename"),
#                 "page": block.get("page")
#             }
#         })

#     if vectors:
#         index.upsert(vectors=vectors)


# # =========================
# # RETRIEVE RELEVANT BLOCKS
# # =========================

# def retrieve_relevant_blocks(query: str, top_k: int = 5):
#     query_text = (
#         "Represent this sentence for searching relevant passages: "+ query
#     )

#     query_embedding = get_embedding(query_text)

#     results = index.query(
#         vector=query_embedding,
#         top_k=top_k,
#         include_metadata=True
#     )

#     matches = []
#     for match in results["matches"]:
#         matches.append(match["metadata"])

#     return matches


# # =========================
# # LLM EXTRACTION
# # =========================

# def run_llm(criterion: Dict, context_blocks: List[Dict]) -> Dict:
#     context_text = "\n\n".join([
#         f"{b['text']} (file: {b['filename']}, page: {b['page']})"
#         for b in context_blocks
#     ])

#     prompt = f"""
# You are a strict JSON generator.

# Criterion:
# {criterion['description']}

# Context:
# {context_text}

# Return ONLY JSON:

# {{
#   "criterion_id": "{criterion['id']}",
#   "description": "Average turnover",
#   "value_found": "...",
#   "document_reference": "...",
#   "page": ...,
#   "confidence": "high/medium/low"
# }}
# """

#     response = client.chat.completions.create(
#         model=os.getenv("MODEL_NAME"),
#         response_format={"type": "json_object"},
#         messages=[
#             {"role": "system", "content": "Return only valid JSON."},
#             {"role": "user", "content": prompt}
#         ]
#     )

#     return response.choices[0].message.content


# # =========================
# # MAIN FUNCTION
# # =========================

# def parse_bids(flat_blocks: List[Dict], criteria: List[Dict]) -> List[Dict]:

#     """
#     Main pipeline:
#     1. Index bidder document blocks into Pinecone
#     2. For each criterion:
#         - Retrieve relevant blocks
#         - Run LLM
#     """
#     print(flat_blocks)
#     print("\n=== INDEXING BLOCKS ===")
#     # try:
#     #     index.delete(delete_all=True)
#     # except Exception as e:
#     #     print("DELETE ERROR:", e)
#     flattened_blocks = []

#     for file_data in flat_blocks:

#         filename = file_data.get("filename")

#         chunk_list = file_data.get("text", [])

#         for chunk in chunk_list:

#             chunk["filename"] = filename

#             flattened_blocks.append(chunk)
#     index_blocks(flattened_blocks)

#     results = []

#     print("\n=== PROCESSING CRITERIA ===")

#     for criterion in criteria:
#         print(f"Processing: {criterion['id']}")

#         # Step 1: Retrieve relevant chunks
#         relevant_blocks = retrieve_relevant_blocks(
#             criterion["description"]
#         )

#         # Step 2: LLM extraction
#         llm_output = run_llm(criterion, relevant_blocks)

#         try:
#             parsed = json.loads(llm_output)
#         except:
#             parsed = {
#                 "criterion_id": criterion["id"],
#                 "value_found": None,
#                 "document_reference": None,
#                 "page": None,
#                 "confidence": "low"
#             }

#         results.append(parsed)

#     return results

"""
bid_parser.py
Given a list of extracted texts and the criteria list,
call the LLM to extract relevant evidence per criterion per bidder.

File grouping convention: filename prefix before first '_' is the bidder ID.
e.g. "BidderA_TurnoverCert.pdf" → bidder "BidderA"
     "Sharma_Construction_GST.pdf" → bidder "Sharma" (first segment)

If grouping cannot be inferred, each file is treated as a separate bidder.
"""

import json
import requests
import os
import re
from dotenv import load_dotenv
load_dotenv()   
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
if not NVIDIA_API_KEY:
    raise ValueError("NVIDIA_API_KEY not set in environment variables")
NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL_NAME = os.getenv("MODEL_NAME")
if not MODEL_NAME:
    raise ValueError("MODEL_NAME not set in environment variables")


def _infer_bidder_name(filename: str) -> str:
    name = os.path.splitext(filename)[0]
    parts = re.split(r'[_\-\s]', name)

    if len(parts) >= 2 and len(parts[0]) > 2:
        return f"{parts[0]} {parts[1]}"
    return parts[0] if parts else filename


def _group_files_by_bidder(bid_texts: list) -> dict:
    groups = {}
    for item in bid_texts:
        bidder = _infer_bidder_name(item["filename"])
        groups.setdefault(bidder, []).append(item)
    return groups
def chunk_blocks(blocks, max_chars=8000):
    """
    Chunk list of {page, block, text} into safe-sized groups
    WITHOUT breaking structure.
    """
    chunks = []
    current_chunk = []
    current_len = 0

    for item in blocks:
        text = item.get("text", "")
        length = len(text)

        if current_len + length > max_chars and current_chunk:
            chunks.append(current_chunk)
            current_chunk = []
            current_len = 0

        current_chunk.append(item)
        current_len += length

    if current_chunk:
        chunks.append(current_chunk)

    return chunks
def build_chunk_text(chunk, filename):
    """
    Convert structured blocks → LLM readable text WITH traceability
    """
    text = ""
    for item in chunk:
        text += f"""
=== DOCUMENT: {filename} | page={item.get('page')} | block={item.get('block')} ===
{item.get('text')}
"""
    return text
def merge_results(results, criteria):
    """
    Merge chunk-wise results into final answer
    """
    priority = {"high": 3, "medium": 2, "low": 1, "not_found": 0}

    merged = {
        c["id"]: {
            "criterion_id": c["id"],
            "value_found": None,
            "document_reference": None,
            "confidence": "not_found",
            "raw_excerpt": None,
            "notes": ""
        }
        for c in criteria
    }

    for res in results:
        for item in res.get("criteria_evidence", []):
            cid = item["criterion_id"]

            if cid not in merged:
                continue

            if priority.get(item["confidence"], 0) > priority.get(merged[cid]["confidence"], 0):
                merged[cid] = item

    return list(merged.values())

BID_PARSE_SYSTEM = """
You are a government procurement analyst parsing a bidder's submission documents.

Given:
1. A list of eligibility criteria (with IDs and descriptions)
2. Text extracted from a bidder's documents

For each criterion, find the relevant evidence in the documents.
You should just give json document, no other information, only and only json.
Return ONLY valid JSON. No markdown, no extra text. Format:

{
  "bidder_name": "...",
  "criteria_evidence": [
    {
      "criterion_id": "C001",
      "value_found": "₹8.2 Crore (FY 2022-23)",
      "document_reference": "CA_Certificate.pdf",
      "confidence": "high",    // high | medium | low
      "raw_excerpt": "...",    // exact text from document (max 200 chars)
      "notes": "..."           // any relevant observation
      "page":null,
      "block":55
    }
  ]
}

confidence guide:
- high: clear numeric/text value found that directly answers the criterion
- medium: value found but requires interpretation or is partially legible
- low: document present but value cannot be read reliably (e.g. blurry scan)

If a criterion's evidence is NOT found in any document, still include it with:
  value_found: null, document_reference: null, confidence: "not_found"
"""


def parse_single_bidder(bidder_name: str, files: list, criteria: list) -> dict:
    criteria_json = json.dumps([
        {
            "id": c["id"],
            "description": c["description"],
            "threshold": c.get("threshold"),
            "mandatory": c.get("mandatory", True)
        }
        for c in criteria
    ], indent=2, ensure_ascii=False)

    all_results = []

    for f in files:
        filename = f["filename"]
        blocks = f["text"]   

        chunks = chunk_blocks(blocks)

        for chunk in chunks:
            chunk_text = build_chunk_text(chunk, filename)

            response = requests.post(
                NVIDIA_URL,
                headers={
                    "Authorization": f"Bearer {NVIDIA_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": MODEL_NAME,
                    "messages": [
                        {"role": "system", "content": BID_PARSE_SYSTEM},
                        {
                            "role": "user",
                            "content": (
                                f"Bidder: {bidder_name}\n\n"
                                f"Criteria:\n{criteria_json}\n\n"
                                f"Documents:\n{chunk_text}"
                            )
                        }
                    ],
                    "temperature": 0,
                    "max_tokens": 2048
                }
            )

            if response.status_code != 200:
                print("API ERROR:", response.status_code, response.text)
                continue

            try:
                data = response.json()
                raw = data["choices"][0]["message"]["content"].strip()
            except:
                continue

            raw = raw.strip()

            # remove markdown block
            raw = raw.replace("```json", "")
            raw = raw.replace("```", "")

            # extract JSON object only
            start = raw.find("{")
            end = raw.rfind("}")

            if start != -1 and end != -1:
                raw = raw[start:end+1]


            try:
                parsed = json.loads(raw)
                all_results.append(parsed)
            except Exception as e:

                print("\n===== RAW LLM OUTPUT =====\n")
                print(raw)

                print("\n===== JSON ERROR =====\n")
                print(e)

                raise e

    final = {
        "bidder_name": bidder_name,
        "criteria_evidence": merge_results(all_results, criteria)
    }

    return final


def parse_bids(bid_texts: list, criteria: list) -> list:
    groups = _group_files_by_bidder(bid_texts)
    parsed = []

    for bidder_name, files in groups.items():
        print(f"[BidParser] Parsing bidder: {bidder_name}")
        parsed.append(parse_single_bidder(bidder_name, files, criteria))

    return parsed