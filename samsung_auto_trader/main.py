import os

from auth import authenticate
from api_client import ApiClient
from logger import get_logger
from trader import TradingSession
from config import ENV_ACCOUNT_NUMBER

logger = get_logger(__name__)


def main() -> None:
    try:
        token = authenticate()
        api_client = ApiClient(token)
        account_number = __import__("os").getenv(ENV_ACCOUNT_NUMBER)
        if not account_number:
            raise EnvironmentError(f"Missing environment variable {ENV_ACCOUNT_NUMBER}")

        session = TradingSession(api_client, account_number)
        session.run()
        logger.info("Trading application finished")
    except Exception as exc:
        logger.exception("Unhandled error occurred: %s", exc)


if __name__ == "__main__":
    main()
