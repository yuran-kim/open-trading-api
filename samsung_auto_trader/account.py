from typing import Any, Dict, List, Optional

from api_client import ApiClient
from config import (
    ACCOUNT_BALANCE_ENDPOINT,
    ACCOUNT_PRODUCT_CODE,
    AVAILABLE_CASH_FIELD,
    HOLDING_QUANTITY_FIELD,
    HOLDING_SYMBOL_FIELD,
    HOLDINGS_RESPONSE_KEY,
    SYMBOL,
)
from logger import get_logger

logger = get_logger(__name__)


def parse_account_response(response: Dict[str, Any]) -> Dict[str, Any]:
    holdings = []
    available_cash = None

    balance_section = response.get("output1")
    if isinstance(balance_section, list) and balance_section:
        available_cash = balance_section[0].get(AVAILABLE_CASH_FIELD)

    holdings_section = response.get(HOLDINGS_RESPONSE_KEY)
    if isinstance(holdings_section, list):
        for item in holdings_section:
            holdings.append(
                {
                    "symbol": item.get(HOLDING_SYMBOL_FIELD),
                    "quantity": int(item.get(HOLDING_QUANTITY_FIELD, 0)),
                    "raw": item,
                }
            )

    return {
        "available_cash": int(available_cash) if available_cash is not None else 0,
        "holdings": holdings,
    }


def get_account_summary(api_client: ApiClient, account_number: str) -> Dict[str, Any]:
    params = {
        "CANO": account_number,
        "ACNT_PRDT_CD": ACCOUNT_PRODUCT_CODE,
        "INQR_DVSN": "02",
        "UNPR_DVSN": "01",
        "FNCG_AMT_ICLD_YN": "N",
    }
    logger.info("Requesting account balance and holdings")
    response = api_client.get(ACCOUNT_BALANCE_ENDPOINT, params=params)
    summary = parse_account_response(response)
    logger.info(
        "Account available cash: %s KRW, holdings count: %s",
        summary["available_cash"],
        len(summary["holdings"]),
    )
    return summary


def get_symbol_holding(summary: Dict[str, Any], symbol: str = SYMBOL) -> Dict[str, Any]:
    for holding in summary.get("holdings", []):
        if holding.get("symbol") == symbol:
            return holding
    return {"symbol": symbol, "quantity": 0}
