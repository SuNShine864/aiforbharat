from fastapi import APIRouter, UploadFile, File,Form
from backend.services.tender_service import process_tender_upload
from backend.database.mongo import tender_collection
from fastapi.responses import FileResponse
from fastapi import HTTPException
from backend.database.mongo import (
    tender_collection,
    bidder_collection
)
router = APIRouter()

@router.post("/upload")
async def upload_tender(
    title: str = Form(...),
    estimated_value: str = Form(...),
    file: UploadFile = File(...)
):
    result = await process_tender_upload(
        file,
        title,
        estimated_value
    )

    return result

from backend.services.bidder_service import get_bidders_by_tender
@router.get("/{tender_id}/bidders")
def get_bidders(tender_id: str):
    return get_bidders_by_tender(tender_id)

from backend.services.bidder_service import get_tender_summary
@router.get("/{tender_id}/summary")
def tender_summary(tender_id: str):
    return get_tender_summary(tender_id)

@router.get("/")
async def get_all_tenders():

    tenders = list(tender_collection.find())

    for t in tenders:
        t["_id"] = str(t["_id"])
        submission_count = bidder_collection.count_documents({

            "tender_id": t["tender_id"]
        })

        t["submission_count"] = submission_count
    return tenders
@router.get("/download/{tender_id}")
async def download_tender(
    tender_id: str
):

    tender = tender_collection.find_one({
        "tender_id": tender_id
    })

    if not tender:

        raise HTTPException(
            status_code=404,
            detail="Tender not found"
        )

    return FileResponse(

        path=tender["file_path"],

        filename=tender["filename"],

        media_type="application/pdf"
    )