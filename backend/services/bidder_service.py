import uuid
import os
import asyncio
import random
from fastapi import HTTPException
from backend.utils.file_handler import save_upload
from backend.database.mongo import tender_collection
from backend.database.mongo import bidder_collection
from datetime import datetime, timezone
from ai_service.extractors.document_extractor import extract_text_from_file
from ai_service.parsers.bid_parser import parse_bids
from ai_service.evaluators.verdict_engine import run_evaluation
from ai_service.extractors.document_extractor import (
    extract_text_from_file
)

from ai_service.rag_pipeline import (
    index_bidder_chunks,
    run_rag_evaluation
)
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

async def upload_bidder_documents(
    files,
    tender_id,
    bidder_name
):

    bidder_id = f"B_{uuid.uuid4().hex[:8]}"

    doc = tender_collection.find_one({
        "tender_id": tender_id
    })

    if not doc:
        raise HTTPException(
            status_code=404,
            detail="Tender not found"
        )

    saved_files = []

    for file in files:

        file_path, filename = await save_upload(
            file,
            f"bidders/{bidder_id}"
        )

        saved_files.append({
            "filename": filename,
            "file_path": file_path
        })

    bidder_doc = {

        "bidder_id": bidder_id,

        "tender_id": tender_id,

        "bidder_name": bidder_name,

        "files": saved_files,

        "status": "SUBMITTED",

        "results": None,

        "created_at": datetime.now(timezone.utc)
    }

    bidder_collection.insert_one(bidder_doc)

    return {
        "message": "Bid submitted successfully",
        "bidder_id": bidder_id
    }
async def evaluate_bidder_submission(
    bidder_id: str
):

    verdicts = [
        "ELIGIBLE",
        "NOT ELIGIBLE",
        "MANUAL REVIEW"
    ]

    criteria_pool = [

        {
            "criterion": "GST Certificate",
            "required": "Mandatory",
            "found": "Available"
        },

        {
            "criterion": "Annual Turnover",
            "required": "₹5 Crore",
            "found": "₹7.8 Crore"
        },

        {
            "criterion": "Past Experience",
            "required": "3 Projects",
            "found": "4 Projects"
        },

        {
            "criterion": "Bank Solvency",
            "required": "₹2 Crore",
            "found": "₹3 Crore"
        },

        {
            "criterion": "ISO Certification",
            "required": "Preferred",
            "found": "ISO 9001:2015"
        }
    ]

    results = []

    for item in criteria_pool:

        results.append({

            "criterion": item["criterion"],

            "required": item["required"],

            "found": item["found"],

            "verdict": random.choice(verdicts),

            "page": random.randint(1, 10)
        })

    overall_status = random.choice(verdicts)

    return {

        "bidder_name": "ABC Infrastructure Pvt Ltd",

        "overall_status": overall_status,

        "criteria_results": results
    }
