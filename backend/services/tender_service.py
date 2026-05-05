import uuid
import asyncio
from backend.utils.file_handler import save_upload
from ai_service.extractors.document_extractor import extract_text_from_file
from ai_service.extractors.criteria_extractor import extract_criteria
from backend.database.mongo import tender_collection
from datetime import datetime,timezone
from fastapi import HTTPException

async def process_tender_upload(file):
    # 1. Generate tender ID
    tender_id = f"T_{uuid.uuid4().hex[:8]}"

    # 2. Save file
    file_path, original_name =await save_upload(file, f"tenders/{tender_id}")

    # 3. Extract text
    text = await asyncio.to_thread(extract_text_from_file, file_path)
    # print(text)
    if not text or len(text) == 0:
        raise ValueError("Could not extract text")

    # 4. Extract criteria
    try:
        criteria = await asyncio.to_thread(extract_criteria, text)

        if not criteria:
            raise ValueError("Empty criteria from LLM")
        # print(criteria)
        tender_doc = {
        "tender_id": tender_id,
        "filename": original_name,
        "file_path": file_path,
        "criteria": criteria,
        "created_at": datetime.now(timezone.utc)
        }

        tender_collection.insert_one(tender_doc)
        return {
            "tender_id": tender_id,
            "filename": original_name,
            "criteria": criteria
        }

    except Exception as e:
        print("LLM ERROR:", str(e))

        raise HTTPException(
            status_code=500,
            detail="Failed to extract criteria. Please try again."
        )