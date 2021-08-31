from TradeViewGUI import Main
import random
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
import time
from profit import profits
from my_functions import Functions

url = 'https://www.tradingview.com/chart/'


class LongShortScript(Functions):

    def __init__(self):
        Main.__init__(self)
        self.driver = self.create_driver()
        self.run_script()

    def run_script(self):
        """find the best stop loss value."""
        wait = WebDriverWait(self.driver, 15)
        try:
            self.driver.get(url)
        except Exception:
            print('WebDriver Error: Please Check Your FireFox Profile Path Is Correct.\n')
            print('Find Your Firefox Path Instructions. https://imgur.com/gallery/rdCqeT5 ')
            return
        time.sleep(1)
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
        self.click_enable_both_checkboxes()
        self.click_rest_all_inputs()
        self.click_ok_button()

        count = 0
        try:
            while count < int(self.maxAttemptsValue.text()):
                try:
                    count += 1
                    long_stoploss_value = round(
                        random.uniform(float(self.minLongStoplossValue.text()), float(self.maxLongStoplossValue.text())),
                        int(self.decimalPlaceValue.text()))
                    long_takeprofit_value = round(
                        random.uniform(float(self.minLongTakeprofitValue.text()), float(self.maxLongTakeprofitValue.text())),
                        int(self.decimalPlaceValue.text()))
                    short_stoploss_value = round(
                        random.uniform(float(self.minShortStoplossValue.text()), float(self.maxShortStoplossValue.text())),
                        int(self.decimalPlaceValue.text()))
                    short_takeprofit_value = round(
                        random.uniform(float(self.minShortTakeprofitValue.text()), float(self.maxShortTakeprofitValue.text())),
                        int(self.decimalPlaceValue.text()))

                    # click settings button
                    self.click_settings_button(wait)

                    # click both input boxes and add values.
                    self.click_all_inputs(long_stoploss_value, long_takeprofit_value, short_stoploss_value,
                                          short_takeprofit_value, wait)

                    # extract the net profit percentage.
                    self.get_net_all(long_stoploss_value, long_takeprofit_value, short_stoploss_value, short_takeprofit_value, wait)
                except (StaleElementReferenceException, TimeoutException, NoSuchElementException):
                    continue
        except ValueError:
            print("\nValue Error: Make sure all available text input boxes are filled with a number for script to run properly.\n")
            return

        # adding new parameters to your strategy.
        self.click_settings_button(wait)
        best_key = self.find_best_key_both()
        self.click_all_inputs(profits[best_key][1], profits[best_key][3], profits[best_key][5], profits[best_key][7],
                              wait)
        time.sleep(.5)

        print("\n----------Results----------\n")
        self.click_overview()
        self.print_best_all()
        self.click_performance_summary()
        self.print_total_closed_trades()
        self.print_net_profit()
        self.print_win_rate()
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
