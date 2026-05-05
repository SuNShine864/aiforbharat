# """
# bid_parser.py
# Given a list of extracted texts and the criteria list,
# call the LLM to extract relevant evidence per criterion per bidder.

# File grouping convention: filename prefix before first '_' is the bidder ID.
# e.g. "BidderA_TurnoverCert.pdf" → bidder "BidderA"
#      "Sharma_Construction_GST.pdf" → bidder "Sharma" (first segment)

# If grouping cannot be inferred, each file is treated as a separate bidder.
# """

# import json
# import requests
# import os
# import re
# from dotenv import load_dotenv
# load_dotenv()   
# NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
# if not NVIDIA_API_KEY:
#     raise ValueError("NVIDIA_API_KEY not set in environment variables")
# NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
# MODEL_NAME = os.getenv("MODEL_NAME")
# if not MODEL_NAME:
#     raise ValueError("MODEL_NAME not set in environment variables")

# def _infer_bidder_name(filename: str) -> str:
#     name = os.path.splitext(filename)[0]
#     parts = re.split(r'[_\-\s]', name)

#     if len(parts) >= 2 and len(parts[0]) > 2:
#         return f"{parts[0]} {parts[1]}"
#     return parts[0] if parts else filename


# def _group_files_by_bidder(bid_texts: list) -> dict:
#     groups = {}
#     for item in bid_texts:
#         bidder = _infer_bidder_name(item["filename"])
#         groups.setdefault(bidder, []).append(item)
#     return groups
# def chunk_blocks(blocks, max_chars=8000):
#     """
#     Chunk list of {page, block, text} into safe-sized groups
#     WITHOUT breaking structure.
#     """
#     chunks = []
#     current_chunk = []
#     current_len = 0

#     for item in blocks:
#         text = item.get("text", "")
#         length = len(text)

#         if current_len + length > max_chars and current_chunk:
#             chunks.append(current_chunk)
#             current_chunk = []
#             current_len = 0

#         current_chunk.append(item)
#         current_len += length

#     if current_chunk:
#         chunks.append(current_chunk)

#     return chunks
# def build_chunk_text(chunk, filename):
#     """
#     Convert structured blocks → LLM readable text WITH traceability
#     """
#     text = ""
#     for item in chunk:
#         text += f"""
# === DOCUMENT: {filename} | page={item.get('page')} | block={item.get('block')} ===
# {item.get('text')}
# """
#     return text
# def merge_results(results, criteria):
#     """
#     Merge chunk-wise results into final answer
#     """
#     priority = {"high": 3, "medium": 2, "low": 1, "not_found": 0}

#     merged = {
#         c["id"]: {
#             "criterion_id": c["id"],
#             "value_found": None,
#             "document_reference": None,
#             "confidence": "not_found",
#             "raw_excerpt": None,
#             "notes": "",
#             "page": None,
#             "block": None,
#         }
#         for c in criteria
#     }

#     for res in results:
#         for item in res.get("criteria_evidence", []):
#             cid = item["criterion_id"]

#             if cid not in merged:
#                 continue

#             if priority.get(item["confidence"], 0) > priority.get(merged[cid]["confidence"], 0):
#                 merged[cid] = item
#             elif merged[cid].get("page") is None and item.get("page") is not None:
#                 merged[cid]["page"] = item["page"]

#             if merged[cid].get("block") is None and item.get("block") is not None:
#                 merged[cid]["block"] = item["block"]
#     return list(merged.values())

# BID_PARSE_SYSTEM = """
# You are a government procurement analyst parsing a bidder's submission documents.

# Given:
# 1. A list of eligibility criteria (with IDs and descriptions)
# 2. Text extracted from a bidder's documents

# For each criterion, find the relevant evidence in the documents 




# Return ONLY valid JSON. No markdown, no extra text. Format:

# {
#   "bidder_name": "...",
#   "criteria_evidence": [
#     {
#       "criterion_id": "C001",
#       "value_found": "₹8.2 Crore (FY 2022-23)",
#       "document_reference": "CA_Certificate.pdf",
#       "confidence": "high",    // high | medium | low
#       "raw_excerpt": "...",    // exact text from document (max 200 chars)
#       "notes": "..."           // any relevant observation
#       "page":null,
#       "block":55
#     }
#   ]
# }

