from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Rating(BaseModel):
    item_id: str
    score: int
    timestamp: datetime
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    version: int = Field(default=1)
    deleted_at: Optional[datetime] = None




