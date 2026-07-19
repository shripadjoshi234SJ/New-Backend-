from typing import List, Optional

from pydantic import BaseModel, Field


class UploadNoteRequest(BaseModel):
    title: Optional[str] = None


class SummarizeRequest(BaseModel):
    title: str
    originalText: str


class NoteResponse(BaseModel):
    id: str = Field(alias="_id")
    title: str
    summary: str
    keywords: List[str]
    mcqs: List[dict]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class NoteUpdateRequest(BaseModel):
    title: str
