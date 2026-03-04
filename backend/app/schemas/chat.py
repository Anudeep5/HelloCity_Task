from typing import Any, Optional
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=3)
    message: str = Field(..., min_length=1)

class FeedbackRequest(BaseModel):
    session_id: str = Field(..., min_length=3)
    interest: str = Field(..., min_length=1)
    choice: str = Field(..., pattern="^(yes|no)$")

class PlaceCard(BaseModel):
    name: str
    address: Optional[str] = None
    rating: Optional[float] = None
    user_ratings_total: Optional[int] = None
    maps_url: Optional[str] = None
    photo_url: Optional[str] = None

class ChatResponse(BaseModel):
    assistant_message: str
    interests: list[str]
    interest_detected: bool
    interest_added: Optional[str] = None
    examples: list[PlaceCard] = Field(default_factory=list)
    onboarding_complete: bool
    profile: Optional[dict[str, Any]] = None