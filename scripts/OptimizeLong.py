import time
import random
from web_commands.commands import Functions
from web_commands.profit import profits
from TradeViewGUI import Main
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.support.ui import WebDriverWait


class LongScript(Functions):
    """Find the best stop loss and take profit values for your strategy."""

    def __init__(self):
        Main.__init__(self)
        self.driver = self.create_driver()
        self.run_script()

    def run_script(self):
        print("Loading script...\n")
        wait = WebDriverWait(self.driver, 15)
        self.get_webpage()

        # Click the Strategy Tester tab to ensure proper automation.
        self.click_strategy_tester(wait)
        self.click_overview(wait)

        # Click the settings button, select the inputs tab, and reset to default settings.
        self.click_settings_button(wait)
        self.click_input_tab()
        self.click_enable_long_strategy_checkbox()
        self.click_reset_all_inputs(wait)
        self.click_ok_button()

        # Loop through max attempts while randomizing values each attempt.
        count = 0
        try:
            while count < int(self.maxAttemptsValue.text()):
                try:
                    count += 1

                    # Create random stoploss and takeprofit values every loop.
                    stoploss_value = round(
                        random.uniform(
                            float(self.minLongStoplossValue.text()),
                            float(self.maxLongStoplossValue.text()),
                        ),
                        int(self.decimalPlaceValue.text()),
                    )
                    takeprofit_value = round(
                        random.uniform(
                            float(self.minLongTakeprofitValue.text()),
                            float(self.maxLongTakeprofitValue.text()),
                        ),
                        int(self.decimalPlaceValue.text()),
                    )

                    # Click the settings button and update input values.
                    self.click_settings_button(wait)
                    self.click_long_inputs(stoploss_value, takeprofit_value, wait)

                    # Allow time for webpage data to refresh.
                    time.sleep(1)

                    # Save the profitability of the new values into a dictionary.
                    self.get_net_both(stoploss_value, takeprofit_value, wait)

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
                "\nValue Error: Ensure all text input boxes are filled with a number for the script to run properly.\n"
            )
            return

        # Add the best parameters to your strategy.
        self.click_settings_button(wait)
        best_key = self.find_best_key_both()
        self.click_long_inputs(profits[best_key][1], profits[best_key][3], wait)
        self.driver.implicitly_wait(1)

        # Print results.
        print("\n----------Results----------\n")
        self.click_overview(wait)
        self.print_best_both()
        self.click_performance_summary(wait)
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
