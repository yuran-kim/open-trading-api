from typing import Any, Dict, Optional

import time
import requests

from config import API_BASE_URL, REQUEST_TIMEOUT_SECONDS, RETRY_BACKOFF_SECONDS, RETRY_MAX
from logger import get_logger

logger = get_logger(__name__)


class ApiClient:
    def __init__(self, token: str, appkey: str, appsecret: str) -> None:
        self.token = token
        self.appkey = appkey
        self.appsecret = appsecret

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "appkey": self.appkey,
            "appsecret": self.appsecret,
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        url = f"{API_BASE_URL}{endpoint}"
        last_exception = None
        for attempt in range(1, RETRY_MAX + 1):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    timeout=REQUEST_TIMEOUT_SECONDS,
                    headers=headers,
                )
                response.raise_for_status()
                return response.json()
            except requests.RequestException as exc:
                last_exception = exc

                status_code = exc.response.status_code if exc.response is not None else None
                response_text = exc.response.text if exc.response is not None else ""

                logger.warning(
                    "API request failed: %s %s (attempt %d/%d): status=%s, response=%s",
                    method,
                    endpoint,
                    attempt,
                    RETRY_MAX,
                    status_code,
                    response_text,
                )
                if attempt < RETRY_MAX:
                    sleep_time = RETRY_BACKOFF_SECONDS * attempt
                    logger.info("Retrying API request after %.1f seconds", sleep_time)
                    time.sleep(sleep_time)
        raise RuntimeError(f"API request failed after {RETRY_MAX} attempts: {method} {endpoint}") from last_exception

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
     return self._request("GET", endpoint, params=params, headers=headers)

    def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        return self._request("POST", endpoint, json_data=json_data, headers=headers)