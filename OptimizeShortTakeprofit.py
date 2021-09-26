import numpy as np
from selenium.common.exceptions import (NoSuchElementException,
                                        StaleElementReferenceException,
                                        TimeoutException)
from selenium.webdriver.support.ui import WebDriverWait

from my_functions import Functions
from TradeViewGUI import Main


class ShortTakeProfit(Functions):
    """find the best take profit values for your strategy."""

    def __init__(self):
        Main.__init__(self)
        self.driver = self.create_driver()
        self.run_script()

    def run_script(self):
        # Loading website with web driver.
        wait = WebDriverWait(self.driver, 15)
        try:
            self.driver.get("https://www.tradingview.com/chart/")
        except Exception:
            print(
                "WebDriver Error: Please Check Your FireFox Profile Path Is Correct.\n"
            )
            print(
                "Find Your Firefox Path Instructions. https://imgur.com/gallery/rdCqeT5 "
            )
            return

        # Making sure strategy tester tab is clicked so automation runs properly.
        try:
            self.click_strategy_tester(wait)
            self.click_overview()
        except NoSuchElementException:
            self.click_overview()
        print("Generating Max Profit For Stop Loss.")
        print("Loading script...\n")

        # Making sure we are on inputs tab and resetting values to default settings.
        self.click_settings_button(wait)
        self.click_input_tab()
        self.click_enable_short_strategy_checkbox()
        self.click_rest_all_inputs()
        self.click_ok_button()

        try:
            # Creating my range variable.
            my_range = np.arange(
                float(self.minShortTakeprofitValue.text()),
                float(self.maxShortTakeprofitValue.text()),
                float(self.ShortIncrementValue.text()),
            )

            # Increment through my range.
            for number in my_range:
                count = round(number, 2)
                try:
                    self.click_settings_button(wait)
                    self.click_short_takeprofit_input(count, wait)
                    self.get_net_profit_stoploss(count, wait)
                except (
                    StaleElementReferenceException,
                    TimeoutException,
                    NoSuchElementException,
                ) as error:
                    if error:
                        count -= 1
                        continue
        except ValueError:
            print(
                "\nValue Error: Make sure all available text input boxes are filled with a number for script to run properly.\n"
            )
            return

        # Adding the best parameters into your strategy.
        self.click_settings_button(wait)
        best_key = self.find_best_stoploss()
        self.click_short_takeprofit_input(best_key, wait)
        self.driver.implicitly_wait(1)

        print("\n----------Results----------\n")
        self.click_overview()
        self.print_best_takeprofit()
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
