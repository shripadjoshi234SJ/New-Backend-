from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class MCQ(BaseModel):
    question: str
    options: List[str]
    answer: str


class Note(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    title: str
    original_text: str
    summary: str
    keywords: List[str] = Field(default_factory=list)
    mcqs: List[MCQ] = Field(default_factory=list)
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