# confidence guide:
# - high: clear numeric/text value found that directly answers the criterion
# - medium: value found but requires interpretation or is partially legible
# - low: document present but value cannot be read reliably (e.g. blurry scan)

# If a criterion's evidence is NOT found in any document, still include it with:
#   value_found: null, document_reference: null, confidence: "not_found"

# STRICT RULES:
# - Return ONLY JSON
# - No explanation
# - No markdown
# - No ```json
# - Output must start with { and end with }
# """


# def _find_page_block(item, chunk):
#     value = item.get("value_found")
#     excerpt = item.get("raw_excerpt", "")

#     # normalize
#     value = str(value).lower() if value else ""
#     excerpt = excerpt.lower()

#     for block in chunk:
#         text = block.get("text", "").lower()

#         # BEST MATCH → value match
#         if value and value in text:
#             return block.get("page"), block.get("block")

#         # fallback → excerpt line match
#         for line in excerpt.split("\n"):
#             line = line.strip()
#             if line and line[:40] in text:
#                 return block.get("page"), block.get("block")

#     return None, None
# def _extract_json(raw_text):
#     try:
#         # If model wraps JSON in markdown fences
#         match = re.search(r'```json\s*(\{.*?\})\s*```', raw_text, re.DOTALL)
#         if match:
#             return json.loads(match.group(1))

#         # If model returns extra text before/after JSON
#         match = re.search(r'(\{.*\})', raw_text, re.DOTALL)
#         if match:
#             return json.loads(match.group(1))

#     except Exception as e:
#         print("Still failed:", e)

#     return None
# def parse_single_bidder(bidder_name: str, files: list, criteria: list) -> dict:
#     criteria_json = json.dumps([
#         {
#             "id": c["id"],
#             "description": c["description"],
#             "threshold": c.get("threshold"),
#             "mandatory": c.get("mandatory", True)
#         }
#         for c in criteria
#     ], indent=2, ensure_ascii=False)

#     all_results = []

#     for f in files:
#         filename = f["filename"]
#         blocks = f["text"]   

#         chunks = chunk_blocks(blocks)

#         for chunk in chunks:
#             chunk_text = build_chunk_text(chunk, filename)
#             # Take first block metadata (basic approach)
            
#             response = requests.post(
#                 NVIDIA_URL,
#                 headers={
#                     "Authorization": f"Bearer {NVIDIA_API_KEY}",
#                     "Content-Type": "application/json"
#                 },
#                 json={
#                     "model": MODEL_NAME,
#                     "messages": [
#                         {"role": "system", "content": BID_PARSE_SYSTEM},
#                         {
#                             "role": "user",
#                             "content": (
#                                 f"Bidder: {bidder_name}\n\n"
#                                 f"Criteria:\n{criteria_json}\n\n"
#                                 f"Documents:\n{chunk_text}"
#                             )
#                         }
#                     ],
#                     "temperature": 0,
#                     "max_tokens": 2048
#                 }
#             )

#             if response.status_code != 200:
#                 print("API ERROR:", response.status_code, response.text)
#                 continue

#             try:
#                 data = response.json()
#                 raw = data["choices"][0]["message"]["content"].strip()
#             except:
#                 continue

#             if raw.startswith("```"):
#                 raw = raw.split("```")[1]
#                 if raw.startswith("json"):
#                     raw = raw[4:]
#             print("\nRAW LLM OUTPUT:\n", raw)
#             try:
                
#             except:
#                 print("JSON parse failed")
#                 continue

#     final = {
#         "bidder_name": bidder_name,
#         "criteria_evidence": merge_results(all_results, criteria)
#     }

#     return final


# def parse_bids(bid_texts: list, criteria: list) -> list:
#     groups = _group_files_by_bidder(bid_texts)
#     parsed = []

