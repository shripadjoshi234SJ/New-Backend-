from fastapi import APIRouter, Depends, File, UploadFile

from app.controllers.note_controller import NoteController
from app.middleware.auth import get_current_user
from app.schemas.note_schema import NoteUpdateRequest, SummarizeRequest
from app.utils.response import success_response

router = APIRouter(prefix="/notes", tags=["notes"])
controller = NoteController()


@router.post("/upload")
async def upload_note(file: UploadFile = File(...), title: str | None = None, user: dict = Depends(get_current_user)):
    return await controller.upload_note(file, title)


@router.post("/summarize")
async def summarize_note(payload: SummarizeRequest, user: dict = Depends(get_current_user)):
    return await controller.summarize_note(payload, user["id"])


@router.get("")
async def list_notes(user: dict = Depends(get_current_user)):
    notes = await controller.list_notes(user["id"])
    return success_response("Notes fetched", notes)


@router.get("/{note_id}")
async def get_note(note_id: str, user: dict = Depends(get_current_user)):
    note = await controller.get_note(note_id, user["id"])
    return success_response("Note fetched", note)


@router.put("/{note_id}")
async def update_note(note_id: str, payload: NoteUpdateRequest, user: dict = Depends(get_current_user)):
    result = await controller.update_note(note_id, payload, user["id"])
    return result


@router.delete("/{note_id}")
async def delete_note(note_id: str, user: dict = Depends(get_current_user)):
    return await controller.delete_note(note_id, user["id"])


@router.get("/{note_id}/download")
async def download_note(note_id: str, user: dict = Depends(get_current_user)):
    return await controller.download_note(note_id, user["id"])
