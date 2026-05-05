from fastapi import APIRouter, UploadFile, File
from backend.services.tender_service import process_tender_upload

router = APIRouter()

@router.post("/upload")
async def upload_tender(file: UploadFile = File(...)):
    result = await process_tender_upload(file)
    return result

from backend.services.bidder_service import get_bidders_by_tender
@router.get("/{tender_id}/bidders")
def get_bidders(tender_id: str):
    return get_bidders_by_tender(tender_id)

from backend.services.bidder_service import get_tender_summary
@router.get("/{tender_id}/summary")
def tender_summary(tender_id: str):
    return get_tender_summary(tender_id)