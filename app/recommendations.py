from sqlalchemy.orm import Session
from app.models import Wine, WinePreference, WinePriceHistory
from typing import List, Optional
import random

MAX_PRICE = 100000.0
MIN_RATING = 0.0
MAX_RATING = 5.0
MAX_LIMIT = 100


class RecommendationService:
    def __init__(self, db: Session):
        self.db = db

    def get_similar_wines(self, wine_id: int, limit: int = 10) -> List[Wine]:
        if wine_id < 1:
            return []

        limit = max(1, min(limit, MAX_LIMIT))

        wine = self.db.query(Wine).filter(Wine.id == wine_id).first()
        if not wine:
            return []

        query = self.db.query(Wine).filter(Wine.id != wine_id)

        if wine.variety:
            query = query.filter(Wine.variety == wine.variety)
        elif wine.region:
            query = query.filter(Wine.region == wine.region)

        wines = query.order_by(Wine.rating.desc()).limit(limit).all()

        if len(wines) < limit:
            additional = (
                self.db.query(Wine)
                .filter(Wine.id != wine_id)
                .order_by(Wine.rating.desc())
                .limit(limit - len(wines))
                .all()
            )
            wines.extend([w for w in additional if w not in wines])

        return wines[:limit]

    def get_recommendations_for_user(self, user_id: int, limit: int = 10) -> List[Wine]:
        if user_id < 1:
            return []

        limit = max(1, min(limit, MAX_LIMIT))

        preference = (
            self.db.query(WinePreference)
            .filter(WinePreference.user_id == user_id)
            .first()
        )

        if not preference:
            return self._get_popular_wines(limit)

        query = self.db.query(Wine)

        if preference.preferred_region:
            query = query.filter(Wine.region.ilike(f"%{preference.preferred_region}%"))
        if preference.preferred_variety:
            query = query.filter(
                Wine.variety.ilike(f"%{preference.preferred_variety}%")
            )
        if preference.min_rating:
            query = query.filter(Wine.rating >= preference.min_rating)
        if preference.max_price:
            query = query.filter(Wine.price <= preference.max_price)

        wines = query.order_by(Wine.rating.desc()).limit(limit).all()

        if not wines:
            return self._get_popular_wines(limit)

        return wines

    def get_recommendations_by_preference(
        self,
        region: Optional[str] = None,
        variety: Optional[str] = None,
        min_rating: Optional[float] = None,
        max_price: Optional[float] = None,
        limit: int = 10,
    ) -> List[Wine]:
        limit = max(1, min(limit, MAX_LIMIT))

        if min_rating is not None and (
            min_rating < MIN_RATING or min_rating > MAX_RATING
        ):
            min_rating = None
        if max_price is not None and max_price < 0:
            max_price = None

        query = self.db.query(Wine)

        if region:
            query = query.filter(Wine.region.ilike(f"%{region}%"))
        if variety:
            query = query.filter(Wine.variety.ilike(f"%{variety}%"))
        if min_rating:
            query = query.filter(Wine.rating >= min_rating)
        if max_price:
            query = query.filter(Wine.price <= max_price)

        return query.order_by(Wine.rating.desc()).limit(limit).all()

    def get_ai_recommendations(
        self,
        wine_id: Optional[int] = None,
        region: Optional[str] = None,
        variety: Optional[str] = None,
        min_rating: Optional[float] = None,
        max_price: Optional[float] = None,
        limit: int = 10,
    ) -> List[dict]:
        limit = max(1, min(limit, MAX_LIMIT))

        if min_rating is not None and (
            min_rating < MIN_RATING or min_rating > MAX_RATING
        ):
            min_rating = None
        if max_price is not None and max_price < 0:
            max_price = None
        if max_price is not None and max_price > MAX_PRICE:
            max_price = MAX_PRICE

        recommendations = []

        if wine_id:
            similar = self.get_similar_wines(wine_id, limit=limit)
            for wine in similar:
                recommendations.append(
                    {
                        "wine": wine,
                        "score": round(0.85 + random.uniform(0, 0.14), 2),
                        "reason": "Similar wine",
                    }
                )

        wines = self.get_recommendations_by_preference(
            region=region,
            variety=variety,
            min_rating=min_rating,
            max_price=max_price,
            limit=limit,
        )

        existing_ids = {r["wine"].id for r in recommendations}
        for wine in wines:
            if wine.id not in existing_ids:
                score = self._calculate_recommendation_score(
                    wine, region, variety, min_rating, max_price
                )
                recommendations.append(
                    {
                        "wine": wine,
                        "score": score,
                        "reason": self._get_recommendation_reason(
                            wine, region, variety
                        ),
                    }
                )

        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:limit]

    def _calculate_recommendation_score(
        self,
        wine: Wine,
        region: Optional[str],
        variety: Optional[str],
        min_rating: Optional[float],
        max_price: Optional[float],
    ) -> float:
        score = 0.5

        if wine.rating:
            score += (wine.rating / 10.0) * 0.3

        if region and wine.region and region.lower() in wine.region.lower():
            score += 0.15
        if variety and wine.variety and variety.lower() in wine.variety.lower():
            score += 0.15

        if max_price and wine.price:
            if wine.price <= max_price:
                score += 0.1

        return round(min(score, 0.99), 2)

    def _get_recommendation_reason(
        self, wine: Wine, region: Optional[str], variety: Optional[str]
    ) -> str:
        if wine.rating and wine.rating >= 4.5:
            return "Highly rated"
        if variety and wine.variety and variety.lower() in wine.variety.lower():
            return f"Similar {wine.variety}"
        if region and wine.region and region.lower() in wine.region.lower():
            return f"From {wine.region}"
        return "Popular choice"

    def _get_popular_wines(self, limit: int) -> List[Wine]:
        limit = max(1, min(limit, MAX_LIMIT))
        return self.db.query(Wine).order_by(Wine.rating.desc()).limit(limit).all()


