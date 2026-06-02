from typing import Any, Dict, Optional

from api_client import ApiClient
from config import (
    MARKET_DIV_CODE,
    PRICE_ENDPOINT,
    PRICE_FIELD,
    PRICE_RESPONSE_KEY,
    SYMBOL,
    TR_ID_PRICE,
)
from logger import get_logger

logger = get_logger(__name__)


def parse_price_response(response: Dict[str, Any]) -> Optional[int]:
    payload = response.get(PRICE_RESPONSE_KEY)
    if not payload or not isinstance(payload, list):
        logger.error("Unexpected price response structure: %s", response)
        return None

    first_item = payload[0] if payload else {}
    price = first_item.get(PRICE_FIELD)
    if price is None:
        logger.error("Could not find price field '%s' in response", PRICE_FIELD)
        return None

    try:
        return int(price)
    except (TypeError, ValueError):
        logger.error("Price value is not numeric: %s", price)
        return None


def get_current_price(api_client: ApiClient) -> Optional[int]:
    params = {
        "fid_cond_mrkt_div_code": MARKET_DIV_CODE,
        "fid_input_iscd": SYMBOL,
    }
    logger.info("Requesting current price for %s", SYMBOL)
    response = api_client.get(
        PRICE_ENDPOINT,
        params=params,
        headers={"tr_id": TR_ID_PRICE},
    )
    current_price = parse_price_response(response)
    if current_price is not None:
        logger.info("Current price for %s is %s KRW", SYMBOL, current_price)
    return current_price
