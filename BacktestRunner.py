import random

from selenium.common.exceptions import (NoSuchElementException,
                                        StaleElementReferenceException,
                                        TimeoutException)
from selenium.webdriver.support.ui import WebDriverWait

from my_functions import TvGetter
from profit import profits


class BacktestRunner:
    """find the best stop loss and take profit values for your strategy."""

    def __init__(self, driver, indicator_params_config):
        self.driver = driver
        self.tvGetter = TvGetter(driver)
        self.run_script(indicator_params_config)

    def run_script(self, indicator_params_config):
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
            self.tvGetter.click_strategy_tester(wait)
            self.tvGetter.click_overview()
        except NoSuchElementException:
            self.tvGetter.click_overview()
        print("Generating Max Profit For Stop Loss.")
        print("Loading script...\n")

        # Making sure we are on inputs tab and resetting values to default settings.
        self.tvGetter.click_settings_button(wait)
        self.tvGetter.click_input_tab()
        self.tvGetter.click_enable_both_checkboxes()
        self.tvGetter.click_rest_all_inputs()
        self.tvGetter.click_ok_button()
        # Click all input boxes and add new values.
        self.tvGetter.backtest_strategy(indicator_params_config, wait)
        # Adding the best parameters into your strategy.
        self.tvGetter.click_settings_button(wait)
        best_key = self.tvGetter.find_best_key_both()
        self.tvGetter.backtest_strategy(profits[best_key], wait)
        self.driver.implicitly_wait(1)

        print("\n----------Results----------\n")
        self.tvGetter.click_overview()
        self.tvGetter.print_best_all()
        self.tvGetter.click_performance_summary()
        self.tvGetter.print_total_closed_trades()
        self.tvGetter.print_net_profit()
        self.tvGetter.print_win_rate()
        self.tvGetter.print_max_drawdown()
        self.tvGetter.print_sharpe_ratio()
        self.tvGetter.print_sortino_ratio()
        self.tvGetter.print_win_loss_ratio()
        self.tvGetter.print_avg_win_trade()
        self.tvGetter.print_avg_loss_trade()
        self.tvGetter.print_avg_bars_in_winning_trades()
        # print("\n----------More Results----------\n")
        # self.tvGetter.print_gross_profit()
        # self.tvGetter.print_gross_loss()
        # self.tvGetter.print_buy_and_hold_return()
        # self.tvGetter.print_max_contracts_held()
        # self.tvGetter.print_open_pl()
        # self.tvGetter.print_commission_paid()
        # self.tvGetter.print_total_open_trades()
        # self.tvGetter.print_number_winning_trades()
        # self.tvGetter.print_number_losing_trades()
        # self.tvGetter.print_percent_profitable()
        # self.tvGetter.print_avg_trade()
        # self.tvGetter.print_avg_win_trade()
        # self.tvGetter.print_avg_loss_trade()
        # self.tvGetter.print_largest_winning_trade()
        # self.tvGetter.print_largest_losing_trade()
        # self.tvGetter.print_avg_bars_in_trades()
        # self.tvGetter.print_avg_bars_in_winning_trades()
        # self.tvGetter.print_avg_bars_in_losing_trades()
        # self.tvGetter.print_margin_calls()
