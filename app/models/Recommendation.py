from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Recommendation(BaseModel):
    item_id: str
    user_id: str
    pred_score: float
    explanation: Optional[str] = None
    enjoy_score: Optional[int] = None
    is_known: Optional[bool] = None
    convincing_score: Optional[int] = None                      # This explanation is convincing
    determinant_score: Optional[int] = None                     # This explanation helps me to determine how well I will like this movie
    resonates_score: Optional[int] = None                       # This explanation resonates well with aspects of movies that I like
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    version: int = Field(default=1)
    deleted_at: Optional[datetime] = None



