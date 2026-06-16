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

        before_summary = get_account_summary(self.api_client, self.account_number)
        before_holding = get_symbol_holding(before_summary, SYMBOL)
        logger.info(
            "Holdings before orders for %s: quantity=%s",
            SYMBOL,
            before_holding.get("quantity", 0),
        )

        def floor_to_tick(price: int, tick: int = 500) -> int:
            return (price // tick) * tick

        def ceil_to_tick(price: int, tick: int = 500) -> int:
            return ((price + tick - 1) // tick) * tick

        buy_price = floor_to_tick(max(1, current_price - ORDER_PRICE_OFFSET))
        sell_price = ceil_to_tick(current_price + ORDER_PRICE_OFFSET)

        buy_response = place_buy_order(self.api_client, self.account_number, buy_price)
        logger.info("Buy order submitted: %s", buy_response)

        logger.info("Waiting 10 seconds after buy order before checking holdings.")
        time.sleep(10)

        after_buy_summary = get_account_summary(self.api_client, self.account_number)
        after_buy_holding = get_symbol_holding(after_buy_summary, SYMBOL)
        after_buy_qty = after_buy_holding.get("quantity", 0)

        logger.info(
            "Holdings after buy order for %s: quantity=%s",
            SYMBOL,
            after_buy_qty,
        )

        if after_buy_qty > 0:
            sell_response = place_sell_order(self.api_client, self.account_number, sell_price)
            logger.info("Sell order submitted: %s", sell_response)
        else:
            logger.info("Sell order skipped because buy order has not been reflected in holdings yet.")

        self._confirm_post_order(before_holding)

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
