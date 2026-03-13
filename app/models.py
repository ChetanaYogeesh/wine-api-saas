from pydantic import BaseModel
from typing import Optional


class Wine(BaseModel):
    id: int
    name: str
    region: Optional[str] = None
    variety: Optional[str] = None
    rating: Optional[float] = None
    notes: Optional[str] = None


class WineListResponse(BaseModel):
    wines: list[Wine]
    total: int
    page: int
    limit: int


class WineStats(BaseModel):
    total_wines: int
    avg_rating: float
    top_region: str
    rating_distribution: dict[str, int]
