import unittest
import pandas as pd
from unittest.mock import patch
from max_profit import Backtester
import numpy as np


class TestBacktester(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the dataset
        cls.dataframe = pd.read_csv('datasets/SPY_DATA_20_YEARS/SPX_1day.csv')
        cls.dataframe.dropna(inplace=True)

    def setUp(self):
        self.backtester = Backtester(self.dataframe)

    def test_generate_indicators(self):
        self.backtester.generate_indicators()
        self.assertTrue('MACD' in self.backtester.dataframe.columns)
        self.assertTrue('Signal' in self.backtester.dataframe.columns)
        self.assertTrue('RSI' in self.backtester.dataframe.columns)

    def test_set_entry_conditions(self):
        self.backtester.set_entry_conditions(30)
        self.assertTrue(np.isin(self.backtester.dataframe['enter_trade'].values, [0, 1]).all())

    def test_set_exit_conditions(self):
        self.backtester = Backtester(self.dataframe)
        self.backtester.generate_indicators()
        self.backtester.set_entry_conditions(30)
        self.backtester.set_exit_conditions(70)
        self.assertTrue(np.isin(self.backtester.dataframe['enter_trade'].values, [0, 1]).all())

    def test_remove_extra_rows(self):
        self.backtester.generate_indicators()
        self.backtester.set_entry_conditions(30)
        self.backtester.set_exit_conditions(70)
        is_valid = self.backtester.remove_extra_rows(self.backtester.dataframe)
        self.assertTrue(is_valid)

    def test_calculate_profit(self):
        buy_signals = [10, 20, 30]
        sell_signals = [15, 25, 35]
        profit_percentage = self.backtester.calculate_profit(buy_signals, sell_signals)
        print(profit_percentage)
        self.assertEqual(profit_percentage, 50)

    def test_process_trading_signals(self):
        self.backtester.generate_indicators()
        self.backtester.set_entry_conditions(30)
        self.backtester.set_exit_conditions(70)
        self.backtester.remove_extra_rows(self.backtester.dataframe)
        self.backtester.process_trading_signals(self.backtester.dataframe)
        self.assertTrue(isinstance(self.backtester.buy_signals, list))
        self.assertTrue(isinstance(self.backtester.sell_signals, list))

    def test_evaluate_strategy(self):
        self.backtester.generate_indicators()
        self.backtester.set_entry_conditions(30)
        self.backtester.set_exit_conditions(70)
        self.backtester.remove_extra_rows(self.backtester.dataframe)
        neg_profit, profit = self.backtester.evaluate_strategy(self.backtester.dataframe)
        self.assertTrue(isinstance(neg_profit, float))
        self.assertTrue(isinstance(profit, float))

    @patch('backtester.gp_minimize', return_value=([20, 80], 10, 'Optimization successful'))
    def test_optimize_trading_strategy(self, mock_gp_minimize):
        best_params, best_profit, message = self.backtester.optimize_trading_strategy(
            self.backtester.find_optimal_parameters,
            Backtester.search_space
        )
        self.assertEqual(best_params, [20, 80])
        self.assertEqual(best_profit, 10)
        self.assertEqual(message, 'Optimization successful')


if __name__ == '__main__':
    unittest.main()
