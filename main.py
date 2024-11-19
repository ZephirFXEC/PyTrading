import logging

from Config import Config
from DataFetcher import DataFetcher
from Plotter import Plotter
from Strategy import Strategy


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def main():
    setup_logging()
    config = Config()

    # Initialize components
    fetcher = DataFetcher(config)

    strategy = Strategy(config)

    plotter = Plotter(config, fetcher, strategy)

    plotter.start()

    # try:
    #     # Fetch historical data
    #     logging.info("Fetching historical data...")
    #     historical_df = fetcher.get_historical_data()
    #     logging.info("Historical data fetched successfully.")
    #
    #     # Initialize live data with historical data
    #     with fetcher.lock:
    #         fetcher.live_data = historical_df.copy()
    #
    #     # Execute strategy on historical data
    #     logging.info("Executing strategy on historical data...")
    #     historical_df = strategy.execute(historical_df)
    #     logging.info("Strategy executed on historical data.")
    #
    #     # Start WebSocket for real-time data
    #     fetcher.start_websocket(fetcher.update_live_data)
    #
    #     # Start Plotter in the main thread
    #     plotter_thread = threading.Thread(target=plotter.start, daemon=True)
    #     plotter_thread.start()
    #
    #     logging.info("Starting real-time strategy execution. Press Ctrl+C to stop.")
    #
    #     # Continuously monitor and execute strategy on live data
    #     while True:
    #         time.sleep(60)  # Wait for the next kline (adjust based on interval)
    #         live_df = fetcher.get_live_data()
    #         if not live_df.empty:
    #             # Execute strategy on the latest data
    #             strategy_result = strategy.execute(live_df)
    #             latest_signal = strategy_result.iloc[-1]['signal']
    #             logging.info(f"Latest signal: {latest_signal} at {strategy_result.index[-1]}")
    #
    # except KeyboardInterrupt:
    #     logging.info("Interrupted by user. Shutting down...")
    # except Exception as e:
    #     logging.error(f"An error occurred: {e}")
    # finally:
    #     fetcher.stop_websocket()
    #     logging.info("Application terminated.")


if __name__ == "__main__":
    main()
