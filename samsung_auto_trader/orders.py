from typing import Any, Dict, Optional

from api_client import ApiClient
from config import (
    ACCOUNT_PRODUCT_CODE,
    DRY_RUN,
    ORDER_DVSN,
    ORDER_ENDPOINT,
    ORD_DVSN,
    ORD_TYPE,
    ORDER_QUANTITY,
    SIDE_BUY,
    SIDE_SELL,
    SYMBOL,
    TR_ID_BUY,
    TR_ID_SELL,
)
from logger import get_logger

logger = get_logger(__name__)


def place_order(
    api_client: ApiClient,
    account_number: str,
    side: str,
    price: int,
    quantity: int = ORDER_QUANTITY,
) -> Dict[str, Any]:
    order_payload: Dict[str, Any] = {
        "CANO": account_number[:8],
        "ACNT_PRDT_CD": account_number[8:] if len(account_number) > 8 else ACCOUNT_PRODUCT_CODE,
        "PDNO": SYMBOL,
        "ORD_DVSN": "01",
        "ORD_QTY": str(quantity),
        "ORD_UNPR": "0",
    }

    order_type = "BUY" if side == SIDE_BUY else "SELL"
    logger.info(
        "Preparing %s MARKET order: symbol=%s reference_price=%s quantity=%s",
        order_type,
        SYMBOL,
        price,
        quantity,
    )

    if DRY_RUN:
        logger.info("DRY_RUN enabled: skipping POST to %s", ORDER_ENDPOINT)
        mock_response = {
            "status": "DRY_RUN",
            "order_type": order_type,
            "symbol": SYMBOL,
            "price": price,
            "quantity": quantity,
            "payload": order_payload,
        }
        logger.info("Mock order response: %s", mock_response)
        return mock_response

    tr_id = TR_ID_BUY if side == SIDE_BUY else TR_ID_SELL

    response = api_client.post(
        ORDER_ENDPOINT,
        json_data=order_payload,
        headers={"tr_id": tr_id},
    )
    logger.info("Order response: %s", response)
    return response


def place_buy_order(api_client: ApiClient, account_number: str, price: int) -> Dict[str, Any]:
    return place_order(api_client, account_number, SIDE_BUY, price)


def place_sell_order(api_client: ApiClient, account_number: str, price: int) -> Dict[str, Any]:
    return place_order(api_client, account_number, SIDE_SELL, price)
