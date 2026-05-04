import json
import requests
import os
from dotenv import load_dotenv
load_dotenv()  
#  NVIDIA CONFIG
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

if not NVIDIA_API_KEY:
    raise ValueError("NVIDIA_API_KEY not set in environment variables")

NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL_NAME = "minimaxai/minimax-m2.5"


VERDICT_SYSTEM = """
You are a government procurement evaluation officer.

Given:
1. An eligibility criterion (with description and threshold)
2. Evidence extracted from a bidder's documents

Assign a verdict and explain it with a citation.

Return ONLY valid JSON:
{
  "verdict": "ELIGIBLE",
  "value": "₹8.2 Cr (avg)",
  "document_ref": "CA_Cert.pdf",
  "page": null,
  "block": 55,
  "reason": "..."
}

Verdict rules:
- ELIGIBLE: evidence clearly meets the criterion threshold
- NOT_ELIGIBLE: evidence clearly does NOT meet the criterion
- MANUAL_REVIEW: use this when:
  * confidence is "low"
  * confidence is "not_found"
  * borderline values
  * ambiguity
  * uncertainty
-If a criterion is optional (mandatory=false), it should NOT cause disqualification.
-Always compare value_found against threshold explicitly before assigning verdict.

NEVER silently disqualify.
"""


# =========================
# NVIDIA CALL
# =========================
def _call_nvidia(messages):
    response = requests.post(
        NVIDIA_URL,
        headers={
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL_NAME,
            "messages": messages,
            "temperature": 0,
            "max_tokens": 1024
        }
    )

    if response.status_code != 200:
        print("NVIDIA ERROR:", response.status_code, response.text)
        return None

    try:
        data = response.json()
        if "choices" not in data:
            print("Invalid response:", data)
            return None

        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        print("JSON decode error:", response.text)
        return None


# =========================
# VERDICT PER CRITERION
# =========================
def _assign_verdict_for_criterion(criterion: dict, evidence: dict) -> dict:

    confidence = evidence.get("confidence", "not_found")

    # Fast rule (keep this — very important)
    if confidence in ["low","not_found"]:
        return {
            "criterion_id": criterion["id"],
            "verdict": "MANUAL_REVIEW",
            "value": None,
            "documentRef": None,
            "page": None,
            "block": None,
            "reason": f"No document found for: {criterion['description']}"
        }

    messages = [
        {"role": "system", "content": VERDICT_SYSTEM},
        {
            "role": "user",
            "content": f"""
Criterion: {criterion['description']}
Threshold: {criterion.get('threshold') or 'see description'}
Mandatory: {criterion.get('mandatory', True)}

Evidence:
Value found: {evidence.get('value_found')}
Document: {evidence.get('document_reference')}
Location: Page: {evidence.get('page')},Block: {evidence.get('block')}
Confidence: {confidence}
Excerpt: {evidence.get('raw_excerpt', '')[:300]}
Notes: {evidence.get('notes', '')}
"""
        }
    ]

    raw = _call_nvidia(messages)

    if not raw:
        return {
            "criterion_id": criterion["id"],
            "verdict": "MANUAL_REVIEW",
            "value": None,
            "documentRef": None,
            "page": None,
            "block": None,
            "reason": "LLM call failed"
        }

    # Clean markdown
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        result = json.loads(raw)
    except Exception:
        print("JSON parse failed:", raw)
        return {
            "criterion_id": criterion["id"],
            "verdict": "MANUAL_REVIEW",
            "value": None,
            "documentRef": None,
            "page": None,
            "block": None,
            "reason": "Parsing failed — manual review required"
        }

    return {
        "criterion_id": criterion["id"],
        "verdict": result.get("verdict", "MANUAL_REVIEW"),
        "value": result.get("value"),
        "documentRef": result.get("document_ref"),
        "page": result.get("page"),
        "block": result.get("block"),
        "reason": result.get("reason", "")
    }


# =========================
# OVERALL VERDICT
# =========================
def _overall_verdict(criterion_verdicts: list, criteria: list) -> str:

    mandatory_ids = {c["id"] for c in criteria if c.get("mandatory", True)}

    for cv in criterion_verdicts:
        if cv["criterion_id"] in mandatory_ids and cv["verdict"] == "NOT_ELIGIBLE":
            return "NOT_ELIGIBLE"

    for cv in criterion_verdicts:
        if cv["criterion_id"] in mandatory_ids and cv["verdict"] == "MANUAL_REVIEW":
            return "MANUAL_REVIEW"

    return "ELIGIBLE"


# =========================
# MAIN FUNCTION
# =========================
def run_evaluation(parsed_bids: list, criteria: list) -> dict:

    bidder_results = []
    summary = {"eligible": 0, "ineligible": 0, "manualReview": 0}

    for i, bid in enumerate(parsed_bids):
        bidder_id = f"B{str(i+1).zfill(3)}"
        bidder_name = bid.get("bidder_name", f"Bidder {i+1}")

        evidence_map = {
            e["criterion_id"]: e
            for e in bid.get("criteria_evidence", [])
        }

        print(f"[VerdictEngine] Evaluating: {bidder_name}")

        criterion_verdicts = []

        for criterion in criteria:
            evidence = evidence_map.get(criterion["id"], {
                "confidence": "not_found",
                "value_found": None,
                "document_reference": None
            })

            verdict = _assign_verdict_for_criterion(criterion, evidence)
            criterion_verdicts.append(verdict)

        overall = _overall_verdict(criterion_verdicts, criteria)

        if overall == "ELIGIBLE":
            summary["eligible"] += 1
        elif overall == "NOT_ELIGIBLE":
            summary["ineligible"] += 1
        else:
            summary["manualReview"] += 1

        bidder_results.append({
            "id": bidder_id,
            "name": bidder_name,
            "overallVerdict": overall,
            "criteria": criterion_verdicts,
        })

    return {
        "summary": summary,
        "bidders": bidder_results,
    }