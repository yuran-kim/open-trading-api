import time
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional

KST = ZoneInfo("Asia/Seoul")

from account import get_account_summary, get_symbol_holding
from config import (
    ORDER_PRICE_OFFSET,
    POLL_INTERVAL_SECONDS,
    SYMBOL,
    TRADING_WINDOW_END,
    TRADING_WINDOW_START,
)
from logger import get_logger
from market_data import get_current_price
from orders import place_buy_order, place_sell_order
from api_client import ApiClient

logger = get_logger(__name__)


class TradingSession:
    def __init__(self, api_client: ApiClient, account_number: str) -> None:
        self.api_client = api_client
        self.account_number = account_number
        self.reference_price: Optional[int] = None
        self.initial_buy_done = False

    def is_trading_window(self) -> bool:
        now = datetime.now(KST).time()
        return TRADING_WINDOW_START <= now <= TRADING_WINDOW_END

    def run(self) -> None:
        logger.info("Trading session started")
        while True:
            current_time = datetime.now(KST)
            if current_time.time() > TRADING_WINDOW_END:
                logger.info("Trading window has closed at %s. Stopping trading loop.", TRADING_WINDOW_END)
                break

            if not self.is_trading_window():
                logger.info("Not in trading window. Waiting until %s", TRADING_WINDOW_START)
                self._wait_until(TRADING_WINDOW_START)
                continue

            self.execute_cycle()
            logger.info("Cycle complete. Sleeping for %s seconds to preserve mock trading quota.", POLL_INTERVAL_SECONDS)
            time.sleep(POLL_INTERVAL_SECONDS)

    def execute_cycle(self) -> None:
        current_price = get_current_price(self.api_client)
        if current_price is None:
            logger.error("Could not read current market price; skipping cycle")
            return

        summary = get_account_summary(self.api_client, self.account_number)
        holding = get_symbol_holding(summary, SYMBOL)
        current_qty = holding.get("quantity", 0)

        logger.info(
            "Current state for %s: price=%s, quantity=%s, reference_price=%s",
            SYMBOL,
            current_price,
            current_qty,
            self.reference_price,
        )

    # 1. 최초 실행 시 시장가 1주 매수
    if not self.initial_buy_done:
        logger.info("Initial buy has not been done yet. Placing initial MARKET buy order.")
        buy_response = place_buy_order(self.api_client, self.account_number, current_price)
        logger.info("Initial buy order submitted: %s", buy_response)

        self.initial_buy_done = True
        self.reference_price = current_price

        logger.info(
            "Reference price set to %s after initial buy order.",
            self.reference_price,
        )
        return

    # reference_price가 없으면 현재가로 초기화
    if self.reference_price is None:
        self.reference_price = current_price
        logger.info("Reference price initialized to %s", self.reference_price)
        return

    upper_trigger = self.reference_price + ORDER_PRICE_OFFSET
    lower_trigger = self.reference_price - ORDER_PRICE_OFFSET

    logger.info(
        "Trigger prices: buy if price <= %s, sell if price >= %s",
        lower_trigger,
        upper_trigger,
    )

    # 2. 기준가격보다 1000원 이상 상승하면 시장가 매도
    if current_price >= upper_trigger:
        if current_qty > 0:
            logger.info(
                "Current price %s >= upper trigger %s. Placing MARKET sell order.",
                current_price,
                upper_trigger,
            )
            sell_response = place_sell_order(self.api_client, self.account_number, current_price)
            logger.info("Sell order submitted: %s", sell_response)

            self.reference_price = current_price
            logger.info("Reference price updated to %s after sell.", self.reference_price)
        else:
            logger.info("Sell signal detected, but no holdings are available. Skipping sell order.")
        return

    # 3. 기준가격보다 1000원 이상 하락하면 시장가 추가 매수
    if current_price <= lower_trigger:
        logger.info(
            "Current price %s <= lower trigger %s. Placing MARKET buy order.",
            current_price,
            lower_trigger,
        )
        buy_response = place_buy_order(self.api_client, self.account_number, current_price)
        logger.info("Buy order submitted: %s", buy_response)

        self.reference_price = current_price
        logger.info("Reference price updated to %s after buy.", self.reference_price)
        return

    logger.info(
        "No trade signal. Current price %s is between %s and %s.",
        current_price,
        lower_trigger,
        upper_trigger,
    )

    def _confirm_post_order(self, before_holding: dict) -> None:
        time.sleep(5)
        after_summary = get_account_summary(self.api_client, self.account_number)
        after_holding = get_symbol_holding(after_summary, SYMBOL)

        before_qty = before_holding.get("quantity", 0)
        after_qty = after_holding.get("quantity", 0)

        logger.info(
            "Post-cycle holdings for %s: quantity=%s.",
            SYMBOL,
            after_qty,
        )

    def _wait_until(self, target_time) -> None:
        now = datetime.now(KST)
        tomorrow = now
        if now.time() > target_time:
            logger.info("Trading window has passed for today")
            return

        target = datetime.combine(now.date(), target_time)
        seconds = (target - now).total_seconds()
        if seconds > 0:
            logger.info("Waiting %s seconds until trading window opens at %s", int(seconds), target_time)
            time.sleep(seconds)
