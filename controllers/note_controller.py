import os
from datetime import datetime
from io import BytesIO
from typing import Dict, List

from fastapi import File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from bson import ObjectId

from app.core.database import db
from app.schemas.note_schema import NoteUpdateRequest, SummarizeRequest, UploadNoteRequest
from app.services.ai_service import ai_service
from app.services.docx_parser import extract_text_from_docx
from app.services.pdf_generator import generate_summary_pdf
from app.services.pdf_parser import extract_text_from_pdf
from app.services.txt_parser import extract_text_from_txt
from app.utils.response import success_response

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class NoteController:
    async def upload_note(self, file: UploadFile, title: str | None) -> Dict[str, object]:
        if not file:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided")

        file_name = file.filename or "uploaded_file"
        file_path = os.path.join(UPLOAD_DIR, f"{ObjectId()}_{file_name}")
        with open(file_path, "wb") as handle:
            handle.write(await file.read())

        extension = os.path.splitext(file_name)[1].lower()
        if extension == ".pdf":
            extracted_text = await extract_text_from_pdf(file_path)
        elif extension == ".docx":
            extracted_text = await extract_text_from_docx(file_path)
        elif extension in {".txt", ".md"}:
            extracted_text = await extract_text_from_txt(file_path)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")

        note_title = title.strip() if title and title.strip() else os.path.splitext(file_name)[0]
        return success_response(
            "File uploaded and text extracted",
            {"title": note_title, "extractedText": extracted_text, "fileName": file_name},
        )

    async def summarize_note(self, payload: SummarizeRequest, user_id: str) -> Dict[str, object]:
        ai_result = await ai_service.summarize_text(payload.originalText, payload.title)
        summary = ai_result.get("summary") or ""
        keywords = ai_result.get("keywords") or []
        mcqs = ai_result.get("mcqs") or []

        note_doc = {
            "_id": str(ObjectId()),
            "user_id": user_id,
            "title": payload.title.strip() or "Untitled Note",
            "original_text": payload.originalText,
            "summary": summary,
            "keywords": keywords,
            "mcqs": mcqs,
            "file_name": None,
            "file_type": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        await db["notes"].insert_one(note_doc)

        return success_response(
            "Summary generated and note saved",
            {
                "_id": note_doc["_id"],
                "title": note_doc["title"],
                "summary": note_doc["summary"],
                "keywords": note_doc["keywords"],
                "mcqs": note_doc["mcqs"],
                "created_at": note_doc["created_at"].isoformat(),
                "updated_at": note_doc["updated_at"].isoformat(),
            },
        )

    async def list_notes(self, user_id: str) -> List[Dict[str, object]]:
        notes_cursor = db["notes"].find({"user_id": user_id}).sort("created_at", -1)
        notes = []
        async for doc in notes_cursor:
            notes.append(
                {
                    "_id": str(doc["_id"]),
                    "title": doc.get("title", "Untitled"),
                    "summary": doc.get("summary", ""),
                    "keywords": doc.get("keywords", []),
                    "mcqs": doc.get("mcqs", []),
                    "created_at": doc.get("created_at").isoformat() if doc.get("created_at") else None,
                    "updated_at": doc.get("updated_at").isoformat() if doc.get("updated_at") else None,
                }
            )
        return notes

    async def get_note(self, note_id: str, user_id: str) -> Dict[str, object]:
        note = await db["notes"].find_one({"_id": note_id, "user_id": user_id})
        if not note:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        return {
            "_id": str(note["_id"]),
            "title": note.get("title", "Untitled"),
            "summary": note.get("summary", ""),
            "keywords": note.get("keywords", []),
            "mcqs": note.get("mcqs", []),
            "created_at": note.get("created_at").isoformat() if note.get("created_at") else None,
            "updated_at": note.get("updated_at").isoformat() if note.get("updated_at") else None,
        }

    async def update_note(self, note_id: str, payload: NoteUpdateRequest, user_id: str) -> Dict[str, object]:
        note = await db["notes"].find_one({"_id": note_id, "user_id": user_id})
        if not note:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

        await db["notes"].update_one(
            {"_id": note_id},
            {"$set": {"title": payload.title.strip(), "updated_at": datetime.utcnow()}},
        )
        return success_response("Note updated", {"_id": note_id, "title": payload.title.strip()})

    async def delete_note(self, note_id: str, user_id: str) -> Dict[str, object]:
        result = await db["notes"].delete_one({"_id": note_id, "user_id": user_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        return success_response("Note deleted", None)

    async def download_note(self, note_id: str, user_id: str):
        note = await db["notes"].find_one({"_id": note_id, "user_id": user_id})
        if not note:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

        pdf_buffer = await generate_summary_pdf(
            note.get("title", "Summary"),
            note.get("summary", ""),
            note.get("keywords", []),
            note.get("mcqs", []),
        )
        return StreamingResponse(pdf_buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename={note.get('title', 'summary')}.pdf"})
