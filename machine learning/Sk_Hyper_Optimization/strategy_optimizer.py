"""This script uses the Scikit-Optimize library (skopt) to optimize the buy and sell thresholds of a trading strategy
based on the Relative Strength Index (RSI) and Moving Average Convergence Divergence (MACD) indicators. The script
reads in a CSV file containing financial data, applies the trading strategy to generate buy and sell signals,
and backtests the results to calculate the profit percentage. The script defines functions to populate the
'enter_trade' and 'exit_trade' columns of the dataset, filter out data before the first buy signal and after the last
sell signal, calculate the total profit percentage, and perform backtesting on the given dataset. Finally,
the script uses the gp_minimize function from skopt to search for the best parameters for the trading strategy using
a Bayesian optimization algorithm. The best parameters are used to generate the best profit and print the result. """
import pandas as pd
from skopt.space import Integer
from skopt import gp_minimize

# Read the dataset and initialize the enter_trade and exit_trade columns
DataFrame = pd.read_csv('../datasets/BATS SPY, 1D.csv')
DataFrame.dropna(inplace=True)  # Remove rows with missing data
DataFrame['enter_trade'] = 0
DataFrame['exit_trade'] = 0

# Buy and sell signals will be stored in these lists
buy_signals = list()
sell_signals = list()

# Parameter search space for Skopt optimization
search_space = [
    Integer(low=5, high=50, name='buy_rsi_value'),
    Integer(low=50, high=100, name='sell_rsi_value'),
]


def populate_entry_trend(dataframe: pd.DataFrame, buy_rsi: int) -> pd.DataFrame:
    """
    Populate the 'enter_trade' column with 1 where the following conditions are met:
    1. MACD crosses above the Signal line.
    2. At least one of the last 5 RSI values is less than or equal to the buy_rsi value.
    """
    macd_crosses_signal = (dataframe['MACD'].shift(1) < dataframe['Signal'].shift(1)) & (
                dataframe['MACD'] > dataframe['Signal'])
    rsi_condition = dataframe['RSI'].rolling(5).min() <= buy_rsi
    dataframe.loc[macd_crosses_signal & rsi_condition, 'enter_trade'] = 1
    return dataframe


def populate_exit_trend(dataframe: pd.DataFrame, sell_rsi: int) -> pd.DataFrame:
    """
    Populate the 'exit_trade' column with 1 where the following conditions are met:
    1. MACD crosses below the Signal line.
    2. At least one of the last 5 RSI values is greater than or equal to the sell_rsi value.
    """
    macd_crosses_under_signal = (dataframe['MACD'].shift(1) > dataframe['Signal'].shift(1)) & (
                dataframe['MACD'] < dataframe['Signal'])
    rsi_condition = dataframe['RSI'].rolling(5).max() >= sell_rsi
    dataframe.loc[macd_crosses_under_signal & rsi_condition, 'exit_trade'] = 1
    return dataframe


def filter_trades(dataframe: pd.DataFrame) -> bool:
    """
    Filter out the data before the first buy signal and data after the last sell signal.
    Also, drop NaN data between buy and sell signals.
    """
    enter_trade_indices = dataframe[dataframe['enter_trade'] == 1].index
    exit_trade_indices = dataframe[dataframe['exit_trade'] == 1].index

    if len(enter_trade_indices) == 0 or len(exit_trade_indices) == 0:
        return False

    start_date = enter_trade_indices[0]
    end_date = exit_trade_indices[-1] + 1

    dataframe.drop(dataframe.index[end_date:], axis=0, inplace=True)
    dataframe.drop(dataframe.index[:start_date], axis=0, inplace=True)
    dataframe.dropna(subset=['enter_trade', 'exit_trade'], inplace=True, thresh=1)

    return True


def calculate_profit(buy_signals: list, sell_signals: list) -> float:
    """Calculate the total profit percentage for a given set of buy and sell signals."""
    profit_percentage = sum((sell - buy) / buy * 100 for buy, sell in zip(buy_signals, sell_signals))
    return profit_percentage


def process_trades(dataframe: pd.DataFrame) -> None:
    """
    Process buy and sell signals to build buy_signals and sell_signals lists.
    Ignore future buy signals until the current trade gets a sell signal.
    """
    iteration = dataframe.iterrows()

    for buy_index, buy_trigger in iteration:
        if buy_trigger['enter_trade'] == 1:
            buy_signals.append(buy_trigger['close'])

            for sell_index, sell_trigger in iteration:
                if sell_index > buy_index and sell_trigger['exit_trade'] == 1:
                    sell_signals.append(sell_trigger['close'])
                    break

    # Remove the last buy signal if there are more buy signals than sell signals
    if len(buy_signals) > len(sell_signals):
        buy_signals.pop(-1)


def backtesting(dataframe: pd.DataFrame) -> tuple:
    """Perform backtesting on the given dataframe and return negative profit and profit as a tuple."""
    buy_signals.clear()
    sell_signals.clear()

    process_trades(dataframe)
    profit = calculate_profit(buy_signals, sell_signals)
    return -profit, profit


def objective(params: list) -> float:
    """Objective function to be minimized during optimization."""
    buy_rsi, sell_rsi = params
    dataframe = DataFrame.copy()

    populate_entry_trend(dataframe, buy_rsi)
    populate_exit_trend(dataframe, sell_rsi)

    is_valid = filter_trades(dataframe)

    if not is_valid:
        return -1e9

    process_trades(dataframe)
    neg_profit, _ = backtesting(dataframe)

    return neg_profit


result = gp_minimize(
    func=objective,
    dimensions=search_space,
    n_calls=300,  # Number of iterations
    n_random_starts=20,  # Number of random points before starting optimization
    random_state=42  # Fix random state for reproducibility
)

best_params = result.x
_, best_profit = backtesting(DataFrame.copy())

# Get the profit for the best parameters
best_dataframe = DataFrame.copy()
populate_entry_trend(best_dataframe, best_params[0])
populate_exit_trend(best_dataframe, best_params[1])
is_valid = filter_trades(best_dataframe)

if is_valid:
    _, best_profit = backtesting(best_dataframe)
    print("Best parameters: buy_rsi_value={}, sell_rsi_value={}, profit={}".format(best_params[0], best_params[1],
                                                                                   best_profit))
else:
    print("Best parameters: buy_rsi_value={}, sell_rsi_value={}, profit not available due to empty DataFrame".format(
        best_params[0], best_params[1]))
