"""
    This script uses the Scikit-Optimize library (skopt) to optimize the buy and sell thresholds of a trading strategy
    based on the Relative Strength Index (RSI) and Moving Average Convergence Divergence (MACD) indicators. The script
    reads in a CSV file containing financial data, applies the trading strategy to generate buy and sell signals,
    and backtests the results to calculate the profit percentage. The script defines functions to populate the
    'enter_trade' and 'exit_trade' columns of the dataset, filter out data before the first buy signal and after the last
    sell signal, calculate the total profit percentage, and perform backtesting on the given dataset. Finally,
    the script uses the gp_minimize function from skopt to search for the best parameters for the trading strategy using
    a Bayesian optimization algorithm. The best parameters are used to generate the best profit and print the result.
"""
from skopt import gp_minimize
import pandas as pd
from skopt.space import Integer
from ta.trend import MACD
from ta.momentum import RSIIndicator

# Read the dataset
dataframe = pd.read_csv('datasets/SPY_DATA_20_YEARS/SPX_5min.csv')
dataframe.dropna(inplace=True)

class Backtester:
    """
        Class for backtesting a trading strategy.
    """
    def __init__(self, dataframe):
        """
            Initializes a new instance of the Backtester class.

            Args:
                dataframe (pandas.DataFrame): The dataframe to use for backtesting.
            Attributes:
                dataframe (pandas.DataFrame): The original dataframe used for backtesting.
                buy_signals (List[float]): The list of buy signals generated by the trading strategy.
                sell_signals (List[float]): The list of sell signals generated by the trading strategy.
                highest_profit (float): The highest Sharpe ratio obtained during optimization.
        """
        self.dataframe = dataframe
        self.dataframe['enter_trade'] = 0
        self.dataframe['exit_trade'] = 0
        self.buy_signals = []
        self.sell_signals = []
        self.generate_indicators()
        self.highest_profit = float('-inf')

    search_space = [
        Integer(low=5, high=50, name='rsi_buy_threshold', dtype=int),
        Integer(low=50, high=100, name='rsi_sell_threshold', dtype=int),
    ]

    def generate_indicators(self):
        """
            Generates indicators for the dataframe.
        """
        macd_indicator = MACD(self.dataframe['close'], window_slow=26, window_fast=12, window_sign=9)
        self.dataframe['MACD'] = macd_indicator.macd()
        self.dataframe['Signal'] = macd_indicator.macd_signal()

        rsi_indicator = RSIIndicator(self.dataframe['close'], window=14)
        self.dataframe['RSI'] = rsi_indicator.rsi()

    def set_entry_conditions(self, buy_rsi: int) -> pd.DataFrame:
        """
            Sets entry conditions for trades based on the MACD and RSI indicators.

            Args:
                buy_rsi (int): The minimum RSI value required to enter a long trade.
            Returns:
                pd.DataFrame: The modified dataframe with 'enter_trade' column set to 1 where the entry conditions are met.
        """
        dataframe = self.dataframe
        macd_crosses_signal = (dataframe['MACD'].shift(1) < dataframe['Signal'].shift(1)) & (
                dataframe['MACD'] > dataframe['Signal'])
        rsi_condition = dataframe['RSI'].rolling(5).min() <= buy_rsi
        dataframe.loc[macd_crosses_signal & rsi_condition, 'enter_trade'] = 1
        return dataframe

    def set_exit_conditions(self, sell_rsi: int) -> pd.DataFrame:
        """
            Sets exit conditions for trades based on the MACD and RSI indicators.

            Args:
                sell_rsi (int): The maximum RSI value required to exit a long trade.
            Returns:
                pd.DataFrame: The modified dataframe with 'exit_trade' column set to 1 where the exit conditions are met.
        """
        dataframe = self.dataframe
        macd_crosses_under_signal = (dataframe['MACD'].shift(1) > dataframe['Signal'].shift(1)) & (
                dataframe['MACD'] < dataframe['Signal'])
        rsi_condition = dataframe['RSI'].rolling(5).max() >= sell_rsi
        dataframe.loc[macd_crosses_under_signal & rsi_condition, 'exit_trade'] = 1
        return dataframe

    @staticmethod
    def remove_extra_rows(dataframe: pd.DataFrame) -> pd.DataFrame:
        """
              Removes extra rows from the dataframe that are not part of any trade.

              Args:
                  dataframe (pandas.DataFrame): The dataframe to remove extra rows from.
              Returns:
                  pd.DataFrame: The modified dataframe with extra rows removed.
        """
        enter_trade_indices = dataframe[dataframe['enter_trade'] == 1].index
        exit_trade_indices = dataframe[dataframe['exit_trade'] == 1].index

        if len(enter_trade_indices) == 0 or len(exit_trade_indices) == 0:
            return pd.DataFrame()

        start_date = enter_trade_indices[0]
        end_date = exit_trade_indices[-1] + 1

        if end_date <= start_date:
            return dataframe.iloc[start_date:end_date]

        dataframe.drop(dataframe.index[end_date + 1:], axis=0, inplace=True)
        dataframe.drop(dataframe.index[:start_date], axis=0, inplace=True)
        dataframe.dropna(subset=['enter_trade', 'exit_trade'], inplace=True, thresh=1)

        return dataframe

    @staticmethod
    def calculate_profit(buy_signals: list, sell_signals: list) -> float:
        """
            Calculates the profit
        """
        profit_percentage = sum((sell - buy) / buy * 100 for buy, sell in zip(buy_signals, sell_signals))
        return profit_percentage

    def process_trading_signals(self, dataframe: pd.DataFrame) -> None:
        """
            Process the trading signals by identifying buy and sell signals and storing them in separate lists.

            Args:
                dataframe (pd.DataFrame): The data on which the trading signals will be processed.
            Returns:
                A tuple of two lists: the buy signals and sell signals.
        """
        iteration = dataframe.iterrows()

        for buy_index, buy_trigger in iteration:
            if buy_trigger['enter_trade'] == 1:
                self.buy_signals.append(buy_trigger['close'])

                for sell_index, sell_trigger in iteration:
                    if sell_index > buy_index and sell_trigger['exit_trade'] == 1:
                        self.sell_signals.append(sell_trigger['close'])
                        break

        if len(self.buy_signals) > len(self.sell_signals):
            self.buy_signals.pop(-1)

    def evaluate_strategy(self, dataframe: pd.DataFrame) -> tuple:
        """
            Evaluate the trading strategy by calculating the Sharpe ratio and profit based on the buy and sell signals and market returns.

            Args:
                dataframe (pd.DataFrame): The data on which the trading signals will be evaluated.
            Returns:
                A tuple of three values: the negative Sharpe ratio, the positive Sharpe ratio, and the profit percentage.
        """
        self.buy_signals.clear()
        self.sell_signals.clear()

        self.process_trading_signals(dataframe)
        profit = self.calculate_profit(self.buy_signals, self.sell_signals)
        return -profit, profit

    def find_optimal_parameters(self, params: list) -> float:
        """
            Find the optimal parameters for the trading strategy by running gp_minimize optimization algorithm.

            Args:
                params (list): A list of the RSI buy and sell thresholds to test.
            Returns:
                The negative Sharpe ratio of the trading strategy.
        """
        buy_rsi, sell_rsi = params
        dataframe = self.dataframe.copy()

        dataframe = self.set_entry_conditions(buy_rsi)
        dataframe = self.set_exit_conditions(sell_rsi)

        filtered_dataframe = self.remove_extra_rows(dataframe)

        if filtered_dataframe.empty:
            return 1e9

        self.process_trading_signals(filtered_dataframe)
        neg_profit, profit = self.evaluate_strategy(filtered_dataframe)
        rounded_profit = round(profit, 2)

        # Check if the current profit is greater than the highest_profit
        if profit > self.highest_profit:
            self.highest_profit = profit
            print("Attempt with rsi_buy_threshold={}, rsi_sell_threshold={}, profit={}%".format(buy_rsi, sell_rsi,
                                                                                                rounded_profit))
        return neg_profit

    def optimize_trading_strategy(self, find_optimal_parameters, search_space):
        """
            Optimize the trading strategy by running the find_optimal_parameters method and returning the best parameters and evaluation metrics.

            Returns:
                A tuple of three values: the best parameters for the trading strategy, the best Sharpe ratio, and a message displaying the best parameters and evaluation metrics.
        """
        result = gp_minimize(
            func=find_optimal_parameters,
            dimensions=search_space,
            n_calls=300,
            n_random_starts=20,
            random_state=42,
            n_jobs=-1
        )

        best_params = result.x
        self.dataframe = self.set_entry_conditions(best_params[0])
        self.dataframe = self.set_exit_conditions(best_params[1])
        best_dataframe = self.remove_extra_rows(self.dataframe)

        if not best_dataframe.empty:
            _, best_profit = self.evaluate_strategy(best_dataframe)
            message = "Best parameters: rsi_buy_threshold={}, rsi_sell_threshold={}, profit={}%".format(
                best_params[0], best_params[1], round(best_profit, 2))
        else:
            best_profit = self.highest_profit
            message = "Best parameters: rsi_buy_threshold={}, rsi_sell_threshold={}, profit={}%".format(
                best_params[0], best_params[1], round(best_profit, 2))

        return best_params, best_profit, message


if __name__ == "__main__":
    backtester = Backtester(dataframe)

    print("Running Hyperopt. This could take a long time depending on the size of your dataframe.")
    best_params, best_profit, message = backtester.optimize_trading_strategy(
        backtester.find_optimal_parameters,
        Backtester.search_space
    )

    print(message)
