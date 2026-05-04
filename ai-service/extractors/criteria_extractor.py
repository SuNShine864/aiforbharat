"""
criteria_extractor.py (NVIDIA API version)
Uses NVIDIA hosted LLM (e.g., Llama 3, Mixtral)
"""

import json
import requests
import os
from dotenv import load_dotenv
load_dotenv()   
# Replace with your NVIDIA API key
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

if not NVIDIA_API_KEY:
    raise ValueError("NVIDIA_API_KEY not set in environment variables")


# NVIDIA endpoint
NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL_NAME = os.getenv("MODEL_NAME")
if not MODEL_NAME:
    raise ValueError("MODEL_NAME not set in environment variables")

CRITERIA_SYSTEM_PROMPT = """
You are an expert government procurement analyst.

Extract ALL eligibility criteria from the tender text.

Return ONLY a valid JSON array. No explanation.

Each item MUST have:
{
  "id": "C001",
  "description": "...",
  "type": "financial",
  "mandatory": true,
  "threshold": "₹5 Crore",
  "raw": "...",
  "page": 5,
  "block": 1
}

Rules:
- Financial: turnover, net worth, bank solvency
- Technical: experience, projects, manpower
- Compliance: GST, PAN, ISO, licenses(GST and PAN are two different information)
- "must/shall/should" => mandatory true
- "preferred/desirable" => false
- DO NOT merge multiple criteria
- Extract EVERY criterion separately
- id's should be sequential eg C001, C002, C003, C004...not random
-Normalise numbers "I5 Crore" → ₹5 Crore = 5,00,00,000 
"""

def deduplicate(criteria_list):
    seen = set()
    unique = []

    for c in criteria_list:
        key = c.get("description", "").strip().lower()
        if key and key not in seen:
            seen.add(key)
            unique.append(c)

    return unique

def extract_criteria(blocks: list) -> list:
    all_criteria = []

    for item in blocks:
        text = item.get("text", "").strip()
        if not text:
            continue

        page = item.get("page")
        block_id = item.get("block")

        response = requests.post(
            NVIDIA_URL,
            headers={
                "Authorization": f"Bearer {NVIDIA_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": CRITERIA_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"""
Source Info:
page={page}, block={block_id}

Text:
{text}
"""
                    }
                ],
                "temperature": 0,
                "max_tokens": 1024
            }
        )

        # Safe handling
        if response.status_code != 200:
            print("API ERROR:", response.status_code, response.text)
            continue

        try:
            data = response.json()
            if "choices" not in data:
                print("Invalid response:", data)
                continue

            result = data["choices"][0]["message"]["content"].strip()
        except Exception:
            print("JSON decode failed:", response.text)
            continue

        # Clean markdown
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]

        try:
            criteria = json.loads(result)

            # attach source info to each criterion
            for c in criteria:
                c["page"] = page
                c["block"] = block_id

            all_criteria.extend(criteria)

        except Exception:
            print("JSON parsing failed:\n", result)
            continue

    # Deduplicate
    all_criteria = deduplicate(all_criteria)

    # Assign IDs
    for i, c in enumerate(all_criteria):
        c["id"] = f"C{str(i+1).zfill(3)}"
        c.setdefault("description", "")
        c.setdefault("type", "compliance")
        c.setdefault("mandatory", True)
        c.setdefault("threshold", None)
        c.setdefault("raw", "")

    return all_criteria
