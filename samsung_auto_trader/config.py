import logging
from datetime import time

# Mock trading base endpoint for Korea Investment & Securities Open API
API_BASE_URL = "https://openapivts.koreainvestment.com:29443"

# Environment variable names
ENV_ACCOUNT_NUMBER = "GH_ACCOUNT"
ENV_APP_KEY = "GH_APPKEY"
ENV_APP_SECRET = "GH_APPSECRET"

ACCOUNT_ENV = ENV_ACCOUNT_NUMBER
APPKEY_ENV = ENV_APP_KEY
APPSECRET_ENV = ENV_APP_SECRET

# Token cache file name in project root
TOKEN_CACHE_FILE = "token_cache.json"

# API endpoint paths (editable placeholders)
AUTH_TOKEN_PATH = "/oauth2/tokenP"
PRICE_ENDPOINT = "/uapi/domestic-stock/v1/quotations/inquire-price"
ACCOUNT_BALANCE_ENDPOINT = "/uapi/domestic-stock/v1/trading/inquire-balance"
ORDER_ENDPOINT = "/uapi/domestic-stock/v1/trading/order-cash"

# Trading target
SYMBOL = "005930"
MARKET_DIV_CODE = "J"  # Market division code for domestic stock (placeholder)
ACCOUNT_PRODUCT_CODE = "01"  # Account product code placeholder
ORDER_QUANTITY = 1
ORDER_PRICE_OFFSET = 1000

# Order side constants
SIDE_BUY = "1"  # Placeholder for buy order side
SIDE_SELL = "2"  # Placeholder for sell order side

# Order type placeholders (these field names and values may need adjustment)
ORDER_DVSN = "01"
ORD_DVSN = "01"
ORD_TYPE = "00"

# Trading window
TRADING_WINDOW_START = time(hour=9, minute=10)
TRADING_WINDOW_END = time(hour=15, minute=30)

# Polling and retry settings
POLL_INTERVAL_SECONDS = 180
REQUEST_TIMEOUT_SECONDS = 30
RETRY_MAX = 3
RETRY_BACKOFF_SECONDS = 2.0

# Logging
LOG_LEVEL = logging.INFO

# Response field names and structure placeholders
PRICE_RESPONSE_KEY = "output"
PRICE_FIELD = "stck_prpr"
BALANCE_RESPONSE_KEY = "output1"
HOLDINGS_RESPONSE_KEY = "output1"
HOLDING_SYMBOL_FIELD = "pdno"
HOLDING_QUANTITY_FIELD = "hldg_qty"
AVAILABLE_CASH_FIELD = "dnca_tot_amt"

# Notes:
# - If the Korean Investment Open API field names or response object names differ,
#   update the endpoint constants and field constants above.
# - This project is intentionally conservative with API calls to preserve the mock trading quota.

DRY_RUN = False #Set to True to enable dry-run mode (no real orders placed)
TR_ID_PRICE = "FHKST01010100"
TR_ID_BALANCE = "VTTC8434R"
TR_ID_BUY = "VTTC0802U"
TR_ID_SELL = "VTTC0801U"