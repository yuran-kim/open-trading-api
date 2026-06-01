# Samsung Auto Trader

A simple mock-trading automation project for Samsung Electronics (`005930`) using the Korea Investment & Securities Open API.

This project uses REST-only requests and caches an authentication token for same-day reuse. It is designed with conservative polling to minimize mock trading API usage.

## Folder structure

- `main.py` - application entry point
- `config.py` - API endpoints, trading settings, environment variable names, and placeholders for uncertain field names
- `auth.py` - token caching and authentication logic
- `api_client.py` - low-level request wrapper with retry support
- `market_data.py` - market price lookup
- `account.py` - balance and holdings inquiry
- `orders.py` - buy/sell order submission
- `trader.py` - trading loop and execution flow
- `logger.py` - structured logging setup
- `token_cache.json` - same-day token cache file
- `requirements.txt` - minimal dependency list

## Requirements

- Python 3.8+
- `requests`

## Environment variables

The application reads credentials from environment variables only. Do not hardcode secrets.

- `GH_ACCOUNT`
- `GH_APPKEY`
- `GH_APPSECRET`

## Install

```bash
python3 -m pip install -r requirements.txt
```

## Run

```bash
export GH_ACCOUNT="your-account"
export GH_APPKEY="your-appkey"
export GH_APPSECRET="your-appsecret"
python main.py
```

## Behavior

- Checks current Samsung Electronics price
- Reads account balance and holdings once per cycle
- Submits a buy order at `current_price - 2000`
- Submits a sell order at `current_price + 2000`
- Verifies holdings after order submission
- Runs only between `09:10` and `15:30`
- Uses conservative polling to minimize mock trading calls

## Notes

- The API field names and order request parameters are intentionally isolated in `config.py`.
- Update the placeholder constants in `config.py` if the exact Korea Investment API field names or transaction identifiers differ.
