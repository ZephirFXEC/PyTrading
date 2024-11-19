import pandas as pd

import Config


class Strategy:
    def __init__(self, config: Config):
        self.config: Config = config
        self.trades = []  # To store individual trade details




    def mean_reversion(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Implement a mean reversion strategy.
        """
        # Calculate rolling mean and standard deviation
        df['mean'] = df['close'].rolling(window=self.config.WINDOW_SIZE).mean()
        df['std'] = df['close'].rolling(window=self.config.WINDOW_SIZE).std()
        df['z_score'] = (df['close'] - df['mean']) / df['std']

        # Initialize signal column if not present
        if 'signal' not in df.columns:
            df['signal'] = 0

        # Generate trading signals
        df.loc[df['z_score'] > 1, 'signal'] = -1  # Sell signal
        df.loc[df['z_score'] < -1, 'signal'] = 1  # Buy signal

        return df




    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Execute the strategy and calculate performance metrics.
        """
        df: pd.DataFrame = self.mean_reversion(df)
        df: pd.DataFrame = self._simulate_trades(df)
        df: pd.DataFrame = self._calculate_performance(df)
        return df

    def _simulate_trades(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Simulate trades based on signals and track performance.
        """
        # Initialize position and other columns
        df['position']: int = 0  # 1 for long, -1 for short, 0 for neutral
        df['entry_price']: float = 0.0
        df['exit_price']: float = 0.0
        df['trade_return']: float = 0.0
        df['cumulative_return']: float = 0.0

        position: int = 0  # Current position
        entry_price: float = 0.0
        cumulative_return: float = 0.0

        for idx, row in df.iterrows():
            signal = row['signal']

            if signal == 1 and position == 0:
                # Enter long position
                position = 1
                entry_price = row['close']
                df.at[idx, 'position'] = position
                df.at[idx, 'entry_price'] = entry_price
                print(f"Entered LONG at {entry_price} on {idx}")

            elif signal == -1 and position == 1:
                # Exit long position
                position = 0
                exit_price = row['close']
                trade_return = (exit_price - entry_price) / entry_price * 100  # Percentage
                cumulative_return += trade_return
                df.at[idx, 'position'] = position
                df.at[idx, 'exit_price'] = exit_price
                df.at[idx, 'trade_return'] = trade_return
                df.at[idx, 'cumulative_return'] = cumulative_return
                self.trades.append({
                    'entry_time': entry_price,
                    'exit_time': exit_price,
                    'return_pct': trade_return
                })
                print(f"Exited LONG at {exit_price} on {idx} with return {trade_return:.2f}%")

            elif signal == -1 and position == 0:
                # Enter short position (if implementing short selling)
                position = -1
                entry_price = row['close']
                df.at[idx, 'position'] = position
                df.at[idx, 'entry_price'] = entry_price
                print(f"Entered SHORT at {entry_price} on {idx}")

            elif signal == 1 and position == -1:
                # Exit short position
                position = 0
                exit_price = row['close']
                trade_return = (entry_price - exit_price) / entry_price * 100  # Percentage
                cumulative_return += trade_return
                df.at[idx, 'position'] = position
                df.at[idx, 'exit_price'] = exit_price
                df.at[idx, 'trade_return'] = trade_return
                df.at[idx, 'cumulative_return'] = cumulative_return
                self.trades.append({
                    'entry_time': entry_price,
                    'exit_time': exit_price,
                    'return_pct': trade_return
                })
                print(f"Exited SHORT at {exit_price} on {idx} with return {trade_return:.2f}%")

            else:
                # Hold position
                df.at[idx, 'position'] = position
                df.at[idx, 'cumulative_return'] = cumulative_return

        return df

    def _calculate_performance(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate performance metrics based on simulated trades.
        """
        total_trades = len(self.trades)
        winning_trades = len([trade for trade in self.trades if trade['return_pct'] > 0])
        losing_trades = len([trade for trade in self.trades if trade['return_pct'] <= 0])
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0

        total_return = sum([trade['return_pct'] for trade in self.trades])
        average_return = (total_return / total_trades) if total_trades > 0 else 0

        gross_profit = sum([trade['return_pct'] for trade in self.trades if trade['return_pct'] > 0])
        gross_loss = abs(sum([trade['return_pct'] for trade in self.trades if trade['return_pct'] <= 0]))
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float('inf')

        # Maximum Drawdown
        df['cumulative_return_plot'] = df['cumulative_return'].cumsum()
        cumulative_max = df['cumulative_return_plot'].cummax()
        drawdown = df['cumulative_return_plot'] - cumulative_max
        max_drawdown = drawdown.min()

        # Print performance metrics
        print("\n--- Strategy Performance Metrics ---")
        print(f"Total Trades: {total_trades}")
        print(f"Winning Trades: {winning_trades}")
        print(f"Losing Trades: {losing_trades}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Total Return: {total_return:.2f}%")
        print(f"Average Return per Trade: {average_return:.2f}%")
        print(f"Profit Factor: {profit_factor:.2f}")
        print(f"Maximum Drawdown: {max_drawdown:.2f}%")
        print("------------------------------------\n")

        return df

    def export_trades(self, filepath: str):
        """
        Export trade details to a CSV file.

        :param filepath: Path to the output CSV file.
        """
        trades_df = pd.DataFrame(self.trades)
        trades_df.to_csv(filepath, index=False)
        print(f"Trades exported to {filepath}")
