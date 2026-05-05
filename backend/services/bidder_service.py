import uuid
import asyncio
from fastapi import HTTPException
from backend.utils.file_handler import save_upload
from backend.database.mongo import tender_collection
from backend.database.mongo import bidder_collection
from datetime import datetime, timezone
from ai_service.extractors.document_extractor import extract_text_from_file
from ai_service.parsers.bid_parser import parse_bids
from ai_service.evaluators.verdict_engine import run_evaluation
def get_tender_summary(tender_id: str):
    bidders = list(bidder_collection.find({"tender_id": tender_id}))

    summary = {
        "tender_id": tender_id,
        "total_bidders": len(bidders),
        "eligible": 0,
        "ineligible": 0,
        "manual_review": 0
    }

    for b in bidders:
        result = b.get("results", {})
        bidders_list = result.get("bidders", [])

        for bd in bidders_list:
            verdict = bd.get("overallVerdict")

            if verdict == "ELIGIBLE":
                summary["eligible"] += 1
            elif verdict == "NOT_ELIGIBLE":
                summary["ineligible"] += 1
            else:
                summary["manual_review"] += 1

    return summary
def get_bidder_by_id(bidder_id: str):
    doc = bidder_collection.find_one({"bidder_id": bidder_id})

    if not doc:
        raise HTTPException(status_code=404, detail="Bidder not found")

    doc["_id"] = str(doc["_id"])  # convert ObjectId

    return doc
def get_bidders_by_tender(tender_id: str):
    bidders = list(bidder_collection.find({"tender_id": tender_id}))

    if not bidders:
        return {
            "message": "No bidders found for this tender",
            "tender_id": tender_id,
            "bidders": []
        }

    # Convert ObjectId → string
    for b in bidders:
        b["_id"] = str(b["_id"])

    return {
        "tender_id": tender_id,
        "count": len(bidders),
        "bidders": bidders
    }
async def process_bidder_upload(files, tender_id, bidder_name):
    bidder_id = f"B_{uuid.uuid4().hex[:8]}"

    # 🔹 Step 1: fetch criteria
    doc = tender_collection.find_one({"tender_id": tender_id})

    if not doc:
        raise HTTPException(status_code=404, detail="Tender not found")

    criteria = doc.get("criteria", [])

    # 🔹 Step 2: save files + extract text
    bid_texts = []

    for file in files:
        file_path, filename = await save_upload(file, f"bidders/{bidder_id}")

        text = await asyncio.to_thread(extract_text_from_file, file_path)

        bid_texts.append({
            "filename": filename,
            "text": text,
            "ocr_used": False
        })

    if not bid_texts:
        raise HTTPException(400, "No bidder documents provided")

    # 🔹 Step 3: parse
    parsed_bids = await asyncio.to_thread(parse_bids, bid_texts, criteria)

    # 🔹 Step 4: evaluate
    results = await asyncio.to_thread(run_evaluation, parsed_bids, criteria)
    print("from bidder service:", results)
    bidder_doc = {
        "bidder_id": bidder_id,
        "tender_id": tender_id,
        "bidder_name": bidder_name,
        "files": [f["filename"] for f in bid_texts],
        "results": results,
        "created_at": datetime.now(timezone.utc)
    }
    existing = bidder_collection.find_one({
    "tender_id": tender_id,
    "bidder_name": bidder_name
    })
    print("INSERTING INTO DB...")
    if existing:
        bidder_collection.delete_one({"_id": existing["_id"]})
    bidder_collection.insert_one(bidder_doc)
    return {
        "bidder_id": bidder_id,
        "bidder_name": bidder_name,
        "results": results
    }