#     for bidder_name, files in groups.items():
#         print(f"[BidParser] Parsing bidder: {bidder_name}")
#         parsed.append(parse_single_bidder(bidder_name, files, criteria))

#     return parsed

"""
bid_parser.py (FINAL VERSION)

- Uses structured blocks instead of raw text
- LLM selects block_id (safe)
- Backend maps block_id → page
- Page only for PDF
- No block in final output
"""

import json
import requests
import os
import re
from dotenv import load_dotenv

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

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


def build_structured_blocks(chunk):
    return [
        {
            "id": i,
            "page": item.get("page"),
            "text": item.get("text")
        }
        for i, item in enumerate(chunk)
    ]


def _extract_json(raw_text):
    try:
        match = re.search(r'```json\s*(\{.*?\})\s*```', raw_text, re.DOTALL)
        if match:
            return json.loads(match.group(1))

        match = re.search(r'(\{.*\})', raw_text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
    except Exception as e:
        print("JSON parse error:", e)

    return None


# ─────────────────────────────────────────────
# PROMPT
# ─────────────────────────────────────────────

BID_PARSE_SYSTEM = """
You are a government procurement analyst.

You are given:
1. Eligibility criteria
2. Structured document blocks

Each block has:
- id
- page
- text

TASK:
For each criterion:
- Extract the correct value
- Identify WHICH block contains it (block_id)

STRICT RULES:
- ONLY choose block_id from given blocks
- DO NOT guess page numbers
- DO NOT hallucinate
- If not found → block_id = null

Return ONLY JSON:

{
  "bidder_name": "...",
  "criteria_evidence": [
    {
      "criterion_id": "C001",
      "value_found": "...",
      "block_id": 5,
      "confidence": "high",
      "raw_excerpt": "...",
      "notes": "..."
    }
  ]
}
"""


# ─────────────────────────────────────────────
# CORE LOGIC
# ─────────────────────────────────────────────

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

        is_pdf = filename.lower().endswith(".pdf")

        chunks = chunk_blocks(blocks)

        for chunk in chunks:
            structured_blocks = build_structured_blocks(chunk)

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
                                f"Blocks:\n{json.dumps(structured_blocks, indent=2, ensure_ascii=False)}"
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
                print("\nRAW LLM OUTPUT:\n", raw)
            except:
                continue

            parsed = _extract_json(raw)

            if not parsed:
                print("JSON parse failed")
                continue

            # 🔥 Map block_id → page
            for item in parsed.get("criteria_evidence", []):
                block_id = item.get("block_id")

                item["document_reference"] = filename

                if is_pdf and block_id is not None and block_id < len(chunk):
                    item["page"] = chunk[block_id].get("page")
                else:
                    item["page"] = None

                # ❌ remove block_id from final output
                if "block_id" in item:
                    del item["block_id"]

            all_results.append(parsed)

    # ─────────────────────────────────────────────
    # Merge results
    # ─────────────────────────────────────────────

    priority = {"high": 3, "medium": 2, "low": 1, "not_found": 0}

    merged = {
        c["id"]: {
            "criterion_id": c["id"],
            "value_found": None,
            "document_reference": None,
            "confidence": "not_found",
            "raw_excerpt": None,
            "notes": "",
            "page": None,
        }
        for c in criteria
    }

    for res in all_results:
        for item in res.get("criteria_evidence", []):
            cid = item["criterion_id"]

            if cid not in merged:
                continue

            if priority.get(item["confidence"], 0) > priority.get(merged[cid]["confidence"], 0):
                merged[cid] = item

            elif merged[cid]["page"] is None and item.get("page") is not None:
                merged[cid]["page"] = item["page"]

    return {
        "bidder_name": bidder_name,
        "criteria_evidence": list(merged.values())
    }


def parse_bids(bid_texts: list, criteria: list) -> list:
    groups = _group_files_by_bidder(bid_texts)
    parsed = []

    for bidder_name, files in groups.items():
        print(f"[BidParser] Parsing bidder: {bidder_name}")
        parsed.append(parse_single_bidder(bidder_name, files, criteria))

    return parsed