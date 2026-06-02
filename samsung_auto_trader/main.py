import os

from auth import authenticate
from api_client import ApiClient
from logger import get_logger
from trader import TradingSession
from config import ENV_ACCOUNT_NUMBER, ENV_APP_KEY, ENV_APP_SECRET

logger = get_logger(__name__)


def main() -> None:
    try:
        token = authenticate()

        appkey = os.getenv(ENV_APP_KEY)
        appsecret = os.getenv(ENV_APP_SECRET)
        account_number = os.getenv(ENV_ACCOUNT_NUMBER)

        if not appkey:
            raise EnvironmentError(f"Missing environment variable {ENV_APP_KEY}")
        if not appsecret:
            raise EnvironmentError(f"Missing environment variable {ENV_APP_SECRET}")
        if not account_number:
            raise EnvironmentError(f"Missing environment variable {ENV_ACCOUNT_NUMBER}")

        api_client = ApiClient(token, appkey, appsecret)
        
        session = TradingSession(api_client, account_number)
        session.run()
        logger.info("Trading application finished")
    except Exception as exc:
        logger.exception("Unhandled error occurred: %s", exc)


if __name__ == "__main__":
    main()
