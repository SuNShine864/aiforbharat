from fastapi import APIRouter, UploadFile, File, Form,HTTPException
from typing import Annotated,List
from backend.services.bidder_service import process_bidder_upload
from backend.services.bidder_service import get_bidder_by_id
from backend.database.mongo import bidder_collection

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
    files: Annotated[List[UploadFile], File(...)],
):
    result = await process_bidder_upload(files, tender_id, bidder_name)

    return result