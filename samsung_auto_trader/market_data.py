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


def parse_price_response(response: dict) -> int | None:
    payload = response.get(PRICE_RESPONSE_KEY)

    if not isinstance(payload, dict):
        logger.error("Unexpected price response structure: %s", response)
        return None

    raw_price = payload.get(PRICE_FIELD)
    if raw_price is None:
        logger.error("Price field %s not found in response: %s", PRICE_FIELD, response)
        return None

    try:
        return int(raw_price)
    except ValueError:
        logger.error("Could not parse price value: %s", raw_price)
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
