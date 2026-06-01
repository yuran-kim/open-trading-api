import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

import requests

from config import (
    API_BASE_URL,
    APPSECRET_ENV,
    APPKEY_ENV,
    AUTH_TOKEN_PATH,
    ENV_ACCOUNT_NUMBER,
    REQUEST_TIMEOUT_SECONDS,
    RETRY_BACKOFF_SECONDS,
    RETRY_MAX,
    TOKEN_CACHE_FILE,
)
from logger import get_logger

logger = get_logger(__name__)


def load_credentials() -> Dict[str, str]:
    account = os.getenv(ENV_ACCOUNT_NUMBER)
    appkey = os.getenv(APPKEY_ENV)
    appsecret = os.getenv(APPSECRET_ENV)

    missing = [name for name, value in ((ENV_ACCOUNT_NUMBER, account), (APPKEY_ENV, appkey), (APPSECRET_ENV, appsecret)) if not value]
    if missing:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

    return {"account": account, "appkey": appkey, "appsecret": appsecret}


def load_token_cache() -> Dict[str, Any]:
    cache_path = Path(TOKEN_CACHE_FILE)
    if not cache_path.exists():
        return {}
    try:
        with cache_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Could not read token cache, refreshing token: %s", exc)
        return {}


def save_token_cache(cache: Dict[str, Any]) -> None:
    cache_path = Path(TOKEN_CACHE_FILE)
    try:
        with cache_path.open("w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
    except OSError as exc:
        logger.error("Failed to write token cache: %s", exc)


def is_token_valid(cache: Dict[str, Any]) -> bool:
    token = cache.get("token")
    expires_at = cache.get("expires_at")
    cache_date = cache.get("date")
    if not token or not expires_at or not cache_date:
        return False

    if cache_date != datetime.now().date().isoformat():
        return False

    try:
        expiry = datetime.fromisoformat(expires_at)
    except ValueError:
        return False

    return expiry > datetime.now()


def request_token(appkey: str, appsecret: str) -> Dict[str, Any]:
    url = f"{API_BASE_URL}{AUTH_TOKEN_PATH}"
    logger.info("Requesting new token from %s", url)
    payload = {
        "grant_type": "client_credentials",
        "appkey": appkey,
        "appsecret": appsecret,
    }
    headers = {"content-type": "application/json"}

    last_exception = None
    for attempt in range(1, RETRY_MAX + 1):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
            response.raise_for_status()
            result = response.json()
            if "access_token" not in result:
                raise ValueError("Token response did not include access_token")
            return result
        except Exception as exc:
            last_exception = exc
            logger.warning("Token request failed (attempt %d/%d): %s", attempt, RETRY_MAX, exc)
            if attempt < RETRY_MAX:
                sleep_time = RETRY_BACKOFF_SECONDS * attempt
                logger.info("Retrying token request after %.1f seconds", sleep_time)
                time.sleep(sleep_time)
    raise RuntimeError(f"Authentication request failed after {RETRY_MAX} attempts") from last_exception


def authenticate() -> str:
    credentials = load_credentials()
    cache = load_token_cache()
    if is_token_valid(cache):
        logger.info("Reusing cached token for the same day")
        return cache["token"]

    token_result = request_token(credentials["appkey"], credentials["appsecret"])
    access_token = token_result["access_token"]
    expires_in = int(token_result.get("expires_in", 3600))
    expires_at = datetime.now() + timedelta(seconds=expires_in - 30)

    cache = {
        "token": access_token,
        "expires_at": expires_at.isoformat(),
        "date": datetime.now().date().isoformat(),
    }
    save_token_cache(cache)
    logger.info("Saved refreshed token for the day")
    return access_token
