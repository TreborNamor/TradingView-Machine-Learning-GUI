from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
import time
import numpy as np
from TradeViewGUI import Main
from my_functions import Functions

url = 'https://www.tradingview.com/chart/'


class LongStoploss(Functions):

    def __init__(self):
        Main.__init__(self)
        self.driver = self.create_driver()
        self.run_script()

    def run_script(self):
        """find the best stop loss value."""

        # Loading Webpage.
        my_range = np.arange(float(self.minLongStoplossValue.text()), float(self.maxLongStoplossValue.text()), float(self.LongIncrementValue.text()))
        wait = WebDriverWait(self.driver, 10)
        try:
            self.driver.get(url)
        except Exception:
            print('WebDriver Error: Please Check Your FireFox Profile Path Is Correct.\n')
            print('Find Your Firefox Path Instructions. https://imgur.com/gallery/rdCqeT5 ')
        self.click_strategy_tester()
        try:
            self.click_overview()
        except NoSuchElementException:
            time.sleep(1)
            self.click_overview()
        print("Generating Max Profit For Stop Loss.")
        print("Loading script...\n")
        self.click_settings_button(wait)
        self.click_input_tab()
        self.click_enable_long_strategy_checkbox()
        self.click_rest_all_inputs()
        self.click_ok_button()

        # Searching for best stop loss for your strategy.
        for number in my_range:
            count = round(number, 2)
            try:
                self.click_settings_button(wait)
                self.click_long_stoploss_input(count, wait)
                self.get_net_profit_stoploss(count, wait)
            except (StaleElementReferenceException, TimeoutException, NoSuchElementException):
                print("script has timed out.")
                break

        # adding the best stop loss to your strategy on TradingView.
        self.click_settings_button(wait)
        best_key = self.find_best_stoploss()
        self.click_long_stoploss_input(best_key, wait)
        time.sleep(.5)

        # Printing Results of the best stop loss value found.
        print("\n----------Results----------\n")
        self.click_overview()
        self.print_best_stoploss()
        self.click_performance_summary()
        self.print_total_closed_trades()
        self.print_win_rate()
        self.print_net_profit()
        self.print_max_drawdown()
        self.print_sharpe_ratio()
        self.print_sortino_ratio()
        self.print_win_loss_ratio()
        self.print_avg_win_trade()
        self.print_avg_loss_trade()
        self.print_avg_bars_in_winning_trades()
        # print("\n----------More Results----------\n")
        # self.print_gross_profit()
        # self.print_gross_loss()
        # self.print_buy_and_hold_return()
        # self.print_max_contracts_held()
        # self.print_open_pl()
        # self.print_commission_paid()
        # self.print_total_open_trades()
        # self.print_number_winning_trades()
        # self.print_number_losing_trades()
        # self.print_percent_profitable()
        # self.print_avg_trade()
        # self.print_avg_win_trade()
        # self.print_avg_loss_trade()
        # self.print_largest_winning_trade()
        # self.print_largest_losing_trade()
        # self.print_avg_bars_in_trades()
        # self.print_avg_bars_in_winning_trades()
        # self.print_avg_bars_in_losing_trades()
        # self.print_margin_calls()