class PriceTrackingService:
    def __init__(self, db: Session):
        self.db = db

    def get_price_history(self, wine_id: int) -> dict:
        if wine_id < 1:
            return {
                "wine_id": wine_id,
                "current_price": None,
                "price_history": [],
                "price_change_percent": None,
                "lowest_price": None,
                "highest_price": None,
            }

        prices = (
            self.db.query(WinePriceHistory)
            .filter(WinePriceHistory.wine_id == wine_id)
            .order_by(WinePriceHistory.recorded_at.desc())
            .all()
        )

        if not prices:
            return {
                "wine_id": wine_id,
                "current_price": None,
                "price_history": [],
                "price_change_percent": None,
                "lowest_price": None,
                "highest_price": None,
            }

        price_values = [p.price for p in prices]
        current_price = prices[0].price if prices else None
        oldest_price = prices[-1].price if len(prices) > 1 else current_price

        price_change = None
        if oldest_price and oldest_price > 0:
            price_change = ((current_price - oldest_price) / oldest_price) * 100

        return {
            "wine_id": wine_id,
            "current_price": current_price,
            "price_history": prices,
            "price_change_percent": round(price_change, 2) if price_change else None,
            "lowest_price": min(price_values),
            "highest_price": max(price_values),
        }

    def record_price(
        self,
        wine_id: int,
        price: float,
        retailer: Optional[str] = None,
        url: Optional[str] = None,
        currency: str = "USD",
    ) -> WinePriceHistory:
        if wine_id < 1:
            raise ValueError("Invalid wine ID")
        if price < 0 or price > MAX_PRICE:
            raise ValueError(f"Price must be between 0 and {MAX_PRICE}")

        price_record = WinePriceHistory(
            wine_id=wine_id,
            price=round(price, 2),
            retailer=retailer[:255] if retailer else None,
            url=url[:500] if url else None,
            currency=currency.upper() if currency else "USD",
        )
        self.db.add(price_record)
        self.db.commit()
        self.db.refresh(price_record)
        return price_record
