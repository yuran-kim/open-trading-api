from typing import Any, Dict, Optional

from api_client import ApiClient
from config import (
    ACCOUNT_PRODUCT_CODE,
    ORDER_DVSN,
    ORDER_ENDPOINT,
    ORD_DVSN,
    ORD_TYPE,
    ORDER_QUANTITY,
    SIDE_BUY,
    SIDE_SELL,
    SYMBOL,
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
        "CANO": account_number,
        "ACNT_PRDT_CD": ACCOUNT_PRODUCT_CODE,
        "PDNO": SYMBOL,
        "ORD_DVSN": ORD_DVSN,
        "ORD_TP": side,
        "ORD_PRC": str(price),
        "ORD_QTY": str(quantity),
        "ORD_UNPR_DVSN": ORD_TYPE,
        "BNS_ADJ_ORDTPS_PRSN_CD": ORDER_DVSN,
    }

    order_type = "BUY" if side == SIDE_BUY else "SELL"
    logger.info(
        "Submitting %s order: symbol=%s price=%s quantity=%s",
        order_type,
        SYMBOL,
        price,
        quantity,
    )
    response = api_client.post(ORDER_ENDPOINT, json_data=order_payload)
    logger.info("Order response: %s", response)
    return response


def place_buy_order(api_client: ApiClient, account_number: str, price: int) -> Dict[str, Any]:
    return place_order(api_client, account_number, SIDE_BUY, price)


def place_sell_order(api_client: ApiClient, account_number: str, price: int) -> Dict[str, Any]:
    return place_order(api_client, account_number, SIDE_SELL, price)
