import logging
import threading
from typing import Any, Callable, List

import pandas as pd
from binance import Client, ThreadedWebsocketManager


class DataFetcher:
    def __init__(self, config: Any):
        self.client: Client = Client(config.BINANCE_API_KEY, config.BINANCE_API_SECRET)
        self.symbol: str = config.SYMBOL
        self.interval: str = config.INTERVAL
        self.start_date: str = config.START_DATE
        self.end_date: str = config.END_DATE
        self.websocket_manager: ThreadedWebsocketManager = ThreadedWebsocketManager(
            api_key=config.BINANCE_API_KEY,
            api_secret=config.BINANCE_API_SECRET
        )
        self.live_data: pd.DataFrame = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        self.lock: threading.Lock = threading.Lock()  # To ensure thread-safe operations on live_data

    def get_historical_data(self) -> pd.DataFrame:
        """
        Fetch historical data from Binance and return a DataFrame.
        """
        logging.info(f"Fetching historical data for {self.symbol} from {self.start_date} to {self.end_date}")

        data: List = self.client.get_historical_klines(
            self.symbol, self.interval, self.start_date, self.end_date
        )

        df: pd.DataFrame = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'
        ])

        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        df.set_index('timestamp', inplace=True)
        df: pd.DataFrame = df[['open', 'high', 'low', 'close', 'volume']].astype(float)

        logging.info("Historical data fetched successfully.")

        return df

    def start_websocket(self, callback: Callable[[dict], None]):
        """
        Start the WebSocket to receive real-time data.
        """
        logging.info("Starting WebSocket for real-time data...")

        self.websocket_manager.start()
        self.websocket_manager.start_kline_socket(
            callback=callback,
            symbol=self.symbol.lower(),
            interval=self.interval
        )

        logging.info("WebSocket started.")

    def stop_websocket(self):
        """
        Stop the WebSocket connection.
        """
        logging.info("Stopping WebSocket...")
        self.websocket_manager.stop()
        logging.info("WebSocket stopped.")

    def update_live_data(self, msg: dict):
        """
        Callback function to update live_data DataFrame with incoming WebSocket messages.
        """
        if msg['e'] != 'kline':
            return  # Ignore non-kline events

        k = msg['k']
        is_final = k['x']
        timestamp = pd.to_datetime(k['t'], unit='ms')

        with self.lock:
            # Update live_data only when the kline is closed
            if is_final:
                new_row = {
                    'timestamp': timestamp,
                    'open': float(k['o']),
                    'high': float(k['h']),
                    'low': float(k['l']),
                    'close': float(k['c']),
                    'volume': float(k['v'])
                }
                self.live_data = self.live_data.append(new_row, ignore_index=True)
                self.live_data.set_index('timestamp', inplace=True)
                logging.info(f"New kline added at {timestamp}")

    def get_live_data(self) -> pd.DataFrame:
        """
        Retrieve the live_data DataFrame.
        """
        with self.lock:
            return self.live_data.copy()
