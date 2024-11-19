import logging

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.animation import FuncAnimation

import Config
import DataFetcher
import Strategy


class Plotter:
    def __init__(self, config: Config, data_fetcher: DataFetcher, strategy: Strategy):
        """
        Initialize the Plotter with configuration, data fetcher, and strategy instances.

        :param config: Configuration object
        :param data_fetcher: Instance of DataFetcher
        :param strategy: Instance of Strategy
        """
        self.config: Config = config
        self.data_fetcher: DataFetcher = data_fetcher
        self.strategy: Strategy = strategy

        # Initialize the plot
        self.fig, self.ax = plt.subplots(figsize=(14, 7))
        self.line_price, = self.ax.plot([], [], label='Close Price', color='blue')
        self.line_mean, = self.ax.plot([], [], label='Rolling Mean', color='orange')
        self.line_upper, = self.ax.plot([], [], label='Upper Band', color='green', linestyle='--')
        self.line_lower, = self.ax.plot([], [], label='Lower Band', color='red', linestyle='--')
        self.scatter_buy = self.ax.scatter([], [], marker='^', color='green', label='Buy Signal', zorder=5)
        self.scatter_sell = self.ax.scatter([], [], marker='v', color='red', label='Sell Signal', zorder=5)

        # Formatting the plot
        self.ax.set_xlabel('Date')
        self.ax.set_ylabel('Price (USDT)')
        self.ax.set_title(f"{self.config.SYMBOL} Price with Real-Time Strategy Indicators")
        self.ax.legend(loc='upper left')
        self.ax.grid(True)
        self.fig.autofmt_xdate()
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))

        # Initialize data containers for signals
        self.buy_signals_x = []
        self.buy_signals_y = []
        self.sell_signals_x = []
        self.sell_signals_y = []

    def init_plot(self):
        """
        Initialize the plot lines.
        """
        self.line_price.set_data([], [])
        self.line_mean.set_data([], [])
        self.line_upper.set_data([], [])
        self.line_lower.set_data([], [])

        # Initialize scatter plots with empty 2D arrays
        self.scatter_buy.set_offsets(np.empty((0, 2)))
        self.scatter_sell.set_offsets(np.empty((0, 2)))

        return self.line_price, self.line_mean, self.line_upper, self.line_lower, self.scatter_buy, self.scatter_sell

    def plot(self):
        """
        Update the plot with new data.

        :param frame: Frame number (required by FuncAnimation)
        """
        try:
            df: pd.DataFrame = self.data_fetcher.get_historical_data()

            if df.empty:
                return self.line_price, self.line_mean, self.line_upper, self.line_lower, self.scatter_buy, self.scatter_sell

            # Update strategy
            df: pd.DataFrame = self.strategy.execute(df)

            # Update price line
            self.line_price.set_data(df.index, df['close'])

            # Update rolling mean and bands
            self.line_mean.set_data(df.index, df['mean'])
            self.line_upper.set_data(df.index, df['mean'] + df['std'])
            self.line_lower.set_data(df.index, df['mean'] - df['std'])

            # Update signals
            buy_signals: pd.DataFrame = df[df['signal'] == 1]
            sell_signals: pd.DataFrame = df[df['signal'] == -1]

            self.buy_signals_x = buy_signals.index
            self.buy_signals_y = buy_signals['close']
            self.sell_signals_x = sell_signals.index
            self.sell_signals_y = sell_signals['close']

            self.scatter_buy.set_offsets(np.c_[mdates.date2num(self.buy_signals_x), self.buy_signals_y])
            self.scatter_sell.set_offsets(np.c_[mdates.date2num(self.sell_signals_x), self.sell_signals_y])

            # Adjust plot limits
            self.ax.relim()
            self.ax.autoscale_view()

            return self.line_price, self.line_mean, self.line_upper, self.line_lower, self.scatter_buy, self.scatter_sell

        except Exception as e:
            logging.error(f"Error updating plot: {e}")
            return self.line_price, self.line_mean, self.line_upper, self.line_lower, self.scatter_buy, self.scatter_sell

    def update_plot(self, frame):
        """
        Update the plot with new data.

        :param frame: Frame number (required by FuncAnimation)
        """
        try:
            df = self.data_fetcher.get_live_data()

            if df.empty:
                return self.line_price, self.line_mean, self.line_upper, self.line_lower, self.scatter_buy, self.scatter_sell

            # Update strategy
            df = self.strategy.execute(df)

            # Update price line
            self.line_price.set_data(df.index, df['close'])

            # Update rolling mean and bands
            self.line_mean.set_data(df.index, df['mean'])
            self.line_upper.set_data(df.index, df['mean'] + df['std'])
            self.line_lower.set_data(df.index, df['mean'] - df['std'])

            # Update signals
            buy_signals = df[df['signal'] == 1]
            sell_signals = df[df['signal'] == -1]

            self.buy_signals_x = buy_signals.index
            self.buy_signals_y = buy_signals['close']
            self.sell_signals_x = sell_signals.index
            self.sell_signals_y = sell_signals['close']

            self.scatter_buy.set_offsets(np.c_[mdates.date2num(self.buy_signals_x), self.buy_signals_y])
            self.scatter_sell.set_offsets(np.c_[mdates.date2num(self.sell_signals_x), self.sell_signals_y])

            # Adjust plot limits
            self.ax.relim()
            self.ax.autoscale_view()

            return self.line_price, self.line_mean, self.line_upper, self.line_lower, self.scatter_buy, self.scatter_sell

        except Exception as e:
            logging.error(f"Error updating plot: {e}")
            return self.line_price, self.line_mean, self.line_upper, self.line_lower, self.scatter_buy, self.scatter_sell

    def start(self, realtime: bool = False):
        """
        Start the real-time plot.
        """
        if not realtime:
            logging.info("Starting static plot...")
            self.plot()
            plt.show()
            return

        logging.info("Starting real-time plot...")
        self.ani = FuncAnimation(
            self.fig,
            self.update_plot,
            init_func=self.init_plot,
            interval=60000,  # Update every 60 seconds (60000 ms)
            blit=False,
            save_count=100  # Added to suppress the UserWarning
        )

        plt.show()
