from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.models import Rating


class User(BaseModel):
    test_group: str  # A/B test group
    test_comment: Optional[str] = None
    email: Optional[str] = None
    age: Optional[str] = None
    gender: Optional[str] = None
    country: Optional[str] = None
    education: Optional[str] = None
    job: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    language: Optional[str] = None
    personality: List[int] = Field(default_factory=list)
    ratings: List[Rating] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    version: int = Field(default=1)
    deleted_at: Optional[datetime] = None
