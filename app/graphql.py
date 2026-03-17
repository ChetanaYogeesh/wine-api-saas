import strawberry
from typing import List, Optional
from datetime import datetime
from app.database import SessionLocal
from app.models import Wine


@strawberry.type
class WineType:
    id: int
    name: str
    region: str
    variety: str
    rating: float
    vintage: Optional[int]
    price: Optional[float]
    notes: Optional[str]
    created_at: datetime


@strawberry.type
class UserType:
    id: int
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime


@strawberry.type
class APIKeyType:
    id: int
    name: str
    key: str
    tier: str
    is_active: bool
    rate_limit: int
    monthly_limit: int
    created_at: datetime


@strawberry.type
class UsageStatsType:
    total_requests: int
    requests_today: int
    requests_this_month: int


@strawberry.type
class RegionType:
    name: str
    wine_count: int


@strawberry.type
class VarietyType:
    name: str
    wine_count: int


@strawberry.type
class WineStatsType:
    total_wines: int
    average_rating: float
    total_regions: int
    total_varieties: int


@strawberry.type
class Query:
    @strawberry.field
    def wines(
        self,
        region: Optional[str] = None,
        variety: Optional[str] = None,
        min_rating: Optional[float] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List[WineType]:
        db = SessionLocal()
        try:
            query = db.query(Wine)
            if region:
                query = query.filter(Wine.region.ilike(f"%{region}%"))
            if variety:
                query = query.filter(Wine.variety.ilike(f"%{variety}%"))
            if min_rating:
                query = query.filter(Wine.rating >= min_rating)

            wines = query.offset(offset).limit(limit).all()
            return [
                WineType(
                    id=w.id,
                    name=w.name,
                    region=w.region,
                    variety=w.variety,
                    rating=w.rating,
                    vintage=w.vintage,
                    price=w.price,
                    notes=w.notes,
                    created_at=w.created_at,
                )
                for w in wines
            ]
        finally:
            db.close()

    @strawberry.field
    def wine(self, id: int) -> Optional[WineType]:
        db = SessionLocal()
        try:
            wine = db.query(Wine).filter(Wine.id == id).first()
            if wine:
                return WineType(
                    id=wine.id,
                    name=wine.name,
                    region=wine.region,
                    variety=wine.variety,
                    rating=wine.rating,
                    vintage=wine.vintage,
                    price=wine.price,
                    notes=wine.notes,
                    created_at=wine.created_at,
                )
            return None
        finally:
            db.close()

    @strawberry.field
    def search_wines(self, query: str, limit: int = 10) -> List[WineType]:
        db = SessionLocal()
        try:
            wines = (
                db.query(Wine)
                .filter(
                    Wine.name.ilike(f"%{query}%")
                    | Wine.region.ilike(f"%{query}%")
                    | Wine.variety.ilike(f"%{query}%")
                )
                .limit(limit)
                .all()
            )
            return [
                WineType(
                    id=w.id,
                    name=w.name,
                    region=w.region,
                    variety=w.variety,
                    rating=w.rating,
                    vintage=w.vintage,
                    price=w.price,
                    notes=w.notes,
                    created_at=w.created_at,
                )
                for w in wines
            ]
        finally:
            db.close()

    @strawberry.field
    def top_rated_wines(self, limit: int = 10) -> List[WineType]:
        db = SessionLocal()
        try:
            wines = db.query(Wine).order_by(Wine.rating.desc()).limit(limit).all()
            return [
                WineType(
                    id=w.id,
                    name=w.name,
                    region=w.region,
                    variety=w.variety,
                    rating=w.rating,
                    vintage=w.vintage,
                    price=w.price,
                    notes=w.notes,
                    created_at=w.created_at,
                )
                for w in wines
            ]
        finally:
            db.close()

    @strawberry.field
    def regions(self) -> List[RegionType]:
        db = SessionLocal()
        try:
            results = (
                db.query(Wine.region, strawberry.field("count(*) as count"))
                .group_by(Wine.region)
                .all()
            )
            return [RegionType(name=r[0], wine_count=r[1]) for r in results]
        finally:
            db.close()

    @strawberry.field
    def varieties(self) -> List[VarietyType]:
        db = SessionLocal()
        try:
            results = (
                db.query(Wine.variety, strawberry.field("count(*) as count"))
                .group_by(Wine.variety)
                .all()
            )
            return [VarietyType(name=r[0], wine_count=r[1]) for r in results]
        finally:
            db.close()

    @strawberry.field
    def wine_stats(self) -> WineStatsType:
        db = SessionLocal()
        try:
            total = db.query(Wine).count()
            avg_rating = db.query(Wine).func.avg(Wine.rating).scalar() or 0
            regions = db.query(Wine.region).distinct().count()
            varieties = db.query(Wine.variety).distinct().count()

            return WineStatsType(
                total_wines=total,
                average_rating=round(float(avg_rating), 2),
                total_regions=regions,
                total_varieties=varieties,
            )
        finally:
            db.close()


@strawberry.type
class Mutation:
    @strawberry.mutation
    def echo(self, message: str) -> str:
        return f"Echo: {message}"


schema = strawberry.Schema(query=Query, mutation=Mutation)
