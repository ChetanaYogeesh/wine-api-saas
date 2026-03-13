import os
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException, Request, Depends
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import Optional
import pandas as pd

from app.data import get_data
from app.models import Wine, WineListResponse, WineStats

load_dotenv()

API_KEY = os.getenv("API_KEY", "dev-api-key-change-me")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app = FastAPI(title="Wine API", version="0.1.0")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

security_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(request: Request, api_key: str = Depends(security_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return {"detail": "Rate limit exceeded. Please try again later."}


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to Wine API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/wines", response_model=WineListResponse)
@limiter.limit("60/minute")
async def list_wines(
    request: Request,
    api_key: str = Depends(verify_api_key),
    region: Optional[str] = None,
    variety: Optional[str] = None,
    min_rating: Optional[float] = None,
    max_rating: Optional[float] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    df = get_data()

    if region:
        df = df[df["region"].str.contains(region, case=False, na=False)]
    if variety:
        df = df[df["variety"].str.contains(variety, case=False, na=False)]
    if min_rating is not None:
        df = df[df["rating"] >= min_rating]
    if max_rating is not None:
        df = df[df["rating"] <= max_rating]

    total = len(df)
    start = (page - 1) * limit
    end = start + limit
    page_df = df.iloc[start:end]

    wines = [
        Wine(
            id=int(idx),
            name=row["name"],
            region=row["region"],
            variety=row["variety"],
            rating=row["rating"],
            notes=row["notes"],
        )
        for idx, row in page_df.iterrows()
    ]

    return WineListResponse(wines=wines, total=total, page=page, limit=limit)


@app.get("/wines/stats", response_model=WineStats)
@limiter.limit("60/minute")
async def wine_stats(request: Request, api_key: str = Depends(verify_api_key)):
    df = get_data()
    df_rated = df.dropna(subset=["rating"])

    total = len(df_rated)
    avg_rating = df_rated["rating"].mean()

    top_region = (
        df_rated["region"].value_counts().idxmax()
        if not df_rated["region"].isna().all()
        else "N/A"
    )

    bins = [0, 85, 90, 95, 100]
    labels = ["0-85", "85-89", "90-94", "95+"]
    df_rated = df_rated.copy()
    df_rated["rating_bin"] = pd.cut(
        df_rated["rating"], bins=bins, labels=labels, right=False
    )
    distribution = df_rated["rating_bin"].value_counts().to_dict()

    return WineStats(
        total_wines=total,
        avg_rating=round(avg_rating, 2),
        top_region=top_region,
        rating_distribution=distribution,
    )


@app.get("/wines/search", response_model=WineListResponse)
@limiter.limit("60/minute")
async def search_wines(
    request: Request,
    api_key: str = Depends(verify_api_key),
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    df = get_data()
    mask = df["name"].str.contains(q, case=False, na=False) | df["notes"].str.contains(
        q, case=False, na=False
    )
    df = df[mask]

    total = len(df)
    start = (page - 1) * limit
    end = start + limit
    page_df = df.iloc[start:end]

    wines = [
        Wine(
            id=int(idx),
            name=row["name"],
            region=row["region"],
            variety=row["variety"],
            rating=row["rating"],
            notes=row["notes"],
        )
        for idx, row in page_df.iterrows()
    ]

    return WineListResponse(wines=wines, total=total, page=page, limit=limit)


@app.get("/wines/top-rated", response_model=WineListResponse)
@limiter.limit("60/minute")
async def top_rated_wines(
    request: Request,
    api_key: str = Depends(verify_api_key),
    limit: int = Query(10, ge=1, le=100),
    region: Optional[str] = None,
):
    df = get_data()
    df = df.dropna(subset=["rating"])
    df = df.sort_values("rating", ascending=False)

    if region:
        df = df[df["region"].str.contains(region, case=False, na=False)]

    top_df = df.head(limit)

    wines = [
        Wine(
            id=int(idx),
            name=row["name"],
            region=row["region"],
            variety=row["variety"],
            rating=row["rating"],
            notes=row["notes"],
        )
        for idx, row in top_df.iterrows()
    ]

    return WineListResponse(wines=wines, total=len(wines), page=1, limit=limit)


@app.get("/wines/{wine_id}", response_model=Wine)
@limiter.limit("60/minute")
async def get_wine(
    request: Request, api_key: str = Depends(verify_api_key), wine_id: int = None
):
    df = get_data()
    if wine_id not in df.index:
        raise HTTPException(status_code=404, detail="Wine not found")
    row = df.loc[wine_id]
    return Wine(
        id=wine_id,
        name=row["name"],
        region=row["region"],
        variety=row["variety"],
        rating=row["rating"],
        notes=row["notes"],
    )


@app.get("/regions")
@limiter.limit("60/minute")
async def list_regions(request: Request, api_key: str = Depends(verify_api_key)):
    df = get_data()
    regions = df["region"].dropna().unique().tolist()
    return {"regions": sorted([r for r in regions if r])}


@app.get("/regions/{region}/wines", response_model=WineListResponse)
@limiter.limit("60/minute")
async def get_wines_by_region(
    request: Request,
    api_key: str = Depends(verify_api_key),
    region: str = None,
    variety: Optional[str] = None,
    min_rating: Optional[float] = None,
    max_rating: Optional[float] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    df = get_data()
    df = df[df["region"].str.contains(region, case=False, na=False)]

    if variety:
        df = df[df["variety"].str.contains(variety, case=False, na=False)]
    if min_rating is not None:
        df = df[df["rating"] >= min_rating]
    if max_rating is not None:
        df = df[df["rating"] <= max_rating]

    total = len(df)
    start = (page - 1) * limit
    end = start + limit
    page_df = df.iloc[start:end]

    wines = [
        Wine(
            id=int(idx),
            name=row["name"],
            region=row["region"],
            variety=row["variety"],
            rating=row["rating"],
            notes=row["notes"],
        )
        for idx, row in page_df.iterrows()
    ]

    return WineListResponse(wines=wines, total=total, page=page, limit=limit)


@app.get("/varieties")
@limiter.limit("60/minute")
async def list_varieties(request: Request, api_key: str = Depends(verify_api_key)):
    df = get_data()
    varieties = df["variety"].dropna().unique().tolist()
    return {"varieties": sorted([v for v in varieties if v])}
