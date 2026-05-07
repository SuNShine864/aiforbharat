from fastapi import APIRouter, UploadFile, File, Form,HTTPException
from typing import Annotated,List
import os
from ai_service.rag_pipeline import (
    index_bidder_chunks
)

from ai_service.extractors.document_extractor import (
    extract_text_from_file
)
from backend.services.bidder_service import (
    get_bidders_by_tender
)
from backend.database.mongo import bidder_collection
from backend.services.bidder_service import (
    upload_bidder_documents,
    evaluate_bidder_submission,
    get_bidder_by_id,
    get_bidders_by_tender
)
router = APIRouter()
def get_bidder_by_id(bidder_id: str):
    doc = bidder_collection.find_one({"bidder_id": bidder_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Bidder not found")
    doc["_id"] = str(doc["_id"])  # convert ObjectId
    return doc
@router.get("/{bidder_id}")
def get_bidder(bidder_id: str):
    return get_bidder_by_id(bidder_id)
@router.post("/upload")
async def upload_bidder(

    tender_id: Annotated[str, Form(...)],

    bidder_name: Annotated[str, Form(...)],

    files: Annotated[List[UploadFile], File(...)]

):
    return await upload_bidder_documents(
        files,
        tender_id,
        bidder_name
    )
@router.get("/submissions")
async def get_submissions():

    submissions = list(

        bidder_collection.find(
            {},
            {
                "_id": 0,
                "bidder_name": 1,
                "tender_id": 1,
                "status": 1
            }
        )
    )
    return submissions
@router.post("/evaluate/{bidder_id}")
async def evaluate_bidder(
    bidder_id: str
):

    return await evaluate_bidder_submission(
        bidder_id
    )
@router.get("/tender/{tender_id}")
async def fetch_bidders_by_tender(
    tender_id: str
):

    return get_bidders_by_tender(
        tender_id
    )
@router.post("/index-demo")
async def index_demo_bidder():

    BASE_DIR = os.path.dirname(
        os.path.dirname(__file__)
    )

    pdf_path = os.path.join(

        BASE_DIR,

        "data",
        "samples",
        "mmrc",
        "bidder",
        "xyz_enterprises_pvt_lmtd_bid.pdf"
    )

    blocks = extract_text_from_file(
        pdf_path
    )

    for b in blocks:

        b["filename"] = (
            "xyz_enterprises_pvt_lmtd_bid.pdf"
        )

    bidder_id = "DEMO_BIDDER"

    index_bidder_chunks(

        bidder_id,

        blocks
    )

    return {

        "message": "Vectors indexed successfully",

        "chunks": len(blocks),

        "bidder_id": bidder_id
    }