import os

from binance import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    BINANCE_API_KEY: str = os.getenv("BINANCE_API_KEY")
    BINANCE_API_SECRET: str = os.getenv("BINANCE_API_SECRET")
    SYMBOL: str = 'DOGEUSDC'
    INTERVAL: str = Client.KLINE_INTERVAL_1MINUTE  # Adjust to 1MINUTE for higher frequency
    START_DATE: str = '15 Nov 2024'
    END_DATE: str = '19 Nov 2024'
    WINDOW_SIZE: int = 100 # Example value
