import re
import logging
from typing import Optional, Any
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

MAX_STRING_LENGTH = 500
MAX_TEXT_LENGTH = 5000
MIN_PRICE = 0.0
MAX_PRICE = 100000.0
MIN_RATING = 0.0
MAX_RATING = 5.0
MIN_QUANTITY = 1
MAX_QUANTITY = 10000
MAX_LIMIT = 100
MAX_OFFSET = 10000


class ValidationError(Exception):
    pass


def sanitize_string(
    value: Optional[str], max_length: int = MAX_STRING_LENGTH
) -> Optional[str]:
    if value is None:
        return None
    value = value.strip()
    value = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]", "", value)
    return value[:max_length]


def sanitize_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = value.strip()
    value = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]", "", value)
    return value[:MAX_TEXT_LENGTH]


def validate_price(price: float) -> float:
    if price < MIN_PRICE:
        raise ValidationError(f"Price must be at least {MIN_PRICE}")
    if price > MAX_PRICE:
        raise ValidationError(f"Price cannot exceed {MAX_PRICE}")
    return round(price, 2)


def validate_rating(rating: Optional[float]) -> Optional[float]:
    if rating is None:
        return None
    if rating < MIN_RATING or rating > MAX_RATING:
        raise ValidationError(f"Rating must be between {MIN_RATING} and {MAX_RATING}")
    return round(rating, 1)


def validate_limit(limit: int) -> int:
    if limit < 1:
        return 1
    if limit > MAX_LIMIT:
        return MAX_LIMIT
    return limit


def validate_offset(offset: int) -> int:
    if offset < 0:
        return 0
    if offset > MAX_OFFSET:
        return MAX_OFFSET
    return offset


def validate_quantity(quantity: int) -> int:
    if quantity < MIN_QUANTITY:
        raise ValidationError(f"Quantity must be at least {MIN_QUANTITY}")
    if quantity > MAX_QUANTITY:
        raise ValidationError(f"Quantity cannot exceed {MAX_QUANTITY}")
    return quantity


def validate_id(value: int, field_name: str = "ID") -> int:
    if value is None or value < 1:
        raise ValidationError(f"Invalid {field_name}")
    return value


def validate_currency(currency: str) -> str:
    valid_currencies = ["USD", "EUR", "GBP", "AUD", "CAD", "JPY", "CHF"]
    currency = currency.upper()
    if currency not in valid_currencies:
        raise ValidationError(f"Currency must be one of: {', '.join(valid_currencies)}")
    return currency


def validate_email(email: str) -> str:
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        raise ValidationError("Invalid email format")
    return email.lower()


def validate_url(url: Optional[str]) -> Optional[str]:
    if url is None:
        return None
    url = url.strip()
    url_pattern = r"^https?:\/\/[\w\-]+(\.[\w\-]+)+[/#?]?.*$"
    if not re.match(url_pattern, url, re.IGNORECASE):
        raise ValidationError("Invalid URL format")
    return url[:MAX_STRING_LENGTH]


def log_security_event(
    event_type: str,
    user_id: Optional[int],
    details: dict[str, Any],
    ip_address: Optional[str] = None,
):
    event_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "user_id": user_id,
        "ip_address": ip_address,
        "details": details,
    }
    logger.warning(f"Security event: {event_data}")


def check_resource_ownership(
    db: Session,
    resource_user_id: int,
    current_user_id: int,
    resource_type: str,
) -> bool:
    if resource_user_id != current_user_id:
        log_security_event(
            event_type="UNAUTHORIZED_ACCESS_ATTEMPT",
            user_id=current_user_id,
            details={
                "resource_type": resource_type,
                "resource_owner_id": resource_user_id,
                "attempted_by": current_user_id,
            },
        )
        return False
    return True


def validate_api_key_ownership(
    db: Session,
    api_key_id: int,
    user_id: int,
) -> bool:
    from app.models import APIKey

    api_key = db.query(APIKey).filter(APIKey.id == api_key_id).first()
    if not api_key or api_key.user_id != user_id:
        log_security_event(
            event_type="API_KEY_MISMATCH",
            user_id=user_id,
            details={"api_key_id": api_key_id},
        )
        return False
    return True


def validate_pagination(page: int, limit: int) -> tuple[int, int]:
    if page < 1:
        page = 1
    if limit < 1:
        limit = 10
    if limit > MAX_LIMIT:
        limit = MAX_LIMIT
    return page, limit


def sanitize_marketplace_listing_params(
    description: Optional[str],
    condition: Optional[str],
) -> tuple[Optional[str], Optional[str]]:
    return sanitize_text(description), sanitize_string(condition, max_length=50)


def validate_marketplace_transaction(
    listing_quantity: int,
    requested_quantity: int,
    buyer_id: int,
    seller_id: int,
) -> None:
    if buyer_id == seller_id:
        log_security_event(
            event_type="SELF_PURCHASE_ATTEMPT",
            user_id=buyer_id,
            details={"listing_quantity": listing_quantity},
        )
        raise HTTPException(status_code=400, detail="Cannot purchase your own listing")

    if requested_quantity > listing_quantity:
        raise HTTPException(
            status_code=400, detail="Requested quantity exceeds available stock"
        )


def create_error_response(status_code: int, detail: str):
    return HTTPException(status_code=status_code, detail=detail)


def validate_sort_field(
    sort_field: Optional[str], allowed_fields: list[str]
) -> Optional[str]:
    if not sort_field:
        return None
    field = sort_field.lstrip("-")
    if field not in allowed_fields:
        return None
    return sort_field
